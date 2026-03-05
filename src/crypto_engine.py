# -*- coding: utf-8 -*-
"""
CryptoEngine — Core cryptographic primitives for Secure-IIoT-DCOPA
==================================================================
Implements ECDSA (signing/verification), ECDH (key agreement),
and ChaCha20-Poly1305 (authenticated encryption) as described in
Sections 5.1–5.3 of the paper.

This module corresponds to:
  - Algorithm 3  : ECDH Key Exchange (Phase 3)
  - Algorithm 5  : CH Candidacy Announcement (ECDSA signature)
  - Algorithm 8  : Secure Data Transmission (ChaCha20-Poly1305)

Authors: Souadih Kamal, Mir Foudil, Meziane Farid
License: MIT (reproducibility package only)
"""

import hashlib
import secrets
import json
import base64
from collections import defaultdict, deque
from typing import Tuple, Dict, Optional

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    raise ImportError(
        "The 'cryptography' library is required. Install it with:\n"
        "  pip install cryptography"
    )


class CryptoEngine:
    """
    Lightweight cryptographic engine for Secure-IIoT-DCOPA.

    Provides:
      - ECDSA key generation, signing, and verification (secp256r1)
      - ECDH shared key derivation with HKDF
      - ChaCha20-Poly1305 authenticated encryption/decryption
      - Anti-replay protection via nonce window

    Parameters
    ----------
    nonce_window_size : int
        Number of recent nonces tracked per node for replay detection.
        Default: 50 (matches paper parameter N_nonce).
    """

    CURVE = ec.SECP256R1()
    KDF_INFO = b'SecureIIoTDCOPA_v1_KeyDerivation'

    def __init__(self, nonce_window_size: int = 50):
        self._key_cache: Dict[int, Tuple] = {}
        self._nonce_windows: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=nonce_window_size)
        )
        self.nonce_window_size = nonce_window_size

    # ------------------------------------------------------------------
    # Key Management
    # ------------------------------------------------------------------

    def generate_key_pair(
        self, node_id: int
    ) -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        """
        Generate (or retrieve cached) ECDSA/ECDH key pair for a node.

        All nodes, including the Base Station (node_id=-1), use secp256r1.
        """
        if node_id not in self._key_cache:
            priv = ec.generate_private_key(self.CURVE)
            self._key_cache[node_id] = (priv, priv.public_key())
        return self._key_cache[node_id]

    def renew_key_pair(
        self, node_id: int
    ) -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        """
        Renew key pair for forward secrecy (triggered every
        `key_renewal_interval` rounds, as per Section 5.1).
        """
        self._key_cache.pop(node_id, None)
        self._nonce_windows[node_id].clear()
        return self.generate_key_pair(node_id)

    # ------------------------------------------------------------------
    # ECDH Key Agreement (Algorithm 3)
    # ------------------------------------------------------------------

    def derive_shared_key(
        self,
        private_key: ec.EllipticCurvePrivateKey,
        peer_public_key: ec.EllipticCurvePublicKey,
    ) -> bytes:
        """
        Derive a 256-bit shared session key via ECDH + HKDF-SHA256.

        This implements the key agreement in Phase 3 of the protocol
        (Algorithm 3 of the paper). The derived key is used directly
        by ChaCha20-Poly1305.
        """
        raw_shared = private_key.exchange(ec.ECDH(), peer_public_key)
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=self.KDF_INFO,
        ).derive(raw_shared)

    # ------------------------------------------------------------------
    # ECDSA Signing / Verification (Algorithm 5)
    # ------------------------------------------------------------------

    def sign_message(
        self,
        private_key: ec.EllipticCurvePrivateKey,
        message: bytes,
    ) -> bytes:
        """
        Sign a message with ECDSA-SHA256.

        A fresh 16-byte nonce is prepended to the message before signing
        to ensure signature uniqueness even for identical payloads.

        Returns
        -------
        bytes
            nonce (16 bytes) + DER-encoded ECDSA signature.
        """
        nonce = secrets.token_bytes(16)
        payload = nonce + message
        signature = private_key.sign(payload, ec.ECDSA(hashes.SHA256()))
        return nonce + signature

    def verify_signature(
        self,
        public_key: ec.EllipticCurvePublicKey,
        message: bytes,
        signed_blob: bytes,
        sender_id: int = -1,
    ) -> bool:
        """
        Verify an ECDSA-SHA256 signature with anti-replay protection.

        Parameters
        ----------
        signed_blob : bytes
            Output of sign_message(): nonce (16 bytes) + DER signature.
        sender_id : int
            Used for per-sender nonce tracking (replay detection).
        """
        if len(signed_blob) < 17:
            return False
        nonce = signed_blob[:16]
        signature = signed_blob[16:]

        # Anti-replay: reject if nonce already seen from this sender
        nonce_hash = hashlib.sha256(nonce).hexdigest()
        if nonce_hash in self._nonce_windows[sender_id]:
            return False  # Replay attack detected
        self._nonce_windows[sender_id].append(nonce_hash)

        try:
            payload = nonce + message
            public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # ChaCha20-Poly1305 Authenticated Encryption (Algorithm 8)
    # ------------------------------------------------------------------

    def encrypt(self, key: bytes, plaintext: bytes, aad: bytes = b'') -> bytes:
        """
        Encrypt plaintext using ChaCha20-Poly1305.

        Parameters
        ----------
        key : bytes
            32-byte session key (output of derive_shared_key).
        plaintext : bytes
            Data to encrypt.
        aad : bytes
            Additional authenticated data (e.g., packet header).

        Returns
        -------
        bytes
            12-byte nonce + ciphertext+tag.
        """
        cipher = ChaCha20Poly1305(key)
        nonce = secrets.token_bytes(12)
        return nonce + cipher.encrypt(nonce, plaintext, aad)

    def decrypt(
        self, key: bytes, ciphertext_blob: bytes, aad: bytes = b''
    ) -> Optional[bytes]:
        """
        Decrypt and authenticate a ChaCha20-Poly1305 ciphertext.

        Returns None if authentication fails (tampering detected).
        """
        if len(ciphertext_blob) < 13:
            return None
        try:
            cipher = ChaCha20Poly1305(key)
            nonce = ciphertext_blob[:12]
            return cipher.decrypt(nonce, ciphertext_blob[12:], aad)
        except Exception:
            return None  # Authentication tag mismatch — tampered packet

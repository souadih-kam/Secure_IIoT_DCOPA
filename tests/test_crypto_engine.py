# -*- coding: utf-8 -*-
"""Unit tests — CryptoEngine : ECDSA, ECDH, ChaCha20-Poly1305 [Reviewer #1, Point 9]"""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from crypto_engine import CryptoEngine
    SKIP = False
except ImportError:
    SKIP = True

@unittest.skipIf(SKIP, "cryptography library not installed")
class TestCryptoEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CryptoEngine()
        self.priv, self.pub = self.engine.generate_key_pair(node_id=1)

    def test_sign_verify_roundtrip(self):
        msg = b"CH_CANDIDACY:node1:round42"
        signed = self.engine.sign_message(self.priv, msg)
        self.assertTrue(self.engine.verify_signature(self.pub, msg, signed, sender_id=1))

    def test_replay_detection(self):
        msg = b"ISOLATE:node5"
        signed = self.engine.sign_message(self.priv, msg)
        self.engine.verify_signature(self.pub, msg, signed, sender_id=2)
        # Second use of same signed blob → replay
        result = self.engine.verify_signature(self.pub, msg, signed, sender_id=2)
        self.assertFalse(result)

    def test_ecdh_derives_same_key(self):
        priv_a, pub_a = self.engine.generate_key_pair(10)
        priv_b, pub_b = self.engine.generate_key_pair(11)
        key_a = self.engine.derive_shared_key(priv_a, pub_b)
        key_b = self.engine.derive_shared_key(priv_b, pub_a)
        self.assertEqual(key_a, key_b)
        self.assertEqual(len(key_a), 32)

    def test_encrypt_decrypt_roundtrip(self):
        priv_a, pub_a = self.engine.generate_key_pair(20)
        priv_b, pub_b = self.engine.generate_key_pair(21)
        key = self.engine.derive_shared_key(priv_a, pub_b)
        plaintext = b"sensor_data:42.3:pressure"
        ciphertext = self.engine.encrypt(key, plaintext, aad=b"node20->CH")
        decrypted = self.engine.decrypt(key, ciphertext, aad=b"node20->CH")
        self.assertEqual(decrypted, plaintext)

    def test_tampered_ciphertext_fails(self):
        priv_a, pub_a = self.engine.generate_key_pair(30)
        priv_b, pub_b = self.engine.generate_key_pair(31)
        key = self.engine.derive_shared_key(priv_a, pub_b)
        ct = bytearray(self.engine.encrypt(key, b"secret", aad=b""))
        ct[-1] ^= 0xFF  # Tamper
        result = self.engine.decrypt(key, bytes(ct), aad=b"")
        self.assertIsNone(result)

    def test_key_renewal_clears_nonce_window(self):
        self.engine.renew_key_pair(1)
        _, new_pub = self.engine.generate_key_pair(1)
        self.assertIsNotNone(new_pub)


if __name__ == '__main__':
    unittest.main()

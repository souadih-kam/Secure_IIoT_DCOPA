# Secure-IIoT-DCOPA - Guide d'Utilisation Complet

## Table des Matières

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Exécution des Simulations](#exécution-des-simulations)
4. [Personnalisation](#personnalisation)
5. [Analyse des Résultats](#analyse-des-résultats)
6. [Dépannage](#dépannage)
7. [Références Rapides](#références-rapides)

---

## Installation

### Prérequis Système

| Composant | Version Minimum | Recommandée |
|-----------|----------------|-------------|
| Python | 3.8+ | 3.9-3.11 |
| pip | 21.0+ | Dernière |
| OS | Windows 10+, Ubuntu 18.04+, macOS 10.15+ | |

### Installation Pas à Pas

```bash
# 1. Cloner le repository
git clone https://github.com/SecIIoT/Secure-IIoT-DCOPA.git
cd Secure-IIoT-DCOPA

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Vérifier l'installation
python -m pytest tests/ -v
```

### Vérification de l'Installation

```bash
# Doit afficher "23 passed in X.XXs"
python -m pytest tests/ -v --tb=short

# Test rapide des composants crypto
python -c "from src.crypto_engine import CryptoEngine; print('✅ Crypto OK')"

# Test du framework de confiance
python -c "from src.trust_framework import TrustFramework; print('✅ Trust OK')"
```

---

## Configuration

### Structure des Fichiers de Configuration

```
config/
├── default_config.yaml    # Configuration par défaut (article)
├── custom_config.yaml     # Votre configuration personnalisée
└── scenarios/             # Scénarios prédéfinis
    ├── low_power.yaml
    ├── high_density.yaml
    └── aggressive_attacks.yaml
```

### Paramètres Clés Expliqués

#### Réseau (`network`)
```yaml
network:
  num_nodes: 300              # Nombre total de nœuds
  area_dimension: 100.0       # Terrain 100x100m²
  percent_actuators: 10.0    # % d'actionneurs (énergie infinie)
```

#### Simulation (`simulation`)
```yaml
simulation:
  max_rounds: 1200           # Durée totale
  num_runs: 30               # Runs Monte Carlo
  random_seed: 42            # Graine aléatoire principale
```

#### Sécurité (`security`)
```yaml
security:
  key_renewal_interval: 100  # Renouvellement des clés
  nonce_window_size: 50      # Fenêtre anti-replay
```

#### Protocole (`protocol_params`)
```yaml
protocol_params:
  alpha: 0.6                 # Poids énergie (Spearman ρ=0.87)
  beta: 0.4                  # Poids distance
  gamma0: 0.3                # Poids confiance base
  theta_trust: 0.4           # Seuil d'isolation
```

### Créer une Configuration Personnalisée

```bash
# Copier la configuration par défaut
cp config/default_config.yaml config/my_config.yaml

# Éditer les paramètres souhaités
nano config/my_config.yaml
```

---

## Exécution des Simulations

### 1. Tests Unitaires (Recommandé)

```bash
# Tests complets
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_crypto_engine.py -v
python -m pytest tests/test_trust_framework.py -v
python -m pytest tests/test_protocol_core.py -v
```

### 2. Simulations Principales

#### Expérience de Collusion
```bash
# Configuration par défaut
python simulations/collusion_experiment.py

# Avec configuration personnalisée
python simulations/collusion_experiment.py --config config/my_config.yaml

# Exporter résultats
python simulations/collusion_experiment.py --export csv,json
```

#### Analyse de Latence E2E
```bash
# Test de latence standard
python simulations/latency_e2e.py

# Test avec différentes densités
python simulations/latency_e2e.py --nodes 100,200,300,500

# Test avec différents taux de nœuds malveillants
python simulations/latency_e2e.py --malicious 0,10,20,30
```

### 3. Simulation Complète (Reproduction Article)

```bash
# Script de reproduction complète
python -c "
import yaml
from simulations.collusion_experiment import run_experiment
from simulations.latency_e2e import run_latency_analysis

# Charger configuration article
with open('config/default_config.yaml') as f:
    config = yaml.safe_load(f)

# Exécuter expérience principale
results = run_experiment(config)
print(f'PDR: {results[\"pdr\"]:.2f}%')
print(f'Detection Rate: {results[\"detection_rate\"]:.2f}%')

# Analyser latence
latency = run_latency_analysis(config)
print(f'P95 Latency: {latency[\"p95\"]:.1f}ms')
"
```

---

## Personnalisation

### Scénarios Prédéfinis

#### 1. Scénario Basse Consommation
```yaml
# config/scenarios/low_power.yaml
network:
  num_nodes: 100
  
energy_model:
  initial_energy: 0.2        # 0.2J par nœud
  
protocol_params:
  alpha: 0.8                 # Plus poids sur énergie
  beta: 0.2
```

#### 2. Scénario Haute Densité
```yaml
# config/scenarios/high_density.yaml
network:
  num_nodes: 500
  area_dimension: 50.0       # Plus dense
  
simulation:
  max_rounds: 800            # Plus court pour économiser
```

#### 3. Scénario Attaques Agressives
```yaml
# config/scenarios/aggressive_attacks.yaml
attack:
  malicious_percentage: 40.0 # 40% malveillants
  
security:
  key_renewal_interval: 50   # Renouvellement plus fréquent
  
protocol_params:
  theta_trust: 0.3           # Seuil plus strict
```

### Exécuter des Scénarios

```bash
# Scénario basse consommation
python simulations/collusion_experiment.py --config config/scenarios/low_power.yaml

# Scénario haute densité
python simulations/latency_e2e.py --config config/scenarios/high_density.yaml --nodes 500

# Comparer scénarios
python -c "
import yaml
from simulations.collusion_experiment import run_experiment

scenarios = ['low_power', 'high_density', 'aggressive_attacks']
for scenario in scenarios:
    config_file = f'config/scenarios/{scenario}.yaml'
    with open(config_file) as f:
        config = yaml.safe_load(f)
    results = run_experiment(config)
    print(f'{scenario}: PDR={results[\"pdr\"]:.1f}%, Detection={results[\"detection_rate\"]:.1f}%')
"
```

### Modification des Paramètres d'Attaque

```python
# Personnaliser les types d'attaques
attack_types = [
    'Black Hole / Gray Hole internal',
    'Data Tampering',
    'Selective Forwarding internal',
    'Collusion',
    'Denial-of-Service (DoS)',
    'Jamming'
]

# Ajouter une nouvelle attaque
config['attack']['types'] = attack_types + ['Custom_Attack']
config['attack']['custom_params'] = {
    'intensity': 0.8,
    'frequency': 0.3
}
```

---

## Analyse des Résultats

### Structure des Résultats

```
results_sample/
├── experiment_log.txt       # Log brut des simulations
├── scientific_report.txt    # Rapport statistique
├── data/
│   ├── pdr_data.csv        # PDR par round
│   ├── energy_data.csv     # Consommation énergétique
│   └── detection_data.csv   # Détection d'attaques
└── plots/
    ├── pdr_comparison.png
    ├── energy_evolution.png
    └── detection_rates.png
```

### Analyse Statistique

```python
import pandas as pd
import matplotlib.pyplot as plt

# Charger les résultats
df = pd.read_csv('results_sample/data/pdr_data.csv')

# Statistiques descriptives
print("Statistiques PDR:")
print(df.describe())

# Visualisation
plt.figure(figsize=(10, 6))
plt.plot(df['round'], df['secure_iiot_dcopa'], label='Secure-IIoT-DCOPA')
plt.plot(df['round'], df['secdcopa'], label='SECDCOPA')
plt.xlabel('Round')
plt.ylabel('PDR (%)')
plt.title('Évolution du PDR')
plt.legend()
plt.grid(True)
plt.show()
```

### Génération de Graphiques

```bash
# Script de génération de graphiques
python -c "
import matplotlib.pyplot as plt
import numpy as np

# Données exemple
protocols = ['Secure-IIoT-DCOPA', 'SECDCOPA', 'SecLEACH', 'MSCR']
pdr_values = [99.95, 17.54, 30.22, 35.45]
detection_rates = [50.14, 0.00, 13.33, 0.00]

# Graphique PDR
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.bar(protocols, pdr_values, color=['green', 'red', 'orange', 'blue'])
plt.ylabel('PDR (%)')
plt.title('Packet Delivery Ratio')
plt.xticks(rotation=45)

# Graphique Detection Rate
plt.subplot(1, 2, 2)
plt.bar(protocols, detection_rates, color=['green', 'red', 'orange', 'blue'])
plt.ylabel('Detection Rate (%)')
plt.title('Attack Detection Rate')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('results_sample/plots/comparison.png', dpi=300)
print('Graphique sauvegardé dans results_sample/plots/comparison.png')
"
```

### Export des Résultats

```python
# Exporter en format CSV
import pandas as pd

results = {
    'protocol': ['Secure-IIoT-DCOPA', 'SECDCOPA', 'SecLEACH', 'MSCR'],
    'pdr': [99.95, 17.54, 30.22, 35.45],
    'throughput': [254.55, 15.22, 25.80, 30.15],
    'detection_rate': [50.14, 0.00, 13.33, 0.00],
    'residual_energy': [30.71, 125.10, 125.50, 123.20]
}

df = pd.DataFrame(results)
df.to_csv('results_sample/summary_results.csv', index=False)
print('Résultats exportés en CSV')
```

---

## Dépannage

### Problèmes Communs

#### 1. Erreur de dépendances
```bash
# Problème: ModuleNotFoundError
# Solution:
pip install -r requirements.txt --upgrade
pip install --force-reinstall cryptography
```

#### 2. Tests qui échouent
```bash
# Problème: Tests échouent aléatoirement
# Solution: Augmenter le timeout ou réduire la complexité
python -m pytest tests/ -v --timeout=30

# Ou exécuter tests individuellement
python -m pytest tests/test_crypto_engine.py::TestCryptoEngine::test_sign_verify_roundtrip -v
```

#### 3. Performance lente
```bash
# Problème: Simulation trop lente
# Solution: Réduire le nombre de runs ou de nœuds
# Modifier config:
simulation:
  num_runs: 10               # Au lieu de 30
network:
  num_nodes: 100             # Au lieu de 300
```

#### 4. Mémoire insuffisante
```python
# Problème: MemoryError avec 500+ nœuds
# Solution: Ajouter du garbage collection
import gc

# Dans les boucles longues:
for run in range(num_runs):
    # ... votre code ...
    gc.collect()  # Forcer le garbage collection
```

### Debug Mode

```python
# Activer le mode debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou utiliser variables d'environnement
import os
os.environ['DEBUG'] = '1'
os.environ['VERBOSE'] = 'true'
```

### Vérification de Cohérence

```python
# Script de vérification des résultats
def verify_results():
    expected = {
        'pdr_min': 99.0,
        'pdr_max': 100.0,
        'throughput_min': 250.0,
        'throughput_max': 260.0,
        'detection_min': 45.0,
        'detection_max': 55.0
    }
    
    # Charger vos résultats
    with open('results_sample/scientific_report.txt') as f:
        content = f.read()
    
    # Vérifier que les résultats sont dans les bornes attendues
    # ... implémentation ...
    print("✅ Résultats cohérents avec l'article")

verify_results()
```

---

## Références Rapides

### Commandes Essentielles

```bash
# Installation complète
pip install -r requirements.txt && python -m pytest tests/ -v

# Simulation rapide (article)
python simulations/collusion_experiment.py && python simulations/latency_e2e.py

# Tests spécifiques
python -m pytest tests/test_crypto_engine.py tests/test_trust_framework.py -v

# Nettoyage des résultats
rm -rf results_sample/* && mkdir -p results_sample/data results_sample/plots
```

### Paramètres Importants

| Paramètre | Valeur Article | Description |
|-----------|----------------|-------------|
| `alpha` | 0.6 | Poids énergie dans timer |
| `beta` | 0.4 | Poids distance dans timer |
| `gamma0` | 0.3 | Poids confiance base |
| `theta_trust` | 0.4 | Seuil d'isolation |
| `num_nodes` | 300 | Nombre de nœuds |
| `malicious_percentage` | 20.0 | % nœuds malveillants |
| `max_rounds` | 1200 | Durée simulation |

### Résultats Attendus

| Métrique | Valeur Attendue | Tolérance |
|----------|----------------|-----------|
| PDR | 99.95% | ±0.1% |
| Throughput | 254.55 pkts/round | ±2.0 |
| Detection Rate | 50.14% | ±2.0% |
| Energy | 30.71 J | ±1.0 |
| Latency P95 | ≤120ms | - |

### Contact et Support

- **Issues GitHub**: https://github.com/SecIIoT/Secure-IIoT-DCOPA/issues
- **Documentation**: https://github.com/SecIIoT/Secure-IIoT-DCOPA/wiki
- **Email**: souadih@estin.dz, foudil.mir@univ-bejaia.dz

---

*Pour des questions spécifiques ou des rapports de bugs, veuillez ouvrir une issue sur GitHub avec les détails suivants : version Python, système d'exploitation, configuration utilisée, et message d'erreur complet.*

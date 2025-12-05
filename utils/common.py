# -*- coding: utf-8 -*-
"""
Utilitaires communs pour éviter la duplication de code
Module centralisé pour les imports conditionnels et fonctions partagées
"""

import os
import sys
from pathlib import Path

# ===== GESTION DES IMPORTS CONDITIONNELS =====

class ConditionalImports:
    """Gestionnaire centralisé des imports conditionnels"""
    
    def __init__(self):
        self._cache = {}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie la disponibilité des dépendances"""
        self._cache = {
            'torch': self._check_import('torch'),
            'transformers': self._check_import('transformers'),
            'datasets': self._check_import('datasets'),
            'pandas': self._check_import('pandas'),
            'nltk': self._check_import('nltk'),
            'numpy': self._check_import('numpy'),
            'sklearn': self._check_import('sklearn')
        }
        
        # Vérifications spéciales
        if self._cache['torch'] and self._cache['transformers']:
            try:
                from transformers import GPT2LMHeadModel, GPT2Tokenizer
                self._cache['pytorch_ml'] = True
            except Exception:
                self._cache['pytorch_ml'] = False
        else:
            self._cache['pytorch_ml'] = False
    
    def _check_import(self, module_name):
        """Teste si un module peut être importé"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
        except Exception as e:
            # Gère les erreurs NumPy/PyTorch
            if "numpy.dtype size changed" in str(e):
                return False
            return False
    
    def is_available(self, module_name):
        """Vérifie si un module est disponible"""
        return self._cache.get(module_name, False)
    
    def get_status(self):
        """Retourne le statut de tous les modules"""
        return self._cache.copy()
    
    def safe_import(self, module_name, fallback=None):
        """Import sécurisé avec fallback"""
        if self.is_available(module_name):
            try:
                return __import__(module_name)
            except Exception:
                return fallback
        return fallback

# Instance globale
deps = ConditionalImports()

# ===== CONFIGURATION SYSTÈME =====

def get_system_info():
    """Retourne les informations système"""
    info = {
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': str(Path.cwd()),
        'dependencies': deps.get_status()
    }
    
    # Informations mémoire si disponible
    try:
        import psutil
        memory = psutil.virtual_memory()
        info['memory'] = {
            'total_gb': round(memory.total / (1024**3), 1),
            'available_gb': round(memory.available / (1024**3), 1),
            'usage_percent': memory.percent
        }
    except ImportError:
        info['memory'] = 'Non disponible (psutil manquant)'
    
    return info

def is_low_resource_env():
    """Détecte si l'environnement a peu de ressources"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return memory.available < 2 * (1024**3)  # Moins de 2GB disponible
    except ImportError:
        return False

# ===== UTILITAIRES POUR L'ENTRAÎNEMENT =====

class TrainingEnvironmentDetector:
    """Détecte les capacités de l'environnement pour l'entraînement"""
    
    @staticmethod
    def detect_best_mode():
        """Détecte le meilleur mode d'entraînement possible"""
        
        if not deps.is_available('pytorch_ml'):
            return 'demo', "PyTorch/Transformers non disponible"
        
        if is_low_resource_env():
            return 'light', "Ressources limitées détectées"
        
        return 'full', "Environnement complet disponible"
    
    @staticmethod
    def get_recommended_config():
        """Retourne la configuration recommandée"""
        mode, reason = TrainingEnvironmentDetector.detect_best_mode()
        
        configs = {
            'demo': {
                'use_pytorch': False,
                'use_huggingface': False,
                'batch_size': None,
                'epochs': None,
                'description': 'Mode simulation sans ML'
            },
            'light': {
                'use_pytorch': True,
                'use_huggingface': True,
                'model_name': 'distilgpt2',
                'batch_size': 1,
                'epochs': 1,
                'limit_data': 50,
                'description': 'Mode léger avec DistilGPT-2'
            },
            'full': {
                'use_pytorch': True,
                'use_huggingface': True,
                'model_name': 'gpt2',
                'batch_size': 2,
                'epochs': 2,
                'limit_data': 200,
                'description': 'Mode complet avec GPT-2'
            }
        }
        
        return {
            'mode': mode,
            'reason': reason,
            'config': configs[mode]
        }

# ===== UTILITAIRES DE LOGGING =====

def print_status(message, level='info'):
    """Affichage formaté avec icônes"""
    icons = {
        'info': '📋',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'process': '🔄',
        'ai': '🤖',
        'data': '📊',
        'file': '📁'
    }
    
    icon = icons.get(level, '💬')
    print(f"{icon} {message}")

def print_section(title):
    """Affiche un titre de section"""
    print(f"\n🎯 {title}")
    print("=" * (len(title) + 4))

# ===== GESTION DES CHEMINS =====

class ProjectPaths:
    """Gestionnaire centralisé des chemins du projet"""
    
    def __init__(self, root_dir=None):
        self.root = Path(root_dir) if root_dir else Path(__file__).parent
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crée les dossiers nécessaires"""
        directories = ['data', 'models', 'config', 'tests', 'static']
        for dir_name in directories:
            (self.root / dir_name).mkdir(exist_ok=True)
    
    @property
    def data_dir(self):
        return self.root / 'data'
    
    @property
    def models_dir(self):
        return self.root / 'models'
    
    @property
    def config_dir(self):
        return self.root / 'config'
    
    @property
    def tests_dir(self):
        return self.root / 'tests'
    
    def get_data_file(self, filename):
        return self.data_dir / filename
    
    def get_model_path(self, model_name):
        return self.models_dir / model_name

# Instance globale
paths = ProjectPaths()

# ===== VALIDATION DE DONNÉES =====

def validate_text_input(text, min_length=1, max_length=2000):
    """Valide un texte d'entrée"""
    if not text or not isinstance(text, str):
        return False, "Texte vide ou invalide"
    
    text = text.strip()
    if len(text) < min_length:
        return False, f"Texte trop court (minimum {min_length} caractères)"
    
    if len(text) > max_length:
        return False, f"Texte trop long (maximum {max_length} caractères)"
    
    return True, "Texte valide"

def validate_rating(rating):
    """Valide une note (1-5)"""
    if not isinstance(rating, (int, float)):
        return False, "Note doit être un nombre"
    
    if rating < 1 or rating > 5:
        return False, "Note doit être entre 1 et 5"
    
    return True, "Note valide"

# ===== UTILITAIRES D'EXPORT/IMPORT =====

def safe_json_dump(data, filepath, encoding='utf-8'):
    """Sauvegarde JSON sécurisée"""
    try:
        import json
        with open(filepath, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, f"Sauvegardé: {filepath}"
    except Exception as e:
        return False, f"Erreur sauvegarde: {e}"

def safe_json_load(filepath, encoding='utf-8'):
    """Chargement JSON sécurisé"""
    try:
        import json
        with open(filepath, 'r', encoding=encoding) as f:
            return True, json.load(f)
    except FileNotFoundError:
        return False, "Fichier non trouvé"
    except Exception as e:
        return False, f"Erreur chargement: {e}"

# ===== TESTS UNITAIRES =====

def run_self_tests():
    """Tests des utilitaires"""
    print_section("Tests des utilitaires communs")
    
    # Test imports
    status = deps.get_status()
    print_status(f"Dépendances détectées: {sum(status.values())}/{len(status)}")
    
    # Test environnement
    env_info = get_system_info()
    print_status(f"Python: {env_info['python_version'].split()[0]}")
    
    # Test détection training
    recommendation = TrainingEnvironmentDetector.get_recommended_config()
    print_status(f"Mode recommandé: {recommendation['mode']} - {recommendation['reason']}")
    
    # Test validation
    valid, msg = validate_text_input("Test de validation")
    assert valid, msg
    print_status("Validation de texte: OK", 'success')
    
    # Test chemins
    assert paths.data_dir.exists()
    print_status("Gestion des chemins: OK", 'success')
    
    print_status("Tous les tests passés!", 'success')

if __name__ == "__main__":
    run_self_tests()
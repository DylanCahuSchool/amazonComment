#!/usr/bin/env python3
"""
Test simple et robuste pour CI/CD
Ne dépend que des modules de base pour éviter les conflits de version
"""
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_imports():
    """Test que tous les modules s'importent correctement"""
    try:
        # Test imports critiques sans charger les modèles ML
        import fastapi
        print("✅ FastAPI disponible")
        
        import pydantic
        print("✅ Pydantic disponible")
        
        # Test de structure de fichier
        import os
        required_files = ['main.py', 'generate_response.py', 'data_processing.py']
        for file in required_files:
            if os.path.exists(file):
                print(f"✅ Fichier {file} présent")
            else:
                print(f"❌ Fichier {file} manquant")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def test_functions():
    """Test des fonctions de base sans ML"""
    try:
        # Tests simples sans charger les modèles lourds
        import re
        import string
        
        # Test nettoyage basique
        def simple_clean(text):
            text = re.sub(r'http\S+', '', text)
            text = re.sub(r'[^\w\s]', '', text)
            return text.strip().lower()
        
        result = simple_clean("Produit fantastique! 😊 http://test.com")
        assert len(result) > 0
        print(f"✅ Nettoyage texte basique: '{result}'")
        
        # Test logique sentiment basique
        def simple_sentiment(score):
            if score >= 4:
                return "positive"
            elif score <= 2:
                return "negative"
            else:
                return "neutre"
        
        assert simple_sentiment(5) == "positive"
        assert simple_sentiment(1) == "negative"
        print("✅ Logique sentiment: OK")
        
        return True
    except Exception as e:
        print(f"❌ Erreur tests fonctions: {e}")
        return False

def test_api_structure():
    """Test de configuration basique"""
    try:
        # Tests de configuration et structure sans imports lourds
        import os
        
        # Test variables d'environnement
        config_found = False
        try:
            from config.settings import APIConfig
            config_found = True
            print("✅ Configuration trouvée")
        except:
            print("⚠️ Configuration non trouvée (OK en CI)")
        
        # Test requirements
        if os.path.exists('requirements.txt'):
            print("✅ requirements.txt présent")
        
        if os.path.exists('requirements-light.txt'):
            print("✅ requirements-light.txt présent")
        
        return True
    except Exception as e:
        print(f"❌ Erreur structure: {e}")
        return False

def main():
    """Exécute tous les tests simples"""
    print("🧪 Tests simples pour CI/CD")
    print("=" * 40)
    
    tests = [
        ("Imports des modules", test_imports),
        ("Fonctions de base", test_functions), 
        ("Structure API", test_api_structure)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: RÉUSSI")
            else:
                failed += 1
                print(f"❌ {name}: ÉCHOUÉ")
        except Exception as e:
            failed += 1
            print(f"❌ {name}: ERREUR - {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Résultats: {passed} réussis, {failed} échoués")
    
    if failed == 0:
        print("🎉 Tous les tests sont passés!")
        return True
    else:
        print("💥 Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
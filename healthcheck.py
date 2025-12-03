#!/usr/bin/env python3
"""
Script de démarrage pour vérifier que l'app peut démarrer
"""

import sys
import os

# Forcer le mode fallback
os.environ["ENABLE_AI_MODEL"] = "false"

def check_dependencies():
    """Vérifie que les dépendances minimales sont présentes"""
    required_modules = [
        'fastapi',
        'uvicorn', 
        'gunicorn',
        'nltk'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"❌ {module}")
    
    return len(missing) == 0

def check_app():
    """Vérifie que l'application peut se charger"""
    try:
        from main import app
        print("✅ Application FastAPI chargée")
        return True
    except Exception as e:
        print(f"❌ Erreur chargement app: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification des dépendances...")
    deps_ok = check_dependencies()
    
    print("\n🔍 Vérification de l'application...")
    app_ok = check_app()
    
    if deps_ok and app_ok:
        print("\n✅ Tout est prêt pour le démarrage!")
        sys.exit(0)
    else:
        print("\n❌ Problèmes détectés")
        sys.exit(1)
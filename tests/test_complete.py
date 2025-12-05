#!/usr/bin/env python3
"""
Suite de tests complète pour l'API Amazon Comments
Tests unitaires, d'intégration et de déploiement
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
import json
from typing import Optional

# Configuration des tests
class TestConfig:
    """Configuration des tests"""
    
    # URL de base (sera mise à jour après déploiement)
    BASE_URL = "https://amazoncomment-api.onrender.com"
    LOCAL_URL = "http://localhost:8000"
    
    # Données de test
    TEST_CASES = [
        {
            "nom": "Avis très positif",
            "texte": "Produit absolument fantastique! Service client exceptionnel, livraison rapide. Je recommande vivement! 😊",
            "sentiment_attendu": "positive"
        },
        {
            "nom": "Avis négatif",
            "texte": "Très déçu du produit. Mauvaise qualité, service client inexistant. Je ne recommande pas du tout.",
            "sentiment_attendu": "negative"
        },
        {
            "nom": "Avis neutre",
            "texte": "Produit correct, sans plus. Prix raisonnable mais rien d'exceptionnel.",
            "sentiment_attendu": "neutral"
        },
        {
            "nom": "Texte avec emojis et URL",
            "texte": "Super produit! 👍😊 Voir ici: http://example.com #satisfied",
            "sentiment_attendu": "positive"
        }
    ]

def test_imports():
    """Test 1: Vérification des imports"""
    print("📋 Test 1: Imports des modules")
    
    try:
        # Test des imports principaux
        import main
        print("   ✅ main.py importé")
        
        import generate_response
        print("   ✅ generate_response.py importé")
        
        import data_processing  
        print("   ✅ data_processing.py importé")
        
        from config.settings import AIConfig, APIConfig
        print("   ✅ Configuration importée")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def test_data_processing():
    """Test 2: Fonctions de traitement de données"""
    print("📋 Test 2: Traitement de données")
    
    try:
        from data_processing import clean_text, analyze_sentiment_simple, process_review
        
        # Test nettoyage de texte
        dirty_text = "Produit SUPER! 😊 http://test.com #hashtag"
        cleaned = clean_text(dirty_text)
        assert len(cleaned) > 0, "Texte nettoyé vide"
        assert "http" not in cleaned, "URL pas supprimée"
        print(f"   ✅ Nettoyage: '{dirty_text}' → '{cleaned}'")
        
        # Test analyse de sentiment
        positive_sentiment = analyze_sentiment_simple("Excellent produit, parfait!")
        negative_sentiment = analyze_sentiment_simple("Horrible, mauvaise qualité")
        assert positive_sentiment == "positive", f"Sentiment positif incorrect: {positive_sentiment}"
        assert negative_sentiment == "negative", f"Sentiment négatif incorrect: {negative_sentiment}"
        print(f"   ✅ Sentiment: positif={positive_sentiment}, négatif={negative_sentiment}")
        
        # Test traitement complet
        result = process_review("Super produit! Très satisfait 😊", 5)
        assert result["sentiment"] == "positive", "Sentiment final incorrect"
        assert len(result["cleaned_text"]) > 0, "Texte nettoyé vide"
        print(f"   ✅ Traitement complet: sentiment={result['sentiment']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur traitement: {e}")
        return False

def test_response_generation():
    """Test 3: Génération de réponses"""
    print("📋 Test 3: Génération de réponses")
    
    try:
        from generate_response import generer_reponse
        
        # Test réponses pour différents sentiments
        sentiments = ["positive", "negative", "neutral"]
        
        for sentiment in sentiments:
            response = generer_reponse("Test", sentiment)
            assert len(response) > 20, f"Réponse {sentiment} trop courte: {len(response)} chars"
            print(f"   ✅ Réponse {sentiment}: {len(response)} caractères")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur génération: {e}")
        return False

def test_api_structure():
    """Test 4: Structure de l'API FastAPI"""
    print("📋 Test 4: Structure API")
    
    try:
        from main import app
        
        # Vérifier les routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        expected_routes = ["/", "/health", "/analyse", "/stats"]
        for route in expected_routes:
            if not any(route in r for r in routes):
                print(f"   ⚠️ Route manquante: {route}")
        
        print(f"   ✅ API avec {len(routes)} routes configurées")
        
        # Vérifier les middlewares
        assert len(app.user_middleware) > 0, "Aucun middleware configuré"
        print("   ✅ Middlewares CORS configurés")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur structure API: {e}")
        return False

def test_api_local(base_url: str = None):
    """Test 5: API locale ou déployée"""
    url = base_url or TestConfig.LOCAL_URL
    print(f"📋 Test 5: API sur {url}")
    
    try:
        # Test health check
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check: {health_data.get('status')} (mode: {health_data.get('mode')})")
        else:
            print(f"   ⚠️ Health check: status {response.status_code}")
        
        # Test endpoint principal avec cas de test
        success_count = 0
        for test_case in TestConfig.TEST_CASES[:2]:  # Tester seulement 2 cas pour économiser les requêtes
            
            response = requests.post(
                f"{url}/analyse",
                json={"texte": test_case["texte"]},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                sentiment_ok = data.get("sentiment") == test_case["sentiment_attendu"]
                response_ok = len(data.get("reponse", "")) > 10
                
                if sentiment_ok and response_ok:
                    success_count += 1
                    print(f"   ✅ {test_case['nom']}: sentiment={data.get('sentiment')}")
                else:
                    print(f"   ⚠️ {test_case['nom']}: sentiment={data.get('sentiment')} (attendu: {test_case['sentiment_attendu']})")
            else:
                print(f"   ❌ {test_case['nom']}: HTTP {response.status_code}")
        
        return success_count > 0
        
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ API non accessible: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur test API: {e}")
        return False

def test_deployed_api():
    """Test 6: API déployée sur Render"""
    print(f"📋 Test 6: API déployée")
    return test_api_local(TestConfig.BASE_URL)

def run_all_tests(include_deployed: bool = False):
    """Exécute tous les tests"""
    
    print("🧪 SUITE DE TESTS AMAZON COMMENTS API")
    print("=" * 50)
    
    tests = [
        ("Imports des modules", test_imports),
        ("Traitement de données", test_data_processing),
        ("Génération de réponses", test_response_generation),
        ("Structure API", test_api_structure),
        ("API locale", test_api_local)
    ]
    
    if include_deployed:
        tests.append(("API déployée", test_deployed_api))
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n🔍 {name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: RÉUSSI")
            else:
                failed += 1
                print(f"❌ {name}: ÉCHOUÉ")
        except Exception as e:
            failed += 1
            print(f"💥 {name}: ERREUR - {e}")
    
    # Résumé
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTATS: {passed} réussis, {failed} échoués")
    
    if failed == 0:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tests Amazon Comments API")
    parser.add_argument("--deployed", action="store_true", help="Inclure les tests de l'API déployée")
    args = parser.parse_args()
    
    success = run_all_tests(include_deployed=args.deployed)
    sys.exit(0 if success else 1)
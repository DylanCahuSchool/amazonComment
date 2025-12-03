#!/usr/bin/env python3
"""
Test simple et robuste pour CI/CD
Ne dépend que des modules de base pour éviter les conflits de version
"""

def test_imports():
    """Test que tous les modules s'importent correctement"""
    try:
        from main import app
        print("✅ Import main.py réussi")
        
        from generate_response import generer_reponse
        print("✅ Import generate_response.py réussi")
        
        from data_processing import clean_text, label_sentiment
        print("✅ Import data_processing.py réussi")
        
        return True
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def test_functions():
    """Test des fonctions de base"""
    try:
        from generate_response import generer_reponse
        from data_processing import clean_text, label_sentiment
        
        # Test nettoyage texte
        result = clean_text("Produit fantastique! 😊 http://test.com")
        assert len(result) > 0
        print(f"✅ clean_text: '{result}'")
        
        # Test sentiment
        sentiment_pos = label_sentiment(4)
        sentiment_neg = label_sentiment(1)
        assert sentiment_pos == "positive"
        assert sentiment_neg == "negative"
        print(f"✅ label_sentiment: positif={sentiment_pos}, négatif={sentiment_neg}")
        
        # Test génération réponse
        reponse_pos = generer_reponse("Super produit!", "positive")
        reponse_neg = generer_reponse("Problème grave", "negative")
        assert len(reponse_pos) > 10
        assert len(reponse_neg) > 10
        print(f"✅ generer_reponse: OK (pos={len(reponse_pos)} chars, neg={len(reponse_neg)} chars)")
        
        return True
    except Exception as e:
        print(f"❌ Erreur tests fonctions: {e}")
        return False

def test_api_structure():
    """Test que l'API FastAPI se construit correctement"""
    try:
        from main import app
        
        # Vérifier que l'app FastAPI est créée
        assert hasattr(app, 'routes')
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        # Vérifier qu'on a nos endpoints
        assert '/analyse' in routes or any('/analyse' in str(route) for route in app.routes)
        print(f"✅ API structure: {len(routes)} routes trouvées")
        
        return True
    except Exception as e:
        print(f"❌ Erreur structure API: {e}")
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
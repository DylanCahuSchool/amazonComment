#!/usr/bin/env python3
"""
Test de l'API déployée sur Render
Test léger sans dépendances lourdes
"""

import requests
import json
from typing import Dict, List

class DeployedAPITester:
    """Testeur pour l'API déployée"""
    
    BASE_URL = "https://amazoncomment-api.onrender.com"
    
    TEST_CASES = [
        {
            "nom": "Avis très positif",
            "texte": "Produit fantastique! Service client exceptionnel! 😊",
            "sentiment_attendu": "positive"
        },
        {
            "nom": "Avis négatif",
            "texte": "Très déçu, mauvaise qualité, service client inexistant",
            "sentiment_attendu": "negative"
        },
        {
            "nom": "Avis neutre",
            "texte": "Produit correct, rien d'extraordinaire",
            "sentiment_attendu": "neutral"
        }
    ]
    
    def test_health(self) -> bool:
        """Test du health check"""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data.get('status')} (mode: {data.get('mode')})")
                return True
            else:
                print(f"⚠️ Health check: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_analyse_endpoint(self) -> Dict:
        """Test de l'endpoint /analyse"""
        results = {"total": 0, "success": 0, "failures": []}
        
        for test_case in self.TEST_CASES:
            results["total"] += 1
            
            try:
                response = requests.post(
                    f"{self.BASE_URL}/analyse",
                    json={"texte": test_case["texte"]},
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    sentiment = data.get("sentiment")
                    response_text = data.get("reponse", "")
                    
                    # Validation basique
                    if sentiment == test_case["sentiment_attendu"] and len(response_text) > 10:
                        results["success"] += 1
                        print(f"✅ {test_case['nom']}: {sentiment}")
                    else:
                        print(f"⚠️ {test_case['nom']}: {sentiment} (attendu: {test_case['sentiment_attendu']})")
                        results["failures"].append(f"{test_case['nom']}: sentiment incorrect")
                else:
                    print(f"❌ {test_case['nom']}: HTTP {response.status_code}")
                    results["failures"].append(f"{test_case['nom']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {test_case['nom']}: {e}")
                results["failures"].append(f"{test_case['nom']}: {str(e)}")
        
        return results
    
    def run_all_tests(self) -> bool:
        """Exécution de tous les tests"""
        print("🌐 Test de l'API déployée Amazon Comments")
        print("=" * 50)
        
        # Test health
        health_ok = self.test_health()
        
        # Test analyse
        print("\n📊 Test de l'endpoint /analyse")
        results = self.test_analyse_endpoint()
        
        print(f"\n📋 Résultats: {results['success']}/{results['total']} réussis")
        
        if results["failures"]:
            print("❌ Échecs:")
            for failure in results["failures"]:
                print(f"   - {failure}")
        
        # Succès si health OK et au moins 1 test d'analyse réussi
        success = health_ok and results["success"] > 0
        
        if success:
            print("✅ API déployée fonctionnelle!")
        else:
            print("⚠️ Problèmes détectés avec l'API déployée")
        
        return success

def main():
    """Point d'entrée principal"""
    tester = DeployedAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
import requests
import json

# URL de base de votre API sur Render
BASE_URL = "https://amazoncomment-api.onrender.com"  # Remplacez par votre vraie URL

def test_api_deployed():
    """Test de l'API déployée sur Render"""
    
    print("🧪 Test de l'API déployée...")
    
    # 1. Test de la documentation
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Documentation accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur documentation: {e}")
    
    # 2. Test de l'endpoint /analyse
    try:
        test_data = {
            "texte": "Ce produit est absolument fantastique! Je le recommande vivement."
        }
        
        response = requests.post(
            f"{BASE_URL}/analyse", 
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentiment: {result['sentiment']}")
            print(f"✅ Réponse: {result['reponse']}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur API: {e}")

if __name__ == "__main__":
    test_api_deployed()
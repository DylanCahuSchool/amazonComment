# 🛒 Amazon Comments API - Analyse de Sentiment & Réponses Client

API FastAPI pour analyser les avis clients et générer des réponses automatiques basées sur le sentiment.

## 🚀 Déploiement sur Render

### Configuration recommandée :
- **Runtime**: Python 3.10
- **Build Command**: `pip install -r requirements-light.txt`
- **Start Command**: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --host 0.0.0.0 --port $PORT`

### Variables d'environnement :
```bash
ENABLE_AI_MODEL=false  # Mode fallback rapide (recommandé)
```

## 🖥️ Développement Local

### Installation des dépendances :
```bash
pip install -r requirements.txt
pip install uvicorn  # Serveur ASGI pour FastAPI
```

### Lancement du serveur de développement :
```bash
# Option 1: Avec uvicorn (recommandé)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Script Python direct
python main.py
```

### 🌐 Interface Web
Accédez à l'interface : `http://localhost:8000`

**Uvicorn** est le serveur web ASGI qui fait tourner votre application FastAPI :
- 🚀 **Performance** : Ultra-rapide avec support async/await
- 🔄 **Hot reload** : Redémarre automatiquement lors des modifications
- 🌍 **Production ready** : Utilisé en production via Gunicorn

## 📋 Fonctionnalités

### Endpoint principal : `POST /analyse`
```json
{
  "texte": "Produit fantastique, très satisfait!"
}
```

### Réponse :
```json
{
  "sentiment": "positive",
  "reponse": "Merci beaucoup pour votre retour positif ! Nous sommes ravis que notre produit vous satisfasse..."
}
```

## 🧪 Tests

```bash
# Tests simples (CI/CD)
python test_simple.py

# Tests complets (développement)
python test_app.py
```

## 📦 Dépendances

- **Production** (légère): `requirements-light.txt` 
- **Développement** (complète): `requirements.txt`

## 🔧 Architecture

- `main.py` - API FastAPI avec endpoint /analyse
- `generate_response.py` - Génération de réponses (mode fallback par défaut)
- `data_processing.py` - Nettoyage de texte et analyse de sentiment
- `test_simple.py` - Tests robustes pour CI/CD

## 📖 Documentation

Une fois déployée : `https://[votre-app].onrender.com/docs`
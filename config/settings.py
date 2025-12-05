"""
Configuration centralisée pour l'application Amazon Comments API
"""
import os
from pathlib import Path

# Dossier racine du projet
ROOT_DIR = Path(__file__).parent.parent

# Configuration de l'IA
class AIConfig:
    """Configuration des modèles d'IA"""
    
    # Par défaut, utiliser le mode fallback (plus stable pour le déploiement)
    ENABLE_AI_MODEL = os.environ.get("ENABLE_AI_MODEL", "false").lower() in ("1", "true", "yes")
    
    # Modèles de génération de texte (par ordre de préférence)
    FALLBACK_MODELS = [
        "distilgpt2",           # Très léger, très compatible
        "gpt2",                 # Léger, très compatible  
        "microsoft/DialoGPT-small"  # Spécialisé dialogue
    ]
    
    # Paramètres de génération
    MAX_LENGTH = 150
    TEMPERATURE = 0.7
    DO_SAMPLE = True

# Configuration de l'API
class APIConfig:
    """Configuration de l'API FastAPI"""
    
    TITLE = "Amazon Comments API"
    DESCRIPTION = "API d'analyse de sentiment et génération de réponses automatiques"
    VERSION = "1.0.0"
    
    # Serveur
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", 8000))
    
    # Workers Gunicorn
    WORKERS = int(os.environ.get("WORKERS", 2))
    WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    TIMEOUT = 30

# Configuration des réponses prédéfinies
class ResponseTemplates:
    """Templates de réponses par sentiment"""
    
    POSITIVE = [
        "Merci beaucoup pour votre retour positif ! Nous sommes ravis que notre produit vous satisfasse. Votre satisfaction est notre priorité.",
        "Quel plaisir de lire votre commentaire ! Nous apprécions vraiment votre confiance et espérons continuer à vous satisfaire.",
        "Nous sommes enchantés de votre satisfaction ! Merci de partager votre expérience positive avec nous."
    ]
    
    NEGATIVE = [
        "Nous vous remercions pour votre retour et nous excusons sincèrement pour les désagréments rencontrés. Notre équipe va examiner votre cas avec attention.",
        "Votre expérience nous tient à cœur et nous regrettons que nos services n'aient pas été à la hauteur de vos attentes. Nous travaillons à nous améliorer.",
        "Nous prenons vos commentaires très au sérieux et nous nous engageons à trouver une solution rapide à votre problème."
    ]
    
    NEUTRAL = [
        "Merci pour votre retour constructif. Nous prenons tous les commentaires en considération pour améliorer continuellement nos services.",
        "Nous apprécions votre feedback équilibré qui nous aide à mieux comprendre les besoins de nos clients.",
        "Votre avis nous guide dans nos efforts d'amélioration continue. Merci de prendre le temps de nous faire part de vos observations."
    ]

# Configuration du traitement de texte
class TextProcessingConfig:
    """Configuration pour le nettoyage et l'analyse de texte"""
    
    # Stopwords français de base (si NLTK n'est pas disponible)
    BASIC_FRENCH_STOPWORDS = {
        'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour',
        'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus',
        'par', 'grand', 'les', 'des', 'du', 'la', 'au', 'aux', 'ces', 'ses', 'nos', 
        'vos', 'leurs', 'est', 'sont', 'était', 'ont', 'cette', 'mais', 'très',
        'bien', 'sans', 'peut', 'fait', 'faire', 'voir', 'deux', 'comme', 'aussi'
    }
    
    # Seuils pour l'analyse de sentiment
    SENTIMENT_THRESHOLDS = {
        "positive": 3,  # >= 3 = positif
        "negative": 2   # < 2 = négatif, sinon neutre
    }

# Configuration de déploiement
class DeploymentConfig:
    """Configuration spécifique au déploiement"""
    
    # Environnement
    ENV = os.environ.get("ENV", "production")
    DEBUG = ENV == "development"
    
    # Render.com spécifique
    IS_RENDER = os.environ.get("RENDER") is not None
    
    # Logs
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
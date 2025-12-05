# -*- coding: utf-8 -*-
"""
Module de traitement de données et d'analyse de sentiment
Utilise la configuration centralisée et gère les dépendances optionnelles
"""

import re
import string
from config.settings import TextProcessingConfig

# Gestion des imports optionnels
nltk_available = False
try:
    import nltk
    from nltk.corpus import stopwords
    nltk_available = True
    print("📚 NLTK disponible")
except ImportError:
    print("📚 NLTK non disponible, utilisation des stopwords basiques")

def initialize_nltk():
    """Initialise NLTK avec gestion d'erreur"""
    global stopwords_fr
    
    if not nltk_available:
        stopwords_fr = TextProcessingConfig.BASIC_FRENCH_STOPWORDS
        return
    
    try:
        # Télécharger stopwords de manière silencieuse
        nltk.download('stopwords', quiet=True)
        stopwords_fr = set(stopwords.words("french"))
        print("✅ Stopwords français chargés depuis NLTK")
    except Exception as e:
        print(f"⚠️ Erreur NLTK: {e}")
        stopwords_fr = TextProcessingConfig.BASIC_FRENCH_STOPWORDS
        print("✅ Stopwords basiques utilisés")

def clean_text(text: str) -> str:
    """
    Nettoie et normalise le texte d'entrée
    
    Args:
        text: Le texte brut à nettoyer
        
    Returns:
        Le texte nettoyé et normalisé
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Conversion en minuscules
    text = text.lower().strip()
    
    # Suppression des URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    
    # Suppression des emojis avec regex Unicode
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symboles & pictographes
        u"\U0001F680-\U0001F6FF"  # transport & map
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002700-\U000027BF"  # dingbats
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # diacritiques
        u"\u3030"
        "]+", 
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Suppression de la ponctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    
    # Conservation des caractères français et chiffres
    text = re.sub(r"[^a-zàâäéèêëîïôöùûüç0-9\s]", " ", text)
    
    # Suppression des stopwords
    if stopwords_fr:
        words = text.split()
        text = " ".join([word for word in words if word not in stopwords_fr and len(word) > 2])
    
    # Nettoyage final des espaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def analyze_sentiment_simple(text: str) -> str:
    """
    Analyse simple du sentiment basée sur des mots-clés
    
    Args:
        text: Le texte à analyser
        
    Returns:
        Le sentiment détecté ("positive", "negative", "neutral")
    """
    if not text:
        return "neutral"
    
    text_lower = text.lower()
    
    # Mots-clés positifs
    positive_keywords = {
        'excellent', 'fantastique', 'parfait', 'super', 'génial', 'formidable',
        'merveilleux', 'incroyable', 'magnifique', 'extraordinaire', 'remarquable',
        'satisfait', 'content', 'heureux', 'ravi', 'enchanté', 'impressionné',
        'recommande', 'qualité', 'rapide', 'efficace', 'professionnel', 'top',
        'bon', 'bien', 'mieux', 'meilleur', 'love', 'adore', 'parfait'
    }
    
    # Mots-clés négatifs
    negative_keywords = {
        'mauvais', 'terrible', 'horrible', 'nul', 'catastrophique', 'décevant',
        'insatisfait', 'mécontent', 'frustré', 'énervé', 'fâché', 'déçu',
        'problème', 'erreur', 'défaut', 'cassé', 'abîmé', 'retard', 'lent',
        'cher', 'arnaque', 'vol', 'scandale', 'inadmissible', 'inacceptable',
        'pire', 'déteste', 'horreur', 'cauchemar', 'regret'
    }
    
    # Compter les occurrences
    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    negative_count = sum(1 for word in negative_keywords if word in text_lower)
    
    # Déterminer le sentiment
    if positive_count > negative_count and positive_count > 0:
        return "positive"
    elif negative_count > positive_count and negative_count > 0:
        return "negative"
    else:
        return "neutral"

def label_sentiment(numeric_label: int) -> str:
    """
    Convertit un label numérique en sentiment textuel
    Basé sur l'échelle Amazon (1-5 étoiles)
    
    Args:
        numeric_label: Score numérique (généralement 1-5)
        
    Returns:
        Le sentiment correspondant ("positive", "negative", "neutral")
    """
    thresholds = TextProcessingConfig.SENTIMENT_THRESHOLDS
    
    if numeric_label >= thresholds["positive"]:
        return "positive"
    elif numeric_label < thresholds["negative"]:
        return "negative"
    else:
        return "neutral"

def process_review(text: str, numeric_rating: int = None) -> dict:
    """
    Traite complètement un avis client
    
    Args:
        text: Le texte de l'avis
        numeric_rating: Note numérique optionnelle
        
    Returns:
        Dictionnaire avec le texte nettoyé et le sentiment
    """
    # Nettoyer le texte
    cleaned_text = clean_text(text)
    
    # Analyser le sentiment
    if numeric_rating is not None:
        # Utiliser la note numérique si disponible
        sentiment = label_sentiment(numeric_rating)
    else:
        # Analyser le texte si pas de note
        sentiment = analyze_sentiment_simple(cleaned_text)
    
    return {
        "original_text": text,
        "cleaned_text": cleaned_text,
        "sentiment": sentiment,
        "numeric_rating": numeric_rating
    }

def load_reviews_dataset(limit: int = 1000) -> list:
    """
    Charge un dataset d'avis (fonction optionnelle)
    
    Args:
        limit: Nombre maximum d'avis à charger
        
    Returns:
        Liste de dictionnaires avec les avis traités
    """
    try:
        import pandas as pd
        from datasets import load_dataset
        
        print(f"📥 Chargement du dataset (limite: {limit})")
        dataset = load_dataset(
            "SetFit/amazon_reviews_multi_fr",
            split=f"train[:{limit}]"
        )
        
        reviews = []
        for item in dataset:
            processed = process_review(item['text'], item['label'])
            reviews.append(processed)
        
        print(f"✅ {len(reviews)} avis chargés et traités")
        return reviews
        
    except ImportError as e:
        print(f"📦 Modules de dataset non disponibles: {e}")
        return []
    except Exception as e:
        print(f"❌ Erreur chargement dataset: {e}")
        return []

# Initialisation du module
print("🔧 Initialisation du module de traitement de données...")
initialize_nltk()
print("✅ Module de traitement prêt")

# Tests si exécuté directement
if __name__ == "__main__":
    print("\n🧪 Test du traitement de données...")
    
    tests = [
        ("Produit FANTASTIQUE! 😊 http://test.com J'adore vraiment!", None),
        ("Service très décevant, problème majeur...", None),
        ("Correct sans plus, peut mieux faire", None),
        ("Avis avec note", 5),
        ("Avis négatif avec note", 1)
    ]
    
    for text, rating in tests:
        result = process_review(text, rating)
        print(f"\n📝 Original: {text}")
        print(f"🧹 Nettoyé: {result['cleaned_text']}")
        print(f"😊 Sentiment: {result['sentiment']}")
        if rating:
            print(f"⭐ Note: {rating}")
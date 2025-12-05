# -*- coding: utf-8 -*-
"""
Module de génération de réponses client
Utilise la configuration centralisée et gère les fallbacks robustes
"""

import os
import random
from config.settings import AIConfig, ResponseTemplates

# Variables globales pour le modèle IA
tokenizer = None
model = None
gen_pipe = None

def load_ai_model():
    """
    Charge le modèle IA avec des fallbacks robustes
    Retourne True si un modèle a été chargé, False sinon
    """
    global tokenizer, model, gen_pipe
    
    if not AIConfig.ENABLE_AI_MODEL:
        print("💬 Mode fallback activé par configuration")
        return False
        
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        print("🤖 Tentative de chargement des modèles IA...")
        
        for model_name in AIConfig.FALLBACK_MODELS:
            try:
                print(f"   Essai: {model_name}")
                
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Configuration du tokenizer
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                gen_pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=AIConfig.MAX_LENGTH,
                    temperature=AIConfig.TEMPERATURE,
                    do_sample=AIConfig.DO_SAMPLE,
                    pad_token_id=tokenizer.eos_token_id
                )
                
                print(f"✅ Modèle {model_name} chargé avec succès")
                return True
                
            except Exception as e:
                print(f"❌ Échec {model_name}: {str(e)[:100]}...")
                continue
        
        print("❌ Aucun modèle IA disponible, utilisation du mode fallback")
        return False
        
    except ImportError:
        print("📦 Transformers non disponible, utilisation du mode fallback")
        return False
    except Exception as e:
        print(f"❌ Erreur générale IA: {e}")
        return False

def generate_fallback_response(texte: str, sentiment: str) -> str:
    """
    Génère une réponse prédéfinie basée sur le sentiment
    
    Args:
        texte: Le texte du client (non utilisé dans le fallback, mais gardé pour compatibilité)
        sentiment: Le sentiment détecté ("positive", "negative", "neutral")
    
    Returns:
        Une réponse appropriée au sentiment
    """
    
    # Sélectionner le bon template selon le sentiment
    if any(word in sentiment.lower() for word in ["positif", "positive", "good", "great"]):
        templates = ResponseTemplates.POSITIVE
    elif any(word in sentiment.lower() for word in ["neutre", "neutral", "mixed"]):
        templates = ResponseTemplates.NEUTRAL
    else:  # Sentiment négatif ou inconnu
        templates = ResponseTemplates.NEGATIVE
    
    # Choisir un template aléatoire pour varier les réponses
    return random.choice(templates)

def generate_ai_response(texte: str, sentiment: str) -> str:
    """
    Génère une réponse avec le modèle IA
    
    Args:
        texte: Le texte du client
        sentiment: Le sentiment détecté
    
    Returns:
        Une réponse générée par IA ou fallback en cas d'erreur
    """
    if gen_pipe is None:
        return generate_fallback_response(texte, sentiment)
    
    try:
        # Prompt optimisé pour les modèles génériques
        context = f"Message client: {texte[:200]} - Réponse service client:"
        
        result = gen_pipe(
            context,
            max_length=len(context) + 80,
            num_return_sequences=1,
            temperature=0.6
        )
        
        generated = result[0]["generated_text"]
        
        # Extraire la réponse générée
        if context in generated:
            response = generated.replace(context, "").strip()
            if len(response) > 20:  # Réponse valide
                return response[:300]  # Limiter la taille
    
    except Exception as e:
        print(f"⚠️ Erreur génération IA: {e}")
    
    # Fallback en cas d'erreur IA
    return generate_fallback_response(texte, sentiment)

def generer_reponse(texte: str, sentiment: str = "negative") -> str:
    """
    Point d'entrée principal pour générer une réponse client
    
    Args:
        texte: Le texte/avis du client
        sentiment: Le sentiment détecté ("positive", "negative", "neutral")
    
    Returns:
        Une réponse appropriée et professionnelle
    """
    
    # Mode IA activé et modèle disponible
    if AIConfig.ENABLE_AI_MODEL and gen_pipe is not None:
        return generate_ai_response(texte, sentiment)
    
    # Mode fallback (par défaut)
    return generate_fallback_response(texte, sentiment)

# Initialisation au chargement du module
print("🚀 Initialisation du module de génération de réponses...")
ai_loaded = load_ai_model()
if ai_loaded:
    print("✅ Modèle IA chargé et prêt")
else:
    print("💬 Mode fallback activé - Réponses prédéfinies")

# Test de la fonction si exécutée directement
if __name__ == "__main__":
    print("\n🧪 Test des réponses...")
    
    tests = [
        ("Produit fantastique, très satisfait!", "positif"),
        ("Problème de livraison, très déçu", "negatif"),
        ("Produit correct mais peut mieux faire", "neutre")
    ]
    
    for texte, sentiment in tests:
        response = generer_reponse(texte, sentiment)
        print(f"\n📝 Texte: {texte}")
        print(f"😊 Sentiment: {sentiment}")
        print(f"💬 Réponse: {response}")
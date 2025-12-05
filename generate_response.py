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

# Chemin vers le modèle entraîné
TRAINED_MODEL_PATH = "./models/amazon_trained"

def load_trained_model():
    """Charge le modèle entraîné Amazon si disponible"""
    global tokenizer, model, gen_pipe
    
    from pathlib import Path
    
    if Path(TRAINED_MODEL_PATH).exists():
        try:
            from transformers import GPT2Tokenizer, GPT2LMHeadModel
            
            print(f"🎯 Chargement du modèle entraîné Amazon: {TRAINED_MODEL_PATH}")
            
            tokenizer = GPT2Tokenizer.from_pretrained(TRAINED_MODEL_PATH)
            model = GPT2LMHeadModel.from_pretrained(TRAINED_MODEL_PATH)
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            print("✅ Modèle Amazon entraîné chargé avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement modèle entraîné: {e}")
            return False
    
    return False

def load_ai_model():
    """
    Charge le modèle IA avec priorité au modèle entraîné
    """
    global tokenizer, model, gen_pipe
    
    if not AIConfig.ENABLE_AI_MODEL:
        print("💬 Mode fallback activé par configuration")
        return False
    
    # Priorité 1: Modèle entraîné Amazon
    if load_trained_model():
        return True
        
    # Priorité 2: Modèles pré-entraînés
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        print("🤖 Tentative de chargement des modèles pré-entraînés...")
        
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
    Génère une réponse avec le modèle IA (priorité au modèle entraîné)
    """
    global tokenizer, model, gen_pipe
    
    if tokenizer is None or model is None:
        return generate_fallback_response(texte, sentiment)
    
    try:
        # Format d'entrée
        input_text = f"Avis client: {texte}"
        
        # Tokenisation
        inputs = tokenizer.encode(input_text, return_tensors="pt")
        
        # Génération avec le modèle
        import torch
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 60,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1,
                repetition_penalty=1.2
            )
        
        # Décoder la réponse
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraire la partie réponse
        response = generated_text[len(input_text):].strip()
        
        # Nettoyer et valider
        if len(response) > 15 and len(response) < 300:
            from pathlib import Path
            if Path(TRAINED_MODEL_PATH).exists():
                print("🎯 Réponse du modèle entraîné Amazon")
            else:
                print("🤖 Réponse du modèle pré-entraîné")
            return response
        else:
            return generate_fallback_response(texte, sentiment)
    
    except Exception as e:
        print(f"⚠️ Erreur génération IA: {e}")
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
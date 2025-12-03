# -*- coding: utf-8 -*-
"""generate_response.py - Génération de réponses client avec fallbacks robustes"""

import os

# Détecte si on veut éviter de charger le vrai modèle (mode tests CI)
SKIP_MODEL = os.environ.get("SKIP_MODEL_DOWNLOAD", "false").lower() in ("1", "true", "yes")

# Variables globales pour le modèle
tokenizer = None
model = None
gen_pipe = None

def load_model():
    """Charge le modèle avec des fallbacks robustes"""
    global tokenizer, model, gen_pipe, SKIP_MODEL
    
    if SKIP_MODEL:
        return False
        
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        # Modèles par ordre de préférence (du plus léger au plus complexe)
        model_options = [
            "distilgpt2",           # Très léger, très compatible
            "gpt2",                 # Léger, très compatible  
            "microsoft/DialoGPT-small"  # Spécialisé dialogue
        ]
        
        for model_name in model_options:
            try:
                print(f"🤖 Tentative de chargement: {model_name}")
                
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Configuration du tokenizer
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                gen_pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                
                print(f"✅ Modèle {model_name} chargé avec succès")
                return True
                
            except Exception as e:
                print(f"❌ Échec {model_name}: {str(e)[:100]}...")
                continue
        
        print("❌ Aucun modèle disponible, utilisation du mode fallback")
        SKIP_MODEL = True
        return False
        
    except Exception as e:
        print(f"❌ Erreur import transformers: {e}")
        SKIP_MODEL = True
        return False

# Tentative de chargement au démarrage
if not SKIP_MODEL:
    load_model()

def generer_reponse(texte, sentiment="negative"):
    """
    Génère une réponse polie au client.
    Utilise des templates prédéfinis si le modèle n'est pas disponible.
    """
    
    # MODE FALLBACK: Réponses prédéfinies intelligentes
    if SKIP_MODEL or gen_pipe is None:
        
        # Analyser le sentiment pour personnaliser
        if any(word in sentiment.lower() for word in ["positif", "positive", "good", "great"]):
            return (
                f"Merci beaucoup pour votre retour positif ! "
                f"Nous sommes ravis que notre produit vous satisfasse. "
                f"Votre satisfaction est notre priorité. "
                f"N'hésitez pas à nous recontacter si vous avez des questions."
            )
        
        elif any(word in sentiment.lower() for word in ["neutre", "neutral", "mixed"]):
            return (
                f"Merci pour votre retour constructif. "
                f"Nous prenons tous les commentaires en considération "
                f"pour améliorer continuellement nos services. "
                f"Votre avis nous aide à mieux vous servir."
            )
        
        else:  # Sentiment négatif
            return (
                f"Nous vous remercions pour votre retour et nous excusons "
                f"sincèrement pour les désagréments rencontrés. "
                f"Votre expérience nous tient à cœur et nous allons examiner "
                f"votre situation avec attention pour trouver une solution rapide."
            )
    
    # MODE IA: Génération avec modèle
    try:
        # Prompt simple et efficace
        context = f"Message client: {texte[:200]}"
        
        result = gen_pipe(
            context,
            max_length=len(context) + 100,
            num_return_sequences=1,
            temperature=0.6
        )
        
        generated = result[0]["generated_text"]
        
        # Nettoyer la réponse générée
        if context in generated:
            response = generated.replace(context, "").strip()
            if len(response) > 20:  # Réponse valide
                return response[:300]  # Limiter la taille
    
    except Exception as e:
        print(f"Erreur génération IA: {e}")
    
    # FALLBACK FINAL en cas d'erreur IA
    return (
        "Merci pour votre message. Nous avons bien reçu vos commentaires "
        "et notre équipe vous recontactera rapidement pour vous assister."
    )


# Test de la fonction
if __name__ == "__main__":
    print("🧪 Test des réponses...")
    
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

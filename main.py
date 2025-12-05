# -*- coding: utf-8 -*-
"""
API FastAPI principale pour l'analyse de sentiment et génération de réponses
Architecture moderne avec configuration centralisée
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from config.settings import APIConfig
from generate_response import generer_reponse
from data_processing import clean_text, analyze_sentiment_simple, label_sentiment, process_review

# Configuration de l'application FastAPI
app = FastAPI(
    title=APIConfig.TITLE,
    description=APIConfig.DESCRIPTION,
    version=APIConfig.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware CORS pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic pour la validation des données
class AnalyseRequest(BaseModel):
    """Modèle de requête pour l'analyse de sentiment"""
    texte: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="Le texte de l'avis client à analyser",
        example="Ce produit est absolument fantastique! Je le recommande vivement."
    )
    note_numerique: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Note optionnelle de 1 à 5 étoiles",
        example=5
    )

class AnalyseResponse(BaseModel):
    """Modèle de réponse pour l'analyse"""
    sentiment: str = Field(description="Sentiment détecté", example="positive")
    reponse: str = Field(description="Réponse générée automatiquement", example="Merci beaucoup pour votre retour positif !")
    texte_nettoye: str = Field(description="Texte après nettoyage", example="produit fantastique recommande")
    confiance: str = Field(description="Niveau de confiance de l'analyse", example="élevée")

class HealthResponse(BaseModel):
    """Modèle de réponse pour le health check"""
    status: str = Field(example="healthy")
    version: str = Field(example="1.0.0")
    mode: str = Field(example="fallback")

# Endpoints de l'API

@app.get("/", summary="Page d'accueil")
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": f"Bienvenue sur {APIConfig.TITLE}",
        "documentation": "/docs",
        "version": APIConfig.VERSION,
        "endpoints": {
            "analyse": "POST /analyse - Analyser un avis client",
            "health": "GET /health - Vérifier l'état de l'API"
        }
    }

@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    from config.settings import AIConfig
    
    return HealthResponse(
        status="healthy",
        version=APIConfig.VERSION,
        mode="ai" if AIConfig.ENABLE_AI_MODEL else "fallback"
    )

@app.post("/analyse", response_model=AnalyseResponse, summary="Analyser un avis client")
async def analyser_avis(request: AnalyseRequest):
    """
    Analyse le sentiment d'un avis client et génère une réponse appropriée
    
    Cette API :
    1. Nettoie le texte d'entrée
    2. Détermine le sentiment (positif, négatif, neutre)  
    3. Génère une réponse professionnelle adaptée
    
    Args:
        request: Objet contenant le texte à analyser et optionnellement une note
        
    Returns:
        Objet avec le sentiment détecté et la réponse générée
        
    Raises:
        HTTPException: Si le traitement échoue
    """
    
    try:
        # Traitement complet de l'avis
        processed = process_review(request.texte, request.note_numerique)
        
        # Génération de la réponse
        reponse = generer_reponse(processed["cleaned_text"], processed["sentiment"])
        
        # Détermination du niveau de confiance
        confiance = "élevée"
        if request.note_numerique is not None:
            confiance = "très élevée"  # Note explicite = plus fiable
        elif len(processed["cleaned_text"]) < 10:
            confiance = "faible"  # Texte très court = moins fiable
        
        return AnalyseResponse(
            sentiment=processed["sentiment"],
            reponse=reponse,
            texte_nettoye=processed["cleaned_text"],
            confiance=confiance
        )
        
    except Exception as e:
        # Log l'erreur (en production, utiliser un logger)
        print(f"❌ Erreur dans l'analyse: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du traitement de l'avis. Veuillez réessayer."
        )

@app.get("/stats", summary="Statistiques de l'API")
async def get_stats():
    """Retourne des statistiques basiques sur l'API"""
    from config.settings import AIConfig
    
    return {
        "mode_ia": AIConfig.ENABLE_AI_MODEL,
        "modeles_disponibles": AIConfig.FALLBACK_MODELS if AIConfig.ENABLE_AI_MODEL else [],
        "endpoints_disponibles": len(app.routes),
        "version": APIConfig.VERSION
    }

# Endpoint de debug (développement uniquement)
@app.post("/debug/texte", summary="Debug - Nettoyage de texte")
async def debug_clean_text(texte: str):
    """
    Endpoint de debug pour tester le nettoyage de texte
    """
    from config.settings import DeploymentConfig
    
    if not DeploymentConfig.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint disponible uniquement en mode développement"
        )
    
    return {
        "original": texte,
        "nettoye": clean_text(texte),
        "sentiment_simple": analyze_sentiment_simple(texte)
    }

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    print(f"🚀 Démarrage de {APIConfig.TITLE} v{APIConfig.VERSION}")
    print(f"📍 Mode: {'IA' if AIConfig.ENABLE_AI_MODEL else 'Fallback'}")
    
    uvicorn.run(
        "main:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        reload=DeploymentConfig.DEBUG,
        log_level=DeploymentConfig.LOG_LEVEL.lower()
    )
# -*- coding: utf-8 -*-
"""
Module de traitement des données Amazon
Logique métier séparée pour une meilleure maintenabilité
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from utils.common import (
    deps, paths, print_status, print_section, 
    safe_json_dump, safe_json_load, validate_text_input, validate_rating
)

class AmazonDataProcessor:
    """Processeur spécialisé pour les données Amazon"""
    
    def __init__(self):
        self.data_dir = paths.data_dir
        self.reviews_file = self.data_dir / "amazon_reviews.json"
        self.training_file = self.data_dir / "training_data.json"
    
    def load_huggingface_data(self, limit: int = 100) -> List[Dict]:
        """Charge les vraies données Amazon depuis Hugging Face"""
        
        if not deps.is_available('datasets') or not deps.is_available('pandas'):
            print_status("Hugging Face datasets non disponible, fallback synthétique", 'warning')
            return self.create_synthetic_data()
        
        try:
            import pandas as pd
            from datasets import load_dataset
            
            print_status(f"Chargement données Hugging Face (limite: {limit})", 'process')
            dataset = load_dataset("SetFit/amazon_reviews_multi_fr", split=f"train[:{limit}]")
            df = pd.DataFrame(dataset)
            
            amazon_data = []
            for _, row in df.iterrows():
                # Mapping des labels : 0=1étoile, 1=2étoiles, etc.
                rating = int(row['label']) + 1
                amazon_data.append({
                    "review_text": str(row['text']),
                    "rating": rating,
                    "source": "huggingface"
                })
            
            # Sauvegarder
            success, msg = safe_json_dump(amazon_data, self.reviews_file)
            if success:
                print_status(f"Dataset Hugging Face sauvegardé: {len(amazon_data)} avis", 'success')
            
            return amazon_data
            
        except Exception as e:
            print_status(f"Erreur Hugging Face: {e}", 'error')
            print_status("Fallback vers données synthétiques", 'warning')
            return self.create_synthetic_data()
    
    def create_synthetic_data(self) -> List[Dict]:
        """Crée des données synthétiques réalistes"""
        
        synthetic_data = [
            # Avis positifs (4-5 étoiles)
            {"review_text": "Produit absolument fantastique ! Très satisfait de mon achat, je le recommande vivement à tous.", "rating": 5, "source": "synthetic"},
            {"review_text": "Excellente qualité, livraison rapide. Conforme à mes attentes, très bon rapport qualité-prix.", "rating": 5, "source": "synthetic"},
            {"review_text": "Très bon produit, bien emballé. Service client réactif. Je recommande cette marque.", "rating": 4, "source": "synthetic"},
            {"review_text": "Satisfait de cet achat. Produit solide et bien fini. Livraison dans les temps.", "rating": 4, "source": "synthetic"},
            {"review_text": "Super produit ! Exactement ce que je cherchais. Merci pour la rapidité d'expédition.", "rating": 5, "source": "synthetic"},
            {"review_text": "Bonne qualité, conforme à la description. Prix correct pour ce type de produit.", "rating": 4, "source": "synthetic"},
            
            # Avis négatifs (1-2 étoiles)
            {"review_text": "Très déçu de cet achat. Qualité médiocre, ne correspond pas à la description.", "rating": 2, "source": "synthetic"},
            {"review_text": "Produit défectueux dès la première utilisation. Service client non réactif. À éviter.", "rating": 1, "source": "synthetic"},
            {"review_text": "Mauvaise qualité, matériaux cheap. Photos trompeuses sur le site. Déçu.", "rating": 1, "source": "synthetic"},
            {"review_text": "Pas terrible du tout. Livraison en retard et produit abîmé. Demande de remboursement.", "rating": 2, "source": "synthetic"},
            {"review_text": "N'achetez pas ce produit ! Arnaque totale, rien ne fonctionne comme annoncé.", "rating": 1, "source": "synthetic"},
            {"review_text": "Qualité décevante pour le prix payé. Attention aux avis bidons, ne vous fiez pas.", "rating": 2, "source": "synthetic"},
            
            # Avis neutres (3 étoiles)
            {"review_text": "Produit correct, sans plus. Fait le travail mais rien d'exceptionnel. Prix moyen.", "rating": 3, "source": "synthetic"},
            {"review_text": "Moyen, la qualité pourrait être mieux. Acceptable pour le prix mais sans plus.", "rating": 3, "source": "synthetic"},
            {"review_text": "Ça va, ni bon ni mauvais. Répond aux besoins de base. On trouve mieux ailleurs.", "rating": 3, "source": "synthetic"},
            {"review_text": "Correct pour dépanner. Qualité moyenne, service client moyen. Rien d'extraordinaire.", "rating": 3, "source": "synthetic"}
        ]
        
        # Sauvegarder
        success, msg = safe_json_dump(synthetic_data, self.reviews_file)
        if success:
            print_status(f"Dataset synthétique créé: {len(synthetic_data)} avis", 'success')
        
        return synthetic_data
    
    def prepare_training_data(self, reviews_data: List[Dict] = None) -> List[Dict]:
        """Prépare les données pour l'entraînement"""
        
        if reviews_data is None:
            # Charger depuis le fichier
            success, data = safe_json_load(self.reviews_file)
            if not success:
                print_status("Fichier de données non trouvé, création données synthétiques", 'warning')
                reviews_data = self.create_synthetic_data()
            else:
                reviews_data = data
        
        training_pairs = []
        
        for review in reviews_data:
            text = review["review_text"]
            rating = review["rating"]
            
            # Validation
            text_valid, _ = validate_text_input(text)
            rating_valid, _ = validate_rating(rating)
            
            if not text_valid or not rating_valid:
                continue
            
            # Déterminer sentiment et réponse
            if rating >= 4:
                sentiment = "positive"
                response = "Merci beaucoup pour votre retour positif ! Nous sommes ravis que le produit vous satisfasse pleinement."
            elif rating <= 2:
                sentiment = "negative" 
                response = "Nous sommes désolés que le produit n'ait pas répondu à vos attentes. Contactez notre service client pour une solution."
            else:
                sentiment = "neutral"
                response = "Merci pour votre retour. Nous prenons note de vos commentaires pour améliorer nos produits."
            
            training_pairs.append({
                "input": f"Avis client: {text}",
                "output": response,
                "sentiment": sentiment,
                "rating": rating,
                "source": review.get("source", "unknown")
            })
        
        # Sauvegarder
        success, msg = safe_json_dump(training_pairs, self.training_file)
        if success:
            print_status(f"Données d'entraînement préparées: {len(training_pairs)} exemples", 'success')
        
        return training_pairs
    
    def create_unified_dataset(self, use_huggingface: bool = True, limit: int = 100) -> List[Dict]:
        """Méthode unifiée pour créer le dataset"""
        
        print_section("Création du dataset Amazon")
        
        if use_huggingface and deps.is_available('datasets'):
            print_status("Tentative avec données Hugging Face", 'process')
            return self.load_huggingface_data(limit)
        else:
            print_status("Utilisation des données synthétiques", 'process')
            return self.create_synthetic_data()
    
    def get_dataset_stats(self) -> Dict:
        """Retourne les statistiques du dataset"""
        
        success, data = safe_json_load(self.reviews_file)
        if not success:
            return {"error": "Dataset non trouvé"}
        
        stats = {
            "total_reviews": len(data),
            "by_rating": {},
            "by_source": {},
            "avg_text_length": 0
        }
        
        # Calcul statistiques
        for review in data:
            rating = review.get("rating", 0)
            source = review.get("source", "unknown")
            
            stats["by_rating"][rating] = stats["by_rating"].get(rating, 0) + 1
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
        
        # Longueur moyenne
        if data:
            avg_length = sum(len(r["review_text"]) for r in data) / len(data)
            stats["avg_text_length"] = round(avg_length, 1)
        
        return stats

class TrainingDataConverter:
    """Convertisseur pour différents formats de données d'entraînement"""
    
    def __init__(self):
        self.data_dir = paths.data_dir
    
    def to_text_format(self, training_pairs: List[Dict], output_file: str = "training_text.txt") -> str:
        """Convertit en format texte pour GPT-2"""
        
        text_lines = []
        for item in training_pairs:
            line = f"{item['input']} <|endoftext|> {item['output']} <|endoftext|>"
            text_lines.append(line)
        
        output_path = self.data_dir / output_file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_lines))
            
            print_status(f"Format texte créé: {output_path}", 'success')
            return str(output_path)
            
        except Exception as e:
            print_status(f"Erreur création format texte: {e}", 'error')
            return None
    
    def to_csv_format(self, training_pairs: List[Dict], output_file: str = "training_data.csv") -> str:
        """Convertit en format CSV"""
        
        if not deps.is_available('pandas'):
            print_status("Pandas requis pour le format CSV", 'error')
            return None
        
        try:
            import pandas as pd
            
            df = pd.DataFrame(training_pairs)
            output_path = self.data_dir / output_file
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            print_status(f"Format CSV créé: {output_path}", 'success')
            return str(output_path)
            
        except Exception as e:
            print_status(f"Erreur création CSV: {e}", 'error')
            return None

# Tests unitaires
def run_data_tests():
    """Tests des modules de données"""
    print_section("Tests des modules de données")
    
    # Test processeur de données
    processor = AmazonDataProcessor()
    
    # Test données synthétiques
    synthetic_data = processor.create_synthetic_data()
    assert len(synthetic_data) > 0, "Données synthétiques vides"
    print_status("Données synthétiques: OK", 'success')
    
    # Test préparation training
    training_data = processor.prepare_training_data(synthetic_data[:5])
    assert len(training_data) > 0, "Données d'entraînement vides"
    print_status("Préparation d'entraînement: OK", 'success')
    
    # Test convertisseur
    converter = TrainingDataConverter()
    text_file = converter.to_text_format(training_data)
    assert text_file is not None, "Conversion texte échoué"
    print_status("Conversion format texte: OK", 'success')
    
    # Test statistiques
    stats = processor.get_dataset_stats()
    assert "total_reviews" in stats, "Statistiques manquantes"
    print_status("Calcul statistiques: OK", 'success')
    
    print_status("Tous les tests de données passés!", 'success')

if __name__ == "__main__":
    run_data_tests()
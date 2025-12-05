# -*- coding: utf-8 -*-
"""
Module d'entraînement de modèles ML
Logique métier séparée et optimisée
"""

from pathlib import Path
from typing import Optional, List, Dict
from utils.common import (
    deps, paths, print_status, print_section,
    TrainingEnvironmentDetector, safe_json_dump, safe_json_load
)
from core.data_manager import AmazonDataProcessor, TrainingDataConverter

class ModelTrainer:
    """Entraîneur de modèles avec gestion intelligente des environnements"""
    
    def __init__(self):
        self.models_dir = paths.models_dir
        self.model_path = self.models_dir / "amazon_trained"
        self.data_processor = AmazonDataProcessor()
        self.data_converter = TrainingDataConverter()
    
    def setup_training_environment(self):
        """Configure l'environnement d'entraînement"""
        recommendation = TrainingEnvironmentDetector.get_recommended_config()
        
        print_section("Configuration de l'environnement d'entraînement")
        print_status(f"Mode recommandé: {recommendation['mode']}", 'ai')
        print_status(f"Raison: {recommendation['reason']}", 'info')
        
        return recommendation
    
    def train_pytorch_model(self, 
                          training_data_path: str,
                          model_name: str = "distilgpt2", 
                          epochs: int = 1,
                          batch_size: int = 1) -> Optional[str]:
        """Entraîne un modèle PyTorch/Transformers"""
        
        if not deps.is_available('pytorch_ml'):
            print_status("PyTorch/Transformers requis pour l'entraînement", 'error')
            return None
        
        try:
            from transformers import (
                GPT2LMHeadModel, GPT2Tokenizer, 
                TextDataset, DataCollatorForLanguageModeling,
                Trainer, TrainingArguments
            )
            import torch
            
            print_status(f"Chargement du modèle {model_name}", 'process')
            
            # Chargement modèle et tokenizer
            tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            model = GPT2LMHeadModel.from_pretrained(model_name)
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Dataset
            dataset = TextDataset(
                tokenizer=tokenizer,
                file_path=training_data_path,
                block_size=64  # Optimisé pour les ressources limitées
            )
            
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # Configuration d'entraînement optimisée
            training_args = TrainingArguments(
                output_dir=str(self.model_path),
                overwrite_output_dir=True,
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=2,
                save_steps=10,
                save_total_limit=1,
                logging_steps=5,
                warmup_steps=10,
                prediction_loss_only=True,
                report_to=[],
                dataloader_num_workers=0,
                dataloader_drop_last=True,
                remove_unused_columns=False,
            )
            
            # Entraînement
            trainer = Trainer(
                model=model,
                args=training_args,
                data_collator=data_collator,
                train_dataset=dataset,
            )
            
            print_status(f"Début de l'entraînement ({epochs} époques)", 'process')
            trainer.train()
            
            # Sauvegarde
            self.model_path.mkdir(exist_ok=True)
            trainer.save_model(str(self.model_path))
            tokenizer.save_pretrained(str(self.model_path))
            
            # Métadonnées
            metadata = {
                "base_model": model_name,
                "epochs": epochs,
                "batch_size": batch_size,
                "training_samples": len(dataset),
                "version": "pytorch",
                "timestamp": str(Path().resolve())
            }
            
            success, _ = safe_json_dump(metadata, self.model_path / "training_metadata.json")
            
            print_status("Modèle entraîné et sauvegardé", 'success')
            return str(self.model_path)
            
        except Exception as e:
            print_status(f"Erreur entraînement: {e}", 'error')
            return None
    
    def test_trained_model(self, test_inputs: List[str] = None) -> Dict:
        """Teste le modèle entraîné"""
        
        if not self.model_path.exists():
            return {"error": "Modèle non trouvé"}
        
        if not deps.is_available('pytorch_ml'):
            return {"error": "PyTorch requis pour tester le modèle"}
        
        if test_inputs is None:
            test_inputs = [
                "Avis client: Produit fantastique, très satisfait!",
                "Avis client: Très déçu, qualité médiocre",
                "Avis client: Correct, fait le travail"
            ]
        
        try:
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            import torch
            
            print_status("Chargement du modèle pour test", 'process')
            
            tokenizer = GPT2Tokenizer.from_pretrained(str(self.model_path))
            model = GPT2LMHeadModel.from_pretrained(str(self.model_path))
            model.eval()
            
            results = []
            
            for test_input in test_inputs:
                inputs = tokenizer.encode(test_input, return_tensors="pt", max_length=100, truncation=True)
                
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_length=inputs.shape[1] + 40,
                        temperature=0.8,
                        do_sample=True,
                        top_k=50,
                        top_p=0.9,
                        pad_token_id=tokenizer.eos_token_id,
                        repetition_penalty=1.2
                    )
                
                full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                generated_part = full_response[len(test_input):].strip()
                
                results.append({
                    "input": test_input,
                    "output": generated_part,
                    "quality": "good" if 10 < len(generated_part) < 200 else "poor"
                })
                
                print_status(f"Test: {test_input[:50]}...", 'info')
                print_status(f"Réponse: {generated_part[:100]}...", 'success')
            
            return {"results": results, "model_path": str(self.model_path)}
            
        except Exception as e:
            print_status(f"Erreur test modèle: {e}", 'error')
            return {"error": str(e)}

class TrainingSimulator:
    """Simulateur d'entraînement pour environnements sans ML"""
    
    def __init__(self):
        self.models_dir = paths.models_dir
        self.model_path = self.models_dir / "amazon_trained"
        self.data_processor = AmazonDataProcessor()
    
    def simulate_training(self, data_limit: int = 10) -> bool:
        """Simule un entraînement complet"""
        
        print_section("Simulation d'entraînement")
        
        try:
            # 1. Données
            print_status("Création des données", 'process')
            reviews = self.data_processor.create_synthetic_data()
            
            # 2. Préparation
            print_status("Préparation de l'entraînement", 'process') 
            training_data = self.data_processor.prepare_training_data(reviews[:data_limit])
            
            # 3. Simulation
            print_status("Simulation de l'entraînement ML", 'process')
            self._create_fake_model(training_data)
            
            # 4. Test
            print_status("Test du modèle simulé", 'process')
            self._test_fake_model()
            
            print_status("Simulation terminée avec succès", 'success')
            return True
            
        except Exception as e:
            print_status(f"Erreur simulation: {e}", 'error')
            return False
    
    def _create_fake_model(self, training_data: List[Dict]):
        """Crée un faux modèle pour la démo"""
        
        self.model_path.mkdir(exist_ok=True)
        
        # Config simulée
        fake_config = {
            "model_type": "gpt2_simulation",
            "trained_on": "amazon_reviews",
            "training_samples": len(training_data),
            "status": "demo_simulation",
            "note": "Version démo - remplacez par un vrai modèle entraîné"
        }
        
        safe_json_dump(fake_config, self.model_path / "config.json")
        
        # Réponses pré-programmées
        demo_responses = {}
        for item in training_data:
            demo_responses[item['input']] = item['output']
        
        safe_json_dump(demo_responses, self.model_path / "demo_responses.json")
    
    def _test_fake_model(self):
        """Teste le modèle simulé"""
        
        success, responses = safe_json_load(self.model_path / "demo_responses.json")
        if not success:
            print_status("Modèle simulé non trouvé", 'error')
            return
        
        test_cases = [
            "Avis client: Produit fantastique!",
            "Avis client: Très déçu",
            "Avis client: Correct, sans plus"
        ]
        
        for test_input in test_cases:
            # Recherche de réponse similaire
            response = self._find_similar_response(test_input, responses)
            print_status(f"Test: {test_input}", 'info')
            print_status(f"Réponse: {response}", 'success')
    
    def _find_similar_response(self, test_input: str, responses: Dict) -> str:
        """Trouve une réponse similaire basée sur des mots-clés"""
        
        test_lower = test_input.lower()
        
        # Mots-clés pour classification
        if any(word in test_lower for word in ["fantastique", "super", "excellent", "satisfait"]):
            sentiment = "positive"
        elif any(word in test_lower for word in ["déçu", "mauvais", "horrible", "problème"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Chercher une réponse du bon type
        for input_key, output_val in responses.items():
            if sentiment == "positive" and "ravis" in output_val:
                return output_val
            elif sentiment == "negative" and "désolés" in output_val:
                return output_val
            elif sentiment == "neutral" and "prenons note" in output_val:
                return output_val
        
        return "Merci pour votre retour, nous l'étudions avec attention."

class TrainingOrchestrator:
    """Orchestrateur principal pour gérer tous les types d'entraînement"""
    
    def __init__(self):
        self.trainer = ModelTrainer()
        self.simulator = TrainingSimulator()
        self.data_processor = AmazonDataProcessor()
        self.data_converter = TrainingDataConverter()
    
    def run_complete_pipeline(self, 
                            force_mode: str = None,
                            use_huggingface: bool = True,
                            data_limit: int = 100,
                            epochs: int = 1) -> Dict:
        """Pipeline complet avec détection automatique du mode optimal"""
        
        print_section("Pipeline d'entraînement Amazon")
        
        # Détection du mode optimal
        if force_mode:
            mode = force_mode
            reason = "Mode forcé par utilisateur"
        else:
            recommendation = self.trainer.setup_training_environment()
            mode = recommendation['mode']
            reason = recommendation['reason']
        
        print_status(f"Mode sélectionné: {mode} ({reason})", 'ai')
        
        results = {
            "mode": mode,
            "reason": reason,
            "success": False,
            "details": {}
        }
        
        try:
            # 1. Préparation des données
            print_status("Préparation des données", 'data')
            dataset = self.data_processor.create_unified_dataset(use_huggingface, data_limit)
            training_data = self.data_processor.prepare_training_data(dataset)
            
            results["details"]["data_samples"] = len(training_data)
            results["details"]["data_source"] = "huggingface" if use_huggingface and deps.is_available('datasets') else "synthetic"
            
            if mode == 'demo':
                # Mode simulation
                success = self.simulator.simulate_training(min(data_limit, 15))
                results["details"]["training_type"] = "simulation"
                
            elif mode in ['light', 'full']:
                # Mode entraînement réel
                text_file = self.data_converter.to_text_format(training_data)
                if text_file:
                    model_name = "distilgpt2" if mode == 'light' else "gpt2"
                    batch_size = 1 if mode == 'light' else 2
                    
                    model_path = self.trainer.train_pytorch_model(
                        text_file, model_name, epochs, batch_size
                    )
                    
                    success = model_path is not None
                    results["details"]["training_type"] = "pytorch"
                    results["details"]["model_name"] = model_name
                    results["details"]["model_path"] = model_path
                else:
                    success = False
            
            results["success"] = success
            
            # Test du modèle si succès
            if success and mode != 'demo':
                test_results = self.trainer.test_trained_model()
                results["details"]["test_results"] = test_results
            
            status_msg = "Pipeline terminé avec succès" if success else "Pipeline échoué"
            level = 'success' if success else 'error'
            print_status(status_msg, level)
            
        except Exception as e:
            print_status(f"Erreur pipeline: {e}", 'error')
            results["details"]["error"] = str(e)
        
        return results

# Tests unitaires
def run_training_tests():
    """Tests des modules d'entraînement"""
    print_section("Tests des modules d'entraînement")
    
    # Test détection environnement
    recommendation = TrainingEnvironmentDetector.get_recommended_config()
    assert "mode" in recommendation, "Recommandation manquante"
    print_status("Détection environnement: OK", 'success')
    
    # Test simulateur
    simulator = TrainingSimulator()
    success = simulator.simulate_training(5)
    assert success, "Simulation d'entraînement échouée"
    print_status("Simulation d'entraînement: OK", 'success')
    
    # Test orchestrateur  
    orchestrator = TrainingOrchestrator()
    results = orchestrator.run_complete_pipeline(force_mode="demo", data_limit=5)
    assert results["success"], "Pipeline orchestrateur échoué"
    print_status("Orchestrateur: OK", 'success')
    
    print_status("Tous les tests d'entraînement passés!", 'success')

if __name__ == "__main__":
    run_training_tests()
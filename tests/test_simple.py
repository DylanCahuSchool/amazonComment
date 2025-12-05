#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unifiés pour l'architecture refactorisée
Suite de tests complète et moderne
"""

import sys
import unittest
from pathlib import Path

# Ajout du chemin du projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.common import (
    deps, print_status, print_section, 
    validate_text_input, validate_rating,
    safe_json_dump, safe_json_load
)
from core.data_manager import AmazonDataProcessor, TrainingDataConverter
from core.training_manager import TrainingOrchestrator
import tempfile
import json

class TestUtilsCommon(unittest.TestCase):
    """Tests pour les utilitaires communs"""
    
    def test_conditional_imports(self):
        """Test de la détection des imports conditionnels"""
        status = deps.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn('torch', status)
        self.assertIn('transformers', status)
    
    def test_text_validation(self):
        """Test de la validation de texte"""
        # Texte valide
        valid, msg = validate_text_input("Texte de test valide")
        self.assertTrue(valid)
        
        # Texte trop court
        invalid, msg = validate_text_input("")
        self.assertFalse(invalid)
        
        # Texte trop long
        long_text = "a" * 3000
        invalid, msg = validate_text_input(long_text)
        self.assertFalse(invalid)
    
    def test_rating_validation(self):
        """Test de la validation des notes"""
        # Note valide
        valid, msg = validate_rating(4)
        self.assertTrue(valid)
        
        # Note invalide
        invalid, msg = validate_rating(10)
        self.assertFalse(invalid)

class TestDataManager(unittest.TestCase):
    """Tests pour le gestionnaire de données"""
    
    def setUp(self):
        self.processor = AmazonDataProcessor()
        self.converter = TrainingDataConverter()
    
    def test_synthetic_data_creation(self):
        """Test de la création de données synthétiques"""
        data = self.processor.create_synthetic_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Vérifier la structure
        first_item = data[0]
        self.assertIn("review_text", first_item)
        self.assertIn("rating", first_item)
        self.assertIn("source", first_item)
    
    def test_training_data_preparation(self):
        """Test de la préparation des données d'entraînement"""
        # Données de test
        test_reviews = [
            {"review_text": "Excellent produit!", "rating": 5, "source": "test"},
            {"review_text": "Très déçu", "rating": 1, "source": "test"}
        ]
        
        training_data = self.processor.prepare_training_data(test_reviews)
        self.assertIsInstance(training_data, list)
        self.assertEqual(len(training_data), 2)
        
        # Vérifier la structure
        first_item = training_data[0]
        self.assertIn("input", first_item)
        self.assertIn("output", first_item)
        self.assertIn("sentiment", first_item)
    
    def test_text_format_conversion(self):
        """Test de la conversion au format texte"""
        test_data = [
            {
                "input": "Avis client: Test",
                "output": "Merci pour votre retour",
                "sentiment": "neutral",
                "rating": 3
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Changer temporairement le répertoire de données
            original_data_dir = self.converter.data_dir
            self.converter.data_dir = Path(temp_dir)
            
            try:
                result = self.converter.to_text_format(test_data)
                self.assertIsNotNone(result)
                self.assertTrue(Path(result).exists())
                
                # Vérifier le contenu
                with open(result, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn("Avis client: Test", content)
                    self.assertIn("<|endoftext|>", content)
                    
            finally:
                # Restaurer le répertoire original
                self.converter.data_dir = original_data_dir

class TestTrainingManager(unittest.TestCase):
    """Tests pour le gestionnaire d'entraînement"""
    
    def setUp(self):
        self.orchestrator = TrainingOrchestrator()
    
    def test_demo_pipeline(self):
        """Test du pipeline en mode démo"""
        results = self.orchestrator.run_complete_pipeline(
            force_mode="demo",
            data_limit=5
        )
        
        self.assertIsInstance(results, dict)
        self.assertIn("success", results)
        self.assertIn("mode", results)
        self.assertEqual(results["mode"], "demo")
    
    def test_orchestrator_configuration(self):
        """Test de la configuration de l'orchestrateur"""
        # Vérifier que tous les composants sont initialisés
        self.assertIsNotNone(self.orchestrator.trainer)
        self.assertIsNotNone(self.orchestrator.simulator)
        self.assertIsNotNone(self.orchestrator.data_processor)
        self.assertIsNotNone(self.orchestrator.data_converter)

class TestJsonOperations(unittest.TestCase):
    """Tests pour les opérations JSON sécurisées"""
    
    def test_safe_json_operations(self):
        """Test des opérations JSON sécurisées"""
        test_data = {"test": "data", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Test sauvegarde
            success, msg = safe_json_dump(test_data, temp_file)
            self.assertTrue(success)
            
            # Test chargement
            success, loaded_data = safe_json_load(temp_file)
            self.assertTrue(success)
            self.assertEqual(loaded_data, test_data)
            
        finally:
            # Nettoyage
            Path(temp_file).unlink(missing_ok=True)

def run_comprehensive_tests():
    """Lance tous les tests avec un rapport détaillé"""
    print_section("Tests unitaires de l'architecture refactorisée")
    
    # Configuration du test runner
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajout des classes de test
    test_classes = [
        TestUtilsCommon,
        TestDataManager,
        TestTrainingManager,
        TestJsonOperations
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Lancement des tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Résumé
    print_section("Résumé des tests")
    print_status(f"Tests exécutés: {result.testsRun}")
    print_status(f"Échecs: {len(result.failures)}")
    print_status(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print_status("ÉCHECS:", 'error')
        for test, traceback in result.failures:
            print_status(f"  - {test}", 'error')
    
    if result.errors:
        print_status("ERREURS:", 'error')
        for test, traceback in result.errors:
            print_status(f"  - {test}", 'error')
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print_status("Tous les tests sont passés!", 'success')
    else:
        print_status("Certains tests ont échoué", 'warning')
    
    return success

def quick_integration_test():
    """Test d'intégration rapide"""
    print_section("Test d'intégration rapide")
    
    try:
        # Test du pipeline complet en mode démo
        print_status("Test du pipeline complet...", 'process')
        orchestrator = TrainingOrchestrator()
        results = orchestrator.run_complete_pipeline(force_mode="demo", data_limit=3)
        
        if results["success"]:
            print_status("Pipeline d'intégration: OK", 'success')
            return True
        else:
            print_status("Pipeline d'intégration: ÉCHEC", 'error')
            return False
    
    except Exception as e:
        print_status(f"Erreur test d'intégration: {e}", 'error')
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tests pour l'architecture refactorisée")
    parser.add_argument('--quick', action='store_true', help='Test d\'intégration rapide seulement')
    parser.add_argument('--unit', action='store_true', help='Tests unitaires seulement')
    
    args = parser.parse_args()
    
    overall_success = True
    
    if args.quick:
        success = quick_integration_test()
        overall_success = overall_success and success
    elif args.unit:
        success = run_comprehensive_tests()
        overall_success = overall_success and success
    else:
        # Par défaut, lancer les deux
        unit_success = run_comprehensive_tests()
        integration_success = quick_integration_test()
        overall_success = unit_success and integration_success
    
    if overall_success:
        print_status("🎉 Tous les tests sont passés!", 'success')
        sys.exit(0)
    else:
        print_status("⚠️ Certains tests ont échoué", 'warning')
        sys.exit(1)
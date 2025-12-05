#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée unifié pour l'entraînement Amazon
Interface simplifiée utilisant l'architecture refactorisée
"""

import sys
import argparse
from pathlib import Path

# Ajout du chemin du projet au PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.common import print_status, print_section, get_system_info
from core.training_manager import TrainingOrchestrator

def show_system_info():
    """Affiche les informations système"""
    print_section("Informations système")
    
    info = get_system_info()
    
    print_status(f"Python: {info['python_version'].split()[0]}")
    print_status(f"Plateforme: {info['platform']}")
    
    if isinstance(info['memory'], dict):
        print_status(f"RAM: {info['memory']['available_gb']:.1f}GB disponible / {info['memory']['total_gb']:.1f}GB total")
        
    deps_available = sum(info['dependencies'].values())
    deps_total = len(info['dependencies'])
    print_status(f"Dépendances: {deps_available}/{deps_total} disponibles")
    
    # Détail des dépendances importantes
    important_deps = ['torch', 'transformers', 'datasets', 'pandas']
    for dep in important_deps:
        status = "✅" if info['dependencies'].get(dep, False) else "❌"
        print_status(f"  {dep}: {status}")

def train_with_options(mode=None, use_huggingface=True, data_limit=100, epochs=1):
    """Lance l'entraînement avec les options spécifiées"""
    
    print_section("Amazon Comments - Entraînement de modèle")
    
    orchestrator = TrainingOrchestrator()
    
    print_status("Démarrage du pipeline d'entraînement", 'process')
    
    results = orchestrator.run_complete_pipeline(
        force_mode=mode,
        use_huggingface=use_huggingface,
        data_limit=data_limit,
        epochs=epochs
    )
    
    # Affichage des résultats
    print_section("Résultats de l'entraînement")
    
    if results["success"]:
        print_status("Entraînement terminé avec succès!", 'success')
        print_status(f"Mode utilisé: {results['mode']}")
        print_status(f"Échantillons: {results['details'].get('data_samples', 'N/A')}")
        print_status(f"Source données: {results['details'].get('data_source', 'N/A')}")
        print_status(f"Type: {results['details'].get('training_type', 'N/A')}")
        
        if 'model_path' in results['details']:
            print_status(f"Modèle sauvegardé: {results['details']['model_path']}", 'file')
    else:
        print_status("Entraînement échoué", 'error')
        if 'error' in results['details']:
            print_status(f"Erreur: {results['details']['error']}", 'error')
    
    return results

def main():
    """Point d'entrée principal avec interface en ligne de commande"""
    
    parser = argparse.ArgumentParser(
        description="Amazon Comments - Entraînement de modèle unifié",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python train.py                          # Mode automatique avec détection
  python train.py --mode demo               # Force le mode simulation
  python train.py --mode light --epochs 2  # Mode léger avec 2 époques
  python train.py --synthetic --limit 50   # Données synthétiques uniquement
  python train.py --info                   # Informations système seulement
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['demo', 'light', 'full', 'auto'],
        default='auto',
        help='Mode d\'entraînement (auto=détection automatique)'
    )
    
    parser.add_argument(
        '--synthetic', 
        action='store_true',
        help='Utiliser uniquement les données synthétiques'
    )
    
    parser.add_argument(
        '--limit', 
        type=int, 
        default=100,
        help='Limite du nombre d\'échantillons (défaut: 100)'
    )
    
    parser.add_argument(
        '--epochs', 
        type=int, 
        default=1,
        help='Nombre d\'époques d\'entraînement (défaut: 1)'
    )
    
    parser.add_argument(
        '--info', 
        action='store_true',
        help='Afficher les informations système et quitter'
    )
    
    parser.add_argument(
        '--quiet', 
        action='store_true',
        help='Mode silencieux (moins de messages)'
    )
    
    args = parser.parse_args()
    
    # Mode information seulement
    if args.info:
        show_system_info()
        return
    
    # Affichage informations si pas en mode silencieux
    if not args.quiet:
        show_system_info()
    
    # Configuration de l'entraînement
    use_huggingface = not args.synthetic
    mode = None if args.mode == 'auto' else args.mode
    
    # Lancement de l'entraînement
    try:
        results = train_with_options(
            mode=mode,
            use_huggingface=use_huggingface, 
            data_limit=args.limit,
            epochs=args.epochs
        )
        
        # Code de sortie
        exit_code = 0 if results["success"] else 1
        
        if not args.quiet:
            print_section("Résumé final")
            if results["success"]:
                print_status("🎉 Entraînement réussi! Modèle prêt à utiliser.", 'success')
                print_status("💡 Pour utiliser le modèle: ENABLE_AI_MODEL=true python main.py")
            else:
                print_status("⚠️ Entraînement échoué, utilisez la démo pour la présentation", 'warning')
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print_status("Entraînement interrompu par l'utilisateur", 'warning')
        sys.exit(1)
    except Exception as e:
        print_status(f"Erreur inattendue: {e}", 'error')
        sys.exit(1)

if __name__ == "__main__":
    main()
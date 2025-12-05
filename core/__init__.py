"""
Package core pour la logique métier d'Amazon Comments API
"""

from .data_manager import AmazonDataProcessor, TrainingDataConverter
from .training_manager import ModelTrainer, TrainingSimulator, TrainingOrchestrator

__all__ = [
    'AmazonDataProcessor',
    'TrainingDataConverter', 
    'ModelTrainer',
    'TrainingSimulator',
    'TrainingOrchestrator'
]
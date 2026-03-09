import os
import yaml
from typing import Optional
from src.config import settings
from src.models.strategy import StrategyModel

class StrategyLoader:
    @staticmethod
    def load(name: str) -> StrategyModel:
        """Load a strategy from a YAML file in the configured directory."""
        filename = f"{name}.yaml" if not name.endswith('.yaml') else name
        filepath = os.path.join(settings.STRATEGY_PATH, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Strategy file not found: {filepath}")
            
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            
        return StrategyModel(**data)

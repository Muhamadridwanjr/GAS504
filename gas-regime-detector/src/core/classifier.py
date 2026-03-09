from src.config import settings
from src.core.rule_based import RuleBasedDetector
from src.core.ml_model import MLRegimeDetector

class RegimeClassifier:
    def __init__(self):
        self.method = settings.regime_method
        self.rule_based = RuleBasedDetector()
        
        if self.method == "ml":
            self.ml_model = MLRegimeDetector(settings.model_path)
        else:
            self.ml_model = None
            
    def get_detector(self):
        if self.method == "ml" and self.ml_model and self.ml_model.model:
            return self.ml_model
        return self.rule_based

classifier = RegimeClassifier()

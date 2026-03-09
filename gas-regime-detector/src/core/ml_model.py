import joblib
from typing import Tuple, Dict, Any
from src.lib.logger import logger

class MLRegimeDetector:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Successfully loaded ML model from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"Model file not found at {self.model_path}. Using fallback rule-based method.")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

    def detect(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Predicts regime using the ML model.
        Requires features to be formatted as a 2D array for sklearn.
        """
        if not self.model:
            # Fallback
            from src.core.rule_based import RuleBasedDetector
            logger.warning("Falling back to rule-based detection due to missing ML model.")
            return RuleBasedDetector().detect(features)
            
        try:
            # Note: The ML model requires specific feature columns in exact order
            # This is a stub implementation. Adjust based on how your model was trained.
            
            # Extract features in alphabetical order as a naive approach
            feature_names = sorted(features.keys())
            feature_values = [[features[name] for name in feature_names]]
            
            pred = self.model.predict(feature_values)[0]
            
            # Predict probability if supported
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(feature_values)[0].max()
            else:
                proba = 0.8 # Arbitrary confidence if probability not supported
                
            return str(pred), float(proba), {"method": "ml"}
            
        except Exception as e:
            logger.error(f"Error during ML prediction: {e}")
            from src.core.rule_based import RuleBasedDetector
            return RuleBasedDetector().detect(features)

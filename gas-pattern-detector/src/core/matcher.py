from typing import List, Dict, Any
from src.vector.client import vector_client
from src.core.aggregator import Aggregator
from src.lib.logger import logger

class PatternMatcher:
    def __init__(self):
        self.aggregator = Aggregator()
        
    async def match(self, features: List[float], top_k: int, min_confidence: float) -> Dict[str, Any]:
        """
        Coordinates the detection process:
        1. Queries vector DB for similar patterns based on features
        2. Aggregates the results
        3. Applies confidence thresholds
        """
        # 1. Search Vector DB
        matches = await vector_client.search_similar(features, top_k)
        
        # 2. Aggregate Results
        result = self.aggregator.aggregate(matches)
        
        # 3. Apply Thresholds
        if result["confidence"] < min_confidence:
            logger.info(f"Pattern matched but confidence ({result['confidence']}) below threshold ({min_confidence})")
            # If confidence is too low, we might still return the stats, 
            # but force direction to NEUTRAL or indicate it's a weak signal
            result["direction"] = "NEUTRAL"
            
        return result

matcher = PatternMatcher()

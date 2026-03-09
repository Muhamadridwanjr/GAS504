from typing import List, Dict, Any

class Aggregator:
    @staticmethod
    def aggregate(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates results from similar patterns retrieved from the vector DB.
        Expected match structure:
        {
           "score": 0.85, # similarity score
           "metadata": {
               "expected_return": 0.001,
               "prob_up": 0.65,
               "sample_size": 100
           }
        }
        """
        if not matches:
            return {
                "confidence": 0.0,
                "expected_return": 0.0,
                "direction": "NEUTRAL",
                "probability_up": 0.5,
                "details": {
                    "matched_patterns": 0,
                    "avg_similarity": 0.0
                }
            }

        total_sim = 0.0
        weighted_return = 0.0
        weighted_prob_up = 0.0
        
        for m in matches:
            sim = m.get("score", 0)
            meta = m.get("metadata", {})
            ret = meta.get("expected_return", 0)
            prob = meta.get("prob_up", 0.5)
            
            total_sim += sim
            weighted_return += ret * sim
            weighted_prob_up += prob * sim
            
        avg_sim = total_sim / len(matches)
        avg_ret = weighted_return / total_sim if total_sim > 0 else 0
        avg_prob_up = weighted_prob_up / total_sim if total_sim > 0 else 0.5
        
        direction = "NEUTRAL"
        if avg_prob_up > 0.55:
            direction = "BUY"
        elif avg_prob_up < 0.45:
            direction = "SELL"
            
        # Naive confidence calculation based on similarity score and sample size
        confidence = min(0.99, avg_sim * (1.0 if len(matches) >= 5 else 0.5))
        
        return {
            "confidence": round(confidence, 4),
            "expected_return": round(avg_ret, 6),
            "direction": direction,
            "probability_up": round(avg_prob_up, 4),
            "details": {
                "matched_patterns": len(matches),
                "avg_similarity": round(avg_sim, 4)
            }
        }

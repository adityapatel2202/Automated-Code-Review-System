import torch


class FeatureExtractor:

    @staticmethod
    def extract(outputs):

        embeddings = outputs.last_hidden_state

        # Mean pooling
        mean_embedding = torch.mean(embeddings, dim=1)

        # Raw features
        semantic_score = float(torch.norm(mean_embedding).item())
        confidence = float(torch.max(mean_embedding).item())

        # Convert to a percentage (temporary normalization)
        normalized_score = min(100, max(0, semantic_score * 3.5))
        normalized_confidence = min(100, max(0, confidence * 20))

        # Readability
        if normalized_score >= 85:
            readability = "Excellent"
        elif normalized_score >= 70:
            readability = "Good"
        elif normalized_score >= 50:
            readability = "Average"
        else:
            readability = "Poor"

        return {
            "embedding_dimension": embeddings.shape[-1],
            "token_count": embeddings.shape[1],
            "semantic_score": round(normalized_score, 1),
            "confidence": round(normalized_confidence, 1),
            "readability": readability
        }
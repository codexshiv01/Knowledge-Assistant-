"""
Embedding generation using sentence transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from django.conf import settings


class EmbeddingGenerator:
    """Generate embeddings for text using sentence transformers"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding generator
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None
    
    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
        
        Returns:
            Numpy array of embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
        
        Returns:
            Numpy array of embedding vectors
        """
        if not texts:
            return np.array([])
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        
        if not valid_texts:
            return np.array([])
        
        embeddings = self.model.encode(
            valid_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.model.get_sentence_embedding_dimension()


# Global instance (singleton pattern)
_embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create the global embedding generator instance"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator

"""
FAISS vector store for similarity search
"""
import faiss
import numpy as np
import json
import os
from typing import List, Dict, Tuple
from pathlib import Path
from django.conf import settings


class FAISSVectorStore:
    """FAISS-based vector store for document chunks"""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS vector store
        
        Args:
            dimension: Dimension of embedding vectors (default for all-MiniLM-L6-v2)
        """
        self.dimension = dimension
        self.index = None
        self.metadata = []  # Store metadata for each vector
        self.index_file = settings.VECTOR_INDEX_FILE
        self.metadata_file = settings.VECTOR_METADATA_FILE
        
        # Ensure vector store directory exists
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        
        # Try to load existing index
        self.load()
    
    def initialize_index(self):
        """Initialize a new FAISS index"""
        # Use IndexFlatL2 for exact search (can be changed to IndexIVFFlat for larger datasets)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print(f"Initialized new FAISS index with dimension {self.dimension}")
    
    def add_vectors(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Add vectors to the index
        
        Args:
            embeddings: Numpy array of embedding vectors (n x dimension)
            metadata: List of metadata dictionaries for each vector
        """
        if self.index is None:
            self.initialize_index()
        
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        
        # Add metadata
        self.metadata.extend(metadata)
        
        print(f"Added {len(embeddings)} vectors to index. Total: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
        
        Returns:
            List of tuples (metadata, distance)
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Ensure query is 2D array and float32
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = query_embedding.astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(dist)))
        
        return results
    
    def save(self):
        """Save index and metadata to disk"""
        if self.index is None or self.index.ntotal == 0:
            print("No index to save")
            return
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_file))
        
        # Save metadata
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"Saved index with {self.index.ntotal} vectors to {self.index_file}")
    
    def load(self):
        """Load index and metadata from disk"""
        if not os.path.exists(self.index_file) or not os.path.exists(self.metadata_file):
            print("No existing index found. Will create new one when needed.")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load metadata
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            print(f"Loaded index with {self.index.ntotal} vectors from {self.index_file}")
            return True
        
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def clear(self):
        """Clear the index and metadata"""
        self.initialize_index()
        print("Cleared vector store")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'metadata_count': len(self.metadata),
        }


# Global instance (singleton pattern)
_vector_store = None


def get_vector_store() -> FAISSVectorStore:
    """Get or create the global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSVectorStore()
    return _vector_store

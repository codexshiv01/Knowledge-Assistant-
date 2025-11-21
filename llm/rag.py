"""
Retrieval-Augmented Generation (RAG) pipeline
"""
from typing import Dict, List
from django.conf import settings
from knowledge_base.embeddings import get_embedding_generator
from knowledge_base.vector_store import get_vector_store
from llm.client import get_llm_client
from llm.prompts import PromptTemplates
import time


class RAGPipeline:
    """Complete RAG pipeline for question answering"""
    
    def __init__(self):
        """Initialize RAG pipeline components"""
        self.embedding_generator = get_embedding_generator()
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client()
        self.top_k = settings.TOP_K_RESULTS
    
    def answer_question(self, question: str) -> Dict:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate embedding for the question
            question_embedding = self.embedding_generator.generate_embedding(question)
            
            # Step 2: Retrieve similar chunks from vector store
            retrieved_chunks = self.vector_store.search(question_embedding, top_k=self.top_k)
            
            # Step 3: Format chunks for prompt
            chunks_with_text = [
                {
                    'text': chunk_metadata.get('text', ''),
                    'source': chunk_metadata.get('source', 'Unknown'),
                    'page': chunk_metadata.get('page', 'N/A'),
                    'distance': distance,
                }
                for chunk_metadata, distance in retrieved_chunks
            ]
            
            # Step 4: Create RAG prompt
            system_prompt, user_prompt = PromptTemplates.create_rag_prompt(
                question, chunks_with_text
            )
            
            # Step 5: Generate response from LLM
            llm_response = self.llm_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # Step 6: Extract sources
            sources = PromptTemplates.extract_sources(chunks_with_text)
            
            end_time = time.time()
            
            return {
                'answer': llm_response['response'],
                'sources': sources,
                'response_time': end_time - start_time,
                'context_used': '\n\n'.join([c['text'][:200] + '...' for c in chunks_with_text[:2]]),
                'chunks_retrieved': len(chunks_with_text),
                'tokens_used': llm_response.get('tokens_used', 0),
            }
        
        except Exception as e:
            return {
                'answer': f"Error processing question: {str(e)}",
                'sources': [],
                'response_time': time.time() - start_time,
                'context_used': '',
                'error': str(e),
            }
    
    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the RAG pipeline"""
        vector_stats = self.vector_store.get_stats()
        
        return {
            'vector_store': vector_stats,
            'embedding_model': self.embedding_generator.model_name,
            'llm_model': self.llm_client.model,
            'top_k': self.top_k,
        }


# Global instance (singleton pattern)
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the global RAG pipeline instance"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline

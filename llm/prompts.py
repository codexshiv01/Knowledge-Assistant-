"""
Prompt templates for RAG system
"""


class PromptTemplates:
    """Collection of prompt templates for the RAG system"""
    
    SYSTEM_PROMPT = """You are a knowledgeable assistant that answers questions based on provided context.

IMPORTANT INSTRUCTIONS:
1. Answer questions ONLY using the information provided in the context below
2. If the context doesn't contain enough information to answer the question, say "I don't have enough information in the knowledge base to answer this question"
3. Do NOT make up information or use knowledge outside the provided context
4. Be concise and accurate
5. If you reference specific information, mention which source it came from
6. Use clear, simple language appropriate for the topic

Your goal is to provide accurate, helpful answers while avoiding hallucinations."""
    
    QUESTION_TEMPLATE = """Context from knowledge base:
{context}

Question: {question}

Answer based on the context above:"""
    
    NO_CONTEXT_RESPONSE = "I don't have enough information in the knowledge base to answer this question. Please try uploading relevant documents or rephrase your question."
    
    @staticmethod
    def format_context(chunks: list) -> str:
        """
        Format retrieved chunks into context string
        
        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
        
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', 'N/A')
            text = chunk.get('text', '')
            
            context_parts.append(f"[Source {i}: {source}, Page {page}]\n{text}")
        
        return "\n\n---\n\n".join(context_parts)
    
    @staticmethod
    def create_rag_prompt(question: str, chunks: list) -> tuple:
        """
        Create complete RAG prompt from question and retrieved chunks
        
        Args:
            question: User's question
            chunks: Retrieved chunks with metadata
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        context = PromptTemplates.format_context(chunks)
        
        if not context:
            return (
                PromptTemplates.SYSTEM_PROMPT,
                PromptTemplates.NO_CONTEXT_RESPONSE
            )
        
        user_prompt = PromptTemplates.QUESTION_TEMPLATE.format(
            context=context,
            question=question
        )
        
        return (PromptTemplates.SYSTEM_PROMPT, user_prompt)
    
    @staticmethod
    def extract_sources(chunks: list) -> list:
        """
        Extract source information from chunks
        
        Args:
            chunks: Retrieved chunks with metadata
        
        Returns:
            List of source strings
        """
        sources = []
        seen = set()
        
        for chunk in chunks:
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', 'N/A')
            source_str = f"{source} - Page {page}"
            
            if source_str not in seen:
                sources.append(source_str)
                seen.add(source_str)
        
        return sources

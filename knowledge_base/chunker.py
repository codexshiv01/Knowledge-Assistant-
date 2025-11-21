"""
Text chunking utilities for splitting documents into manageable pieces
"""
import re
from typing import List, Dict
from django.conf import settings


class TextChunker:
    """Chunks text into smaller pieces with overlap for better context preservation"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize chunker with size and overlap settings
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, source_metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to chunk
            source_metadata: Metadata about the source (filename, etc.)
        
        Returns:
            List of dictionaries containing chunk text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split by paragraphs first for better semantic boundaries
        paragraphs = self._split_into_paragraphs(text)
        
        chunks = []
        current_chunk = ""
        current_page = 1
        
        for paragraph in paragraphs:
            # Extract page number if present
            page_match = re.match(r'\[Page (\d+)\]', paragraph)
            if page_match:
                current_page = int(page_match.group(1))
                paragraph = re.sub(r'\[Page \d+\]\s*', '', paragraph)
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append(self._create_chunk(current_chunk, current_page, source_metadata))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, current_page, source_metadata))
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _create_chunk(self, text: str, page: int, source_metadata: Dict = None) -> Dict:
        """Create a chunk dictionary with metadata"""
        chunk = {
            'text': text.strip(),
            'page': page,
        }
        
        if source_metadata:
            chunk.update(source_metadata)
        
        return chunk


class SemanticChunker(TextChunker):
    """Advanced chunker that tries to preserve semantic boundaries"""
    
    def chunk_text(self, text: str, source_metadata: Dict = None) -> List[Dict]:
        """
        Split text into semantically meaningful chunks
        
        This version tries to split at sentence boundaries when possible
        """
        if not text or not text.strip():
            return []
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_page = 1
        
        for sentence in sentences:
            # Extract page number if present
            page_match = re.search(r'\[Page (\d+)\]', sentence)
            if page_match:
                current_page = int(page_match.group(1))
                sentence = re.sub(r'\[Page \d+\]\s*', '', sentence)
            
            # Check if adding this sentence exceeds chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(self._create_chunk(current_chunk, current_page, source_metadata))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, current_page, source_metadata))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

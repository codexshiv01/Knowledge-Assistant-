"""
Document parsers for different file formats
"""
from abc import ABC, abstractmethod
import PyPDF2
import markdown
from pathlib import Path


class DocumentParser(ABC):
    """Base class for document parsers"""
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Parse document and return text content"""
        pass


class PDFParser(DocumentParser):
    """Parser for PDF files"""
    
    def parse(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text_content = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        # Add page marker for source attribution
                        text_content.append(f"[Page {page_num}]\n{text}")
                
            return "\n\n".join(text_content)
        
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")


class MarkdownParser(DocumentParser):
    """Parser for Markdown files"""
    
    def parse(self, file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Convert markdown to plain text (removing formatting)
            # We keep the markdown as-is for better context preservation
            return content
        
        except Exception as e:
            raise ValueError(f"Error parsing Markdown: {str(e)}")


class TextParser(DocumentParser):
    """Parser for plain text files"""
    
    def parse(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        except Exception as e:
            raise ValueError(f"Error parsing text file: {str(e)}")


class ParserFactory:
    """Factory class to get appropriate parser based on file type"""
    
    _parsers = {
        'pdf': PDFParser,
        'md': MarkdownParser,
        'txt': TextParser,
    }
    
    @classmethod
    def get_parser(cls, file_type: str) -> DocumentParser:
        """Get parser instance for given file type"""
        parser_class = cls._parsers.get(file_type.lower())
        
        if not parser_class:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return parser_class()

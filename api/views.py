from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
import time

from .models import Document, Query
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    QuestionSerializer,
    AnswerSerializer,
    QueryHistorySerializer,
)
from knowledge_base.parsers import ParserFactory
from knowledge_base.chunker import TextChunker
from knowledge_base.embeddings import get_embedding_generator
from knowledge_base.vector_store import get_vector_store
from llm.rag import get_rag_pipeline


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for document management"""
    
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload_document(self, request):
        """
        Upload and process a document
        
        POST /api/documents/upload/
        """
        serializer = DocumentUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        title = serializer.validated_data.get('title', file.name)
        
        # Determine file type
        file_extension = file.name.split('.')[-1].lower()
        
        try:
            # Save file
            file_path = default_storage.save(f'documents/{file.name}', file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Create document record
            document = Document.objects.create(
                title=title,
                file=file_path,
                file_type=file_extension,
                file_size=file.size,
            )
            
            # Process document in background (for now, do it synchronously)
            self._process_document(document, full_path)
            
            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error processing document: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _process_document(self, document: Document, file_path: str):
        """Process document: parse, chunk, embed, and index"""
        try:
            # Parse document
            parser = ParserFactory.get_parser(document.file_type)
            text_content = parser.parse(file_path)
            
            # Chunk text
            chunker = TextChunker()
            chunks = chunker.chunk_text(
                text_content,
                source_metadata={'source': document.title, 'document_id': document.id}
            )
            
            if not chunks:
                document.processed = True
                document.save()
                return
            
            # Generate embeddings
            embedding_generator = get_embedding_generator()
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = embedding_generator.generate_embeddings(chunk_texts)
            
            # Add to vector store
            vector_store = get_vector_store()
            vector_store.add_vectors(embeddings, chunks)
            vector_store.save()
            
            # Update document
            document.processed = True
            document.chunk_count = len(chunks)
            document.save()
            
            print(f"Successfully processed document: {document.title} ({len(chunks)} chunks)")
        
        except Exception as e:
            print(f"Error processing document {document.title}: {e}")
            raise
    
    def destroy(self, request, *args, **kwargs):
        """Delete document and remove from vector store"""
        # Note: For simplicity, we're not removing from vector store
        # In production, you'd want to track which vectors belong to which document
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
def ask_question(request):
    """
    Answer a question using RAG pipeline
    
    POST /api/ask-question/
    Body: {"question": "What is...?"}
    """
    serializer = QuestionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    question = serializer.validated_data['question']
    
    try:
        # Get RAG pipeline
        rag_pipeline = get_rag_pipeline()
        
        # Answer question
        result = rag_pipeline.answer_question(question)
        
        # Log query
        Query.objects.create(
            question=question,
            answer=result['answer'],
            sources=result['sources'],
            response_time=result['response_time'],
            context_used=result.get('context_used', ''),
        )
        
        # Return response
        response_data = {
            'answer': result['answer'],
            'sources': result['sources'],
            'response_time': result['response_time'],
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Error processing question: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def query_history(request):
    """
    Get query history
    
    GET /api/queries/
    """
    queries = Query.objects.all()[:20]  # Last 20 queries
    serializer = QueryHistorySerializer(queries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def system_stats(request):
    """
    Get system statistics
    
    GET /api/stats/
    """
    rag_pipeline = get_rag_pipeline()
    stats = rag_pipeline.get_pipeline_stats()
    
    stats['documents'] = {
        'total': Document.objects.count(),
        'processed': Document.objects.filter(processed=True).count(),
        'total_chunks': sum(Document.objects.values_list('chunk_count', flat=True)),
    }
    
    stats['queries'] = {
        'total': Query.objects.count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)

from rest_framework import serializers
from .models import Document, Query


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'file_type', 'uploaded_at', 'processed', 'chunk_count', 'file_size']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'chunk_count', 'file_size']
    
    def validate_file(self, value):
        """Validate file size (max 10MB)"""
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    file = serializers.FileField()
    title = serializers.CharField(max_length=255, required=False)
    
    def validate_file(self, value):
        """Validate file extension and size"""
        allowed_extensions = ['pdf', 'md', 'txt']
        ext = value.name.split('.')[-1].lower()
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value


class QuestionSerializer(serializers.Serializer):
    """Serializer for question input"""
    question = serializers.CharField(max_length=1000, required=True)
    
    def validate_question(self, value):
        """Validate question is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty")
        return value.strip()


class AnswerSerializer(serializers.Serializer):
    """Serializer for answer output"""
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.CharField())
    response_time = serializers.FloatField()
    context_used = serializers.CharField(required=False)


class QueryHistorySerializer(serializers.ModelSerializer):
    """Serializer for query history"""
    
    class Meta:
        model = Query
        fields = ['id', 'question', 'answer', 'sources', 'created_at', 'response_time']
        read_only_fields = ['id', 'created_at']

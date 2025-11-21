from django.db import models
from django.core.validators import FileExtensionValidator


class Document(models.Model):
    """Model for uploaded knowledge base documents"""
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('md', 'Markdown'),
        ('txt', 'Text'),
    ]
    
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'md', 'txt'])]
    )
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    chunk_count = models.IntegerField(default=0)
    file_size = models.IntegerField(help_text="File size in bytes", default=0)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.file_type})"


class Query(models.Model):
    """Model for logging user queries and responses"""
    
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list, help_text="List of source documents and page numbers")
    created_at = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(help_text="Response time in seconds")
    context_used = models.TextField(blank=True, help_text="Retrieved context used for answering")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Queries"
    
    def __str__(self):
        return f"Query: {self.question[:50]}..."

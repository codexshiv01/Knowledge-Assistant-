from django.contrib import admin
from .models import Document, Query


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model"""
    list_display = ['title', 'file_type', 'uploaded_at', 'processed', 'chunk_count', 'file_size']
    list_filter = ['file_type', 'processed', 'uploaded_at']
    search_fields = ['title']
    readonly_fields = ['uploaded_at', 'file_size']
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation"""
        if obj:  # Editing existing object
            return self.readonly_fields + ['file', 'file_type']
        return self.readonly_fields


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    """Admin interface for Query model"""
    list_display = ['question_preview', 'created_at', 'response_time']
    list_filter = ['created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['created_at']
    
    def question_preview(self, obj):
        """Show preview of question"""
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "Question"

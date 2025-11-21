"""
Logging utilities for query tracking
"""
from api.models import Query
from typing import Dict


def log_query(question: str, answer: str, sources: list, response_time: float, context: str = "") -> Query:
    """
    Log a query to the database
    
    Args:
        question: User's question
        answer: Generated answer
        sources: List of source references
        response_time: Time taken to generate response
        context: Context used for answering
    
    Returns:
        Created Query object
    """
    query = Query.objects.create(
        question=question,
        answer=answer,
        sources=sources,
        response_time=response_time,
        context_used=context,
    )
    return query


def get_recent_queries(limit: int = 10) -> list:
    """
    Get recent queries
    
    Args:
        limit: Number of queries to retrieve
    
    Returns:
        List of Query objects
    """
    return list(Query.objects.all()[:limit])


def get_query_stats() -> Dict:
    """
    Get statistics about queries
    
    Returns:
        Dictionary with query statistics
    """
    total_queries = Query.objects.count()
    
    if total_queries == 0:
        return {
            'total_queries': 0,
            'average_response_time': 0,
        }
    
    avg_response_time = Query.objects.aggregate(
        avg_time=models.Avg('response_time')
    )['avg_time']
    
    return {
        'total_queries': total_queries,
        'average_response_time': avg_response_time or 0,
    }

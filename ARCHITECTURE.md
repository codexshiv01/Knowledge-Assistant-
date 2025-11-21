# Knowledge Assistant API - Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│                    (Postman, Web App, Mobile)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django REST Framework                       │
│                         (API Layer)                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Document   │  │   Question   │  │    Query     │         │
│  │   Upload     │  │   Answering  │  │   History    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Document Processing Pipeline               │    │
│  │                                                          │    │
│  │  Upload → Parse → Chunk → Embed → Index                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                  RAG Pipeline                            │    │
│  │                                                          │    │
│  │  Question → Embed → Search → Retrieve → Prompt → LLM   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & Service Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   SQLite     │  │    FAISS     │  │   OpenAI     │         │
│  │  Database    │  │ Vector Store │  │     API      │         │
│  │              │  │              │  │              │         │
│  │ • Documents  │  │ • Embeddings │  │ • GPT-3.5    │         │
│  │ • Queries    │  │ • Metadata   │  │ • Responses  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Processing Flow

```
┌──────────────┐
│ User uploads │
│   document   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│   File Validation    │
│ • Type check         │
│ • Size check         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Document Parser    │
│ • PDF → PyPDF2       │
│ • MD → Markdown      │
│ • TXT → Plain text   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Text Chunker       │
│ • Semantic split     │
│ • 500 char chunks    │
│ • 50 char overlap    │
│ • Page tracking      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Embedding Generator  │
│ • Sentence-BERT      │
│ • 384 dimensions     │
│ • Batch processing   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   FAISS Indexing     │
│ • Add vectors        │
│ • Store metadata     │
│ • Persist to disk    │
└──────────────────────┘
```

### 2. Question Answering Flow (RAG)

```
┌──────────────┐
│ User asks    │
│  question    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Generate Question    │
│    Embedding         │
│ (384-dim vector)     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Vector Similarity   │
│      Search          │
│ • Top-K retrieval    │
│ • Distance scoring   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Context Assembly    │
│ • Format chunks      │
│ • Add sources        │
│ • Preserve metadata  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Prompt Construction │
│ • System prompt      │
│ • Context injection  │
│ • Question           │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   OpenAI API Call    │
│ • GPT-3.5-turbo      │
│ • Temperature: 0.3   │
│ • Max tokens: 500    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Response Assembly   │
│ • Extract answer     │
│ • Add sources        │
│ • Calculate time     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Log to Database    │
│ • Question           │
│ • Answer             │
│ • Sources            │
│ • Response time      │
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│ Return JSON  │
│  to client   │
└──────────────┘
```

## Data Models

### Document Model
```python
Document {
    id: Integer (PK)
    title: String
    file: FileField
    file_type: String (pdf/md/txt)
    uploaded_at: DateTime
    processed: Boolean
    chunk_count: Integer
    file_size: Integer
}
```

### Query Model
```python
Query {
    id: Integer (PK)
    question: Text
    answer: Text
    sources: JSON Array
    created_at: DateTime
    response_time: Float
    context_used: Text
}
```

### Vector Store Metadata
```python
ChunkMetadata {
    text: String
    source: String (document title)
    page: Integer
    document_id: Integer
}
```

## Technology Stack

### Backend Framework
- **Django 5.0.1** - Web framework
- **Django REST Framework 3.14.0** - API layer
- **django-cors-headers** - CORS support

### AI/ML Components
- **OpenAI API** - LLM (GPT-3.5-turbo)
- **sentence-transformers 2.3.1** - Embeddings
- **FAISS** - Vector similarity search

### Document Processing
- **PyPDF2 3.0.1** - PDF parsing
- **markdown 3.5.2** - Markdown parsing

### Database
- **SQLite** - Development database
- **PostgreSQL** - Recommended for production

## Security Considerations

### API Security
- Environment-based configuration
- Secret key management
- CORS configuration
- File upload validation

### Data Security
- File type validation
- File size limits (10MB)
- Input sanitization
- SQL injection protection (Django ORM)

### API Key Management
- Environment variables
- Never commit to version control
- Rotation recommended

## Performance Optimizations

### Embedding Generation
- Lazy loading of models
- Batch processing
- Model caching

### Vector Search
- FAISS IndexFlatL2 (exact search)
- Can upgrade to IndexIVFFlat for large datasets
- Persistent index storage

### Query Optimization
- Database indexing
- Query result caching (optional)
- Pagination support

## Scalability Considerations

### Current Limitations
- Synchronous document processing
- Single-server deployment
- SQLite database

### Production Recommendations
1. **Async Processing** - Celery for document processing
2. **Database** - PostgreSQL with connection pooling
3. **Caching** - Redis for query results
4. **Load Balancing** - Multiple API servers
5. **Object Storage** - S3 for document storage
6. **Monitoring** - Prometheus + Grafana
7. **Logging** - Centralized logging (ELK stack)

## API Rate Limits

### Recommended Limits
- Document uploads: 10 per hour per user
- Questions: 100 per hour per user
- Query history: 1000 per hour per user

### OpenAI Limits
- Depends on your OpenAI plan
- Monitor token usage
- Implement retry logic

## Monitoring Metrics

### Key Metrics to Track
1. **Response Time** - Average query response time
2. **Token Usage** - OpenAI API costs
3. **Document Processing Time** - Upload to indexed
4. **Vector Store Size** - Number of chunks
5. **Error Rate** - Failed requests
6. **Cache Hit Rate** - Query cache effectiveness

## Deployment Architecture (Production)

```
                    ┌─────────────┐
                    │   Nginx     │
                    │ (Reverse    │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼─────┐            ┌─────▼────┐
         │ Gunicorn │            │ Gunicorn │
         │ Worker 1 │            │ Worker 2 │
         └────┬─────┘            └─────┬────┘
              │                         │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │                         │
         ┌────▼─────┐            ┌─────▼────┐
         │PostgreSQL│            │  Redis   │
         │          │            │  Cache   │
         └──────────┘            └──────────┘
              │
         ┌────▼─────┐
         │  Celery  │
         │  Worker  │
         └──────────┘
```

## Error Handling

### Document Upload Errors
- Invalid file type → 400 Bad Request
- File too large → 400 Bad Request
- Processing failure → 500 Internal Server Error

### Question Answering Errors
- Empty question → 400 Bad Request
- No documents → 200 OK (informative message)
- OpenAI API error → 500 Internal Server Error
- Rate limit → 429 Too Many Requests

## API Response Formats

### Success Response
```json
{
  "answer": "...",
  "sources": ["..."],
  "response_time": 2.34
}
```

### Error Response
```json
{
  "error": "Error message here"
}
```

## Future Enhancements

### Phase 1 (Short-term)
- [ ] Async document processing
- [ ] Redis caching
- [ ] User authentication
- [ ] Rate limiting

### Phase 2 (Medium-term)
- [ ] Multi-language support
- [ ] Advanced chunking strategies
- [ ] Query analytics dashboard
- [ ] Document versioning

### Phase 3 (Long-term)
- [ ] Fine-tuned models
- [ ] Multi-modal support (images)
- [ ] Collaborative knowledge bases
- [ ] Real-time updates

---

**Architecture designed for scalability, maintainability, and performance.**

# Knowledge Assistant API

A Django-based backend system that powers a Knowledge Assistant using Retrieval-Augmented Generation (RAG) to answer questions based on an external knowledge base.

## 🎯 Features

- **Document Upload & Processing**: Support for PDF, Markdown, and text files
- **Intelligent Chunking**: Semantic text chunking with overlap for better context preservation
- **Vector Embeddings**: Using sentence-transformers for high-quality embeddings
- **FAISS Vector Store**: Fast similarity search for relevant context retrieval
- **RAG Pipeline**: Retrieval-Augmented Generation to minimize hallucinations
- **OpenAI Integration**: GPT-3.5-turbo for natural language responses
- **Query Logging**: Track all questions and answers with response times
- **RESTful API**: Clean API endpoints using Django REST Framework

## 🏗️ Architecture

```
User Question
     ↓
[Embedding Generation]
     ↓
[Vector Similarity Search] ← FAISS Index
     ↓
[Context Retrieval]
     ↓
[Prompt Construction]
     ↓
[LLM Query (OpenAI)]
     ↓
[Response + Sources]
```

## 📋 Requirements

- Python 3.8+
- OpenAI API Key
- 2GB+ RAM (for embedding models)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd "d:\company projects\Artikate Studio\knowledge-assistant"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# IMPORTANT: Add your OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Customize these settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Start Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Document Management

#### Upload Document
```http
POST /api/documents/upload/
Content-Type: multipart/form-data

{
  "file": <file>,
  "title": "Science Class IX" (optional)
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Science Class IX",
  "file": "/media/documents/science_class_ix.md",
  "file_type": "md",
  "uploaded_at": "2025-11-21T21:00:00Z",
  "processed": true,
  "chunk_count": 45,
  "file_size": 15234
}
```

#### List Documents
```http
GET /api/documents/
```

#### Delete Document
```http
DELETE /api/documents/{id}/
```

### Question Answering

#### Ask Question
```http
POST /api/ask-question/
Content-Type: application/json

{
  "question": "What is the function of mitochondria?"
}
```

**Response:**
```json
{
  "answer": "The mitochondria is known as the powerhouse of the cell because it produces energy in the form of ATP (Adenosine Triphosphate) through cellular respiration...",
  "sources": [
    "Science Class IX - Page 1"
  ],
  "response_time": 2.34
}
```

### Query History

#### Get Query History
```http
GET /api/queries/
```

**Response:**
```json
[
  {
    "id": 1,
    "question": "What is the function of mitochondria?",
    "answer": "The mitochondria is known as...",
    "sources": ["Science Class IX - Page 1"],
    "created_at": "2025-11-21T21:00:00Z",
    "response_time": 2.34
  }
]
```

### System Statistics

#### Get System Stats
```http
GET /api/stats/
```

**Response:**
```json
{
  "vector_store": {
    "total_vectors": 45,
    "dimension": 384,
    "metadata_count": 45
  },
  "embedding_model": "all-MiniLM-L6-v2",
  "llm_model": "gpt-3.5-turbo",
  "top_k": 3,
  "documents": {
    "total": 1,
    "processed": 1,
    "total_chunks": 45
  },
  "queries": {
    "total": 5
  }
}
```

## 🧪 Testing with Sample Data

A sample Science Class IX knowledge base is provided in `data/samples/science_class_ix.md`.

### Upload Sample Document

```bash
# Using curl (Windows PowerShell)
$file = Get-Item "data\samples\science_class_ix.md"
$form = @{
    file = $file
    title = "Science Class IX"
}
Invoke-RestMethod -Uri "http://localhost:8000/api/documents/upload/" -Method Post -Form $form
```

### Test Questions

Try these sample questions:

1. **Cell Biology**
   ```json
   {"question": "What is the function of mitochondria?"}
   {"question": "What are the types of cells?"}
   ```

2. **Physics**
   ```json
   {"question": "Explain Newton's first law of motion"}
   {"question": "What is the formula for force?"}
   ```

3. **Chemistry**
   ```json
   {"question": "What is a molecule?"}
   {"question": "Explain ionic bonding"}
   ```

## 🛠️ Project Structure

```
knowledge-assistant/
├── api/                      # Main API app
│   ├── models.py            # Document & Query models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API endpoints
│   └── urls.py              # URL routing
├── knowledge_base/          # Knowledge base management
│   ├── parsers.py          # PDF/MD/TXT parsers
│   ├── chunker.py          # Text chunking
│   ├── embeddings.py       # Embedding generation
│   └── vector_store.py     # FAISS integration
├── llm/                     # LLM integration
│   ├── client.py           # OpenAI client
│   ├── prompts.py          # Prompt templates
│   └── rag.py              # RAG pipeline
├── utils/                   # Utilities
│   └── logger.py           # Query logging
├── data/                    # Data storage
│   ├── documents/          # Uploaded files
│   ├── vectors/            # FAISS index
│   └── samples/            # Sample data
└── knowledge_assistant/     # Django project
    └── settings.py         # Configuration
```

## 🔧 Configuration Options

### Embedding Model
Change the embedding model in `.env`:
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Fast, 384 dimensions
# EMBEDDING_MODEL=all-mpnet-base-v2  # Better quality, 768 dimensions
```

### LLM Model
Change the OpenAI model:
```env
LLM_MODEL=gpt-3.5-turbo  # Fast and cost-effective
# LLM_MODEL=gpt-4  # Better quality, higher cost
```

### Chunking Parameters
Adjust text chunking:
```env
CHUNK_SIZE=500        # Characters per chunk
CHUNK_OVERLAP=50      # Overlap between chunks
TOP_K_RESULTS=3       # Number of chunks to retrieve
```

## 🎨 Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to:
- View uploaded documents
- Browse query history
- Monitor system activity

## 📊 Optimization Features

### Anti-Hallucination Measures
1. **Strict Context Adherence**: LLM instructed to use only provided context
2. **Source Attribution**: Every answer includes source references
3. **Confidence Thresholds**: Can be configured for minimum similarity scores

### Performance Optimizations
1. **Lazy Loading**: Models loaded only when needed
2. **Batch Processing**: Embeddings generated in batches
3. **Persistent Index**: FAISS index saved to disk
4. **Query Caching**: Can be enabled with Redis (optional)

## 🐛 Troubleshooting

### OpenAI API Error
```
Error: OpenAI API key not configured
```
**Solution**: Add your API key to `.env` file

### Import Error
```
ModuleNotFoundError: No module named 'sentence_transformers'
```
**Solution**: Reinstall dependencies: `pip install -r requirements.txt`

### Empty Responses
```
Answer: "I don't have enough information..."
```
**Solution**: Upload relevant documents first using `/api/documents/upload/`

## 📝 Development

### Running Tests
```bash
python manage.py test
```

### Code Style
```bash
# Format code
black .

# Lint
flake8 .
```

## 🚀 Production Deployment

1. **Set DEBUG=False** in `.env`
2. **Use PostgreSQL** instead of SQLite
3. **Set up Redis** for caching
4. **Use Gunicorn** or uWSGI
5. **Configure CORS** properly
6. **Use environment variables** for secrets
7. **Set up monitoring** and logging

## 📄 License

This project is for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or issues, please open an issue on the repository.

---

**Built with ❤️ using Django, OpenAI, and FAISS**

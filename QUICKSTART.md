# Quick Start Guide - Knowledge Assistant API

## Prerequisites
- Python 3.8+ installed
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## Setup (5 minutes)

### 1. Navigate to Project
```bash
cd "d:\company projects\Artikate Studio\knowledge-assistant"
```

### 2. Activate Virtual Environment
```bash
.\venv\Scripts\Activate.ps1
```

### 3. Configure API Key
Edit `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Start Server
```bash
python manage.py runserver
```

Server will start at: http://localhost:8000

## Test the API (2 minutes)

### Upload Sample Document
```powershell
$file = Get-Item "data\samples\science_class_ix.md"
$form = @{
    file = $file
    title = "Science Class IX"
}
Invoke-RestMethod -Uri "http://localhost:8000/api/documents/upload/" -Method Post -Form $form
```

### Ask a Question
```powershell
$body = @{
    question = "What is the function of mitochondria?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/ask-question/" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Expected Response
```json
{
  "answer": "The mitochondria is known as the powerhouse of the cell...",
  "sources": ["Science Class IX - Page 1"],
  "response_time": 2.34
}
```

## Next Steps

1. **Try More Questions**: See README.md for sample questions
2. **Upload Your Documents**: Upload PDF, Markdown, or text files
3. **Use Postman**: Import the Postman collection for easier testing
4. **Admin Interface**: Visit http://localhost:8000/admin/

## Troubleshooting

**Problem**: "OpenAI API key not configured"
**Solution**: Make sure you've added your API key to the `.env` file

**Problem**: "No module named 'X'"
**Solution**: Run `pip install -r requirements.txt`

**Problem**: "I don't have enough information..."
**Solution**: Upload documents first using `/api/documents/upload/`

## API Endpoints

- `POST /api/documents/upload/` - Upload document
- `GET /api/documents/` - List documents
- `POST /api/ask-question/` - Ask question
- `GET /api/queries/` - Query history
- `GET /api/stats/` - System stats

## Documentation

- Full documentation: README.md
- Implementation details: walkthrough.md
- Postman collection: Knowledge_Assistant_API.postman_collection.json

---

**Need Help?** Check the README.md for detailed documentation.

"""
Upload sample document to Knowledge Assistant API
"""
import requests

# Upload document
url = "http://localhost:8000/api/documents/upload/"
file_path = "data/samples/science_class_ix.md"

with open(file_path, 'rb') as f:
    files = {'file': f}
    data = {'title': 'Science Class IX'}
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 201:
        result = response.json()
        print("✓ Document uploaded successfully!")
        print(f"  Document ID: {result['id']}")
        print(f"  Title: {result['title']}")
        print(f"  Chunks: {result['chunk_count']}")
        print(f"  Processed: {result['processed']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)

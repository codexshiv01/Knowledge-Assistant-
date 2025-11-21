"""
Test asking questions to the Knowledge Assistant API
"""
import requests
import json

# Ask a question
url = "http://localhost:8000/api/ask-question/"

questions = [
    "What is the function of mitochondria?",
    "Explain Newton's first law of motion",
    "What are the different types of animal tissues?",
]

for question in questions:
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)
    
    data = {'question': question}
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAnswer: {result['answer']}")
            print(f"\nSources: {', '.join(result['sources'])}")
            print(f"Response time: {result['response_time']:.2f}s")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

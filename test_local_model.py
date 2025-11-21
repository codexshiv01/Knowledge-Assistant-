"""
Test local model deployment
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_assistant.settings')
django.setup()

from llm.client import get_llm_client

print("Testing Local Model...")
print("="*60)
print("Note: First run will download the model (~250MB)")
print("="*60)

try:
    print("\n1. Initializing client...")
    client = get_llm_client()
    print(f"   Client type: {client.client_type}")
    print(f"   Model: {client.model}")
    print(f"   Device: {client.device if hasattr(client, 'device') else 'N/A'}")
    
    # Test simple generation
    print("\n2. Testing text generation...")
    result = client.generate_response(
        prompt="What is 2+2?",
        system_prompt="You are a helpful assistant. Answer briefly.",
        max_tokens=50
    )
    
    print("\n3. Generation successful!")
    print(f"   Response: {result['response']}")
    print(f"   Time: {result['response_time']:.2f}s")
    print(f"   Tokens: {result['tokens_used']}")
    
    # Test with knowledge base question
    print("\n4. Testing with sample question...")
    result2 = client.generate_response(
        prompt="What is the function of mitochondria?",
        system_prompt="Answer based on biology knowledge.",
        max_tokens=100
    )
    
    print(f"   Response: {result2['response']}")
    print(f"   Time: {result2['response_time']:.2f}s")
    
    print("\nLocal model is working perfectly!")
    
except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    traceback.print_exc()

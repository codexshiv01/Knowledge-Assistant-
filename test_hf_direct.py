"""
Direct test of HuggingFace API - write output to file
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_assistant.settings')
django.setup()

from llm.client import get_llm_client
import traceback

output = []
output.append("Testing HuggingFace LLM Client...")
output.append("="*60)

try:
    client = get_llm_client()
    output.append("Client initialized")
    output.append(f"Type: {client.client_type}")
    output.append(f"Model: {client.model}")
    
    # Test simple generation
    output.append("\nTesting text generation...")
    result = client.generate_response(
        prompt="What is 2+2?",
        system_prompt="You are a helpful assistant.",
        max_tokens=50
    )
    
    output.append("\nGeneration successful!")
    output.append(f"Response: {result['response']}")
    output.append(f"Time: {result['response_time']} seconds")
    
except Exception as e:
    output.append("\nError occurred:")
    output.append(str(e))
    output.append("\nFull traceback:")
    output.append(traceback.format_exc())

# Write to file
with open('hf_test_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Output written to hf_test_output.txt")

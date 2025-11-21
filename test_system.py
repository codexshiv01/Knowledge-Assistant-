"""
Test script to verify the Knowledge Assistant API
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_assistant.settings')
django.setup()

from knowledge_base.parsers import ParserFactory
from knowledge_base.chunker import TextChunker
from knowledge_base.embeddings import get_embedding_generator
from knowledge_base.vector_store import get_vector_store
from llm.rag import get_rag_pipeline


def test_parsers():
    """Test document parsers"""
    print("\n=== Testing Document Parsers ===")
    
    # Test Markdown parser
    md_file = "data/samples/science_class_ix.md"
    if os.path.exists(md_file):
        parser = ParserFactory.get_parser('md')
        content = parser.parse(md_file)
        print(f"✓ Markdown parser: Extracted {len(content)} characters")
    else:
        print("✗ Sample file not found")
        return False
    
    return True


def test_chunker():
    """Test text chunking"""
    print("\n=== Testing Text Chunker ===")
    
    md_file = "data/samples/science_class_ix.md"
    if not os.path.exists(md_file):
        print("✗ Sample file not found")
        return False
    
    parser = ParserFactory.get_parser('md')
    content = parser.parse(md_file)
    
    chunker = TextChunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_text(content, {'source': 'Science Class IX', 'document_id': 1})
    
    print(f"✓ Created {len(chunks)} chunks")
    print(f"  First chunk preview: {chunks[0]['text'][:100]}...")
    
    return True


def test_embeddings():
    """Test embedding generation"""
    print("\n=== Testing Embeddings ===")
    
    try:
        generator = get_embedding_generator()
        
        # Test single embedding
        text = "The mitochondria is the powerhouse of the cell"
        embedding = generator.generate_embedding(text)
        
        print(f"✓ Generated embedding with dimension: {len(embedding)}")
        
        # Test batch embeddings
        texts = [
            "Cell biology is fascinating",
            "Newton's laws explain motion",
            "Molecules are made of atoms"
        ]
        embeddings = generator.generate_embeddings(texts)
        
        print(f"✓ Generated {len(embeddings)} batch embeddings")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_vector_store():
    """Test FAISS vector store"""
    print("\n=== Testing Vector Store ===")
    
    try:
        vector_store = get_vector_store()
        generator = get_embedding_generator()
        
        # Create test embeddings
        texts = [
            "Mitochondria produce ATP energy",
            "Chloroplasts perform photosynthesis",
            "Nucleus contains genetic material"
        ]
        
        embeddings = generator.generate_embeddings(texts)
        
        metadata = [
            {'text': texts[0], 'source': 'Test', 'page': 1},
            {'text': texts[1], 'source': 'Test', 'page': 2},
            {'text': texts[2], 'source': 'Test', 'page': 3},
        ]
        
        # Clear and add vectors
        vector_store.clear()
        vector_store.add_vectors(embeddings, metadata)
        
        print(f"✓ Added {len(embeddings)} vectors to store")
        
        # Test search
        query = "What produces energy in cells?"
        query_embedding = generator.generate_embedding(query)
        results = vector_store.search(query_embedding, top_k=2)
        
        print(f"✓ Search returned {len(results)} results")
        if results:
            print(f"  Top result: {results[0][0]['text'][:50]}...")
        
        # Save and load
        vector_store.save()
        print("✓ Saved vector store to disk")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_full_pipeline():
    """Test complete RAG pipeline"""
    print("\n=== Testing Full RAG Pipeline ===")
    
    try:
        # First, process the sample document
        print("Processing sample document...")
        
        md_file = "data/samples/science_class_ix.md"
        parser = ParserFactory.get_parser('md')
        content = parser.parse(md_file)
        
        chunker = TextChunker()
        chunks = chunker.chunk_text(content, {'source': 'Science Class IX', 'document_id': 1})
        
        generator = get_embedding_generator()
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = generator.generate_embeddings(chunk_texts)
        
        vector_store = get_vector_store()
        vector_store.clear()
        vector_store.add_vectors(embeddings, chunks)
        vector_store.save()
        
        print(f"✓ Processed document: {len(chunks)} chunks indexed")
        
        # Now test RAG pipeline (requires OpenAI API key)
        print("\nTesting RAG pipeline (requires OpenAI API key)...")
        
        from django.conf import settings
        if not settings.OPENAI_API_KEY:
            print("⚠ OpenAI API key not configured - skipping LLM test")
            print("  Set OPENAI_API_KEY in .env to test full pipeline")
            return True
        
        rag_pipeline = get_rag_pipeline()
        
        # Test question
        question = "What is the function of mitochondria?"
        result = rag_pipeline.answer_question(question)
        
        print(f"\n✓ RAG Pipeline Test:")
        print(f"  Question: {question}")
        print(f"  Answer: {result['answer'][:200]}...")
        print(f"  Sources: {result['sources']}")
        print(f"  Response time: {result['response_time']:.2f}s")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Knowledge Assistant API - System Test")
    print("=" * 60)
    
    tests = [
        ("Document Parsers", test_parsers),
        ("Text Chunker", test_chunker),
        ("Embeddings", test_embeddings),
        ("Vector Store", test_vector_store),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()

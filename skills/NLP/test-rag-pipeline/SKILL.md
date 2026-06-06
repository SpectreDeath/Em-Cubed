---
name: test-rag-pipeline
Domain: NLP
Version: 1.0.0
surfaces:
  - python
---

## Purpose

Retrieval-Augmented Generation pipeline with keyword-based context retrieval and template text generation.

## Description

Retrieves relevant documents from a knowledge base and generates responses using pure Python string processing.

## Implementation

### Python RAG Pipeline

```python
from typing import Dict, List, Any

def retrieve_context(query: str, knowledge_base: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve relevant documents using keyword matching."""
    if not query or not knowledge_base:
        return []
    
    query_words = set(query.lower().split())
    scored_docs = []
    
    for doc in knowledge_base:
        content = doc.get("content", "").lower()
        content_words = set(content.split())
        overlap = len(query_words.intersection(content_words))
        if overlap > 0:
            scored_docs.append((doc, overlap))
    
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in scored_docs[:top_k]]

def generate_response(query: str, context_docs: List[Dict[str, Any]]) -> str:
    """Generate response from query and context."""
    if not context_docs:
        return f"No relevant context found for: {query}"
    
    context_str = " ".join([doc.get("content", "")[:50] for doc in context_docs[:2]])
    return f"Retrieved {len(context_docs)} relevant documents. Based on context: {context_str}... For query: {query}"
```

## Testing

```python
import pytest

def test_retrieve():
    kb = [{"content": "Paris is capital of France"}, {"content": "Berlin is capital of Germany"}]
    docs = retrieve_context("Paris France", kb, top_k=1)
    assert len(docs) == 1

def test_generate():
    docs = [{"content": "Paris is capital of France"}]
    resp = generate_response("What is capital?", docs)
    assert "Paris" in resp
```

## Security Considerations

- Pure string processing, no external dependencies.

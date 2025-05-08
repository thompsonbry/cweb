"""
Mock implementation of GraphRAG Toolkit for testing purposes.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Mock Document class
class Document:
    def __init__(self, id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.text = text
        self.metadata = metadata or {}
        self.chunks = []
        logger.info(f"Created document with ID: {id}")

# Mock Chunk class
class Chunk:
    def __init__(self, id: str, text: str, embedding: Optional[List[float]] = None):
        self.id = id
        self.text = text
        self.embedding = embedding or []
        logger.info(f"Created chunk with ID: {id}")

# Mock Fact class
class Fact:
    def __init__(self, id: str, subject: str, predicate: str, object: str, confidence: float = 1.0):
        self.id = id
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.confidence = confidence
        logger.info(f"Created fact: {subject} {predicate} {object}")

# Mock DocumentProcessor class
class DocumentProcessor:
    def __init__(self, embedding_model=None, chunk_size: int = 512, chunk_overlap: int = 128, max_tokens_per_chunk: int = 512):
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_tokens_per_chunk = max_tokens_per_chunk
        logger.info("Initialized DocumentProcessor")
    
    def process(self, document: Document) -> Document:
        # Mock chunking
        text = document.text
        chunk_size = self.chunk_size
        
        # Simple chunking by character count
        chunks = []
        for i in range(0, len(text), chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + chunk_size]
            if chunk_text:
                chunk_id = f"{document.id}_chunk_{len(chunks)}"
                chunk = Chunk(id=chunk_id, text=chunk_text)
                
                # Mock embedding
                if self.embedding_model:
                    chunk.embedding = [0.1] * 10  # Mock embedding vector
                
                chunks.append(chunk)
        
        document.chunks = chunks
        logger.info(f"Processed document into {len(chunks)} chunks")
        return document

# Mock FactExtractor class
class FactExtractor:
    def __init__(self, llm=None, namespace: str = "default"):
        self.llm = llm
        self.namespace = namespace
        logger.info("Initialized FactExtractor")
    
    def extract_facts(self, document: Document) -> List[Fact]:
        facts = []
        
        # Mock fact extraction based on document content
        text = document.text.lower()
        
        # Extract some facts based on keywords
        if "recognition/metacognition" in text or "r/m framework" in text:
            facts.append(Fact(
                id=f"{document.id}_fact_1",
                subject="Recognition/Metacognition Framework",
                predicate="is",
                object="model of tactical decision making"
            ))
            
            facts.append(Fact(
                id=f"{document.id}_fact_2",
                subject="Recognition/Metacognition Framework",
                predicate="integrates",
                object="recognition-primed decision making with metacognitive processes"
            ))
        
        if "recognition-primed decision" in text or "rpd" in text:
            facts.append(Fact(
                id=f"{document.id}_fact_3",
                subject="Recognition-Primed Decision Making",
                predicate="includes",
                object="pattern matching to recognize situations"
            ))
            
            facts.append(Fact(
                id=f"{document.id}_fact_4",
                subject="Recognition-Primed Decision Making",
                predicate="includes",
                object="mental simulation to evaluate courses of action"
            ))
        
        if "metacognitive processes" in text:
            facts.append(Fact(
                id=f"{document.id}_fact_5",
                subject="Metacognitive Processes",
                predicate="include",
                object="Quick Test"
            ))
            
            facts.append(Fact(
                id=f"{document.id}_fact_6",
                subject="Metacognitive Processes",
                predicate="include",
                object="Story Building"
            ))
            
            facts.append(Fact(
                id=f"{document.id}_fact_7",
                subject="Metacognitive Processes",
                predicate="include",
                object="Assumption Testing"
            ))
        
        logger.info(f"Extracted {len(facts)} facts from document")
        return facts

# Mock LexicalGraph class
class LexicalGraph:
    def __init__(self, graph=None, vector_store=None, namespace: str = "default"):
        self.graph = graph
        self.vector_store = vector_store
        self.namespace = namespace
        self.documents = {}
        self.facts = []
        logger.info("Initialized LexicalGraph")
    
    def add_document(self, document: Document) -> None:
        self.documents[document.id] = document
        logger.info(f"Added document to graph: {document.id}")
    
    def add_facts(self, facts: List[Fact]) -> None:
        self.facts.extend(facts)
        logger.info(f"Added {len(facts)} facts to graph")
    
    def query(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        # Mock query results
        results = []
        query = query.lower()
        
        for fact in self.facts:
            score = 0
            if query in fact.subject.lower():
                score += 0.8
            if query in fact.predicate.lower():
                score += 0.5
            if query in fact.object.lower():
                score += 0.7
            
            if score > 0:
                results.append({
                    "fact": {
                        "subject": fact.subject,
                        "predicate": fact.predicate,
                        "object": fact.object
                    },
                    "score": score
                })
        
        # Sort by score and limit to top_k
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
        logger.info(f"Query '{query}' returned {len(results)} results")
        return results
    
    def get_facts_by_document_id(self, document_id: str) -> List[Fact]:
        # Mock implementation
        return [fact for fact in self.facts if fact.id.startswith(document_id)]

#!/usr/bin/env python3
"""
Build a lexical graph from a text file using mock GraphRAG Toolkit implementation.
"""

import os
import sys
import argparse
import logging
from typing import Optional
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_lexical_graph(file_path: str, document_id: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Build a lexical graph from a text file using mock implementation.
    
    Args:
        file_path (str): Path to the text file
        document_id (str, optional): The document ID (defaults to file name)
        verbose (bool, optional): Enable verbose output
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from src.graphrag_integration.mock_implementation import Document, DocumentProcessor, FactExtractor, LexicalGraph
        
        # Set log level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Use file name as document ID if not provided
        if document_id is None:
            document_id = os.path.basename(file_path)
        
        # Create document
        logger.info(f"Creating document from {file_path}...")
        document = Document(
            id=document_id,
            text=text,
            metadata={"source_file": file_path}
        )
        
        # Process document
        logger.info("Processing document...")
        document_processor = DocumentProcessor(
            chunk_size=512,
            chunk_overlap=128,
            max_tokens_per_chunk=512
        )
        processed_document = document_processor.process(document)
        
        # Extract facts
        logger.info("Extracting facts...")
        fact_extractor = FactExtractor(namespace="cweb")
        facts = fact_extractor.extract_facts(processed_document)
        
        logger.info(f"Extracted {len(facts)} facts from document {document.id}")
        
        if verbose:
            logger.debug("Sample facts:")
            for i, fact in enumerate(facts[:5]):
                logger.debug(f"Fact {i+1}: {fact.subject} {fact.predicate} {fact.object}")
        
        # Build lexical graph
        logger.info("Building lexical graph...")
        graph = LexicalGraph(namespace="cweb")
        graph.add_document(processed_document)
        graph.add_facts(facts)
        
        # Save graph to file for demonstration
        save_graph_to_file(graph, document_id)
        
        logger.info("Lexical graph built successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error building lexical graph: {str(e)}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return False

def save_graph_to_file(graph, document_id):
    """
    Save graph facts to a file for demonstration purposes.
    """
    output_dir = os.path.join(os.path.dirname(__file__), '../output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{document_id}_facts.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Facts extracted from document: {document_id}\n")
        f.write("=" * 50 + "\n\n")
        
        for i, fact in enumerate(graph.facts):
            f.write(f"Fact {i+1}:\n")
            f.write(f"  Subject: {fact.subject}\n")
            f.write(f"  Predicate: {fact.predicate}\n")
            f.write(f"  Object: {fact.object}\n")
            f.write(f"  Confidence: {fact.confidence}\n")
            f.write("\n")
    
    logger.info(f"Saved facts to {output_file}")

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Build a lexical graph from a text file")
    parser.add_argument("file_path", help="Path to the text file")
    parser.add_argument("--document-id", help="Document ID (defaults to file name)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        logger.error(f"File not found: {args.file_path}")
        sys.exit(1)
    
    if build_lexical_graph(args.file_path, args.document_id, args.verbose):
        logger.info("Lexical graph built successfully")
        sys.exit(0)
    else:
        logger.error("Failed to build lexical graph")
        sys.exit(1)

if __name__ == "__main__":
    main()

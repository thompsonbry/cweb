#!/usr/bin/env python3

"""
GraphRAG Example

This script demonstrates how to use the GraphRAG toolkit to process documents
and build a lexical graph.

Usage:
  python graphrag_example.py <file_path> [--output OUTPUT] [--verbose]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Replace sqlite3 with pysqlite3
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
    print("Using pysqlite3 as sqlite3")
except ImportError:
    print("pysqlite3 not available, using system sqlite3")

# Import GraphRAG toolkit components
from graphrag_toolkit.lexical_graph import LexicalGraphIndex, TenantId
from graphrag_toolkit.lexical_graph import GraphRAGConfig
from graphrag_toolkit.lexical_graph.storage.graph.dummy_graph_store import DummyGraphStore
from graphrag_toolkit.lexical_graph.storage.vector.vector_store import VectorStore
from llama_index.core import SimpleDirectoryReader

# Load environment variables
load_dotenv()

def process_document(file_path, verbose=False, output_dir=None):
    """Process a document using GraphRAG toolkit"""
    if verbose:
        print(f"Processing document: {file_path}")
    
    # Set up AWS region
    region = os.environ.get("AWS_REGION", "us-west-2")
    GraphRAGConfig.aws_region = region
    
    # Configure embedding model
    GraphRAGConfig.embed_model = "amazon.titan-embed-text-v1"
    GraphRAGConfig.embed_dimensions = 1536
    
    # Configure LLM
    GraphRAGConfig.extraction_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
    GraphRAGConfig.response_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Create tenant ID - must be 1-10 lowercase letters and numbers
    tenant_id = TenantId("doc1")
    
    # Set up output directory
    output_directory = output_dir or "./graphrag_output"
    os.makedirs(output_directory, exist_ok=True)
    
    # Initialize stores
    graph_store = DummyGraphStore()
    vector_store = VectorStore()  # Using default VectorStore
    
    # Initialize LexicalGraphIndex
    graph_index = LexicalGraphIndex(
        tenant_id=tenant_id,
        extraction_dir=output_directory,
        graph_store=graph_store,
        vector_store=vector_store
    )
    
    # Load document
    if verbose:
        print("Loading document...")
    
    path = Path(file_path)
    reader = SimpleDirectoryReader(input_files=[str(file_path)])
    documents = reader.load_data()
    
    if verbose:
        print(f"Loaded {len(documents)} document(s)")
        for doc in documents:
            print(f"Document ID: {doc.doc_id}, Text length: {len(doc.text)}")
    
    # Process document and build graph
    if verbose:
        print("Building graph...")
    
    try:
        # Extract and build the graph
        graph_index.extract_and_build(documents, show_progress=verbose)
        
        if verbose:
            print("Graph built successfully")
        
        # Save results
        results = {
            "document_id": path.stem,
            "status": "success",
            "message": "Graph built successfully"
        }
        
        output_file = os.path.join(output_directory, f"{path.stem}_graph.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        if verbose:
            print(f"Results saved to {output_file}")
        
        return results
    except Exception as e:
        print(f"Error processing document: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Process documents with GraphRAG toolkit')
    parser.add_argument('file_path', help='Path to the document file')
    parser.add_argument('--output', '-o', help='Output directory for results', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Process the document
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    try:
        process_document(file_path, verbose=args.verbose, output_dir=args.output)
        print("Processing complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

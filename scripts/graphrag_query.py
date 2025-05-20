#!/usr/bin/env python3

"""
GraphRAG Query Example

This script demonstrates how to query a graph built with the GraphRAG toolkit.

Usage:
  python graphrag_query.py <query_text> [--verbose]
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
from graphrag_toolkit.lexical_graph.query import GraphRAGQueryEngine

# Load environment variables
load_dotenv()

def query_graph(query_text, verbose=False):
    """Query a graph built with GraphRAG toolkit"""
    if verbose:
        print(f"Query: {query_text}")
    
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
    output_directory = "./graphrag_output"
    
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
    
    # Create query engine
    query_engine = GraphRAGQueryEngine(graph_index)
    
    # Execute query
    if verbose:
        print("Executing query...")
    
    try:
        response = query_engine.query(query_text)
        
        if verbose:
            print("Query executed successfully")
        
        # Print response
        print("\nResponse:")
        print(response)
        
        return response
    except Exception as e:
        print(f"Error executing query: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Query a graph built with GraphRAG toolkit')
    parser.add_argument('query_text', help='Query text')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        query_graph(args.query_text, verbose=args.verbose)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

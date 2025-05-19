#!/usr/bin/env python3

"""
Neptune Analytics Query Examples

This script demonstrates how to query a Neptune Analytics graph using the GraphRAG toolkit.
It provides examples of different query patterns for extracting information from the graph.

Usage:
  uv run python scripts/neptune_query_examples.py [--verbose]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Try to use pysqlite3 if available
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
    print("Using pysqlite3 as sqlite3")
except ImportError:
    print("pysqlite3 not available, using system sqlite3")

# Import GraphRAG toolkit components
try:
    from graphrag_toolkit.lexical_graph import GraphRAGConfig, set_logging_config
    from graphrag_toolkit.lexical_graph.storage import GraphStoreFactory, VectorStoreFactory
    from graphrag_toolkit.lexical_graph import LexicalGraphIndex, TenantId
    from graphrag_toolkit.lexical_graph import LexicalGraphQueryEngine
    GRAPHRAG_AVAILABLE = True
    print("Successfully imported GraphRAG toolkit components")
except ImportError as e:
    print(f"Warning: Could not import GraphRAG toolkit: {e}")
    print(f"Make sure you're using Python 3.10+ with: uv run python scripts/neptune_query_examples.py")
    GRAPHRAG_AVAILABLE = False

# Load environment variables
load_dotenv()

class NeptuneQueryExamples:
    """Examples of querying Neptune Analytics graph using GraphRAG toolkit"""
    
    def __init__(self, verbose=False):
        """Initialize with Neptune Analytics connection"""
        self.verbose = verbose
        
        if not GRAPHRAG_AVAILABLE:
            raise ImportError("GraphRAG toolkit not available")
        
        # Configure AWS region
        region = os.environ.get("AWS_REGION", "us-west-2")
        GraphRAGConfig.aws_region = region
        
        # Configure embedding model to match Neptune Analytics dimensions (1024)
        GraphRAGConfig.embed_model = "cohere.embed-english-v3"
        GraphRAGConfig.embed_dimensions = 1024
        
        # Configure LLM
        GraphRAGConfig.extraction_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
        GraphRAGConfig.response_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        # Set logging
        set_logging_config('INFO')
        
        try:
            # Get Neptune Analytics configuration from environment
            neptune_graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID", "g-k2n0lshd74")
            neptune_region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
            
            # Set AWS region for GraphRAG
            GraphRAGConfig.aws_region = neptune_region
            
            # Create connection string
            neptune_connection = f"neptune-graph://{neptune_graph_id}"
            print(f"Connecting to Neptune Analytics: {neptune_connection}")
            
            # Create Neptune Analytics stores using factory methods
            self.graph_store = GraphStoreFactory.for_graph_store(neptune_connection)
            self.vector_store = VectorStoreFactory.for_vector_store(neptune_connection)
            
            # Create tenant ID
            self.tenant_id = TenantId("doc1")
            
            # Create output directory
            output_dir = "/tmp/graphrag_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize LexicalGraphIndex
            self.graph_index = LexicalGraphIndex(
                tenant_id=self.tenant_id,
                extraction_dir=output_dir,
                graph_store=self.graph_store,
                vector_store=self.vector_store
            )
            
            print("Successfully initialized GraphRAG components with Neptune Analytics")
        except Exception as e:
            print(f"Error initializing GraphRAG components: {e}")
            raise
    
    def execute_query(self, query, description=None):
        """Execute an OpenCypher query and return the results"""
        if description and self.verbose:
            print(f"\n=== {description} ===")
            print(f"Query: {query}")
        
        try:
            results = self.graph_store.execute_query(query)
            
            # Convert results to a list for easier handling
            result_list = list(results)
            
            if description and self.verbose:
                print(f"Found {len(result_list)} results")
                for i, record in enumerate(result_list[:5]):
                    print(f"  Result {i+1}: {record}")
                if len(result_list) > 5:
                    print(f"  ... and {len(result_list) - 5} more results")
            
            return result_list
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def example_1_basic_node_query(self):
        """Example 1: Basic query to get all nodes"""
        print("\n=== EXAMPLE 1: Basic Node Query ===")
        
        query = """
        MATCH (n)
        RETURN n
        LIMIT 10
        """
        
        results = self.execute_query(query, "Get all nodes")
        return results
    
    def example_2_entity_query(self):
        """Example 2: Query to get entities"""
        print("\n=== EXAMPLE 2: Entity Query ===")
        
        query = """
        MATCH (e:Entity)
        RETURN e.id as id, e.name as name, e.type as type
        LIMIT 10
        """
        
        results = self.execute_query(query, "Get entities")
        return results
    
    def example_3_relationship_query(self):
        """Example 3: Query to get relationships"""
        print("\n=== EXAMPLE 3: Relationship Query ===")
        
        query = """
        MATCH (e1)-[r]->(e2)
        RETURN e1.name as source, type(r) as relationship, e2.name as target
        LIMIT 10
        """
        
        results = self.execute_query(query, "Get relationships")
        return results
    
    def example_4_fact_extraction(self):
        """Example 4: Fact extraction query"""
        print("\n=== EXAMPLE 4: Fact Extraction ===")
        
        query = """
        MATCH (s)-[r:FACT]->(o)
        RETURN s.name as subject, r.predicate as predicate, o.name as object
        LIMIT 10
        """
        
        results = self.execute_query(query, "Extract facts")
        return results
    
    def example_5_document_query(self):
        """Example 5: Query to get documents"""
        print("\n=== EXAMPLE 5: Document Query ===")
        
        query = """
        MATCH (d:Document)
        RETURN d.id as id, d.title as title
        LIMIT 10
        """
        
        results = self.execute_query(query, "Get documents")
        return results
    
    def example_6_schema_query(self):
        """Example 6: Query to get schema information"""
        print("\n=== EXAMPLE 6: Schema Query ===")
        
        # Get node labels
        node_labels_query = """
        MATCH (n)
        RETURN DISTINCT labels(n) as labels, count(*) as count
        ORDER BY count DESC
        LIMIT 20
        """
        
        # Get relationship types
        rel_types_query = """
        MATCH ()-[r]->()
        RETURN DISTINCT type(r) as type, count(*) as count
        ORDER BY count DESC
        LIMIT 20
        """
        
        node_labels = self.execute_query(node_labels_query, "Node labels")
        rel_types = self.execute_query(rel_types_query, "Relationship types")
        
        return {
            "node_labels": node_labels,
            "relationship_types": rel_types
        }
    
    def example_7_custom_query(self, query):
        """Example 7: Custom query"""
        print("\n=== EXAMPLE 7: Custom Query ===")
        
        results = self.execute_query(query, "Custom query")
        return results
    
    def run_all_examples(self):
        """Run all query examples"""
        results = {}
        
        try:
            results["example_1"] = self.example_1_basic_node_query()
            results["example_2"] = self.example_2_entity_query()
            results["example_3"] = self.example_3_relationship_query()
            results["example_4"] = self.example_4_fact_extraction()
            results["example_5"] = self.example_5_document_query()
            results["example_6"] = self.example_6_schema_query()
        except Exception as e:
            print(f"Error running examples: {e}")
        
        return results
    
    def save_results(self, results, output_path):
        """Save results to a JSON file"""
        try:
            # Convert results to serializable format
            serializable_results = {}
            for key, value in results.items():
                if isinstance(value, list):
                    # Convert each item in the list to a dict
                    serializable_results[key] = [dict(item) if hasattr(item, 'keys') else item for item in value]
                elif isinstance(value, dict):
                    # Handle nested dictionaries
                    serializable_results[key] = {}
                    for k, v in value.items():
                        if isinstance(v, list):
                            serializable_results[key][k] = [dict(item) if hasattr(item, 'keys') else item for item in v]
                        else:
                            serializable_results[key][k] = v
                else:
                    serializable_results[key] = value
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2)
                
            print(f"Results saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Neptune Analytics Query Examples')
    parser.add_argument('--output', '-o', help='Output file for the query results', default="/tmp/neptune_query_examples.json")
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--query', '-q', help='Custom OpenCypher query to run', default=None)
    
    args = parser.parse_args()
    
    try:
        # Create query examples
        examples = NeptuneQueryExamples(verbose=args.verbose)
        
        # Run examples
        results = {}
        
        if args.query:
            # Run custom query
            results["custom_query"] = examples.example_7_custom_query(args.query)
        else:
            # Run all examples
            results = examples.run_all_examples()
        
        # Save results
        examples.save_results(results, args.output)
        
        print("\nExamples complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

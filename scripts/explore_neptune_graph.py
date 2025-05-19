#!/usr/bin/env python3

"""
Neptune Analytics Graph Explorer

This script explores the content of a Neptune Analytics graph using various query patterns.
It demonstrates how to execute OpenCypher queries against the graph.

Usage:
  uv run python scripts/explore_neptune_graph.py [--verbose]
"""

import os
import sys
import json
import argparse
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
    GRAPHRAG_AVAILABLE = True
    print("Successfully imported GraphRAG toolkit components")
except ImportError as e:
    print(f"Warning: Could not import GraphRAG toolkit: {e}")
    print(f"Make sure you're using Python 3.10+ with: uv run python scripts/explore_neptune_graph.py")
    GRAPHRAG_AVAILABLE = False

# Load environment variables
load_dotenv()

class NeptuneGraphExplorer:
    """Explore Neptune Analytics graph using OpenCypher queries"""
    
    def __init__(self):
        """Initialize the graph explorer with Neptune Analytics connection"""
        if not GRAPHRAG_AVAILABLE:
            raise ImportError("GraphRAG toolkit not available")
            
        # Configure AWS region
        region = os.environ.get("AWS_REGION", "us-west-2")
        GraphRAGConfig.aws_region = region
        
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
            
            # Create Neptune Analytics graph store using factory method
            self.graph_store = GraphStoreFactory.for_graph_store(neptune_connection)
            print("Successfully connected to Neptune Analytics graph store")
        except Exception as e:
            print(f"Error connecting to Neptune Analytics: {e}")
            raise
    
    def execute_query(self, query, description=None):
        """Execute an OpenCypher query and return the results"""
        if description:
            print(f"\n=== {description} ===")
            print(f"Query: {query}")
        
        try:
            results = self.graph_store.execute_query(query)
            
            # Convert results to a list for easier handling
            result_list = list(results)
            
            if description:
                print(f"Found {len(result_list)} results")
            
            return result_list
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def explore_graph_schema(self):
        """Explore the schema of the graph"""
        print("\n=== EXPLORING GRAPH SCHEMA ===")
        
        # Get node labels
        node_labels_query = """
        MATCH (n)
        RETURN DISTINCT labels(n) as labels, count(*) as count
        ORDER BY count DESC
        """
        node_labels = self.execute_query(node_labels_query, "Node Labels")
        
        # Get relationship types
        rel_types_query = """
        MATCH ()-[r]->()
        RETURN DISTINCT type(r) as type, count(*) as count
        ORDER BY count DESC
        """
        rel_types = self.execute_query(rel_types_query, "Relationship Types")
        
        # Get node properties
        node_props_query = """
        MATCH (n)
        UNWIND keys(n) as key
        RETURN DISTINCT key, count(*) as count
        ORDER BY count DESC
        """
        node_props = self.execute_query(node_props_query, "Node Properties")
        
        return {
            "node_labels": node_labels,
            "relationship_types": rel_types,
            "node_properties": node_props
        }
    
    def explore_entities(self):
        """Explore entities in the graph"""
        print("\n=== EXPLORING ENTITIES ===")
        
        # Get all entities
        entities_query = """
        MATCH (e:Entity)
        RETURN e.id as id, e.name as name, e.type as type
        LIMIT 20
        """
        entities = self.execute_query(entities_query, "Entities")
        
        # Get entity types
        entity_types_query = """
        MATCH (e:Entity)
        RETURN DISTINCT e.type as type, count(*) as count
        ORDER BY count DESC
        """
        entity_types = self.execute_query(entity_types_query, "Entity Types")
        
        return {
            "entities": entities,
            "entity_types": entity_types
        }
    
    def explore_relationships(self):
        """Explore relationships in the graph"""
        print("\n=== EXPLORING RELATIONSHIPS ===")
        
        # Get relationships
        relationships_query = """
        MATCH (e1)-[r]->(e2)
        RETURN e1.name as source, type(r) as relationship, e2.name as target
        LIMIT 20
        """
        relationships = self.execute_query(relationships_query, "Relationships")
        
        # Get relationship counts by type
        rel_counts_query = """
        MATCH (e1)-[r]->(e2)
        RETURN type(r) as type, count(*) as count
        ORDER BY count DESC
        """
        rel_counts = self.execute_query(rel_counts_query, "Relationship Counts by Type")
        
        return {
            "relationships": relationships,
            "relationship_counts": rel_counts
        }
    
    def explore_documents(self):
        """Explore documents in the graph"""
        print("\n=== EXPLORING DOCUMENTS ===")
        
        # Get documents
        documents_query = """
        MATCH (d:Document)
        RETURN d.id as id, d.title as title
        LIMIT 20
        """
        documents = self.execute_query(documents_query, "Documents")
        
        # Get document counts
        doc_count_query = """
        MATCH (d:Document)
        RETURN count(d) as document_count
        """
        doc_count = self.execute_query(doc_count_query, "Document Count")
        
        return {
            "documents": documents,
            "document_count": doc_count
        }
    
    def explore_facts(self):
        """Explore facts in the graph"""
        print("\n=== EXPLORING FACTS ===")
        
        # Get facts
        facts_query = """
        MATCH (s)-[r:FACT]->(o)
        RETURN s.name as subject, r.predicate as predicate, o.name as object
        LIMIT 20
        """
        facts = self.execute_query(facts_query, "Facts")
        
        # Get fact counts
        fact_count_query = """
        MATCH ()-[r:FACT]->()
        RETURN count(r) as fact_count
        """
        fact_count = self.execute_query(fact_count_query, "Fact Count")
        
        return {
            "facts": facts,
            "fact_count": fact_count
        }
    
    def run_custom_query(self, query, description=None):
        """Run a custom OpenCypher query"""
        return self.execute_query(query, description or "Custom Query")
    
    def save_results(self, results, output_path):
        """Save results to a JSON file"""
        try:
            # Convert results to serializable format
            serializable_results = {}
            for key, value in results.items():
                if isinstance(value, list):
                    # Convert each item in the list to a dict
                    serializable_results[key] = [dict(item) if hasattr(item, 'keys') else item for item in value]
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
    parser = argparse.ArgumentParser(description='Explore Neptune Analytics graph')
    parser.add_argument('--output', '-o', help='Output file for the exploration results', default="/tmp/neptune_exploration.json")
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--query', '-q', help='Custom OpenCypher query to run', default=None)
    
    args = parser.parse_args()
    
    try:
        # Create graph explorer
        explorer = NeptuneGraphExplorer()
        
        # Run exploration
        results = {}
        
        if args.query:
            # Run custom query
            results["custom_query"] = explorer.run_custom_query(args.query)
        else:
            # Run standard exploration
            results["schema"] = explorer.explore_graph_schema()
            results["entities"] = explorer.explore_entities()
            results["relationships"] = explorer.explore_relationships()
            results["documents"] = explorer.explore_documents()
            results["facts"] = explorer.explore_facts()
        
        # Save results
        explorer.save_results(results, args.output)
        
        print("\nExploration complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

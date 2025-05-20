#!/usr/bin/env python3

"""
Neptune Analytics Query Examples

This script demonstrates how to query a Neptune Analytics graph using OpenCypher.
It provides examples of common query patterns and how to execute them.

Usage:
  uv run python scripts/neptune_query_examples.py [--query QUERY] [--verbose]
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NeptuneAnalyticsClient:
    """Client for querying Neptune Analytics graphs"""
    
    def __init__(self):
        """Initialize the Neptune Analytics client"""
        try:
            # Import required libraries
            import boto3
            from botocore.config import Config
            
            # Get Neptune Analytics configuration from environment
            neptune_graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
            if not neptune_graph_id:
                raise ValueError("NEPTUNE_ANALYTICS_GRAPH_ID environment variable is required")
                
            neptune_region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
            
            # Configure boto3 client
            config = Config(
                region_name=neptune_region,
                signature_version='v4',
                retries={
                    'max_attempts': 10,
                    'mode': 'standard'
                }
            )
            
            # Create Neptune Analytics client
            self.client = boto3.client('neptune-graph', config=config)
            self.graph_id = neptune_graph_id
            
            print(f"Connected to Neptune Analytics graph: {self.graph_id}")
            
        except ImportError as e:
            print(f"Error importing required libraries: {e}")
            raise
        except Exception as e:
            print(f"Error initializing Neptune Analytics client: {e}")
            raise
    
    def execute_query(self, query, parameters=None):
        """Execute an OpenCypher query against Neptune Analytics"""
        try:
            # Prepare parameters
            params = {}
            if parameters:
                params = parameters
                
            # Execute query
            response = self.client.execute_query(
                graphIdentifier=self.graph_id,
                language='OPEN_CYPHER',
                queryString=query,
                parameters=params
            )
            
            # Process results
            results = []
            for record in response.get('results', []):
                result_dict = {}
                for key, value in record.items():
                    # Convert Neptune Analytics value format to Python native types
                    result_dict[key] = self._convert_value(value)
                results.append(result_dict)
                
            return results
            
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    def _convert_value(self, value):
        """Convert Neptune Analytics value format to Python native types"""
        if 'stringValue' in value:
            return value['stringValue']
        elif 'integerValue' in value:
            return int(value['integerValue'])
        elif 'doubleValue' in value:
            return float(value['doubleValue'])
        elif 'booleanValue' in value:
            return value['booleanValue']
        elif 'listValue' in value:
            return [self._convert_value(item) for item in value['listValue']]
        elif 'mapValue' in value:
            return {k: self._convert_value(v) for k, v in value['mapValue'].items()}
        elif 'nullValue' in value:
            return None
        else:
            return str(value)  # Default fallback

def run_example_queries(client, verbose=False):
    """Run example queries against Neptune Analytics"""
    
    # Example 1: Get all entity types
    entity_types_query = """
    MATCH (e:Entity)
    RETURN DISTINCT e.type as entity_type, count(*) as count
    ORDER BY count DESC
    """
    
    print("\nExample 1: Entity Types")
    entity_types = client.execute_query(entity_types_query)
    for item in entity_types:
        print(f"  {item['entity_type']}: {item['count']} entities")
    
    # Example 2: Get relationships between entities
    relationships_query = """
    MATCH (e1:Entity)-[r]->(e2:Entity)
    RETURN DISTINCT type(r) as relationship_type, count(*) as count
    ORDER BY count DESC
    """
    
    print("\nExample 2: Relationship Types")
    relationships = client.execute_query(relationships_query)
    for item in relationships:
        print(f"  {item['relationship_type']}: {item['count']} relationships")
    
    # Example 3: Get specific entity and its relationships
    if verbose:
        entity_query = """
        MATCH (e:Entity)
        WHERE e.name CONTAINS 'neural'
        RETURN e.id as id, e.name as name, e.type as type
        LIMIT 5
        """
        
        print("\nExample 3: Entities containing 'neural'")
        entities = client.execute_query(entity_query)
        for entity in entities:
            print(f"  {entity['name']} ({entity['type']})")
            
            # Get relationships for this entity
            entity_id = entity['id']
            rel_query = f"""
            MATCH (e1:Entity {{id: '{entity_id}'}})-[r]->(e2:Entity)
            RETURN e2.name as target, type(r) as relationship
            LIMIT 10
            """
            
            relationships = client.execute_query(rel_query)
            for rel in relationships:
                print(f"    -{rel['relationship']}-> {rel['target']}")
    
    # Example 4: Get document information
    document_query = """
    MATCH (d:Document)
    RETURN d.id as id, d.title as title
    LIMIT 5
    """
    
    print("\nExample 4: Documents")
    documents = client.execute_query(document_query)
    for doc in documents:
        print(f"  {doc['title'] if doc['title'] else doc['id']}")
    
    # Example 5: Get graph schema information
    schema_query = """
    MATCH (n)
    RETURN DISTINCT labels(n) as labels, count(*) as count
    ORDER BY count DESC
    """
    
    print("\nExample 5: Graph Schema")
    schema = client.execute_query(schema_query)
    for item in schema:
        print(f"  {item['labels']}: {item['count']} nodes")

def main():
    parser = argparse.ArgumentParser(description='Query Neptune Analytics graph using OpenCypher')
    parser.add_argument('--query', '-q', help='Custom OpenCypher query to execute')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        # Initialize Neptune Analytics client
        client = NeptuneAnalyticsClient()
        
        if args.query:
            # Execute custom query
            print(f"\nExecuting custom query: {args.query}")
            results = client.execute_query(args.query)
            
            # Print results
            print("\nResults:")
            for i, result in enumerate(results):
                print(f"  {i+1}. {json.dumps(result)}")
                
            print(f"\nTotal results: {len(results)}")
        else:
            # Run example queries
            run_example_queries(client, args.verbose)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""
Explore Neptune Analytics Graph

This script explores the schema and content of a Neptune Analytics graph.
It extracts information about node labels, relationship types, and properties.

Usage:
  uv run python scripts/explore_neptune_graph.py [--output OUTPUT] [--verbose]
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NeptuneGraphExplorer:
    """Explorer for Neptune Analytics graphs"""
    
    def __init__(self):
        """Initialize the Neptune Analytics explorer"""
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
            print(f"Error initializing Neptune Analytics explorer: {e}")
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
    
    def explore_graph(self, verbose=False):
        """Explore the Neptune Analytics graph and return schema information"""
        schema_info = {}
        
        try:
            # Get node labels
            node_labels_query = """
            MATCH (n)
            RETURN DISTINCT labels(n) as labels, count(*) as count
            ORDER BY count DESC
            """
            
            print("Exploring node labels...")
            node_labels = self.execute_query(node_labels_query)
            schema_info['node_labels'] = node_labels
            
            # Get relationship types
            rel_types_query = """
            MATCH ()-[r]->()
            RETURN DISTINCT type(r) as type, count(*) as count
            ORDER BY count DESC
            """
            
            print("Exploring relationship types...")
            rel_types = self.execute_query(rel_types_query)
            schema_info['relationship_types'] = rel_types
            
            # Get node properties
            if verbose:
                print("Exploring node properties...")
                node_properties = {}
                
                for label_info in node_labels:
                    label = label_info['labels'][0] if isinstance(label_info['labels'], list) else label_info['labels']
                    
                    properties_query = f"""
                    MATCH (n:{label})
                    RETURN keys(n) as properties
                    LIMIT 1
                    """
                    
                    try:
                        properties = self.execute_query(properties_query)
                        if properties and 'properties' in properties[0]:
                            node_properties[label] = properties[0]['properties']
                    except Exception as e:
                        print(f"Error getting properties for {label}: {e}")
                
                schema_info['node_properties'] = node_properties
            
            # Get sample data
            if verbose:
                print("Getting sample data...")
                samples = {}
                
                for label_info in node_labels[:5]:  # Limit to first 5 labels
                    label = label_info['labels'][0] if isinstance(label_info['labels'], list) else label_info['labels']
                    
                    sample_query = f"""
                    MATCH (n:{label})
                    RETURN n LIMIT 3
                    """
                    
                    try:
                        sample_data = self.execute_query(sample_query)
                        samples[label] = sample_data
                    except Exception as e:
                        print(f"Error getting sample data for {label}: {e}")
                
                schema_info['samples'] = samples
            
            return schema_info
            
        except Exception as e:
            print(f"Error exploring graph: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Explore Neptune Analytics graph schema')
    parser.add_argument('--output', '-o', help='Output file for the schema information')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        # Initialize Neptune Graph Explorer
        explorer = NeptuneGraphExplorer()
        
        # Explore graph
        schema_info = explorer.explore_graph(args.verbose)
        
        # Print summary
        print("\nGraph Schema Summary:")
        print(f"  Node Labels: {len(schema_info['node_labels'])}")
        print(f"  Relationship Types: {len(schema_info['relationship_types'])}")
        
        # Print top node labels
        print("\nTop Node Labels:")
        for i, label_info in enumerate(schema_info['node_labels'][:5]):
            label = label_info['labels'][0] if isinstance(label_info['labels'], list) else label_info['labels']
            count = label_info['count']
            print(f"  {i+1}. {label}: {count} nodes")
        
        # Print top relationship types
        print("\nTop Relationship Types:")
        for i, rel_info in enumerate(schema_info['relationship_types'][:5]):
            rel_type = rel_info['type']
            count = rel_info['count']
            print(f"  {i+1}. {rel_type}: {count} relationships")
        
        # Save to file if output specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(schema_info, f, indent=2)
            print(f"\nSchema information saved to {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

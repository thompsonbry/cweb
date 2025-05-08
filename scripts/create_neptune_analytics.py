#!/usr/bin/env python3
"""
Script to create a Neptune Analytics graph with vector search enabled.
"""

import argparse
import boto3
import json
import time
import sys
from botocore.exceptions import ClientError

def create_neptune_analytics_graph(
    graph_name,
    region,
    instance_type="db.r6g.4xlarge",  # 16GB RAM
    vector_search_dimensions=1024,
    wait_for_creation=True
):
    """
    Create a Neptune Analytics graph with vector search enabled.
    
    Args:
        graph_name: Name of the graph
        region: AWS region
        instance_type: Instance type (default: db.r6g.4xlarge with 16GB RAM)
        vector_search_dimensions: Dimensions for vector search (default: 1024)
        wait_for_creation: Whether to wait for the graph to be created
        
    Returns:
        dict: Response from the create_graph API call
    """
    client = boto3.client('neptune-graph', region_name=region)
    
    # Configure vector search
    vector_search_config = {
        "vectorSearchConfiguration": {
            "dimension": vector_search_dimensions,
            "similarityMetric": "cosine"
        }
    }
    
    try:
        response = client.create_graph(
            graphName=graph_name,
            instanceType=instance_type,
            graphOptions=json.dumps(vector_search_config),
            tags=[
                {
                    'key': 'Project',
                    'value': 'CWEB'
                },
                {
                    'key': 'Environment',
                    'value': 'Development'
                }
            ]
        )
        
        print(f"Creating Neptune Analytics graph: {graph_name}")
        print(f"Graph ID: {response['id']}")
        
        if wait_for_creation:
            print("Waiting for graph to be created (this may take several minutes)...")
            waiter = client.get_waiter('graph_available')
            waiter.wait(id=response['id'])
            print("Graph creation complete!")
            
            # Get graph details
            graph_details = client.get_graph(id=response['id'])
            print(f"Graph endpoint: {graph_details['endpoint']}")
            
        return response
        
    except ClientError as e:
        print(f"Error creating Neptune Analytics graph: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Create a Neptune Analytics graph with vector search enabled')
    parser.add_argument('--name', required=True, help='Name of the graph')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--instance-type', default='db.r6g.4xlarge', help='Instance type')
    parser.add_argument('--vector-dimensions', type=int, default=1024, help='Vector search dimensions')
    parser.add_argument('--no-wait', action='store_true', help='Do not wait for graph creation to complete')
    
    args = parser.parse_args()
    
    create_neptune_analytics_graph(
        graph_name=args.name,
        region=args.region,
        instance_type=args.instance_type,
        vector_search_dimensions=args.vector_dimensions,
        wait_for_creation=not args.no_wait
    )

if __name__ == "__main__":
    main()

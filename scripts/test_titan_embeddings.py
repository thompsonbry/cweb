#!/usr/bin/env python3
"""
Script to test Amazon Bedrock Titan Embeddings and Neptune Analytics integration.
"""

import os
import sys
import json
import boto3
import time
from datetime import datetime

def list_available_models():
    """List available Bedrock models."""
    try:
        # Create Bedrock client
        bedrock = boto3.client(
            service_name='bedrock',
            region_name='us-west-2'
        )
        
        # List foundation models
        response = bedrock.list_foundation_models()
        
        # Filter for embedding models
        embedding_models = []
        for model in response.get('modelSummaries', []):
            if 'embed' in model.get('modelId', '').lower():
                embedding_models.append({
                    'modelId': model.get('modelId'),
                    'modelName': model.get('modelName'),
                    'providerName': model.get('providerName')
                })
        
        return embedding_models
        
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def test_neptune_analytics_connection():
    """Test connection to Neptune Analytics."""
    try:
        # Neptune Analytics endpoint
        graph_endpoint = "g-k2n0lshd74.us-west-2.neptune-graph.amazonaws.com"
        
        # Create a simple query to test connection
        query = "MATCH (n) RETURN count(n) as count"
        
        # Print the command that would be used
        print("\nCommand to test Neptune Analytics connection:")
        print(f"awscurl -X POST --region us-west-2 --service neptune-graph https://{graph_endpoint}/opencypher -d \"query={query}\" -H \"Content-Type: application/x-www-form-urlencoded\"")
        
        # Execute the command using os.system
        import os
        cmd = f"awscurl -X POST --region us-west-2 --service neptune-graph https://{graph_endpoint}/opencypher -d \"query={query}\" -H \"Content-Type: application/x-www-form-urlencoded\""
        print("\nExecuting command...")
        exit_code = os.system(cmd)
        
        if exit_code == 0:
            print("\n✅ Successfully connected to Neptune Analytics")
            return True
        else:
            print(f"\n❌ Failed to connect to Neptune Analytics (exit code: {exit_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing Neptune Analytics connection: {e}")
        return False

if __name__ == "__main__":
    print("Testing Bedrock and Neptune Analytics integration...")
    
    # List available embedding models
    print("\nListing available embedding models in Bedrock:")
    embedding_models = list_available_models()
    
    if embedding_models:
        print(f"Found {len(embedding_models)} embedding models:")
        for i, model in enumerate(embedding_models):
            print(f"{i+1}. {model['modelName']} ({model['modelId']}) by {model['providerName']}")
    else:
        print("No embedding models found or error occurred.")
    
    # Test Neptune Analytics connection
    print("\nTesting Neptune Analytics connection:")
    success = test_neptune_analytics_connection()
    
    if success:
        print("\n✅ All tests completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

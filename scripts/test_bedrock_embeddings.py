#!/usr/bin/env python3
"""
Script to test Amazon Bedrock embeddings with Neptune Analytics.
"""

import os
import sys
import json
import boto3
import time
from datetime import datetime

def generate_embedding(text, model_id='amazon.titan-embed-text-v1'):
    """Generate embedding using Amazon Bedrock."""
    try:
        # Create Bedrock Runtime client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-west-2'
        )
        
        # Prepare request body
        request_body = {
            "inputText": text
        }
        
        # Call embedding model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        embedding = response_body['embedding']
        
        return {
            'success': True,
            'embedding': embedding,
            'dimension': len(embedding)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def execute_query(query):
    """Execute an openCypher query against Neptune Analytics."""
    try:
        # Neptune Analytics endpoint
        graph_endpoint = "g-k2n0lshd74.us-west-2.neptune-graph.amazonaws.com"
        
        # Prepare the query for command line
        escaped_query = query.replace('"', '\\"').replace('\n', ' ')
        
        # Create the command
        cmd = f'awscurl -X POST --region us-west-2 --service neptune-graph https://{graph_endpoint}/opencypher -d "query={escaped_query}" -H "Content-Type: application/x-www-form-urlencoded"'
        
        # Execute the command
        print(f"Executing query: {query[:60]}...")
        result = os.popen(cmd).read()
        
        # Parse the result
        try:
            result_json = json.loads(result)
            return True, result_json
        except:
            return True, result
            
    except Exception as e:
        return False, str(e)

def create_evidence_with_embedding():
    """Create evidence node with embedding in Neptune Analytics."""
    try:
        # Generate embedding for a test text
        test_text = "Aircraft is flying slowly at low altitude and not responding to radio calls"
        print(f"Generating embedding for text: '{test_text}'")
        
        result = generate_embedding(test_text)
        
        if not result['success']:
            print(f"❌ Failed to generate embedding: {result['error']}")
            return False
            
        print(f"✅ Successfully generated embedding with dimension: {result['dimension']}")
        
        # Print first 5 values of the embedding vector
        print(f"First 5 values of embedding: {result['embedding'][:5]}")
        
        # Create a shorter embedding for storage in the graph
        # Neptune Analytics can handle the full embedding, but we'll use a shorter one for this example
        short_embedding = result['embedding'][:10]
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Create Evidence node with embedding
        evidence_id = f'evidence-embedding-{int(time.time())}'
        evidence_query = f"""
        CREATE (:Evidence {{
          id: '{evidence_id}',
          source: 'Radar Operator',
          content: '{test_text}',
          reliability: 0.9,
          embedding_sample: {short_embedding},
          created_at: '{timestamp}'
        }})
        """
        
        success, result = execute_query(evidence_query)
        if not success:
            print(f"❌ Failed to create Evidence node with embedding: {result}")
            return False
            
        print(f"✅ Created Evidence node with embedding sample (id: {evidence_id})")
        
        # Connect the evidence to the story
        connect_query = f"""
        MATCH (e:Evidence {{id: '{evidence_id}'}}), (s:Story {{id: 'story-example'}})
        CREATE (e)-[:SUPPORTS {{strength: 0.85}}]->(s)
        """
        
        success, result = execute_query(connect_query)
        if not success:
            print(f"❌ Failed to connect Evidence to Story: {result}")
            return False
            
        print("✅ Connected Evidence to Story with SUPPORTS relationship")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating evidence with embedding: {e}")
        return False

if __name__ == "__main__":
    print("Testing Bedrock embeddings with Neptune Analytics...")
    success = create_evidence_with_embedding()
    
    if success:
        print("\n✅ Successfully created evidence with embedding")
        sys.exit(0)
    else:
        print("\n❌ Failed to create evidence with embedding")
        sys.exit(1)

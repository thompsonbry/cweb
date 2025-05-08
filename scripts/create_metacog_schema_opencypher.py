#!/usr/bin/env python3
"""
Script to create the metacognition schema in Neptune Analytics using openCypher.
"""

import os
import sys
import time
import json
from datetime import datetime

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

def create_metacog_schema():
    """Create the metacognition schema in Neptune Analytics."""
    try:
        print("Creating metacognition schema in Neptune Analytics...")
        
        # Check if we already have nodes
        success, result = execute_query("MATCH (n) RETURN count(n) as count")
        
        if not success:
            print(f"❌ Failed to query graph: {result}")
            return False
            
        count = result.get('results', [{}])[0].get('count', 0)
        if count > 0:
            print(f"⚠️ Graph already contains {count} nodes.")
            proceed = input("Do you want to proceed with schema creation anyway? (y/n): ")
            if proceed.lower() != 'y':
                print("Schema creation aborted.")
                return False
        
        # Create example nodes for each label to establish schema
        print("\nCreating example nodes for each label...")
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Create an Agent
        agent_query = f"""
        CREATE (:Agent {{
          id: 'agent-example',
          name: 'Example Agent',
          expertise_level: 'expert',
          confidence_threshold: 0.7,
          created_at: '{timestamp}'
        }})
        """
        success, result = execute_query(agent_query)
        if not success:
            print(f"❌ Failed to create Agent node: {result}")
            return False
        print("✅ Created example Agent node")
        
        # Create a Story
        story_query = f"""
        CREATE (:Story {{
          id: 'story-example',
          name: 'Aircraft Approaching Ship',
          description: 'The aircraft is searching visually for a target',
          confidence: 0.6,
          coherence: 0.8,
          completeness: 0.5,
          created_at: '{timestamp}'
        }})
        """
        success, result = execute_query(story_query)
        if not success:
            print(f"❌ Failed to create Story node: {result}")
            return False
        print("✅ Created example Story node")
        
        # Create Evidence
        evidence_query = f"""
        CREATE (:Evidence {{
          id: 'evidence-example',
          source: 'Radar',
          content: 'Slow-moving aircraft approaching',
          reliability: 0.9,
          created_at: '{timestamp}'
        }})
        """
        success, result = execute_query(evidence_query)
        if not success:
            print(f"❌ Failed to create Evidence node: {result}")
            return False
        print("✅ Created example Evidence node")
        
        # Create an Assumption
        assumption_query = f"""
        CREATE (:Assumption {{
          id: 'assumption-example',
          description: 'Aircraft is searching for a target',
          created_at: '{timestamp}'
        }})
        """
        success, result = execute_query(assumption_query)
        if not success:
            print(f"❌ Failed to create Assumption node: {result}")
            return False
        print("✅ Created example Assumption node")
        
        # Create a Critique
        critique_query = f"""
        CREATE (:Critique {{
          id: 'critique-example',
          critique_type: 'conflict',
          description: 'Aircraft flying straight, not erratically as expected for visual search',
          severity: 0.8,
          created_at: '{timestamp}'
        }})
        """
        success, result = execute_query(critique_query)
        if not success:
            print(f"❌ Failed to create Critique node: {result}")
            return False
        print("✅ Created example Critique node")
        
        # Create example relationships
        print("\nCreating example relationships...")
        
        # Story ASSUMES Assumption
        assumes_query = """
        MATCH (s:Story {id: 'story-example'}), (a:Assumption {id: 'assumption-example'})
        CREATE (s)-[:ASSUMES]->(a)
        """
        success, result = execute_query(assumes_query)
        if not success:
            print(f"❌ Failed to create ASSUMES relationship: {result}")
            return False
        print("✅ Created ASSUMES relationship")
        
        # Critique CRITIQUES Story
        critiques_query = """
        MATCH (c:Critique {id: 'critique-example'}), (s:Story {id: 'story-example'})
        CREATE (c)-[:CRITIQUES]->(s)
        """
        success, result = execute_query(critiques_query)
        if not success:
            print(f"❌ Failed to create CRITIQUES relationship: {result}")
            return False
        print("✅ Created CRITIQUES relationship")
        
        # Agent ASSESSES Story
        assesses_query = f"""
        MATCH (a:Agent {{id: 'agent-example'}}), (s:Story {{id: 'story-example'}})
        CREATE (a)-[:ASSESSES {{belief: 0.6, confidence: 0.7, timestamp: '{timestamp}'}}]->(s)
        """
        success, result = execute_query(assesses_query)
        if not success:
            print(f"❌ Failed to create ASSESSES relationship: {result}")
            return False
        print("✅ Created ASSESSES relationship")
        
        # Evidence SUPPORTS Story
        supports_query = """
        MATCH (e:Evidence {id: 'evidence-example'}), (s:Story {id: 'story-example'})
        CREATE (e)-[:SUPPORTS {strength: 0.8}]->(s)
        """
        success, result = execute_query(supports_query)
        if not success:
            print(f"❌ Failed to create SUPPORTS relationship: {result}")
            return False
        print("✅ Created SUPPORTS relationship")
        
        print("\n✅ Metacognition schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating metacognition schema: {e}")
        return False

if __name__ == "__main__":
    print("Creating metacognition schema in Neptune Analytics...")
    success = create_metacog_schema()
    
    if success:
        print("\n✅ Schema creation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Schema creation failed")
        sys.exit(1)

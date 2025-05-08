#!/usr/bin/env python3
"""
Script to create the HyperIBIS schema in Neptune Analytics.

This script defines and creates the schema for modeling arguments to support metacognition
based on the HyperIBIS model, which extends the traditional IBIS (Issue-Based Information System)
with belief and expected utility assessments.
"""

import os
import sys
import time
from dotenv import load_dotenv
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T, P, Cardinality

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from config.neptune_config import get_neptune_connection_string, VECTOR_DIMENSION

# Define schema constants
VERTEX_LABELS = {
    # Core IBIS elements
    'Issue': 'Issue',
    'Position': 'Position',
    'Argument': 'Argument',
    'Evidence': 'Evidence',
    
    # Specialized issue types
    'MutexIssue': 'MutexIssue',
    'Hypothesis': 'Hypothesis',
    'WorldIssue': 'WorldIssue',
    
    # Assessment elements
    'Assessment': 'Assessment',
    'Assessor': 'Assessor',
    
    # Metacognitive elements
    'Story': 'Story',
    'Assumption': 'Assumption',
    'Critique': 'Critique',
    'Correction': 'Correction'
}

EDGE_LABELS = {
    # Core IBIS relationships
    'HAS_POSITION': 'HAS_POSITION',  # Issue to Position
    'SUPPORTS': 'SUPPORTS',          # Argument to Position (supporting)
    'REBUTS': 'REBUTS',              # Argument to Position (rebutting)
    
    # Evidence relationships
    'PROVIDES_EVIDENCE': 'PROVIDES_EVIDENCE',  # Evidence to Argument
    
    # Assessment relationships
    'ASSESSES': 'ASSESSES',          # Assessor to Assessment
    'ASSESSED_ON': 'ASSESSED_ON',    # Assessment to any element
    
    # Metacognitive relationships
    'PART_OF': 'PART_OF',            # Element to Story
    'CRITIQUES': 'CRITIQUES',        # Critique to any element
    'CORRECTS': 'CORRECTS',          # Correction to any element
    'ASSUMES': 'ASSUMES',            # Story to Assumption
    
    # Specialized relationships
    'DEPENDS_ON': 'DEPENDS_ON',      # Position to Position (conditional dependency)
    'CONTRADICTS': 'CONTRADICTS'     # Position to Position (mutual exclusion)
}

PROPERTY_KEYS = {
    # Common properties
    'name': 'name',
    'description': 'description',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'created_by': 'created_by',
    
    # Issue properties
    'question': 'question',
    'issue_type': 'issue_type',  # regular, mutex, hypothesis, world
    
    # Position properties
    'answer': 'answer',
    
    # Argument properties
    'warrant': 'warrant',  # Justification for the argument
    
    # Evidence properties
    'source': 'source',
    'url': 'url',
    'content': 'content',
    'embedding': 'embedding',  # Vector embedding of the evidence content
    
    # Assessment properties
    'belief': 'belief',  # Degree of belief (0-1)
    'expected_value': 'expected_value',  # Expected utility if true
    'strength': 'strength',  # Strength of evidentiary link (0-1)
    
    # Metacognitive properties
    'confidence': 'confidence',  # Confidence in a story or assumption
    'critique_type': 'critique_type',  # incompleteness, conflict, unreliability
    'correction_type': 'correction_type'  # elaboration, revision, rejection
}

def create_hyperibis_schema():
    """Create the HyperIBIS schema in Neptune Analytics."""
    try:
        print(f"Connecting to Neptune Analytics at {os.getenv('NEPTUNE_ENDPOINT')}...")
        connection = DriverRemoteConnection(get_neptune_connection_string(), 'g')
        g = traversal().withRemote(connection)
        
        print("✅ Successfully connected to Neptune Analytics")
        
        # Create property keys with appropriate data types
        print("\nCreating property keys...")
        
        # Check if we already have vertices to avoid recreating schema
        count = g.V().count().next()
        if count > 0:
            print(f"⚠️ Graph already contains {count} vertices. Schema may already exist.")
            proceed = input("Do you want to proceed with schema creation anyway? (y/n): ")
            if proceed.lower() != 'y':
                print("Schema creation aborted.")
                connection.close()
                return False
        
        # Create example vertices for each label to establish schema
        print("\nCreating example vertices for each label...")
        
        # Create an Assessor
        assessor_id = "assessor-example"
        g.addV(VERTEX_LABELS['Assessor']) \
            .property(T.id, assessor_id) \
            .property(PROPERTY_KEYS['name'], "Example Assessor") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Assessor vertex")
        
        # Create an Issue
        issue_id = "issue-example"
        g.addV(VERTEX_LABELS['Issue']) \
            .property(T.id, issue_id) \
            .property(PROPERTY_KEYS['question'], "What is the best approach for modeling arguments?") \
            .property(PROPERTY_KEYS['issue_type'], "regular") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Issue vertex")
        
        # Create a Position
        position_id = "position-example"
        g.addV(VERTEX_LABELS['Position']) \
            .property(T.id, position_id) \
            .property(PROPERTY_KEYS['answer'], "HyperIBIS is the best approach") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Position vertex")
        
        # Create an Argument
        argument_id = "argument-example"
        g.addV(VERTEX_LABELS['Argument']) \
            .property(T.id, argument_id) \
            .property(PROPERTY_KEYS['warrant'], "HyperIBIS extends IBIS with belief and utility") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Argument vertex")
        
        # Create Evidence
        evidence_id = "evidence-example"
        g.addV(VERTEX_LABELS['Evidence']) \
            .property(T.id, evidence_id) \
            .property(PROPERTY_KEYS['source'], "HyperIBIS Documentation") \
            .property(PROPERTY_KEYS['content'], "HyperIBIS extends the standard IBIS model with belief and utility") \
            .property(PROPERTY_KEYS['embedding'], [0.0] * VECTOR_DIMENSION)  # Placeholder vector
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Evidence vertex")
        
        # Create an Assessment
        assessment_id = "assessment-example"
        g.addV(VERTEX_LABELS['Assessment']) \
            .property(T.id, assessment_id) \
            .property(PROPERTY_KEYS['belief'], 0.8) \
            .property(PROPERTY_KEYS['expected_value'], 0.9) \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Assessment vertex")
        
        # Create a Story (metacognitive element)
        story_id = "story-example"
        g.addV(VERTEX_LABELS['Story']) \
            .property(T.id, story_id) \
            .property(PROPERTY_KEYS['name'], "Example Story") \
            .property(PROPERTY_KEYS['confidence'], 0.7) \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Story vertex")
        
        # Create example edges to establish relationships
        print("\nCreating example edges for each relationship type...")
        
        # Issue HAS_POSITION Position
        g.V(issue_id).addE(EDGE_LABELS['HAS_POSITION']).to(g.V(position_id)).next()
        print(f"✅ Created HAS_POSITION edge")
        
        # Argument SUPPORTS Position
        g.V(argument_id).addE(EDGE_LABELS['SUPPORTS']).to(g.V(position_id)).next()
        print(f"✅ Created SUPPORTS edge")
        
        # Evidence PROVIDES_EVIDENCE Argument
        g.V(evidence_id).addE(EDGE_LABELS['PROVIDES_EVIDENCE']).to(g.V(argument_id)).next()
        print(f"✅ Created PROVIDES_EVIDENCE edge")
        
        # Assessor ASSESSES Assessment
        g.V(assessor_id).addE(EDGE_LABELS['ASSESSES']).to(g.V(assessment_id)).next()
        print(f"✅ Created ASSESSES edge")
        
        # Assessment ASSESSED_ON Position
        g.V(assessment_id).addE(EDGE_LABELS['ASSESSED_ON']).to(g.V(position_id)).next()
        print(f"✅ Created ASSESSED_ON edge")
        
        # Position PART_OF Story
        g.V(position_id).addE(EDGE_LABELS['PART_OF']).to(g.V(story_id)).next()
        print(f"✅ Created PART_OF edge")
        
        print("\n✅ HyperIBIS schema created successfully")
        
        # Close the connection
        connection.close()
        print("✅ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating HyperIBIS schema: {e}")
        return False

if __name__ == "__main__":
    if not os.getenv('NEPTUNE_ENDPOINT'):
        print("❌ NEPTUNE_ENDPOINT environment variable is not set")
        sys.exit(1)
        
    print(f"Creating HyperIBIS schema in Neptune Analytics at {os.getenv('NEPTUNE_ENDPOINT')}")
    success = create_hyperibis_schema()
    
    if success:
        print("\n✅ Schema creation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Schema creation failed")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script to create the metacognition schema in Neptune Analytics.

This script defines and creates the schema for modeling metacognitive processes
based on the Recognition/Metacognition (R/M) model described in the WCNN 1995 paper.
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
    # Core metacognitive elements
    'Story': 'Story',                # Causal structure organizing complex information
    'Evidence': 'Evidence',          # Observations or data points
    'Assumption': 'Assumption',      # Explicit assumptions made in a story
    'Goal': 'Goal',                  # Goals in a story
    'Action': 'Action',              # Actions in a story
    'Consequence': 'Consequence',    # Consequences in a story
    
    # Metacognitive processes
    'Critique': 'Critique',          # Critique of a story (incompleteness, conflict, unreliability)
    'Correction': 'Correction',      # Correction to a story
    'QuickTest': 'QuickTest',        # Gating function for metacognitive processes
    
    # Recognition elements
    'Pattern': 'Pattern',            # Recognized pattern
    'Response': 'Response',          # Triggered response
    
    # Agent elements
    'Agent': 'Agent',                # Agent performing metacognition
    'AttentionalFocus': 'AttentionalFocus'  # Current focus of attention
}

EDGE_LABELS = {
    # Story structure relationships
    'CONTAINS': 'CONTAINS',          # Story to its elements
    'INITIATES': 'INITIATES',        # Event to Goal
    'MOTIVATES': 'MOTIVATES',        # Goal to Action
    'RESULTS_IN': 'RESULTS_IN',      # Action to Consequence
    
    # Evidence relationships
    'SUPPORTS': 'SUPPORTS',          # Evidence supporting a story element
    'CONTRADICTS': 'CONTRADICTS',    # Evidence contradicting a story element
    
    # Metacognitive relationships
    'CRITIQUES': 'CRITIQUES',        # Critique to Story
    'CORRECTS': 'CORRECTS',          # Correction to Story
    'TESTS': 'TESTS',                # QuickTest to Story
    'ASSUMES': 'ASSUMES',            # Story to Assumption
    
    # Recognition relationships
    'RECOGNIZES': 'RECOGNIZES',      # Agent to Pattern
    'TRIGGERS': 'TRIGGERS',          # Pattern to Response
    
    # Attention relationships
    'FOCUSES_ON': 'FOCUSES_ON',      # Agent to AttentionalFocus
    'ATTENDS_TO': 'ATTENDS_TO'       # AttentionalFocus to any element
}

PROPERTY_KEYS = {
    # Common properties
    'name': 'name',
    'description': 'description',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    
    # Story properties
    'confidence': 'confidence',      # Confidence in a story (0-1)
    'coherence': 'coherence',        # Coherence of a story (0-1)
    'completeness': 'completeness',  # Completeness of a story (0-1)
    
    # Evidence properties
    'source': 'source',
    'content': 'content',
    'reliability': 'reliability',    # Reliability of evidence (0-1)
    'embedding': 'embedding',        # Vector embedding of evidence
    
    # Critique properties
    'critique_type': 'critique_type',  # incompleteness, conflict, unreliability
    'severity': 'severity',          # Severity of the critique (0-1)
    
    # Correction properties
    'correction_type': 'correction_type',  # elaboration, revision, rejection
    
    # QuickTest properties
    'threshold': 'threshold',        # Threshold for triggering metacognition
    'result': 'result',              # Result of the quick test (pass/fail)
    
    # Pattern properties
    'cues': 'cues',                  # Cues that trigger the pattern
    'familiarity': 'familiarity',    # Familiarity of the pattern (0-1)
    
    # Agent properties
    'expertise_level': 'expertise_level',  # Expertise level of the agent
    
    # AttentionalFocus properties
    'priority': 'priority',          # Priority of the focus (0-1)
    'duration': 'duration'           # Duration of attention
}

def create_metacog_schema():
    """Create the metacognition schema in Neptune Analytics."""
    try:
        print(f"Connecting to Neptune Analytics at {os.getenv('NEPTUNE_ENDPOINT')}...")
        connection = DriverRemoteConnection(get_neptune_connection_string(), 'g')
        g = traversal().withRemote(connection)
        
        print("✅ Successfully connected to Neptune Analytics")
        
        # Check if we already have vertices to avoid recreating schema
        count = g.V().hasLabel(VERTEX_LABELS['Story']).count().next()
        if count > 0:
            print(f"⚠️ Graph already contains {count} Story vertices. Schema may already exist.")
            proceed = input("Do you want to proceed with schema creation anyway? (y/n): ")
            if proceed.lower() != 'y':
                print("Schema creation aborted.")
                connection.close()
                return False
        
        # Create example vertices for each label to establish schema
        print("\nCreating example vertices for each label...")
        
        # Create an Agent
        agent_id = "agent-example"
        g.addV(VERTEX_LABELS['Agent']) \
            .property(T.id, agent_id) \
            .property(PROPERTY_KEYS['name'], "Example Agent") \
            .property(PROPERTY_KEYS['expertise_level'], "expert") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Agent vertex")
        
        # Create a Story
        story_id = "story-example"
        g.addV(VERTEX_LABELS['Story']) \
            .property(T.id, story_id) \
            .property(PROPERTY_KEYS['name'], "Aircraft Approaching Ship") \
            .property(PROPERTY_KEYS['confidence'], 0.7) \
            .property(PROPERTY_KEYS['coherence'], 0.8) \
            .property(PROPERTY_KEYS['completeness'], 0.6) \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Story vertex")
        
        # Create Evidence
        evidence_id = "evidence-example"
        g.addV(VERTEX_LABELS['Evidence']) \
            .property(T.id, evidence_id) \
            .property(PROPERTY_KEYS['source'], "Radar") \
            .property(PROPERTY_KEYS['content'], "Slow-moving aircraft approaching") \
            .property(PROPERTY_KEYS['reliability'], 0.9) \
            .property(PROPERTY_KEYS['embedding'], [0.0] * VECTOR_DIMENSION)  # Placeholder vector
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Evidence vertex")
        
        # Create an Assumption
        assumption_id = "assumption-example"
        g.addV(VERTEX_LABELS['Assumption']) \
            .property(T.id, assumption_id) \
            .property(PROPERTY_KEYS['description'], "Aircraft is searching for a target") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Assumption vertex")
        
        # Create a Goal
        goal_id = "goal-example"
        g.addV(VERTEX_LABELS['Goal']) \
            .property(T.id, goal_id) \
            .property(PROPERTY_KEYS['description'], "Locate target ship") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Goal vertex")
        
        # Create an Action
        action_id = "action-example"
        g.addV(VERTEX_LABELS['Action']) \
            .property(T.id, action_id) \
            .property(PROPERTY_KEYS['description'], "Fly slowly to search visually") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Action vertex")
        
        # Create a Consequence
        consequence_id = "consequence-example"
        g.addV(VERTEX_LABELS['Consequence']) \
            .property(T.id, consequence_id) \
            .property(PROPERTY_KEYS['description'], "Aircraft would fly erratically") \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Consequence vertex")
        
        # Create a Critique
        critique_id = "critique-example"
        g.addV(VERTEX_LABELS['Critique']) \
            .property(T.id, critique_id) \
            .property(PROPERTY_KEYS['critique_type'], "conflict") \
            .property(PROPERTY_KEYS['description'], "Aircraft flying straight, not erratically") \
            .property(PROPERTY_KEYS['severity'], 0.8) \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Critique vertex")
        
        # Create a Pattern
        pattern_id = "pattern-example"
        g.addV(VERTEX_LABELS['Pattern']) \
            .property(T.id, pattern_id) \
            .property(PROPERTY_KEYS['name'], "Hostile Intent Pattern") \
            .property(PROPERTY_KEYS['cues'], "Approaching, Non-responsive") \
            .property(PROPERTY_KEYS['familiarity'], 0.9) \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example Pattern vertex")
        
        # Create an AttentionalFocus
        focus_id = "focus-example"
        g.addV(VERTEX_LABELS['AttentionalFocus']) \
            .property(T.id, focus_id) \
            .property(PROPERTY_KEYS['priority'], 0.9) \
            .property(PROPERTY_KEYS['duration'], 30) \
            .property(PROPERTY_KEYS['created_at'], int(time.time())) \
            .next()
        print(f"✅ Created example AttentionalFocus vertex")
        
        # Create example edges to establish relationships
        print("\nCreating example edges for each relationship type...")
        
        # Story CONTAINS elements
        g.V(story_id).addE(EDGE_LABELS['CONTAINS']).to(g.V(goal_id)).next()
        g.V(story_id).addE(EDGE_LABELS['CONTAINS']).to(g.V(action_id)).next()
        g.V(story_id).addE(EDGE_LABELS['CONTAINS']).to(g.V(consequence_id)).next()
        print(f"✅ Created CONTAINS edges")
        
        # Story structure relationships
        g.V(goal_id).addE(EDGE_LABELS['MOTIVATES']).to(g.V(action_id)).next()
        g.V(action_id).addE(EDGE_LABELS['RESULTS_IN']).to(g.V(consequence_id)).next()
        print(f"✅ Created story structure edges")
        
        # Evidence relationships
        g.V(evidence_id).addE(EDGE_LABELS['SUPPORTS']).to(g.V(goal_id)).next()
        g.V(evidence_id).addE(EDGE_LABELS['CONTRADICTS']).to(g.V(consequence_id)).next()
        print(f"✅ Created evidence relationship edges")
        
        # Metacognitive relationships
        g.V(critique_id).addE(EDGE_LABELS['CRITIQUES']).to(g.V(story_id)).next()
        g.V(story_id).addE(EDGE_LABELS['ASSUMES']).to(g.V(assumption_id)).next()
        print(f"✅ Created metacognitive relationship edges")
        
        # Recognition relationships
        g.V(agent_id).addE(EDGE_LABELS['RECOGNIZES']).to(g.V(pattern_id)).next()
        print(f"✅ Created recognition relationship edge")
        
        # Attention relationships
        g.V(agent_id).addE(EDGE_LABELS['FOCUSES_ON']).to(g.V(focus_id)).next()
        g.V(focus_id).addE(EDGE_LABELS['ATTENDS_TO']).to(g.V(story_id)).next()
        print(f"✅ Created attention relationship edges")
        
        print("\n✅ Metacognition schema created successfully")
        
        # Close the connection
        connection.close()
        print("✅ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating metacognition schema: {e}")
        return False

if __name__ == "__main__":
    if not os.getenv('NEPTUNE_ENDPOINT'):
        print("❌ NEPTUNE_ENDPOINT environment variable is not set")
        sys.exit(1)
        
    print(f"Creating metacognition schema in Neptune Analytics at {os.getenv('NEPTUNE_ENDPOINT')}")
    success = create_metacog_schema()
    
    if success:
        print("\n✅ Schema creation completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Schema creation failed")
        sys.exit(1)

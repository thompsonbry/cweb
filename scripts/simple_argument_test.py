#!/usr/bin/env python3

"""
Simple test script for argument extraction
"""

import os
import sys
import json

def main():
    print("Starting simple argument extraction test")
    
    # Mock data for testing
    mock_issue = {
        "id": "issue1",
        "question": "How can metacognitive processes improve decision-making?",
        "issue_type": "regular",
        "description": "This issue explores the role of metacognition in enhancing decision-making capabilities."
    }
    
    mock_positions = [
        {
            "id": "position1",
            "answer": "Metacognitive processes improve decision-making by enabling critical evaluation of initial hypotheses",
            "description": "This position argues that metacognition allows decision-makers to question their initial assessments."
        },
        {
            "id": "position2",
            "answer": "Metacognitive processes improve decision-making by facilitating adaptation to changing circumstances",
            "description": "This position focuses on how metacognition enables flexibility in thinking."
        }
    ]
    
    mock_arguments = [
        {
            "id": "arg1",
            "position_id": "position1",
            "warrant": "Research shows metacognitive monitoring improves decision quality",
            "is_supporting": True,
            "evidence": "Studies have demonstrated that individuals who engage in metacognitive monitoring make fewer errors in complex decision tasks."
        },
        {
            "id": "arg2",
            "position_id": "position1",
            "warrant": "Metacognitive processes can lead to overthinking",
            "is_supporting": False,
            "evidence": "In time-critical situations, excessive metacognitive reflection can delay necessary action."
        }
    ]
    
    # Create a simple argument model
    argument_model = {
        "issues": [mock_issue],
        "positions": mock_positions,
        "arguments": mock_arguments
    }
    
    # Print the model
    print("\nArgument Model:")
    print(json.dumps(argument_model, indent=2))
    
    # Save to file
    output_path = "output/simple_argument_test.json"
    with open(output_path, 'w') as f:
        json.dump(argument_model, f, indent=2)
    
    print(f"\nSaved argument model to {output_path}")
    print("Test completed successfully")

if __name__ == "__main__":
    main()

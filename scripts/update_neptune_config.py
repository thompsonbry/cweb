#!/usr/bin/env python3
"""
Script to update the Neptune Analytics configuration in the project.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_neptune_config():
    """Update the Neptune Analytics configuration."""
    try:
        # Check if .env file exists
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if not os.path.exists(env_path):
            print("❌ .env file not found. Creating a new one...")
            
            # Create .env file with Neptune Analytics configuration
            with open(env_path, 'w') as f:
                f.write("# Neptune Analytics Configuration\n")
                f.write("NEPTUNE_ENDPOINT=g-k2n0lshd74.us-west-2.neptune-graph.amazonaws.com\n")
                f.write("NEPTUNE_PORT=8182\n")
                f.write("NEPTUNE_AUTH_MODE=IAM\n")
                f.write("NEPTUNE_REGION=us-west-2\n\n")
                f.write("# AWS Configuration\n")
                f.write("AWS_PROFILE=default\n")
                f.write("AWS_REGION=us-west-2\n")
            
            print("✅ Created .env file with Neptune Analytics configuration")
        else:
            # Load existing environment variables
            load_dotenv(env_path)
            
            # Check if Neptune Analytics configuration exists
            if not os.getenv('NEPTUNE_ENDPOINT'):
                print("❌ NEPTUNE_ENDPOINT not found in .env file. Updating...")
                
                # Read existing .env file
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                # Update or add Neptune Analytics configuration
                with open(env_path, 'w') as f:
                    neptune_config_added = False
                    aws_config_added = False
                    
                    for line in lines:
                        if line.startswith('NEPTUNE_ENDPOINT='):
                            f.write("NEPTUNE_ENDPOINT=g-k2n0lshd74.us-west-2.neptune-graph.amazonaws.com\n")
                            neptune_config_added = True
                        elif line.startswith('NEPTUNE_REGION='):
                            f.write("NEPTUNE_REGION=us-west-2\n")
                        elif line.startswith('AWS_REGION='):
                            f.write("AWS_REGION=us-west-2\n")
                            aws_config_added = True
                        else:
                            f.write(line)
                    
                    # Add Neptune configuration if not found
                    if not neptune_config_added:
                        f.write("\n# Neptune Analytics Configuration\n")
                        f.write("NEPTUNE_ENDPOINT=g-k2n0lshd74.us-west-2.neptune-graph.amazonaws.com\n")
                        f.write("NEPTUNE_PORT=8182\n")
                        f.write("NEPTUNE_AUTH_MODE=IAM\n")
                        f.write("NEPTUNE_REGION=us-west-2\n")
                    
                    # Add AWS configuration if not found
                    if not aws_config_added:
                        f.write("\n# AWS Configuration\n")
                        f.write("AWS_PROFILE=default\n")
                        f.write("AWS_REGION=us-west-2\n")
                
                print("✅ Updated .env file with Neptune Analytics configuration")
            else:
                # Check if the endpoint matches our target
                current_endpoint = os.getenv('NEPTUNE_ENDPOINT')
                target_endpoint = "g-k2n0lshd74.us-west-2.neptune-graph.amazonaws.com"
                
                if current_endpoint != target_endpoint:
                    print(f"⚠️ Current NEPTUNE_ENDPOINT ({current_endpoint}) doesn't match target ({target_endpoint})")
                    update = input("Do you want to update the endpoint? (y/n): ")
                    
                    if update.lower() == 'y':
                        # Read existing .env file
                        with open(env_path, 'r') as f:
                            lines = f.readlines()
                        
                        # Update Neptune endpoint
                        with open(env_path, 'w') as f:
                            for line in lines:
                                if line.startswith('NEPTUNE_ENDPOINT='):
                                    f.write(f"NEPTUNE_ENDPOINT={target_endpoint}\n")
                                elif line.startswith('NEPTUNE_REGION='):
                                    f.write("NEPTUNE_REGION=us-west-2\n")
                                elif line.startswith('AWS_REGION='):
                                    f.write("AWS_REGION=us-west-2\n")
                                else:
                                    f.write(line)
                        
                        print("✅ Updated NEPTUNE_ENDPOINT in .env file")
                    else:
                        print("⚠️ Keeping current NEPTUNE_ENDPOINT")
                else:
                    print("✅ NEPTUNE_ENDPOINT is already set correctly")
        
        # Update config/neptune_config.py if needed
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'neptune_config.py')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Check if NEPTUNE_REGION needs to be updated
            if "NEPTUNE_REGION = os.getenv('NEPTUNE_REGION', 'us-east-1')" in config_content:
                updated_content = config_content.replace(
                    "NEPTUNE_REGION = os.getenv('NEPTUNE_REGION', 'us-east-1')",
                    "NEPTUNE_REGION = os.getenv('NEPTUNE_REGION', 'us-west-2')"
                )
                
                with open(config_path, 'w') as f:
                    f.write(updated_content)
                
                print("✅ Updated default NEPTUNE_REGION in neptune_config.py")
            
            # Check if we need to add HyperIBIS and metacognition specific constants
            if "# HyperIBIS specific constants" not in config_content:
                with open(config_path, 'a') as f:
                    f.write("\n# HyperIBIS specific constants\n")
                    f.write("ISSUE_TYPES = {\n")
                    f.write("    'REGULAR': 'regular',\n")
                    f.write("    'MUTEX': 'mutex',\n")
                    f.write("    'HYPOTHESIS': 'hypothesis',\n")
                    f.write("    'WORLD': 'world'\n")
                    f.write("}\n\n")
                    f.write("# Metacognition specific constants\n")
                    f.write("CRITIQUE_TYPES = {\n")
                    f.write("    'INCOMPLETENESS': 'incompleteness',\n")
                    f.write("    'CONFLICT': 'conflict',\n")
                    f.write("    'UNRELIABILITY': 'unreliability'\n")
                    f.write("}\n\n")
                    f.write("CORRECTION_TYPES = {\n")
                    f.write("    'ELABORATION': 'elaboration',\n")
                    f.write("    'REVISION': 'revision',\n")
                    f.write("    'REJECTION': 'rejection'\n")
                    f.write("}\n")
                
                print("✅ Added HyperIBIS and metacognition constants to neptune_config.py")
        
        print("\n✅ Neptune Analytics configuration updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Neptune Analytics configuration: {e}")
        return False

if __name__ == "__main__":
    print("Updating Neptune Analytics configuration...")
    success = update_neptune_config()
    
    if success:
        print("\n✅ Configuration update completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Configuration update failed")
        sys.exit(1)

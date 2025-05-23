#!/usr/bin/env python3

"""
Extract claims and arguments from a text sample using Amazon Bedrock
This version uses declarative claims instead of questions for issues
"""

import os
import sys
import json
import boto3
import argparse
import logging
import hashlib
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("claim_extractor")

class BedrockClient:
    """Client for interacting with Amazon Bedrock"""
    
    def __init__(self):
        """Initialize the Bedrock client"""
        region = os.environ.get("AWS_REGION", "us-west-2")
        self.client = boto3.client('bedrock-runtime', region_name=region)
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def extract_claims(self, text, chunk_id="chunk1"):
        """Extract claims from text using Bedrock"""
        prompt = """
        Analyze the following text and identify the key issues or claims being discussed.
        For each issue:
        1. Formulate it as a clear, declarative statement that makes a specific claim
        2. Ensure the statement represents a testable claim about the content
        3. Provide a brief description of the issue's context
        4. Identify specific text spans that support the identification of this issue

        Format your response as a JSON array of objects with these fields:
        - id: A short identifier (e.g., "claim1")
        - claim: The issue formulated as a declarative statement making a claim
        - description: Brief context about the issue
        - text_evidence: Direct quotes from the text that led to identifying this claim
        - chunk_ids: Array of chunk identifiers where this issue appears

        TEXT:
        {text}

        CLAIMS (JSON format):
        """
        
        response = self._invoke_model(prompt.format(text=text))
        claims = self._extract_json(response)
        
        # Add chunk_id to each claim
        for claim in claims:
            if "chunk_ids" not in claim:
                claim["chunk_ids"] = [chunk_id]
            elif chunk_id not in claim["chunk_ids"]:
                claim["chunk_ids"].append(chunk_id)
                
        return claims
    
    def extract_positions(self, text, claim):
        """Extract positions on a claim using Bedrock"""
        prompt = """
        Analyze the following text and identify the different positions or viewpoints on this claim:
        
        CLAIM: {claim}
        
        For each position:
        1. Formulate it as a clear, declarative statement (a position on the claim)
        2. Provide a brief description or explanation of the position
        3. Indicate whether this position supports or rebuts the claim
        
        Format your response as a JSON array of objects with these fields:
        - id: A short identifier (e.g., "position1")
        - statement: The position as a declarative statement
        - description: Brief explanation of the position
        - is_supporting: Boolean indicating whether this position supports (true) or rebuts (false) the claim
        - text_evidence: Direct quotes from the text that support this position
        
        TEXT:
        {text}
        
        POSITIONS (JSON format):
        """
        
        response = self._invoke_model(prompt.format(text=text, claim=claim))
        return self._extract_json(response)
    
    def extract_arguments(self, text, claim, position, is_supporting=True):
        """Extract arguments for a position using Bedrock"""
        arg_type = "supporting" if is_supporting else "rebutting"
        supports_or_rebuts = "supports" if is_supporting else "rebuts"
        ARG_TYPE = "SUPPORTING" if is_supporting else "REBUTTING"
        
        prompt = """
        Analyze the following text and identify {arg_type} arguments for this position:
        
        CLAIM: {claim}
        POSITION: {position}
        
        For each {arg_type} argument:
        1. Provide a warrant (justification for why this argument {supports_or_rebuts} the position)
        2. Extract specific evidence from the text that backs this argument
        
        Format your response as a JSON array of objects with these fields:
        - id: A short identifier (e.g., "arg1")
        - warrant: The justification for why this argument {supports_or_rebuts} the position
        - evidence: Specific text evidence that backs this argument
        
        TEXT:
        {text}
        
        {ARG_TYPE} ARGUMENTS (JSON format):
        """
        
        response = self._invoke_model(prompt.format(
            text=text, 
            claim=claim, 
            position=position, 
            arg_type=arg_type,
            supports_or_rebuts=supports_or_rebuts,
            ARG_TYPE=ARG_TYPE
        ))
        return self._extract_json(response)
    
    def _invoke_model(self, prompt):
        """Invoke the Bedrock model with a prompt"""
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            return None
    
    def _extract_json(self, response):
        """Extract JSON from the model response"""
        if not response:
            return []
            
        try:
            # Try to find JSON array in the response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try to find a single JSON object
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    return json.loads(json_str)
                    
                logger.warning(f"Could not parse JSON from response: {response}")
                return []
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return []

class ArgumentModel:
    """Class to represent the argument model with claims instead of issues"""
    
    def __init__(self):
        self.claims = []
        self.positions = []
        self.arguments = []
        self.evidence = []
    
    def add_claim(self, claim_id, claim_text, description=None, text_evidence=None, chunk_ids=None):
        """Add a claim to the model"""
        self.claims.append({
            "id": claim_id,
            "claim": claim_text,
            "description": description,
            "text_evidence": text_evidence,
            "chunk_ids": chunk_ids or []
        })
        return claim_id
    
    def add_position(self, position_id, claim_id, statement, description=None, is_supporting=True, text_evidence=None):
        """Add a position to the model"""
        self.positions.append({
            "id": position_id,
            "claim_id": claim_id,
            "statement": statement,
            "description": description,
            "is_supporting": is_supporting,
            "text_evidence": text_evidence
        })
        return position_id
    
    def add_argument(self, argument_id, position_id, warrant, is_supporting=True):
        """Add an argument to the model"""
        self.arguments.append({
            "id": argument_id,
            "position_id": position_id,
            "warrant": warrant,
            "is_supporting": is_supporting
        })
        return argument_id
    
    def add_evidence(self, evidence_id, argument_id, content, source=None):
        """Add evidence to the model"""
        self.evidence.append({
            "id": evidence_id,
            "argument_id": argument_id,
            "content": content,
            "source": source
        })
        return evidence_id
    
    def to_dict(self):
        """Convert the model to a dictionary"""
        return {
            "claims": self.claims,
            "positions": self.positions,
            "arguments": self.arguments,
            "evidence": self.evidence
        }

def generate_stable_id(prefix, text, index=None):
    """Generate a stable ID based on text content"""
    # Create a hash of the text
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    
    # Combine prefix, hash, and optional index
    if index is not None:
        return f"{prefix}_{text_hash}_{index}"
    else:
        return f"{prefix}_{text_hash}"

def process_text(text, document_id="sample", chunk_id="chunk1"):
    """Process text and extract arguments"""
    try:
        logger.info(f"Processing text for argument extraction ({len(text)} characters)")
        
        # Initialize Bedrock client
        bedrock = BedrockClient()
        
        # Initialize argument model
        argument_model = ArgumentModel()
        
        # Extract claims
        logger.info("Extracting claims...")
        claims = bedrock.extract_claims(text, chunk_id)
        logger.info(f"Extracted {len(claims)} claims")
        
        # For each claim, extract positions
        for i, claim_data in enumerate(claims):
            # Generate a stable claim ID
            claim_id = generate_stable_id("claim", claim_data["claim"], i)
            logger.info(f"Claim {i+1}: {claim_data['claim']}")
            
            # Add claim to model
            argument_model.add_claim(
                claim_id=claim_id,
                claim_text=claim_data["claim"],
                description=claim_data.get("description"),
                text_evidence=claim_data.get("text_evidence"),
                chunk_ids=claim_data.get("chunk_ids", [chunk_id])
            )
            
            # Extract positions
            logger.info(f"Extracting positions for claim: {claim_data['claim']}")
            positions = bedrock.extract_positions(text, claim_data["claim"])
            logger.info(f"Extracted {len(positions)} positions")
            
            # For each position, extract arguments
            for j, position in enumerate(positions):
                # Generate a stable position ID
                position_id = generate_stable_id("position", position["statement"], j)
                is_supporting = position.get("is_supporting", True)
                position_type = "supporting" if is_supporting else "rebutting"
                logger.info(f"{position_type.capitalize()} position {j+1}: {position['statement']}")
                
                # Add position to model
                argument_model.add_position(
                    position_id=position_id,
                    claim_id=claim_id,
                    statement=position["statement"],
                    description=position.get("description"),
                    is_supporting=is_supporting,
                    text_evidence=position.get("text_evidence")
                )
                
                # Extract supporting arguments for this position
                logger.info(f"Extracting supporting arguments for position...")
                supporting_args = bedrock.extract_arguments(
                    text, 
                    claim_data["claim"], 
                    position["statement"], 
                    is_supporting=True
                )
                logger.info(f"Extracted {len(supporting_args)} supporting arguments")
                
                # Add supporting arguments to model
                for k, arg in enumerate(supporting_args):
                    # Generate a stable argument ID
                    arg_id = generate_stable_id("arg", arg["warrant"], k)
                    logger.info(f"Supporting argument {k+1}: {arg['warrant']}")
                    
                    # Add argument to model
                    argument_model.add_argument(
                        argument_id=arg_id,
                        position_id=position_id,
                        warrant=arg["warrant"],
                        is_supporting=True
                    )
                    
                    # Add evidence
                    if "evidence" in arg:
                        evidence_id = generate_stable_id("evidence", arg["evidence"], k)
                        argument_model.add_evidence(
                            evidence_id=evidence_id,
                            argument_id=arg_id,
                            content=arg["evidence"],
                            source=chunk_id
                        )
                
                # Extract rebutting arguments for this position
                logger.info(f"Extracting rebutting arguments for position...")
                rebutting_args = bedrock.extract_arguments(
                    text, 
                    claim_data["claim"], 
                    position["statement"], 
                    is_supporting=False
                )
                logger.info(f"Extracted {len(rebutting_args)} rebutting arguments")
                
                # Add rebutting arguments to model
                for k, arg in enumerate(rebutting_args):
                    # Generate a stable argument ID
                    arg_id = generate_stable_id("arg", arg["warrant"], k + 100)  # Offset to avoid collisions
                    logger.info(f"Rebutting argument {k+1}: {arg['warrant']}")
                    
                    # Add argument to model
                    argument_model.add_argument(
                        argument_id=arg_id,
                        position_id=position_id,
                        warrant=arg["warrant"],
                        is_supporting=False
                    )
                    
                    # Add evidence
                    if "evidence" in arg:
                        evidence_id = generate_stable_id("evidence", arg["evidence"], k + 100)
                        argument_model.add_evidence(
                            evidence_id=evidence_id,
                            argument_id=arg_id,
                            content=arg["evidence"],
                            source=chunk_id
                        )
        
        return {
            "document_id": document_id,
            "arguments": argument_model.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise

def save_results(results, output_path):
    """Save results to a JSON file"""
    if not results:
        logger.warning("No results to save.")
        return False
        
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Results saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Extract claims and arguments from text')
    parser.add_argument('file_path', help='Path to the text file')
    parser.add_argument('--document-id', help='Unique identifier for the document', default=None)
    parser.add_argument('--chunk-id', help='Identifier for the chunk being processed', default="chunk1")
    parser.add_argument('--output', '-o', help='Output file for the extracted arguments', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Process the document
    file_path = Path(args.file_path)
    if not file_path.exists():
        logger.error(f"Error: File {file_path} not found")
        sys.exit(1)
    
    # Generate document ID if not provided
    document_id = args.document_id or file_path.stem
    
    try:
        # Read the text file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Process the text
        results = process_text(text, document_id, args.chunk_id)
        
        # Save results
        output_path = args.output or f"output/{document_id}_claims.json"
        save_results(results, output_path)
        
        logger.info("Argument extraction complete.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

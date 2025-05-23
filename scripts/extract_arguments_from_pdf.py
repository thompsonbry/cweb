#!/usr/bin/env python3

"""
Extract arguments from PDF using Bedrock Claude model
This script extracts argument structures from a PDF document using Amazon Bedrock
"""

import os
import sys
import json
import boto3
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentReader:
    """Read documents from various file formats"""
    
    @staticmethod
    def read_pdf_file(file_path):
        """Read text from a PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                return text
        except ImportError:
            print("PyPDF2 not available. Cannot process PDF files.")
            return None
        except Exception as e:
            print("Error processing PDF:", e)
            return None

class DocumentChunker:
    """Split documents into semantic chunks for processing"""
    
    @staticmethod
    def chunk_text(text, chunk_size=4000, overlap=200):
        """Split text into overlapping chunks of approximately chunk_size characters"""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Find a good breaking point near chunk_size
            end = min(start + chunk_size, text_length)
            
            # If we're not at the end, try to find a good breaking point
            if end < text_length:
                # Try to find a paragraph break
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break != -1 and paragraph_break > start + chunk_size // 2:
                    end = paragraph_break + 2
                else:
                    # Try to find a sentence break
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('! ', start, end),
                        text.rfind('? ', start, end)
                    )
                    if sentence_break != -1 and sentence_break > start + chunk_size // 2:
                        end = sentence_break + 2
            
            # Add the chunk
            chunks.append(text[start:end])
            
            # Move to next chunk with overlap
            start = max(start, end - overlap)
            
            # If we can't make progress, force a break
            if start >= end:
                start = end
        
        return chunks

class BedrockClient:
    """Client for interacting with Amazon Bedrock"""
    
    def __init__(self):
        """Initialize the Bedrock client"""
        region = os.environ.get("BEDROCK_REGION", "us-west-2")
        self.client = boto3.client('bedrock-runtime', region_name=region)
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def extract_issues(self, text):
        """Extract issues from text using Bedrock"""
        prompt = """
        Analyze the following text and identify the key issues, questions, or problems being discussed.
        For each issue:
        1. Formulate it as a clear, specific question
        2. Classify it as one of these types:
           - regular: A general issue with multiple possible answers
           - mutex: An issue where positions are mutually exclusive
           - hypothesis: A yes/no question with only two possible states
           - world: An issue where each position represents a different possible world
        3. Provide a brief description of the issue's context
        
        Format your response as a JSON array of objects with these fields:
        - id: A short identifier (e.g., "issue1")
        - question: The issue formulated as a question
        - issue_type: The classification (regular, mutex, hypothesis, world)
        - description: Brief context about the issue
        
        TEXT:
        {text}
        
        ISSUES (JSON format):
        """
        
        response = self._invoke_model(prompt.format(text=text))
        return self._extract_json(response)
    
    def extract_positions(self, text, issue):
        """Extract positions on an issue using Bedrock"""
        prompt = """
        Analyze the following text and identify the different positions or viewpoints on this issue:
        
        ISSUE: {issue}
        
        For each position:
        1. Formulate it as a clear, declarative statement (an answer to the issue)
        2. Provide a brief description or explanation of the position
        
        Format your response as a JSON array of objects with these fields:
        - id: A short identifier (e.g., "position1")
        - answer: The position as a declarative statement
        - description: Brief explanation of the position
        
        TEXT:
        {text}
        
        POSITIONS (JSON format):
        """
        
        response = self._invoke_model(prompt.format(text=text, issue=issue))
        return self._extract_json(response)
    
    def extract_arguments(self, text, issue, position, is_supporting=True):
        """Extract arguments for or against a position using Bedrock"""
        arg_type = "supporting" if is_supporting else "rebutting"
        supports_or_rebuts = "supports" if is_supporting else "rebuts"
        ARG_TYPE = "SUPPORTING" if is_supporting else "REBUTTING"
        
        prompt = """
        Analyze the following text and identify {arg_type} arguments for this position:
        
        ISSUE: {issue}
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
            issue=issue, 
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
            print(f"Error invoking Bedrock model: {e}")
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
                    
                print(f"Could not parse JSON from response: {response}")
                return []
        except Exception as e:
            print(f"Error extracting JSON: {e}")
            return []

class ArgumentModel:
    """Class to represent the HyperIBIS argument model"""
    
    def __init__(self):
        self.issues = []
        self.positions = []
        self.arguments = []
        self.evidence = []
        self.assessments = []
        self.relationships = []
    
    def add_issue(self, issue_id, question, issue_type="regular", description=None):
        """Add an issue to the model"""
        self.issues.append({
            "id": issue_id,
            "question": question,
            "issue_type": issue_type,
            "description": description
        })
        return issue_id
    
    def add_position(self, position_id, issue_id, answer, description=None):
        """Add a position to the model"""
        self.positions.append({
            "id": position_id,
            "issue_id": issue_id,
            "answer": answer,
            "description": description
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
            "issues": self.issues,
            "positions": self.positions,
            "arguments": self.arguments,
            "evidence": self.evidence,
            "assessments": self.assessments,
            "relationships": self.relationships
        }

def main():
    parser = argparse.ArgumentParser(description='Extract argument models from PDF documents')
    parser.add_argument('file_path', help='Path to the PDF file')
    parser.add_argument('--output', '-o', help='Output file for the extracted arguments', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Starting argument extraction process...")
    
    # Process the document
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: Document {file_path} not found")
        sys.exit(1)
    
    # Generate output path if not provided
    document_id = file_path.stem
    output_path = args.output or f"output/{document_id}_arguments.json"
    
    try:
        # Read the document
        print(f"Reading document: {file_path}")
        content = DocumentReader.read_pdf_file(file_path)
        if not content:
            print("Failed to read document content")
            sys.exit(1)
        
        print(f"Document length: {len(content)} characters")
        
        # Split into chunks
        print("Splitting document into chunks...")
        chunks = DocumentChunker.chunk_text(content)
        print(f"Document split into {len(chunks)} chunks")
        
        # Initialize Bedrock client
        bedrock = BedrockClient()
        
        # Initialize argument model
        argument_model = ArgumentModel()
        
        # Process first chunk only for testing
        print("\nProcessing first chunk for testing...")
        first_chunk = chunks[0]
        print(f"Chunk length: {len(first_chunk)} characters")
        
        # Extract issues
        print("\nExtracting issues...")
        issues = bedrock.extract_issues(first_chunk)
        print(f"Extracted {len(issues)} issues")
        
        # For each issue, extract positions
        for i, issue in enumerate(issues):
            issue_id = f"issue{i+1}"
            print(f"\nIssue {i+1}: {issue['question']}")
            
            # Add issue to model
            argument_model.add_issue(
                issue_id=issue_id,
                question=issue['question'],
                issue_type=issue.get('issue_type', 'regular'),
                description=issue.get('description')
            )
            
            # Extract positions
            print(f"Extracting positions for issue: {issue['question']}")
            positions = bedrock.extract_positions(first_chunk, issue['question'])
            print(f"Extracted {len(positions)} positions")
            
            # For each position, extract arguments
            for j, position in enumerate(positions):
                position_id = f"position{i+1}_{j+1}"
                print(f"\nPosition {j+1}: {position['answer']}")
                
                # Add position to model
                argument_model.add_position(
                    position_id=position_id,
                    issue_id=issue_id,
                    answer=position['answer'],
                    description=position.get('description')
                )
                
                # Extract supporting arguments
                print(f"Extracting supporting arguments...")
                supporting_args = bedrock.extract_arguments(
                    first_chunk, 
                    issue['question'], 
                    position['answer'], 
                    is_supporting=True
                )
                print(f"Extracted {len(supporting_args)} supporting arguments")
                
                # Add supporting arguments to model
                for k, arg in enumerate(supporting_args):
                    arg_id = f"arg{i+1}_{j+1}_sup{k+1}"
                    print(f"Supporting argument {k+1}: {arg['warrant']}")
                    
                    # Add argument to model
                    argument_model.add_argument(
                        argument_id=arg_id,
                        position_id=position_id,
                        warrant=arg['warrant'],
                        is_supporting=True
                    )
                    
                    # Add evidence
                    if 'evidence' in arg:
                        evidence_id = f"evidence{i+1}_{j+1}_sup{k+1}"
                        argument_model.add_evidence(
                            evidence_id=evidence_id,
                            argument_id=arg_id,
                            content=arg['evidence'],
                            source="Chunk 1"
                        )
                
                # Extract rebutting arguments
                print(f"Extracting rebutting arguments...")
                rebutting_args = bedrock.extract_arguments(
                    first_chunk, 
                    issue['question'], 
                    position['answer'], 
                    is_supporting=False
                )
                print(f"Extracted {len(rebutting_args)} rebutting arguments")
                
                # Add rebutting arguments to model
                for k, arg in enumerate(rebutting_args):
                    arg_id = f"arg{i+1}_{j+1}_reb{k+1}"
                    print(f"Rebutting argument {k+1}: {arg['warrant']}")
                    
                    # Add argument to model
                    argument_model.add_argument(
                        argument_id=arg_id,
                        position_id=position_id,
                        warrant=arg['warrant'],
                        is_supporting=False
                    )
                    
                    # Add evidence
                    if 'evidence' in arg:
                        evidence_id = f"evidence{i+1}_{j+1}_reb{k+1}"
                        argument_model.add_evidence(
                            evidence_id=evidence_id,
                            argument_id=arg_id,
                            content=arg['evidence'],
                            source="Chunk 1"
                        )
        
        # Save results
        print(f"\nSaving results to {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(argument_model.to_dict(), f, indent=2)
        
        print("Argument extraction complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""
Simple Argument Extractor

This script extracts argument models from documents using Amazon Bedrock directly.
It's a simplified version that doesn't depend on the GraphRAG toolkit.

Usage:
  uv run python scripts/simple_argument_extractor.py <file_path> [--output OUTPUT] [--verbose]
"""

import os
import sys
import json
import boto3
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_argument_extractor")

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
            logger.error("PyPDF2 not available. Cannot process PDF files.")
            return None
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None
    
    @staticmethod
    def read_file(file_path):
        """Read text from a file based on its extension"""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Error: File {file_path} not found")
            return None
            
        if path.suffix.lower() == '.pdf':
            return DocumentReader.read_pdf_file(file_path)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                return None

class DocumentChunker:
    """Split documents into semantic chunks for processing"""
    
    @staticmethod
    def chunk_text(text, chunk_size=3000, overlap=200):
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
        region = os.environ.get("AWS_REGION", "us-west-2")
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
    """Class to represent the HyperIBIS argument model"""
    
    def __init__(self):
        self.issues = []
        self.positions = []
        self.arguments = []
        self.evidence = []
    
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
            "evidence": self.evidence
        }

def process_document(file_path, document_id=None, verbose=False):
    """Process a document and extract arguments"""
    path = Path(file_path)
    if not document_id:
        document_id = path.stem
        
    try:
        logger.info(f"Processing document for argument extraction: {file_path}")
        
        # Read the document content
        content = DocumentReader.read_file(file_path)
        if not content:
            raise ValueError(f"Could not read content from {file_path}")
        
        logger.info(f"Document length: {len(content)} characters")
        
        # Split into chunks
        chunks = DocumentChunker.chunk_text(content)
        logger.info(f"Document split into {len(chunks)} chunks")
        
        # Initialize Bedrock client
        bedrock = BedrockClient()
        
        # Initialize argument model
        argument_model = ArgumentModel()
        
        # Process first chunk only for testing
        logger.info("Processing first chunk for testing...")
        first_chunk = chunks[0]
        logger.info(f"Chunk length: {len(first_chunk)} characters")
        
        # Extract issues
        logger.info("Extracting issues...")
        issues = bedrock.extract_issues(first_chunk)
        logger.info(f"Extracted {len(issues)} issues")
        
        # For each issue, extract positions
        for i, issue in enumerate(issues):
            issue_id = f"issue{i+1}"
            logger.info(f"Issue {i+1}: {issue['question']}")
            
            # Add issue to model
            argument_model.add_issue(
                issue_id=issue_id,
                question=issue['question'],
                issue_type=issue.get('issue_type', 'regular'),
                description=issue.get('description')
            )
            
            # Extract positions
            logger.info(f"Extracting positions for issue: {issue['question']}")
            positions = bedrock.extract_positions(first_chunk, issue['question'])
            logger.info(f"Extracted {len(positions)} positions")
            
            # For each position, extract arguments
            for j, position in enumerate(positions):
                position_id = f"position{i+1}_{j+1}"
                logger.info(f"Position {j+1}: {position['answer']}")
                
                # Add position to model
                argument_model.add_position(
                    position_id=position_id,
                    issue_id=issue_id,
                    answer=position['answer'],
                    description=position.get('description')
                )
                
                # Extract supporting arguments
                logger.info(f"Extracting supporting arguments...")
                supporting_args = bedrock.extract_arguments(
                    first_chunk, 
                    issue['question'], 
                    position['answer'], 
                    is_supporting=True
                )
                logger.info(f"Extracted {len(supporting_args)} supporting arguments")
                
                # Add supporting arguments to model
                for k, arg in enumerate(supporting_args):
                    arg_id = f"arg{i+1}_{j+1}_sup{k+1}"
                    logger.info(f"Supporting argument {k+1}: {arg['warrant']}")
                    
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
                logger.info(f"Extracting rebutting arguments...")
                rebutting_args = bedrock.extract_arguments(
                    first_chunk, 
                    issue['question'], 
                    position['answer'], 
                    is_supporting=False
                )
                logger.info(f"Extracted {len(rebutting_args)} rebutting arguments")
                
                # Add rebutting arguments to model
                for k, arg in enumerate(rebutting_args):
                    arg_id = f"arg{i+1}_{j+1}_reb{k+1}"
                    logger.info(f"Rebutting argument {k+1}: {arg['warrant']}")
                    
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
        
        return {
            "document_id": document_id,
            "arguments": argument_model.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
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
    parser = argparse.ArgumentParser(description='Extract argument models from documents')
    parser.add_argument('file_path', help='Path to the document file (PDF or text)')
    parser.add_argument('--document-id', help='Unique identifier for the document', default=None)
    parser.add_argument('--output', '-o', help='Output file for the extracted arguments', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Process the document
    file_path = Path(args.file_path)
    if not file_path.exists():
        logger.error(f"Error: Document {file_path} not found")
        sys.exit(1)
    
    # Generate document ID if not provided
    document_id = args.document_id or file_path.stem
    
    try:
        # Process the document
        results = process_document(file_path, document_id, args.verbose)
        
        # Save results
        output_path = args.output or f"output/{document_id}_arguments.json"
        save_results(results, output_path)
        
        logger.info("Argument extraction complete.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

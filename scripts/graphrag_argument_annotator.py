#!/usr/bin/env python3

"""
GraphRAG Argument Annotator

This script extends the GraphRAG toolkit to extract and annotate argument models from documents.
It integrates with the existing GraphRAG workflow and logs extracted arguments.

Usage:
  uv run python scripts/graphrag_argument_annotator.py <file_path> [--output OUTPUT] [--verbose]
"""

import os
import sys
import json
import boto3
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Try to use pysqlite3 if available
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
    print("Using pysqlite3 as sqlite3")
except ImportError:
    print("pysqlite3 not available, using system sqlite3")

# Now try to import GraphRAG toolkit components
try:
    from graphrag_toolkit.lexical_graph import LexicalGraphIndex, TenantId, GraphRAGConfig, set_logging_config
    from graphrag_toolkit.llm import LLMClient
    from llama_index.core import Document
    GRAPHRAG_AVAILABLE = True
    print("Successfully imported GraphRAG toolkit components")
except ImportError as e:
    print(f"Warning: Could not import GraphRAG toolkit: {e}")
    print(f"Make sure you're using Python 3.10+ with: uv run python scripts/graphrag_argument_annotator.py")
    GRAPHRAG_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("argument_annotator")

class ArgumentAnnotator:
    """
    Annotate documents with argument structures by integrating with GraphRAG workflow
    """
    
    def __init__(self):
        """Initialize the argument annotator"""
        if not GRAPHRAG_AVAILABLE:
            raise ImportError("GraphRAG toolkit not available")
            
        # Configure AWS region
        region = os.environ.get("AWS_REGION", "us-west-2")
        GraphRAGConfig.aws_region = region
        
        # Configure embedding model to match Neptune Analytics dimensions (1024)
        GraphRAGConfig.embed_model = "cohere.embed-english-v3"
        GraphRAGConfig.embed_dimensions = 1024
        
        # Configure LLM
        GraphRAGConfig.extraction_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
        GraphRAGConfig.response_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        # Set logging
        set_logging_config('INFO')
        
        try:
            # Initialize GraphRAG components with Neptune Analytics
            from graphrag_toolkit.lexical_graph.storage import GraphStoreFactory, VectorStoreFactory
            
            # Get Neptune Analytics configuration from environment
            neptune_graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
            if not neptune_graph_id:
                raise ValueError("NEPTUNE_ANALYTICS_GRAPH_ID environment variable is required")
                
            neptune_region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
            
            # Set AWS region for GraphRAG
            GraphRAGConfig.aws_region = neptune_region
            
            # Create connection string
            neptune_connection = f"neptune-graph://{neptune_graph_id}"
            logger.info(f"Connecting to Neptune Analytics: {neptune_connection}")
            
            # Create Neptune Analytics stores using factory methods
            graph_store = GraphStoreFactory.for_graph_store(neptune_connection)
            vector_store = VectorStoreFactory.for_vector_store(neptune_connection)
            
            # Create output directory
            output_dir = "/tmp/graphrag_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize with explicit parameters
            self.graph_index = LexicalGraphIndex(
                extraction_dir=output_dir,
                graph_store=graph_store,
                vector_store=vector_store
            )
            
            # Initialize LLM client for argument extraction
            self.llm_client = LLMClient()
            
            logger.info("Successfully initialized GraphRAG components with Neptune Analytics")
            
        except Exception as e:
            logger.error(f"Error initializing ArgumentAnnotator: {e}")
            raise
    
    def process_document(self, file_path, document_id=None):
        """Process a document and extract arguments"""
        path = Path(file_path)
        if not document_id:
            document_id = path.stem
            
        try:
            logger.info(f"Processing document for argument extraction: {file_path}")
            
            # Read the document content
            content = self._read_document(file_path)
            if not content:
                raise ValueError(f"Could not read content from {file_path}")
            
            # Create a Document object
            doc = Document(text=content, metadata={"source": str(path), "document_id": document_id})
            
            # Extract and build the graph using GraphRAG's standard pipeline
            # This will handle chunking, embedding, and graph construction
            logger.info("Running standard GraphRAG extraction pipeline")
            self.graph_index.extract_and_build([doc], show_progress=True)
            
            # Now extract arguments from the document chunks
            # We'll use the chunks that GraphRAG created
            logger.info("Extracting arguments from document chunks")
            arguments = self._extract_arguments_from_chunks(doc)
            
            # Log the extracted arguments
            logger.info(f"Extracted {len(arguments.get('issues', []))} issues with arguments")
            
            return {
                "document_id": document_id,
                "arguments": arguments
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def _read_document(self, file_path):
        """Read document content from file"""
        path = Path(file_path)
        
        try:
            if path.suffix.lower() == '.pdf':
                import PyPDF2
                with open(path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n\n"
                    return text
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading document: {e}")
            return None
    
    def _extract_arguments_from_chunks(self, document):
        """Extract arguments from document chunks"""
        # Get the document text
        text = document.text
        
        # Use a smaller chunk size for argument extraction to avoid memory issues
        # This is separate from GraphRAG's chunking for graph construction
        chunks = self._chunk_text(text, chunk_size=3000, overlap=200)
        logger.info(f"Split document into {len(chunks)} chunks for argument extraction")
        
        # Process each chunk to extract arguments
        all_issues = []
        all_positions = []
        all_arguments = []
        
        # Process only the first chunk for now to avoid resource issues
        # In a full implementation, we would process all chunks and merge results
        logger.info("Processing first chunk for argument extraction")
        first_chunk = chunks[0] if chunks else text[:3000]
        
        # Extract issues from the first chunk
        issues = self._extract_issues(first_chunk)
        logger.info(f"Extracted {len(issues)} issues from first chunk")
        
        # For each issue, extract positions and arguments
        for issue in issues:
            issue_id = issue['id']
            all_issues.append(issue)
            
            # Extract positions for this issue
            positions = self._extract_positions(first_chunk, issue['question'])
            logger.info(f"Extracted {len(positions)} positions for issue: {issue['question']}")
            
            # Add issue_id to each position
            for position in positions:
                position['issue_id'] = issue_id
                all_positions.append(position)
                
                # Extract supporting arguments
                supporting_args = self._extract_arguments(
                    first_chunk, 
                    issue['question'], 
                    position['answer'], 
                    is_supporting=True
                )
                logger.info(f"Extracted {len(supporting_args)} supporting arguments for position: {position['answer']}")
                
                # Add position_id and is_supporting to each argument
                for arg in supporting_args:
                    arg['position_id'] = position['id']
                    arg['is_supporting'] = True
                    all_arguments.append(arg)
                
                # Extract rebutting arguments
                rebutting_args = self._extract_arguments(
                    first_chunk, 
                    issue['question'], 
                    position['answer'], 
                    is_supporting=False
                )
                logger.info(f"Extracted {len(rebutting_args)} rebutting arguments for position: {position['answer']}")
                
                # Add position_id and is_supporting to each argument
                for arg in rebutting_args:
                    arg['position_id'] = position['id']
                    arg['is_supporting'] = False
                    all_arguments.append(arg)
        
        # Return the extracted argument model
        return {
            "issues": all_issues,
            "positions": all_positions,
            "arguments": all_arguments
        }
    
    def _chunk_text(self, text, chunk_size=3000, overlap=200):
        """Split text into overlapping chunks"""
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
    
    def _extract_issues(self, text):
        """Extract issues from text using LLM"""
        try:
            # Create a prompt for the LLM to identify issues
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
            
            # Call the LLM to extract issues
            response = self.llm_client.complete(prompt.format(text=text))
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                issues = json.loads(json_str)
                return issues
            else:
                # Try to extract JSON with more lenient pattern
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    issues = json.loads(json_str)
                    return issues
                
                logger.warning(f"Could not parse issues from LLM response: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting issues: {e}")
            return []
    
    def _extract_positions(self, text, issue):
        """Extract positions on an issue using LLM"""
        try:
            # Create a prompt for the LLM to identify positions
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
            
            # Call the LLM to extract positions
            response = self.llm_client.complete(prompt.format(text=text, issue=issue))
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                positions = json.loads(json_str)
                return positions
            else:
                # Try to extract JSON with more lenient pattern
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    positions = json.loads(json_str)
                    return positions
                    
                logger.warning(f"Could not parse positions from LLM response: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting positions: {e}")
            return []
    
    def _extract_arguments(self, text, issue, position, is_supporting=True):
        """Extract arguments for or against a position using LLM"""
        try:
            # Create a prompt for the LLM to identify arguments
            arg_type = "supporting" if is_supporting else "rebutting"
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
            
            supports_or_rebuts = "supports" if is_supporting else "rebuts"
            ARG_TYPE = "SUPPORTING" if is_supporting else "REBUTTING"
            
            # Call the LLM to extract arguments
            response = self.llm_client.complete(prompt.format(
                text=text, 
                issue=issue, 
                position=position, 
                arg_type=arg_type,
                supports_or_rebuts=supports_or_rebuts,
                ARG_TYPE=ARG_TYPE
            ))
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                arguments = json.loads(json_str)
                return arguments
            else:
                # Try to extract JSON with more lenient pattern
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    arguments = json.loads(json_str)
                    return arguments
                    
                logger.warning(f"Could not parse arguments from LLM response: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting arguments: {e}")
            return []
    
    def save_results(self, results, output_path):
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
    parser = argparse.ArgumentParser(description='Extract and annotate argument models from documents')
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
        # Create argument annotator
        annotator = ArgumentAnnotator()
        
        # Process the document
        results = annotator.process_document(file_path, document_id)
        
        if args.verbose:
            logger.info(f"Document processed: {document_id}")
        
        # Save results
        output_path = args.output or f"output/{document_id}_arguments.json"
        annotator.save_results(results, output_path)
        
        logger.info("Argument extraction and annotation complete.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

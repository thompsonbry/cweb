#!/usr/bin/env python3

"""
Test script for argument extraction
This simplified script tests the core functionality of argument extraction
without the full GraphRAG integration to identify any issues.
"""

import os
import sys
import json
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
            print(f"Error processing PDF: {e}")
            return None

class DocumentChunker:
    """Split documents into semantic chunks for processing"""
    
    @staticmethod
    def chunk_text(text, chunk_size=2000, overlap=200):
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

def extract_issues_mock(text):
    """Mock function to simulate issue extraction"""
    print("Extracting issues from text chunk...")
    print(f"Text length: {len(text)} characters")
    
    # In a real implementation, this would call an LLM
    # For testing, we'll return a mock result
    return [
        {
            "id": "issue1",
            "question": "How can metacognitive processes improve decision-making?",
            "issue_type": "regular",
            "description": "This issue explores the role of metacognition in enhancing decision-making capabilities."
        }
    ]

def extract_positions_mock(text, issue):
    """Mock function to simulate position extraction"""
    print(f"Extracting positions for issue: {issue}")
    
    # In a real implementation, this would call an LLM
    # For testing, we'll return mock results
    return [
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

def extract_arguments_mock(text, issue, position, is_supporting=True):
    """Mock function to simulate argument extraction"""
    arg_type = "supporting" if is_supporting else "rebutting"
    print(f"Extracting {arg_type} arguments for position: {position}")
    
    # In a real implementation, this would call an LLM
    # For testing, we'll return mock results
    if is_supporting:
        return [
            {
                "id": "arg1",
                "warrant": "Research shows metacognitive monitoring improves decision quality",
                "evidence": "Studies have demonstrated that individuals who engage in metacognitive monitoring make fewer errors in complex decision tasks."
            }
        ]
    else:
        return [
            {
                "id": "arg2",
                "warrant": "Metacognitive processes can lead to overthinking",
                "evidence": "In time-critical situations, excessive metacognitive reflection can delay necessary action."
            }
        ]

def main():
    # Get the test document
    file_path = Path("tests/data/wcnn_1995.pdf")
    if not file_path.exists():
        print(f"Error: Document {file_path} not found")
        sys.exit(1)
    
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
    
    # Process first chunk only for testing
    print("\nProcessing first chunk for testing...")
    first_chunk = chunks[0]
    print(f"Chunk length: {len(first_chunk)} characters")
    print(f"Chunk preview: {first_chunk[:200]}...")
    
    # Extract issues
    issues = extract_issues_mock(first_chunk)
    print(f"Extracted {len(issues)} issues")
    
    # For each issue, extract positions
    for issue in issues:
        print(f"\nIssue: {issue['question']}")
        
        positions = extract_positions_mock(first_chunk, issue['question'])
        print(f"Extracted {len(positions)} positions")
        
        for position in positions:
            print(f"\nPosition: {position['answer']}")
            
            # Extract supporting arguments
            supporting_args = extract_arguments_mock(first_chunk, issue['question'], position['answer'], is_supporting=True)
            print(f"Extracted {len(supporting_args)} supporting arguments")
            
            # Extract rebutting arguments
            rebutting_args = extract_arguments_mock(first_chunk, issue['question'], position['answer'], is_supporting=False)
            print(f"Extracted {len(rebutting_args)} rebutting arguments")
    
    print("\nTest completed successfully")

if __name__ == "__main__":
    main()

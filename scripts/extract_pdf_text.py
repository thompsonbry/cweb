#!/usr/bin/env python3

"""
Extract text from PDF files using pdfplumber
"""

import os
import sys
import pdfplumber
import argparse
from pathlib import Path

def extract_text_from_pdf(pdf_path, output_path=None):
    """Extract text from a PDF file"""
    try:
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from each page
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
            
            # Save to file if output path is provided
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Text extracted and saved to {output_path}")
            
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF files')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output', '-o', help='Output file for the extracted text')
    
    args = parser.parse_args()
    
    # Process the PDF file
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: File {pdf_path} not found")
        sys.exit(1)
    
    # Generate output path if not provided
    output_path = args.output
    if not output_path:
        output_path = pdf_path.with_suffix('.txt')
    
    # Extract text
    extract_text_from_pdf(pdf_path, output_path)

if __name__ == "__main__":
    main()

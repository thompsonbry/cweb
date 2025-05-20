#!/usr/bin/env python3
"""
Extract text from a PDF file using PyMuPDF (fitz)
"""

import sys
import os
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyMuPDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    text = ""
    
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
            
        # Close the document
        doc.close()
        
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise
        
    return text

def main():
    """
    Main function.
    """
    if len(sys.argv) != 3:
        print("Usage: python3 extract_pdf_text.py <pdf_path> <output_path>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' does not exist.")
        sys.exit(1)
        
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Write the extracted text to the output file
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
            
        print(f"Text extracted successfully and saved to '{output_path}'.")
        
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

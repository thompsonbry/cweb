#!/usr/bin/env python3

"""
Extract a small sample from a PDF document for testing
"""

import sys
from pathlib import Path

def extract_sample(file_path, output_path, max_chars=2000):
    """Extract a small sample from a PDF document"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
                if len(text) >= max_chars:
                    break
            
            # Truncate to max_chars
            text = text[:max_chars]
            
            # Write to output file
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write(text)
            
            print(f"Extracted {len(text)} characters to {output_path}")
            return True
    except Exception as e:
        print(f"Error extracting sample: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_small_sample.py <input_pdf> <output_txt> [max_chars]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    
    success = extract_sample(input_path, output_path, max_chars)
    sys.exit(0 if success else 1)

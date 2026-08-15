import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from datetime import date 
import pdfplumber
from schemas import DocumentMetadata

def extract_test(path: str = "sample.pdf") -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_tables(path: str = "sample.pdf") -> list:
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return tables

def extract_images_to_text(path: str = "sample.pdf") -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for image in page.images:
                img = Image.open(image["path"])
                text += pytesseract.image_to_string(img)
    return text

def main():
    load_dotenv()
    client = genai.Client()
    sample_pdf_path = "sample.pdf"
    
    # 1. Extract the raw pieces
    extracted_text = extract_test(sample_pdf_path)
    extracted_tables = extract_tables(sample_pdf_path)
    extracted_images = extract_images_to_text(sample_pdf_path)
    
    # 2. Structure the final prompt context
    final_context = f"--- Document Text ---\n{extracted_text}\n"
    
    # Safely format tables into a pseudo-Markdown grid
    if extracted_tables:
        final_context += "\n--- Document Tables ---\n"
        for i, table in enumerate(extracted_tables):
            final_context += f"\nTable {i + 1}:\n"
            for row in table:
                # Handle NoneTypes and remove unexpected newlines inside cells
                clean_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                final_context += " | ".join(clean_row) + "\n"

    # Append image text directly (no for-loop needed)
    if extracted_images.strip():
        final_context += f"\n--- Text Extracted From Images ---\n{extracted_images}\n"
        
    # 3. Send to Gemini
    response = client.models.generate_content(
        model='gemini-3.7-flash',
        contents=f"Extract the metadata from the following document:\n\n{final_context}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DocumentMetadata,
            temperature=0.0
        )
    )
    
    structured_doc = response.parsed
    print(structured_doc)

if __name__ == "__main__":
    main()    

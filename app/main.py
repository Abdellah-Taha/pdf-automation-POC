import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from datetime import date 
import pdfplumber
from PIL import Image          # FIX: Added missing Image import
import pytesseract             # FIX: Added missing pytesseract import
from schemas import DocumentMetadata
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

def upload_to_drive(local_file_path: str, structured_data):
    # Fetch the shared folder ID from your .env file
    shared_root_id = os.getenv("SHARED_ROOT_FOLDER_ID")
    if not shared_root_id:
        raise ValueError("SHARED_ROOT_FOLDER_ID is missing from the .env file.")

    # 1. Authenticate with Google Drive
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)

    folder_name = structured_data.destination_folder
    file_name = structured_data.suggested_filename

    # 2. Check if the destination folder exists INSIDE the shared root folder
    query = f"name='{folder_name}' and '{shared_root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        # Create the folder INSIDE the shared root folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [shared_root_id] # This links the new folder to your shared Drive
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"Created new folder '{folder_name}' with ID: {folder_id}")
    else:
        # Use existing folder
        folder_id = items[0]['id']
        print(f"Found existing folder '{folder_name}' with ID: {folder_id}")

    # 3. Check if the file already exists in that specific newly found/created folder
    file_query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    file_results = service.files().list(q=file_query, fields="files(id, name)").execute()
    existing_files = file_results.get('files', [])

    # Prepare the media file for upload
    media = MediaFileUpload(local_file_path, mimetype='application/pdf', resumable=True)

    # 4. Upload or Update the file
    if existing_files:
        existing_file_id = existing_files[0]['id']
        uploaded_file = service.files().update(
            fileId=existing_file_id,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Updated existing file '{file_name}' with ID: {existing_file_id}")
    else:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Created new file '{file_name}' with ID: {uploaded_file.get('id')}")



def extract_test(path: str = "sample.pdf") -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_tables(path: str = "sample.pdf") -> list:
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_tables()
            if extracted:
                tables.extend(extracted)
    return tables

def extract_images_to_text(path: str = "sample.pdf") -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for image in page.images:
                # Requires a valid image path extraction depending on pdfplumber version
                # If image["path"] fails, standard OCR on the whole page might be needed
                try:
                    img = Image.open(image["path"])
                    text += pytesseract.image_to_string(img)
                except Exception as e:
                    pass 
    return text

def main():
    load_dotenv()
    client = genai.Client()
    sample_pdf_path = "sample.pdf"
    
    print("Extracting document content...")
    # 1. Extract the raw pieces
    extracted_text = extract_test(sample_pdf_path)
    extracted_tables = extract_tables(sample_pdf_path)
    extracted_images = extract_images_to_text(sample_pdf_path)
    
    final_context = f"--- Document Text ---\n{extracted_text}\n"
    
    if extracted_tables:
        final_context += "\n--- Document Tables ---\n"
        for i, table in enumerate(extracted_tables):
            final_context += f"\nTable {i + 1}:\n"
            for row in table:
                clean_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                final_context += " | ".join(clean_row) + "\n"

    if extracted_images.strip():
        final_context += f"\n--- Text Extracted From Images ---\n{extracted_images}\n"
        
    print("Calling Gemini API...")
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
    print("\n--- Extracted Metadata ---")
    print(structured_doc)
    
    print("\n--- Uploading to Google Drive ---")
    # FIX: Actually call the upload function to execute the Drive API logic
    upload_to_drive(sample_pdf_path, structured_doc)

if __name__ == "__main__":
    main()
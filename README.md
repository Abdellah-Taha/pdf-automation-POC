# PDF Automation POC

This Proof of Concept (POC) automates the extraction of structured metadata from PDF documents using the Gemini API. It parses PDF text and tables, enforces a strict JSON output using Pydantic, and can be extended to automatically upload the file to Google Drive based on the extracted metadata.

## Setup Instructions

1. **Install dependencies:**
   This project uses `uv` for dependency management. 
   ```bash
   uv sync
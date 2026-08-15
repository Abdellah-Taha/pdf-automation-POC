# PDF Automation POC

This Proof of Concept (POC) automates the extraction of structured metadata from PDF documents using the Gemini API. It parses PDF text and tables, enforces a strict JSON output using Pydantic, and can be extended to automatically upload the file to Google Drive based on the extracted metadata.

## Setup Instructions

1. **Install dependencies:**
   This project uses `uv` for dependency management. 
   ```bash
   uv sync

2. **To run this POC locally, you will need:**
    1. A `.env` file in the `/app` directory containing `GEMINI_API_KEY=...`
    2. An OAuth 2.0 Client ID file named `credentials.json` in the `/app` directory to enable Google Drive uploads.
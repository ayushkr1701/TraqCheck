# TraqCheck Backend

Flask-based backend for TraqCheck candidate management system.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env` file with Azure OpenAI credentials

4. Run application:
```bash
python app.py
```

## API Documentation

Base URL: `http://localhost:5000/api`

### Endpoints

#### Upload Resume
```
POST /candidates/upload
Content-Type: multipart/form-data

Body: { file: <resume.pdf> }

Response: {
  "candidate_id": "uuid",
  "message": "Resume uploaded successfully",
  "extraction_status": "completed"
}
```

#### List Candidates
```
GET /candidates?page=1&limit=10&status=completed

Response: {
  "candidates": [...],
  "total": 50,
  "page": 1,
  "limit": 10,
  "pages": 5
}
```

#### Get Candidate
```
GET /candidates/:id

Response: {
  "id": "uuid",
  "extracted_data": {...},
  "document_requests": [...],
  "submitted_documents": [...]
}
```

#### Request Documents
```
POST /candidates/:id/request-documents

Response: {
  "request_id": "uuid",
  "request_preview": "Generated message...",
  "status": "sent"
}
```

#### Submit Documents
```
POST /candidates/:id/submit-documents
Content-Type: multipart/form-data

Body: {
  file: <document.pdf>,
  document_type: "pan" | "aadhaar"
}

Response: {
  "document_id": "uuid",
  "message": "Document uploaded successfully"
}
```

## Services

### ResumeParser
Extracts text from PDF and DOCX files

### AIExtractor
Uses Azure OpenAI to extract structured data with confidence scores

### AIAgent
Generates personalized document request messages using AI

### FileStorage
Handles secure file upload and storage

## Database Models

- **Candidate**: Resume metadata and status
- **ExtractedData**: AI-extracted information with confidence scores
- **DocumentRequest**: Generated request messages
- **SubmittedDocument**: Uploaded identity documents

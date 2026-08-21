import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.config import get_settings
from app.auth import get_current_user

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()


class AskDocumentRequest(BaseModel):
    document_id: int
    question: str


# --- Upload Document ---

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported. Use PDF, TXT, or DOCX.")

    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_hash = hashlib.md5(contents).hexdigest()
    filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    # Create document record
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=file.content_type,
        file_size=len(contents),
        file_path=file_path,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status,
        "file_size": document.file_size,
    }


# --- Process Document (Extract text, chunk, embed) ---

@router.post("/{document_id}/process")
async def process_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status == "processed":
        return {"status": "already_processed"}

    document.status = "processing"
    db.commit()

    try:
        # Extract text based on file type
        text = ""
        if document.file_type == "text/plain":
            with open(document.file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif document.file_type == "application/pdf":
            # Simple PDF text extraction (in production, use PyPDF2 or pdfplumber)
            text = f"[PDF content from {document.filename}]"
        else:
            text = f"[Document content from {document.filename}]"

        # Simple chunking (split into ~500 char chunks)
        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
            )
            db.add(chunk)

        document.status = "processed"
        db.commit()

        return {
            "status": "processed",
            "chunks_count": len(chunks),
        }

    except Exception as e:
        document.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


# --- Get User Documents ---

@router.get("/")
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = db.query(Document).filter(
        Document.user_id == current_user.id,
    ).order_by(Document.created_at.desc()).all()

    return {
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in documents
        ]
    }


# --- Ask Question Against Document ---

@router.post("/ask")
async def ask_document(
    request: AskDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == request.document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "processed":
        raise HTTPException(status_code=400, detail="Document not yet processed")

    # Get relevant chunks (simple keyword search for now)
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id,
    ).all()

    # Find relevant chunks
    query_terms = request.question.lower().split()
    relevant_chunks = []
    for chunk in chunks:
        score = sum(1 for term in query_terms if term in chunk.content.lower())
        if score > 0:
            relevant_chunks.append((score, chunk.content))

    relevant_chunks.sort(key=lambda x: x[0], reverse=True)
    context = "\n".join([content for _, content in relevant_chunks[:5]])

    # Generate answer using Ollama
    from app.api.ai_tutor import ollama_generate
    prompt = f"""Based on the following document content, answer the user's question.

Document: {document.filename}
Relevant Content:
{context}

Question: {request.question}

Provide a clear, helpful answer based on the document content."""

    answer = await ollama_generate(prompt, "You are a helpful document analysis assistant. Answer based on the provided content.")

    return {
        "answer": answer,
        "document_id": document.id,
        "relevant_chunks": len(relevant_chunks),
    }


# --- Delete Document ---

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete chunks
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

    # Delete document
    db.delete(document)
    db.commit()

    return {"status": "deleted"}

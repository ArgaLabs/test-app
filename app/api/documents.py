"""Document parsing endpoint using Unstructured."""
from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.services.document_parser import parse_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/parse")
async def parse(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or "document"
    content_type = file.content_type or "application/octet-stream"
    elements = await parse_document(filename, content, content_type)
    return {"filename": filename, "elements": elements, "count": len(elements)}

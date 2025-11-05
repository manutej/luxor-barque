"""
BARQUE Microservice API

FastAPI-based REST API for PDF generation and email delivery.
Wraps existing BARQUE CLI functionality without modifying core code.

Usage:
    uvicorn barque_service:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum
import tempfile
import shutil
import uuid
from datetime import datetime

# Import BARQUE core modules (CLI untouched)
from barque.core.generator import PDFGenerator, GenerationResult
from barque.core.config import BarqueConfig
from barque.core.email import EmailSender, EmailConfig, EmailProvider, EmailMessage

# API Version
API_VERSION = "1.0.0"
BARQUE_VERSION = "2.0.0"

# FastAPI app
app = FastAPI(
    title="BARQUE Microservice API",
    description="Multi-modal document orchestration with dual-theme PDF generation and email delivery",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Pydantic Models for API
class ThemeEnum(str, Enum):
    """PDF theme options"""
    light = "light"
    dark = "dark"
    both = "both"


class ProviderEnum(str, Enum):
    """Email provider options"""
    resend = "resend"
    smtp = "smtp"


class GeneratePDFRequest(BaseModel):
    """Request model for PDF generation"""
    markdown_content: str = Field(..., description="Markdown content to convert to PDF")
    theme: ThemeEnum = Field(ThemeEnum.both, description="PDF theme selection")
    filename: Optional[str] = Field(None, description="Optional filename (default: auto-generated)")

    class Config:
        json_schema_extra = {
            "example": {
                "markdown_content": "# Report Title\n\nContent here...",
                "theme": "both",
                "filename": "my-report"
            }
        }


class SendEmailRequest(BaseModel):
    """Request model for sending email with attachments"""
    to: List[EmailStr] = Field(..., description="Recipient email addresses")
    subject: str = Field(..., description="Email subject")
    body: Optional[str] = Field(None, description="Email body (markdown supported)")
    from_email: Optional[EmailStr] = Field(None, description="Sender email address")
    cc: Optional[List[EmailStr]] = Field(None, description="CC recipients")
    bcc: Optional[List[EmailStr]] = Field(None, description="BCC recipients")
    provider: ProviderEnum = Field(ProviderEnum.resend, description="Email provider")

    class Config:
        json_schema_extra = {
            "example": {
                "to": ["user@example.com"],
                "subject": "Monthly Report",
                "body": "# Report Summary\n\nPlease review attached.",
                "provider": "resend"
            }
        }


class GenerateAndSendRequest(BaseModel):
    """Request model for generate PDF and send via email"""
    markdown_content: str = Field(..., description="Markdown content")
    to: List[EmailStr] = Field(..., description="Recipient email addresses")
    subject: Optional[str] = Field(None, description="Email subject (auto-generated if not provided)")
    theme: ThemeEnum = Field(ThemeEnum.both, description="PDF theme")
    body: Optional[str] = Field(None, description="Email body")
    from_email: Optional[EmailStr] = Field(None, description="Sender email")
    provider: ProviderEnum = Field(ProviderEnum.resend, description="Email provider")

    class Config:
        json_schema_extra = {
            "example": {
                "markdown_content": "# Monthly Report\n\nQ4 Results...",
                "to": ["team@company.com"],
                "subject": "Q4 Report",
                "theme": "both",
                "provider": "resend"
            }
        }


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Health check endpoint
@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint - API information"""
    return APIResponse(
        success=True,
        message="BARQUE Microservice API",
        data={
            "version": API_VERSION,
            "barque_version": BARQUE_VERSION,
            "docs": "/docs",
            "health": "/health"
        }
    )


@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="Service healthy",
        data={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": API_VERSION
        }
    )


@app.post("/generate", response_model=APIResponse)
async def generate_pdf(request: GeneratePDFRequest, background_tasks: BackgroundTasks):
    """
    Generate PDF from markdown content

    Returns URLs to download generated PDFs
    """
    try:
        # Create temporary file for markdown
        temp_dir = Path(tempfile.mkdtemp())
        job_id = str(uuid.uuid4())[:8]
        filename = request.filename or f"document-{job_id}"
        md_file = temp_dir / f"{filename}.md"

        # Write markdown content
        md_file.write_text(request.markdown_content, encoding='utf-8')

        # Generate PDF using BARQUE core
        config = BarqueConfig()
        config.output_dir = temp_dir / "output"
        generator = PDFGenerator(config)

        result = generator.generate(
            input_file=md_file,
            theme=request.theme.value
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Prepare response with file URLs
        files = []
        for pdf_path in result.files:
            files.append({
                "filename": Path(pdf_path).name,
                "url": f"/download/{job_id}/{Path(pdf_path).name}",
                "size_bytes": Path(pdf_path).stat().st_size
            })

        # Schedule cleanup after some time
        background_tasks.add_task(cleanup_temp_dir, temp_dir, delay=3600)

        return APIResponse(
            success=True,
            message="PDF generated successfully",
            data={
                "job_id": job_id,
                "files": files,
                "metadata": result.metadata
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-email", response_model=APIResponse)
async def send_email(request: SendEmailRequest, files: List[UploadFile] = File(...)):
    """
    Send email with file attachments

    Upload files and specify email details
    """
    try:
        # Create temporary directory for attachments
        temp_dir = Path(tempfile.mkdtemp())
        attachments = []

        # Save uploaded files
        for file in files:
            file_path = temp_dir / file.filename
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            attachments.append(file_path)

        # Configure email
        email_config = EmailConfig(
            provider=EmailProvider.RESEND if request.provider == ProviderEnum.resend else EmailProvider.SMTP,
            from_email=request.from_email
        )

        # Create message
        message = EmailMessage(
            to=request.to,
            subject=request.subject,
            body=request.body or "Please find attached files.",
            attachments=attachments,
            from_email=request.from_email,
            cc=request.cc,
            bcc=request.bcc
        )

        # Send email using BARQUE core
        sender = EmailSender(email_config)
        result = sender.send(message)

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return APIResponse(
            success=True,
            message="Email sent successfully",
            data={
                "recipients": result.recipients,
                "attachments": [f.name for f in attachments]
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-and-send", response_model=APIResponse)
async def generate_and_send(request: GenerateAndSendRequest, background_tasks: BackgroundTasks):
    """
    Generate PDF from markdown and send via email (convenience endpoint)

    Combines /generate and /send-email into single operation
    """
    try:
        # Create temporary file for markdown
        temp_dir = Path(tempfile.mkdtemp())
        job_id = str(uuid.uuid4())[:8]
        md_file = temp_dir / f"document-{job_id}.md"

        # Write markdown content
        md_file.write_text(request.markdown_content, encoding='utf-8')

        # Generate PDF
        config = BarqueConfig()
        config.output_dir = temp_dir / "output"
        generator = PDFGenerator(config)

        gen_result = generator.generate(
            input_file=md_file,
            theme=request.theme.value
        )

        if not gen_result.success:
            raise HTTPException(status_code=500, detail=gen_result.error)

        # Prepare email
        pdf_files = [Path(f) for f in gen_result.files]
        subject = request.subject or f"Report: {gen_result.metadata.get('title', 'Document')}"

        # Configure email
        email_config = EmailConfig(
            provider=EmailProvider.RESEND if request.provider == ProviderEnum.resend else EmailProvider.SMTP,
            from_email=request.from_email
        )

        # Send email
        sender = EmailSender(email_config)
        email_result = sender.send_pdf_report(
            to=request.to,
            subject=subject,
            pdf_files=pdf_files,
            body_template=request.body,
            from_email=request.from_email
        )

        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_dir, temp_dir, delay=600)

        if not email_result.success:
            raise HTTPException(status_code=500, detail=email_result.error)

        return APIResponse(
            success=True,
            message="PDF generated and email sent successfully",
            data={
                "job_id": job_id,
                "recipients": email_result.recipients,
                "pdf_files": [f.name for f in pdf_files],
                "metadata": gen_result.metadata
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """
    Download generated PDF file

    Note: Files are temporarily available after generation
    """
    # In production, use proper file storage (S3, etc.)
    temp_base = Path(tempfile.gettempdir())
    file_path = temp_base / job_id / "output" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found or expired")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )


# Helper functions
async def cleanup_temp_dir(directory: Path, delay: int = 0):
    """Cleanup temporary directory after delay"""
    import asyncio
    if delay > 0:
        await asyncio.sleep(delay)

    if directory.exists():
        shutil.rmtree(directory, ignore_errors=True)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

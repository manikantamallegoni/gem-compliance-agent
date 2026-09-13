from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from agent.config import settings
from agent.router import router as agent_router
from agent.schema import EvaluationRequest
from agent.compliance_agent import GeMComplianceAgent

# Single FastAPI initialization instance
app = FastAPI(title=settings.project_name)
agent = GeMComplianceAgent()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include external routers if needed
app.include_router(agent_router)


# Audit Endpoint (Handles Multi-file Ingestion)
@app.post("/audit")
async def run_audit(
        tender_id: str = Form(...),
        bidder_name: str = Form(...),
        tender_requirements: str = Form(...),
        file: UploadFile = File(...),
        pan_file: Optional[UploadFile] = File(None),
        gst_file: Optional[UploadFile] = File(None),
        financial_file: Optional[UploadFile] = File(None),
):
    # Read main bid document
    content = await file.read()
    combined_text = f"--- MAIN BID DOCUMENT ---\n{content.decode('utf-8', errors='ignore')}\n\n"

    # Append optional uploaded documents
    if pan_file and pan_file.filename:
        pan_content = await pan_file.read()
        combined_text += f"--- PAN DOCUMENT ---\n{pan_content.decode('utf-8', errors='ignore')}\n\n"

    if gst_file and gst_file.filename:
        gst_content = await gst_file.read()
        combined_text += f"--- GST CERTIFICATE ---\n{gst_content.decode('utf-8', errors='ignore')}\n\n"

    if financial_file and financial_file.filename:
        fin_content = await financial_file.read()
        combined_text += f"--- FINANCIAL PROOF ---\n{fin_content.decode('utf-8', errors='ignore')}\n\n"

    request = EvaluationRequest(
        tender_id=tender_id,
        bidder_name=bidder_name,
        tender_requirements=tender_requirements,
        bidder_document_text=combined_text,
    )

    return agent.evaluate(request)


# Locate index.html inside frontend folder
CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parent.parent
INDEX_FILE = BASE_DIR / "frontend" / "index.html"


# Dashboard Endpoint
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard/", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard():
    if INDEX_FILE.exists():
        content = INDEX_FILE.read_text(encoding="utf-8")
        return HTMLResponse(content=content)

    return HTMLResponse(
        content=f"<h2>404 - Frontend File Not Found</h2><p>Looked for index.html at: <code>{INDEX_FILE}</code></p>",
        status_code=404,
    )


@app.get("/")
def root():
    return {
        "status": "running",
        "dashboard": "http://127.0.0.1:8000/dashboard",
        "docs": "http://127.0.0.1:8000/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent.main:app", host="0.0.0.0", port=8000, reload=True)
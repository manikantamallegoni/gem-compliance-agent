from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

import firebase_admin
from firebase_admin import auth, credentials

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from agent.compliance_agent import GeMComplianceAgent
from agent.config import settings
from agent.router import router as agent_router
from agent.schema import EvaluationRequest


# ============================================================
# PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DASHBOARD_FILE = FRONTEND_DIR / "index.html"


# ============================================================
# FIREBASE ADMIN INITIALIZATION
# ============================================================

def initialize_firebase():
    """
    Initialize Firebase Admin SDK.

    Supported methods:

    1. GOOGLE_APPLICATION_CREDENTIALS
       Example Windows:

       set GOOGLE_APPLICATION_CREDENTIALS=C:\\path\\firebase-service-account.json

    2. FIREBASE_SERVICE_ACCOUNT_JSON
       Complete service-account JSON stored in an environment variable.

    The service-account credentials NEVER go into index.html.
    """

    # Already initialized
    if firebase_admin._apps:
        return

    credentials_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )

    # --------------------------------------------------------
    # METHOD 1: SERVICE ACCOUNT FILE
    # --------------------------------------------------------

    if credentials_path:

        credentials_path = os.path.abspath(
            credentials_path
        )

        if not os.path.isfile(credentials_path):

            raise RuntimeError(
                "Firebase credentials file not found:\n"
                f"{credentials_path}\n\n"
                "Set GOOGLE_APPLICATION_CREDENTIALS "
                "to the correct service-account JSON path."
            )

        cred = credentials.Certificate(
            credentials_path
        )

        firebase_admin.initialize_app(cred)

        print(
            "Firebase Admin initialized successfully."
        )

        print(
            f"Service account: {credentials_path}"
        )

        return

    # --------------------------------------------------------
    # METHOD 2: ENVIRONMENT JSON
    # --------------------------------------------------------

    firebase_json = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON"
    )

    if firebase_json:

        try:

            service_account_info = json.loads(
                firebase_json
            )

            cred = credentials.Certificate(
                service_account_info
            )

            firebase_admin.initialize_app(cred)

            print(
                "Firebase Admin initialized using "
                "FIREBASE_SERVICE_ACCOUNT_JSON."
            )

            return

        except Exception as exc:

            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON is invalid."
            ) from exc

    # --------------------------------------------------------
    # NOTHING CONFIGURED
    # --------------------------------------------------------

    raise RuntimeError(
        "Firebase Admin credentials are not configured.\n\n"
        "Set either:\n"
        "GOOGLE_APPLICATION_CREDENTIALS\n"
        "or\n"
        "FIREBASE_SERVICE_ACCOUNT_JSON"
    )


# Initialize Firebase before the application starts.
initialize_firebase()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.project_name
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# FIREBASE WEB CONFIGURATION
# ============================================================

@app.get(
    "/firebase-config",
    include_in_schema=False,
)
async def firebase_config():

    config = {
        "apiKey": os.getenv(
            "FIREBASE_API_KEY",
            "AIzaSyArvva3d5qqIixi4RUpUzEVO55b_KULjhc",
        ),

        "authDomain": os.getenv(
            "FIREBASE_AUTH_DOMAIN",
            "gem-compliance-agent-main.firebaseapp.com",
        ),

        "projectId": os.getenv(
            "FIREBASE_PROJECT_ID",
            "gem-compliance-agent-main",
        ),

        "storageBucket": os.getenv(
            "FIREBASE_STORAGE_BUCKET",
            "gem-compliance-agent-main.firebasestorage.app",
        ),

        "messagingSenderId": os.getenv(
            "FIREBASE_MESSAGING_SENDER_ID",
            "306370513406",
        ),

        "appId": os.getenv(
            "FIREBASE_APP_ID",
            "1:306370513406:web:8205f7209f8acda94a18af",
        ),

        "measurementId": os.getenv(
            "FIREBASE_MEASUREMENT_ID",
            "G-QH1RG06Z91",
        ),
    }

    required = [
        "apiKey",
        "authDomain",
        "projectId",
        "storageBucket",
        "messagingSenderId",
        "appId",
    ]

    missing = [
        key
        for key in required
        if not config.get(key)
    ]

    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Firebase Web configuration is missing: "
                + ", ".join(missing)
            ),
        )

    return config

# ============================================================
# AGENT
# ============================================================

agent = GeMComplianceAgent()


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    agent_router
)


# ============================================================
# FIREBASE AUTHENTICATION
# ============================================================

security = HTTPBearer(
    auto_error=True
)


async def verify_firebase_token(
    credentials_data: HTTPAuthorizationCredentials =
    Depends(security),
):
    """
    Verify Firebase ID token.

    Expected:

        Authorization: Bearer <Firebase ID token>
    """

    if (
        credentials_data.scheme.lower()
        != "bearer"
    ):

        raise HTTPException(
            status_code=401,
            detail="Authorization scheme must be Bearer.",
        )

    token = credentials_data.credentials

    if not token:

        raise HTTPException(
            status_code=401,
            detail="Firebase ID token is missing.",
        )

    try:

        decoded_token = auth.verify_id_token(
            token
        )

        return decoded_token

    except auth.ExpiredIdTokenError:

        raise HTTPException(
            status_code=401,
            detail=(
                "Firebase ID token has expired. "
                "Please sign in again."
            ),
        )

    except auth.RevokedIdTokenError:

        raise HTTPException(
            status_code=401,
            detail=(
                "Firebase ID token has been revoked."
            ),
        )

    except Exception as exc:

        print(
            "Firebase token verification failed:",
            repr(exc),
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase ID token.",
        )


# ============================================================
# AUDIT ENDPOINT
# ============================================================

@app.post("/audit")
async def run_audit(
    tender_id: str = Form(...),

    bidder_name: str = Form(...),

    tender_requirements: str = Form(...),

    file: UploadFile = File(...),

    pan_file: Optional[UploadFile] = File(None),

    gst_file: Optional[UploadFile] = File(None),

    financial_file: Optional[UploadFile] = File(None),

    firebase_user: dict = Depends(
        verify_firebase_token
    ),
):

    # ========================================================
    # VERIFIED FIREBASE USER
    # ========================================================

    firebase_uid = firebase_user.get(
        "uid"
    )

    user_email = firebase_user.get(
        "email"
    )

    user_name = firebase_user.get(
        "name"
    )

    print(
        "Authenticated audit request:"
    )

    print(
        f"  UID: {firebase_uid}"
    )

    print(
        f"  Email: {user_email}"
    )

    print(
        f"  Name: {user_name}"
    )


    # ========================================================
    # MAIN BID DOCUMENT
    # ========================================================

    content = await file.read()

    combined_text = (
        "--- MAIN BID DOCUMENT ---\n"
        f"{content.decode('utf-8', errors='ignore')}\n\n"
    )


    # ========================================================
    # PAN DOCUMENT
    # ========================================================

    if pan_file and pan_file.filename:

        pan_content = await pan_file.read()

        combined_text += (
            "--- PAN DOCUMENT ---\n"
            f"{pan_content.decode('utf-8', errors='ignore')}\n\n"
        )


    # ========================================================
    # GST DOCUMENT
    # ========================================================

    if gst_file and gst_file.filename:

        gst_content = await gst_file.read()

        combined_text += (
            "--- GST CERTIFICATE ---\n"
            f"{gst_content.decode('utf-8', errors='ignore')}\n\n"
        )


    # ========================================================
    # FINANCIAL DOCUMENT
    # ========================================================

    if financial_file and financial_file.filename:

        financial_content = (
            await financial_file.read()
        )

        combined_text += (
            "--- FINANCIAL PROOF ---\n"
            f"{financial_content.decode('utf-8', errors='ignore')}\n\n"
        )


    # ========================================================
    # EVALUATION REQUEST
    # ========================================================

    evaluation_request = EvaluationRequest(
        tender_id=tender_id,

        bidder_name=bidder_name,

        tender_requirements=tender_requirements,

        bidder_document_text=combined_text,
    )


    # ========================================================
    # RUN COMPLIANCE AGENT
    # ========================================================

    result = agent.evaluate(
        evaluation_request
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return result


# ============================================================
# DASHBOARD
# ============================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse,
    include_in_schema=False,
)
@app.get(
    "/dashboard/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def serve_dashboard():

    if not DASHBOARD_FILE.exists():

        return HTMLResponse(
            content=(
                "<h2>Dashboard file not found</h2>"
                f"<p>Expected:</p>"
                f"<code>{DASHBOARD_FILE}</code>"
            ),
            status_code=404,
        )

    try:

        content = DASHBOARD_FILE.read_text(
            encoding="utf-8"
        )

    except Exception as exc:

        return HTMLResponse(
            content=(
                "<h2>Unable to read dashboard</h2>"
                f"<p>{exc}</p>"
            ),
            status_code=500,
        )

    return HTMLResponse(
        content=content
    )


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def root():

    if not DASHBOARD_FILE.exists():

        return HTMLResponse(
            content=(
                "<h2>index.html not found</h2>"
                f"<p>Expected:</p>"
                f"<code>{DASHBOARD_FILE}</code>"
            ),
            status_code=404,
        )

    content = DASHBOARD_FILE.read_text(
        encoding="utf-8"
    )

    return HTMLResponse(
        content=content
    )


# ============================================================
# FAVICON
# ============================================================

@app.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():

    return HTMLResponse(
        content="",
        status_code=204,
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    include_in_schema=False,
)
async def health():

    return {
        "status": "running",
        "firebase_admin": bool(
            firebase_admin._apps
        ),
        "dashboard": "/dashboard",
        "docs": "/docs",
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "agent.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
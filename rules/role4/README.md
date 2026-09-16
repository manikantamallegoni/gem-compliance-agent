# SIH 26100 — Role 4: Rules & Decision Engine

**Problem Statement:** 26100  
**Role:** Rules & Decision Engine Engineer

This repository contains the Role 4 module for the SIH 26100 prototype:
**AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement.**

## What this module does

The Rules & Decision Engine receives structured bidder information and tender requirements and evaluates compliance.

It can perform:

- GST verification
- PAN verification
- Udyam/MSME verification
- Minimum turnover check
- OEM authorization check
- Blacklist/debarment check
- Startup India check
- NSIC check
- Make in India check
- EPFO/ESIC compliance checks
- Certificate requirement check
- Document expiry check
- Cross-document company-name conflict detection
- PASS / FAIL / REVIEW / MISSING / CONFLICT / NOT_REQUIRED status
- Weighted compliance score
- Risk classification
- Explainable recommendation
- Audit trail
- REST API using FastAPI
- Automated tests

> **Important:** `sample_bidder.json` and `sample_tender_rules.json` contain DEMO DATA ONLY.  
> Real bidder data should come from the team's Document Intelligence/OCR module and verification/integration modules.

## Architecture

```text
                 REAL BIDDER DOCUMENTS
                          |
                          v
              Member 2 — Document Intelligence
                          |
                          v
                 Structured bidder data
                          |
                          v
                +---------------------+
                |     ROLE 4          |
                | Rules & Decision     |
                |      Engine          |
                +----------+----------+
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
   Rule Results       Score + Risk       Recommendation
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                    Audit / Evidence
                           |
                           v
             Member 5 Backend / Member 6 UI
```

## Project structure

```text
SIH26100_Role4_Compliance_Engine/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── engine.py
│   ├── scoring.py
│   ├── audit.py
│   │
│   └── rules/
│       ├── __init__.py
│       ├── common.py
│       ├── identity.py
│       ├── registrations.py
│       ├── financial.py
│       ├── eligibility.py
│       └── documents.py
│
├── data/
│   ├── sample_bidder.json
│   └── sample_tender_rules.json
│
├── tests/
│   ├── __init__.py
│   └── test_engine.py
│
├── requirements.txt
├── run.py
└── README.md
```

## Run the demo

### 1. Open terminal in this folder

```bash
cd SIH26100_Role4_Compliance_Engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the sample engine

```bash
python run.py
```

The sample files are only there to demonstrate the engine.

## Run the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger will show the API and allow your team to test it.

## Main API

```text
POST /api/v1/compliance/check
```

The API accepts:

```json
{
  "bidder": {
    "company_name": "REAL COMPANY NAME",
    "pan": "REAL PAN",
    "pan_status": "Valid",
    "gst": "REAL GST",
    "gst_status": "Active",
    "udyam": "REAL UDYAM",
    "udyam_status": "Active",
    "turnover": 150000000,
    "oem_status": "Valid",
    "blacklisted": false,
    "startup_status": "Not Applicable",
    "nsic_status": "Not Applicable",
    "make_in_india_status": "Compliant",
    "epfo_status": "Compliant",
    "esic_status": "Compliant",
    "certificate_status": "Valid",
    "document_expiry_date": "2027-12-31",
    "company_name_pan": "REAL COMPANY NAME",
    "company_name_gst": "REAL COMPANY NAME",
    "company_name_udyam": "REAL COMPANY NAME",
    "company_name_oem": "REAL COMPANY NAME"
  },
  "tender": {
    "tender_id": "GEM-EXAMPLE",
    "gst_required": true,
    "pan_required": true,
    "udyam_required": true,
    "oem_required": true,
    "startup_required": false,
    "nsic_required": false,
    "make_in_india_required": false,
    "epfo_required": false,
    "esic_required": false,
    "certificate_required": true,
    "minimum_turnover": 100000000
  }
}
```

The engine returns:

```text
Rule results
+
Compliance score
+
Risk level
+
Recommendation
+
Review flag
+
Audit trail
```

## How the real data will enter this module

Do NOT manually edit `sample_bidder.json` for the production flow.

The intended flow is:

```text
Bidder uploads PDF/documents
        ↓
Member 2 extracts information
        ↓
Structured JSON
        ↓
Role 4 API
        ↓
Rules are evaluated
        ↓
Compliance report
        ↓
Backend / Dashboard
```

Example extracted data:

```json
{
  "company_name": "XYZ Enterprises Pvt Ltd",
  "pan": "XYZAB1234K",
  "pan_status": "Valid",
  "gst_status": "Active",
  "udyam_status": "Active",
  "turnover": 85000000,
  "oem_status": "Valid",
  "blacklisted": false
}
```

The engine is designed to work with different bidder information; the company in the sample files is not a required bidder.

## Status meanings

| Status | Meaning |
|---|---|
| PASS | Requirement is satisfied |
| FAIL | Requirement is not satisfied |
| REVIEW | Human verification is needed |
| MISSING | Required information/document is absent |
| CONFLICT | Different documents contain inconsistent information |
| NOT_REQUIRED | Tender does not require this check |

## Important procurement behavior

This module is a **decision-support engine**.

It should not claim:

```text
"Bidder is officially qualified."
```

Instead, it produces an explainable recommendation such as:

```text
RECOMMENDED FOR FURTHER EVALUATION
```

or:

```text
REVIEW REQUIRED - COMPLIANCE FAILURE
```

The final procurement decision remains with the authorized Procurement Officer.

## Backend integration

This version is **integration-ready**.

The production backend should call:

```text
POST /api/v1/compliance/check
```

with the current bidder's structured data and the current tender's requirements.

The engine does **not** read `sample_bidder.json` during a normal API request.

`sample_bidder.json` is used only by:

```text
python run.py
GET /api/v1/demo
```

For the exact request/response contract, see:

```text
integration/API_CONTRACT.md
```

A backend test payload is provided in:

```text
integration/backend_test_request.json
```

### Important data ownership

```text
Member 2 → extracts document information
Member 3 → supplies verification statuses
Role 4   → evaluates rules and makes the decision-support report
Member 5 → connects services and database
Member 6 → displays the report
```

Real bidder information therefore flows into Role 4 through the API; it does not overwrite the sample files.

## Testing

Run:

```bash
pytest -q
```

The tests cover the main decision paths, including:

- successful compliance
- turnover failure
- missing GST
- blacklist failure
- company-name conflict
- expired document
- optional/not-required rules

## Team integration

### Member 1 — AI Agent / Orchestration
Can call:

```text
POST /api/v1/compliance/check
```

as a compliance-verification tool.

### Member 2 — Document Intelligence
Provides extracted bidder information.

### Member 3 — Compliance & Verification
Can provide verified/mock statuses from external-source integrations.

### Member 5 — Backend / Integration
Connects this service with the main backend/database/authentication.

### Member 6 — Frontend + Visualization
Displays rule results, score, risk and recommendation.

## Current prototype limitation

External government systems should only be connected when the team has an authorized API/integration. Until then, this repository supports structured/mock verification results so the complete workflow can be demonstrated safely.

## GitHub

Upload this entire folder to the team's repository.

Do not upload:
- passwords
- API keys
- tokens
- private certificates
- real bidder confidential documents
- `.env` files containing secrets

For the SIH prototype, use sample/mock data in GitHub.

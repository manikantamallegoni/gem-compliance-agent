# Role 4 API Contract

## Endpoint

```text
POST /api/v1/compliance/check
```

Base URL when running locally:

```text
http://127.0.0.1:8000
```

Production base URL will be decided by the backend team.

## Purpose

The backend sends **one bidder's extracted/verified information** plus the **requirements of the current tender**.

Role 4 evaluates the data and returns an explainable compliance report.

## Request

```json
{
  "bidder": {
    "company_name": "REAL COMPANY NAME",
    "pan": "ABCDE1234F",
    "pan_status": "Valid",
    "gst": "29ABCDE1234F1Z5",
    "gst_status": "Active",
    "udyam": "UDYAM-TS-01-1234567",
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

## Important

The values above are examples only.

For real use:

```text
company_name       → extracted real company
PAN                → extracted real PAN
GST                → extracted real GST
turnover           → extracted real turnover
verification status → Member 3 / authorized integration result
```

Do not hard-code bidder information in the backend.

## Response

Example:

```json
{
  "bidder_name": "REAL COMPANY NAME",
  "tender_id": "GEM-EXAMPLE",
  "results": [
    {
      "rule_id": "R001",
      "rule_name": "GST Verification",
      "status": "PASS",
      "severity": "INFO",
      "reason": "GST registration status is Active.",
      "evidence": []
    }
  ],
  "compliance_score": 94.12,
  "risk_level": "LOW",
  "recommendation": "RECOMMENDED FOR FURTHER EVALUATION",
  "review_required": false,
  "summary": {
    "PASS": 9,
    "NOT_REQUIRED": 5
  },
  "audit_trail": []
}
```

## Status values

```text
PASS
FAIL
REVIEW
MISSING
CONFLICT
NOT_REQUIRED
```

### Meaning

- `PASS` → requirement satisfied
- `FAIL` → requirement failed
- `REVIEW` → human verification required
- `MISSING` → required information unavailable
- `CONFLICT` → documents disagree
- `NOT_REQUIRED` → tender does not require the check

## Integration flow

```text
FRONTEND
   |
   | bidder uploads documents
   v
BACKEND
   |
   +----> Document Intelligence / OCR
   |              |
   |              v
   |       extracted bidder data
   |
   +----> Compliance / Verification module
   |              |
   |              v
   |       verified statuses
   |
   v
POST /api/v1/compliance/check
   |
   v
ROLE 4 RULES ENGINE
   |
   +--> individual rule results
   +--> score
   +--> risk
   +--> recommendation
   +--> audit trail
   |
   v
BACKEND
   |
   v
FRONTEND DASHBOARD
```

## Simple backend call

Python:

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/v1/compliance/check",
    json={
        "bidder": real_bidder_data,
        "tender": tender_rules
    },
    timeout=30
)

report = response.json()
print(report["compliance_score"])
print(report["recommendation"])
```

JavaScript:

```javascript
const response = await fetch(
  "http://127.0.0.1:8000/api/v1/compliance/check",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      bidder: realBidderData,
      tender: tenderRules
    })
  }
);

const report = await response.json();

console.log(report.compliance_score);
console.log(report.recommendation);
```

## Rule IDs

| ID | Rule |
|---|---|
| R001 | GST Verification |
| R002 | PAN Verification |
| R003 | Udyam/MSME Verification |
| R004 | Minimum Turnover |
| R005 | OEM Authorization |
| R006 | Blacklist / Debarment |
| R007 | Certificate Requirement |
| R008 | Company Name Consistency |
| R009 | Document Expiry |
| R010 | Startup India |
| R011 | NSIC |
| R012 | Make in India |
| R013 | EPFO |
| R014 | ESIC |

## Integration rule

**Role 4 does not own document extraction.**

It accepts structured data and makes decisions from that data.

This keeps the modules independent:

```text
Member 2 = extracts
Member 3 = verifies
Role 4   = decides
Member 5 = integrates
Member 6 = displays
```

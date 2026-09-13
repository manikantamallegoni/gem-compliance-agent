"""
Deterministic Verification Module using RegEx.
"""

import re
from typing import Dict, Any, List

GSTIN_PATTERN = r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b"
PAN_PATTERN = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
UDYAM_PATTERN = r"\bUDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}\b"


def verify_bidder_metadata(document_text: str) -> Dict[str, Any]:
    gstin_matches = list(set(re.findall(GSTIN_PATTERN, document_text)))
    pan_matches = list(set(re.findall(PAN_PATTERN, document_text)))
    udyam_matches = list(set(re.findall(UDYAM_PATTERN, document_text)))

    return {
        "found_gstin": gstin_matches,
        "found_pan": pan_matches,
        "found_udyam": udyam_matches,
        "has_gstin": len(gstin_matches) > 0,
        "has_pan": len(pan_matches) > 0,
        "has_udyam": len(udyam_matches) > 0,
    }
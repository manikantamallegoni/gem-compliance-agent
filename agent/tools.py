"""
Tools and integration wrappers for the GeM Compliance Agent.

Provides dual-mode operational support:
  1. Executes local extraction, dynamic rule lookup, and regex verification routines.
  2. Tries to invoke teammates' modules (`document_intelligence`, `rules`, `verification`).
  3. Falls back gracefully to structured defaults if modules or target files are missing.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agent.tools")

# Directory setup for dynamic JSON rules
RULES_DIR = Path(__file__).resolve().parent.parent / "rules"


# ---------------------------------------------------------------------------
# Document Intelligence Integration
# ---------------------------------------------------------------------------

def extract_document_text(file_path: str) -> str:
    """
    Extract raw text from a bidder document via `document_intelligence` module or local fallback.
    """
    try:
        from document_intelligence.extractor import extract_text  # type: ignore

        result = extract_text(file_path)
        if isinstance(result, str) and result.strip():
            return result
        logger.warning(
            "document_intelligence.extract_text returned empty/invalid output; using fallback."
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "document_intelligence module unavailable (%s); using fallback.", exc
        )

    return _mock_extract_document_text(file_path)


def _mock_extract_document_text(file_path: str) -> str:
    path = Path(file_path)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception as err:
            logger.error("Failed reading file content locally: %s", err)

    return (
        f"[MOCK DOCUMENT TEXT] Placeholder text standing in for '{file_path}' content."
    )


# ---------------------------------------------------------------------------
# Rules Engine Integration
# ---------------------------------------------------------------------------

def get_tender_rules(tender_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch structured compliance rules dynamically.
    Checks external team module -> local JSON rules directory -> default rule set.
    """
    # 1. Try importing teammate's rules engine module
    try:
        from rules.engine import get_rules_for_tender  # type: ignore

        result = get_rules_for_tender(tender_id)
        if isinstance(result, list) and result:
            return result
    except Exception as exc:  # noqa: BLE001
        logger.debug("rules.engine module unavailable (%s); checking local rules.", exc)

    # 2. Try loading dynamic JSON rule file from rules/<tender_id>.json
    if tender_id:
        RULES_DIR.mkdir(parents=True, exist_ok=True)
        sanitized_id = tender_id.replace("/", "_")
        rule_file = RULES_DIR / f"{sanitized_id}.json"

        if rule_file.exists():
            try:
                with open(rule_file, "r", encoding="utf-8") as f:
                    rules = json.load(f)
                    if isinstance(rules, list) and rules:
                        logger.info("Loaded %d dynamic rules for %s", len(rules), tender_id)
                        return rules
            except Exception as exc:
                logger.error("Failed to parse local rule file %s: %s", rule_file, exc)

    # 3. Standard fallback rules
    return _mock_get_tender_rules(tender_id)


def _mock_get_tender_rules(tender_id: Optional[str]) -> List[Dict[str, Any]]:
    return [
        {
            "clause_id": "GEM-ELG-001",
            "requirement_name": "Minimum Years of Experience",
            "expected_value": "Min 3 years of relevant experience",
        },
        {
            "clause_id": "TURNOVER_REQ",
            "requirement_name": "Minimum Annual Turnover",
            "expected_value": "Average annual turnover >= INR 50,00,000 over the last 3 financial years",
        },
        {
            "clause_id": "GSTIN_REQ",
            "requirement_name": "Valid GST Registration",
            "expected_value": "Bidder must hold a valid, active GST registration certificate",
        },
        {
            "clause_id": "PAN_REQ",
            "requirement_name": "PAN Registration",
            "expected_value": "Valid 10-character PAN Card registration",
        },
    ]


# ---------------------------------------------------------------------------
# Verification Integration
# ---------------------------------------------------------------------------

def verify_document_credentials(doc_text: str) -> Dict[str, Any]:
    """
    Executes regex verification checks for GSTIN, PAN, and Udyam numbers directly against document text.
    """
    gstin_pattern = r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b"
    pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
    udyam_pattern = r"\bUDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}\b"

    found_gstins = re.findall(gstin_pattern, doc_text)
    found_pans = re.findall(pan_pattern, doc_text)
    found_udyams = re.findall(udyam_pattern, doc_text)

    return {
        "gstin": {
            "found": found_gstins[0] if found_gstins else None,
            "valid": len(found_gstins) > 0,
            "all_matches": found_gstins,
        },
        "pan": {
            "found": found_pans[0] if found_pans else None,
            "valid": len(found_pans) > 0,
            "all_matches": found_pans,
        },
        "udyam": {
            "found": found_udyams[0] if found_udyams else None,
            "valid": len(found_udyams) > 0,
            "all_matches": found_udyams,
        },
    }


def verify_turnover(
        expected_value: str, bidder_document_text: str
) -> Dict[str, Any]:
    """
    Run a turnover check via external `verification` module or local keyword/numeric verification.
    """
    try:
        from verification.financial import verify_turnover as _verify  # type: ignore

        result = _verify(expected_value, bidder_document_text)
        if isinstance(result, dict) and result:
            return result
    except Exception as exc:  # noqa: BLE001
        logger.debug("verification module unavailable (%s); using local check.", exc)

    return _mock_verify_turnover(expected_value, bidder_document_text)


def _mock_verify_turnover(
        expected_value: str, bidder_document_text: str
) -> Dict[str, Any]:
    has_keywords = any(kw in bidder_document_text.lower() for kw in ["turnover", "lakhs", "crores", "revenue"])
    return {
        "verified": has_keywords,
        "note": (
            "Verified via local heuristic scan." if has_keywords
            else "Turnover metrics could not be automatically confirmed in raw text."
        ),
        "expected_value": expected_value,
    }


def verify_document_authenticity(file_path: str) -> Dict[str, Any]:
    """
    Check document integrity/authenticity via external `verification` module or fallback check.
    """
    try:
        from verification.integrity import verify_document  # type: ignore

        result = verify_document(file_path)
        if isinstance(result, dict) and result:
            return result
    except Exception as exc:  # noqa: BLE001
        logger.debug("verification.integrity module unavailable (%s).", exc)

    return _mock_verify_document_authenticity(file_path)


def _mock_verify_document_authenticity(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    return {
        "verified": path.exists(),
        "file_exists": path.exists(),
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "note": "Local file metadata checked.",
    }
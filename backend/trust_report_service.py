"""
TruthTag Intelligence Platform — Product Trust Report Synthesizer
Combines sample-registry results and configured demo signals into an explainable report.
"""

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .models import TrustReportResponse
from .verification_service import run_verification
from .pricing_service import get_product_pricing

def generate_product_trust_report(
    identifier_or_sku: str,
    user_id: Optional[str] = None,
    client_ip: Optional[str] = None
) -> TrustReportResponse:
    """
    Generate a report with an explicitly heuristic score over fictional sample data.
    """
    # 1. Run Verification
    verification = run_verification(
        query=identifier_or_sku,
        user_id=user_id,
        client_ip=client_ip
    )

    # 2. Fetch Pricing if Product Identified
    pricing_data = None
    if verification.product_id:
        pricing_data = get_product_pricing(verification.product_id)

    # 3. Transparent Composite Trust Index Calculation (0 to 100, where 100 = Maximum Trust / Low Risk)
    # Rules:
    # - Baseline: 95 points
    # - Inconclusive registry lookup: -45 points
    # - Batch flagged alert: -50 points
    # - Recalled batch: -60 points
    # - Duplicate scan detected: -15 points
    # - High repeat-lookup count (scan_count >= 10): -25 points
    # - Sample listings marked unauthorized: -5 points

    score = 95
    deductions = []

    if verification.outcome == "inconclusive":
        score -= 45
        deductions.append({
            "rule": "UNREGISTERED_IDENTIFIER",
            "impact": -45,
            "rationale": "Identifier is unlisted in brand manufacturer ledger."
        })
    else:
        if "SAMPLE_BATCH_FLAGGED" in verification.anomaly_flags:
            score -= 50
            deductions.append({
                "rule": "SAMPLE_BATCH_FLAGGED",
                "impact": -50,
                "rationale": "The sample batch is marked as flagged in the demo database."
            })
        if "SAMPLE_BATCH_MARKED_RECALLED" in verification.anomaly_flags:
            score -= 60
            deductions.append({
                "rule": "SAMPLE_BATCH_MARKED_RECALLED",
                "impact": -60,
                "rationale": "The sample batch is marked as recalled in the demo database; this is not a real safety notice."
            })
        if verification.duplicate_alert:
            score -= 15
            deductions.append({
                "rule": "DUPLICATE_SCAN_HISTORY",
                "impact": -15,
                "rationale": f"Identifier has {verification.scan_count} recorded lookups in the demo database."
            })
        if "HIGH_REPEAT_LOOKUP_COUNT" in verification.anomaly_flags:
            score -= 25
            deductions.append({
                "rule": "HIGH_REPEAT_LOOKUP_COUNT",
                "impact": -25,
                "rationale": "The lookup count crossed the demo's configured threshold; repeat lookups do not establish cloning."
            })

    # Pricing dimension deductions
    if pricing_data and pricing_data.listings:
        unauth_count = sum(1 for l in pricing_data.listings if not l.is_authorized_seller)
        if unauth_count > 0 and len(pricing_data.listings) > 1:
            score -= 5
            deductions.append({
                "rule": "GRAY_MARKET_LISTINGS_PRESENT",
                "impact": -5,
                "rationale": f"The sample catalog marks {unauth_count} listing(s) as unauthorized; this status is fictional demo data."
            })

    trust_index = max(5, min(99, score))

    if verification.outcome == "warning" or trust_index < 50:
        trust_category = "Suspicious Signals Detected"
    elif verification.outcome == "inconclusive":
        trust_category = "Inconclusive Registry Lookup"
    else:
        trust_category = "Registered Record Matched"

    report_id = "TRUTH-REP-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:8].upper()
    now_iso = datetime.now(timezone.utc).isoformat()
    digest_source = f"{report_id}|{identifier_or_sku}|{trust_index}|{now_iso}"
    crypto_digest = "SHA256: " + hashlib.sha256(digest_source.encode("utf-8")).hexdigest()

    scoring_methodology = {
        "formula": "Composite Trust Index (0-100) = Baseline(95) - Σ(Heuristic Anomaly Deductions)",
        "base_score": 95,
        "final_trust_index": trust_index,
        "deductions_applied": deductions,
        "interpretative_ranges": {
            "80_to_100": "Fewer configured demo signals; this is not a probability of authenticity.",
            "50_to_79": "Some configured demo signals or an inconclusive sample-registry lookup.",
            "0_to_49": "More configured demo signals; this is not a counterfeit determination."
        }
    }

    limitations = [
        "A registry match means the identifier matched a fictional demo record. It does not verify brand authorization or physical authenticity.",
        "Retailer authorization labels and prices are fictional sample data, not current market observations.",
        "The SHA-256 report digest covers the report ID, requested identifier, score, and generation time; it does not validate registry sources or physical authenticity."
    ]

    next_steps = [
        "Compare packaging with manufacturer guidance obtained through an independently verified contact channel.",
        "Confirm seller and warranty terms directly with the manufacturer.",
        "The incident form stores reports in the demo database; no real brand-investigation workflow is configured."
    ]

    pricing_summary = None
    if pricing_data:
        pricing_summary = {
            "lowest_price": pricing_data.lowest_observed_price,
            "average_price": pricing_data.average_observed_price,
            "deal_rating": pricing_data.deal_rating,
            "deal_description": pricing_data.deal_description,
            "tracked_listings_count": len(pricing_data.listings),
            "authorized_retailers": [l.retailer_name for l in pricing_data.listings if l.is_authorized_seller],
            "price_history_trend": f"{pricing_data.price_change_90d_pct}% over 90 days"
        }

    return TrustReportResponse(
        report_id=report_id,
        generated_at=now_iso,
        cryptographic_digest=crypto_digest,
        verification=verification,
        pricing_summary=pricing_summary,
        composite_trust_index=trust_index,
        trust_category=trust_category,
        scoring_methodology=scoring_methodology,
        limitations_and_disclaimers=limitations,
        next_steps=next_steps
    )

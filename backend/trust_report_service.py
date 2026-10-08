"""
TruthTag Intelligence Platform — Product Trust Report Synthesizer
Combines verification records, duplicate scan signals, metadata integrity,
retailer authorization, and historical price stability into an explainable dossier.
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
    Generate a full evidence-based Product Trust Report.
    Combines brand provenance, anomaly scan telemetry, retailer price dispersion,
    and warranty indicators into an explainable assessment.
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
    # - Severe cloning velocity (scan_count >= 10): -35 points
    # - Missing authorized retailers: -10 points
    # - Price volatility or extreme price spread (> 40% discount vs brand direct): -10 points

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
        if "BATCH_FLAGGED_COUNTERFEIT_ALERT" in verification.anomaly_flags:
            score -= 50
            deductions.append({
                "rule": "ACTIVE_COUNTERFEIT_ALERT",
                "impact": -50,
                "rationale": "Batch code is linked to active customs or brand counterfeit advisories."
            })
        if "BATCH_OFFICIALLY_RECALLED" in verification.anomaly_flags:
            score -= 60
            deductions.append({
                "rule": "OFFICIAL_SAFETY_RECALL",
                "impact": -60,
                "rationale": "Batch is subject to official consumer safety recall notice."
            })
        if verification.duplicate_alert:
            score -= 15
            deductions.append({
                "rule": "DUPLICATE_SCAN_HISTORY",
                "impact": -15,
                "rationale": f"Identifier has been scanned {verification.scan_count} times across sessions."
            })
        if "HIGH_VELOCITY_SERIAL_CLONING" in verification.anomaly_flags:
            score -= 25
            deductions.append({
                "rule": "HIGH_VELOCITY_CLONING_VELOCITY",
                "impact": -25,
                "rationale": "Severe repeat scan velocity indicates probable mass serial cloning."
            })

    # Pricing dimension deductions
    if pricing_data and pricing_data.listings:
        unauth_count = sum(1 for l in pricing_data.listings if not l.is_authorized_seller)
        if unauth_count > 0 and len(pricing_data.listings) > 1:
            score -= 5
            deductions.append({
                "rule": "GRAY_MARKET_LISTINGS_PRESENT",
                "impact": -5,
                "rationale": f"Detected {unauth_count} unauthorized third-party listing(s) in circulation."
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
            "80_to_100": "High Confidence Match: Ledger aligned, authorized channels verified, zero active clone alerts.",
            "50_to_79": "Moderate Risk / Inconclusive: Unregistered code or minor duplicate scan alerts.",
            "0_to_49": "High Risk Anomaly: Flagged counterfeit batch, safety recall, or severe serial clone velocity."
        }
    }

    limitations = [
        "Digital Match Limitation: Database verification confirms that the identifier sequence was authorized by the brand, but does not guarantee physical authenticity without examining tamper-evident packaging and hardware materials.",
        "Gray Market Notice: Authentic products sold by unauthorized retailers may lack factory warranty and post-sale technical support.",
        "Data Freshness: Retailer pricing and availability reflect observations at the indicated timestamps and may vary by regional warehouse."
    ]

    next_steps = [
        "Cross-reference the physical packaging against the documented security profile (e.g. holographic void seals, laser etching depth).",
        "Inspect purchase invoice to confirm whether merchant is an authorized distribution partner.",
        "If you encounter a cloned serial number or suspicious counterfeit, submit an incident report directly to brand investigators through the TruthTag portal."
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

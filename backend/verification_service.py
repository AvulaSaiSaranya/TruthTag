"""
TruthTag Intelligence Platform — Verification & Anomaly Engine
Handles identifier normalization, ledger querying, duplicate scan tracking,
consistency inspection, and transparent heuristic risk scoring.
"""

import uuid
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from .database import get_db
from .models import VerificationResponse, ConsistencyField

INTEGRITY_DISCLOSURE = (
    "DEMO LIMITATION: A positive result means that the identifier matched a record in this fictional demo "
    "database. It does not verify a manufacturer, prove that a physical item is genuine, or establish that "
    "an identifier has not been copied. Contact the manufacturer or an authorized seller and inspect the "
    "physical item before relying on a result."
)

def normalize_identifier(raw: str) -> str:
    """Normalize input strings for robust query lookup (lowercase, remove spaces and hyphens)."""
    if not raw:
        return ""
    return re.sub(r"[\s\-_]", "", str(raw).strip().lower())

def run_verification(
    query: str,
    query_type: str = "auto",
    submitted_brand: Optional[str] = None,
    submitted_model: Optional[str] = None,
    submitted_batch: Optional[str] = None,
    user_id: Optional[str] = None,
    client_ip: Optional[str] = None
) -> VerificationResponse:
    """
    Compare an identifier with stored demo records and return configured warning signals.
    """
    raw_query = query.strip()
    norm_query = normalize_identifier(raw_query)
    scan_id = "AUDIT-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6].upper()
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        cursor = conn.cursor()

        # Step 1: Search in Identifiers table (by serial number or QR payload)
        cursor.execute("""
            SELECT i.id as identifier_id, i.serial_number, i.qr_payload, i.scan_count, i.last_scanned_at, i.status as ident_status,
                   p.id as product_id, p.name as product_name, p.model_sku, p.category, p.description, p.image_url,
                   p.security_feature, p.authorized_channels, p.inspection_notes,
                   b.id as batch_id, b.batch_number, b.facility, b.production_date, b.status as batch_status, b.status_notes,
                   br.id as brand_id, br.name as brand_name, br.code as brand_code
            FROM identifiers i
            JOIN products p ON i.product_id = p.id
            JOIN batches b ON i.batch_id = b.id
            JOIN brands br ON p.brand_id = br.id
        """)
        all_idents = cursor.fetchall()

        matched_record = None
        match_type = None

        # Try matching serial numbers and QR payloads only when the selected mode allows it.
        if query_type in ("auto", "serial", "qr"):
            for row in all_idents:
                if query_type in ("auto", "serial") and normalize_identifier(row["serial_number"]) == norm_query:
                    matched_record = row
                    match_type = "serial"
                    break
                if query_type in ("auto", "qr") and normalize_identifier(row["qr_payload"]) == norm_query:
                    matched_record = row
                    match_type = "qr"
                    break

        # Step 2: Fallback to Model SKU or Batch Number or Product Name
        if not matched_record and query_type in ("auto", "sku", "batch"):
            cursor.execute("""
                SELECT NULL as identifier_id, NULL as serial_number, NULL as qr_payload, 0 as scan_count, NULL as last_scanned_at, 'active' as ident_status,
                       p.id as product_id, p.name as product_name, p.model_sku, p.category, p.description, p.image_url,
                       p.security_feature, p.authorized_channels, p.inspection_notes,
                       b.id as batch_id, b.batch_number, b.facility, b.production_date, b.status as batch_status, b.status_notes,
                       br.id as brand_id, br.name as brand_name, br.code as brand_code
                FROM products p
                JOIN brands br ON p.brand_id = br.id
                LEFT JOIN batches b ON b.product_id = p.id
            """)
            catalog_rows = cursor.fetchall()

            # SKU Match
            if query_type in ("auto", "sku"):
                for row in catalog_rows:
                    if normalize_identifier(row["model_sku"]) == norm_query:
                        matched_record = row
                        match_type = "sku"
                        break

            # Batch Match
            if not matched_record and query_type in ("auto", "batch"):
                for row in catalog_rows:
                    if row["batch_number"] and normalize_identifier(row["batch_number"]) == norm_query:
                        matched_record = row
                        match_type = "batch"
                        break

            # Name / Brand Substring Match
            if not matched_record and query_type == "auto":
                for row in catalog_rows:
                    p_name_norm = normalize_identifier(row["product_name"])
                    b_name_norm = normalize_identifier(row["brand_name"])
                    if norm_query in p_name_norm or p_name_norm in norm_query or norm_query in b_name_norm:
                        matched_record = row
                        match_type = "catalog_search"
                        break

        # Case A: Inconclusive (Identifier not found in registry)
        if not matched_record:
            risk_score = 65.0
            anomaly_flags = ["IDENTIFIER_NOT_FOUND_IN_LEDGER"]
            recommended_actions = [
                "Verify that the serial number or model code was entered correctly without typos.",
                "Check packaging for official brand verification portal instructions or dedicated customer QR tags.",
                "Contact the manufacturer's customer care desk with high-resolution photos of packaging seals.",
                "Exercise caution if purchased from an unauthorized marketplace or third-party reseller at an unusually steep discount."
            ]

            # Save scan event in database
            cursor.execute("""
                INSERT INTO scan_events (id, identifier_id, product_id, user_id, submitted_query, query_type, outcome, risk_score, anomaly_flags, client_ip, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (scan_id, None, None, user_id, raw_query, query_type, "inconclusive", risk_score, json.dumps(anomaly_flags), client_ip, now_iso))

            return VerificationResponse(
                scan_id=scan_id,
                outcome="inconclusive",
                outcome_title="Verification Inconclusive",
                risk_score=risk_score,
                risk_level="Unverified · score is heuristic",
                risk_explanation="The identifier was not found in the fictional sample registry. It may be mistyped or absent from this limited dataset; this result alone is not evidence that an item is counterfeit.",
                scanned_at=now_iso,
                submitted_query=raw_query,
                product_id=None,
                product_name="Unregistered Identifier",
                brand_name="No matching brand field",
                brand_code="N/A",
                category="Unverified Category",
                model_sku="N/A",
                batch_number="N/A",
                serial_number="N/A",
                production_facility="Not available",
                production_date="N/A",
                authorized_channels="Unknown",
                security_feature="Unverified",
                inspection_notes="No baseline profile found for this identifier.",
                product_image_url=None,
                scan_count=1,
                duplicate_alert=False,
                anomaly_flags=anomaly_flags,
                consistency_matrix=[
                    ConsistencyField(
                        field="Product Commercial Name",
                        submitted=raw_query,
                        registered="No Matching Record",
                        status="unverified",
                        diagnostic_rationale="Identifier not found in the current sample database."
                    ),
                    ConsistencyField(
                        field="Brand Authority",
                        submitted=submitted_brand or "Not Specified",
                        registered="No Matching Record",
                        status="unverified",
                        diagnostic_rationale="No matching brand record was found in the sample database."
                    ),
                    ConsistencyField(
                        field="Model SKU",
                        submitted=submitted_model or "Not Specified",
                        registered="No Matching Record",
                        status="unverified",
                        diagnostic_rationale="No model SKU specification aligned with this query."
                    ),
                    ConsistencyField(
                        field="Batch / Lot Code",
                        submitted=submitted_batch or "Not Specified",
                        registered="No Matching Record",
                        status="unverified",
                        diagnostic_rationale="No matching batch record was found in the sample database."
                    ),
                    ConsistencyField(
                        field="Unit Serial Number",
                        submitted=raw_query if match_type == "serial" else "Not Provided",
                        registered="No Matching Record",
                        status="unverified",
                        diagnostic_rationale="No matching serial record was found in the sample database."
                    )
                ],
                recommended_actions=recommended_actions,
                integrity_disclosure=INTEGRITY_DISCLOSURE
            )

        # Case B: Record Found! Check for duplicates and anomalies
        identifier_id = matched_record["identifier_id"]
        product_id = matched_record["product_id"]
        current_scan_count = (matched_record["scan_count"] or 0) + 1
        
        # Update identifier scan count in DB if unit serial matched
        if identifier_id:
            cursor.execute("""
                UPDATE identifiers
                SET scan_count = ?, last_scanned_at = ?
                WHERE id = ?
            """, (current_scan_count, now_iso, identifier_id))

        anomaly_flags = []
        is_warning = False
        risk_score = 5.0 # Baseline for a record match before configured signals
        risk_reasons = []

        # 1. Batch status evaluation
        batch_status = matched_record["batch_status"] or "active"
        if batch_status == "flagged":
            is_warning = True
            risk_score += 55.0
            anomaly_flags.append("SAMPLE_BATCH_FLAGGED")
            risk_reasons.append(f"Sample batch '{matched_record['batch_number']}' is marked as flagged in the demo database.")
        elif batch_status == "recalled":
            is_warning = True
            risk_score += 70.0
            anomaly_flags.append("SAMPLE_BATCH_MARKED_RECALLED")
            risk_reasons.append(f"Sample batch '{matched_record['batch_number']}' is marked as recalled in the demo database; this is not a real safety notice.")

        # 2. Identifier status evaluation
        ident_status = matched_record["ident_status"] or "active"
        if ident_status in ("flagged_cloned", "recalled"):
            is_warning = True
            risk_score += 50.0
            anomaly_flags.append("SAMPLE_IDENTIFIER_MARKED_FLAGGED")
            risk_reasons.append("This sample identifier is marked as flagged in the demo database.")

        # 3. Duplicate scan velocity evaluation
        duplicate_alert = False
        if current_scan_count > 1:
            duplicate_alert = True
            anomaly_flags.append("DUPLICATE_SCAN_DETECTED")
            if current_scan_count >= 10:
                is_warning = True
                risk_score += 45.0
                anomaly_flags.append("HIGH_REPEAT_LOOKUP_COUNT")
                risk_reasons.append(f"This identifier has {current_scan_count} recorded lookups in the demo database. Repeat lookups alone do not establish cloning.")
            else:
                risk_score += 15.0
                risk_reasons.append(f"Identifier previously verified {current_scan_count - 1} times. If you did not scan this code previously, verify seller authenticity.")

        # 4. Submitted metadata mismatch checks
        model_conflict = False
        if submitted_model and normalize_identifier(submitted_model) != normalize_identifier(matched_record["model_sku"]):
            model_conflict = True
            risk_score += 30.0
            anomaly_flags.append("MODEL_METADATA_MISMATCH")
            risk_reasons.append(f"Submitted model '{submitted_model}' conflicts with registered SKU '{matched_record['model_sku']}'.")

        brand_conflict = False
        if submitted_brand and normalize_identifier(submitted_brand) != normalize_identifier(matched_record["brand_name"]):
            brand_conflict = True
            risk_score += 30.0
            anomaly_flags.append("BRAND_METADATA_MISMATCH")
            risk_reasons.append(f"Submitted brand '{submitted_brand}' conflicts with the stored brand field '{matched_record['brand_name']}'.")

        batch_conflict = False
        if submitted_batch and matched_record["batch_number"] and normalize_identifier(submitted_batch) != normalize_identifier(matched_record["batch_number"]):
            batch_conflict = True
            risk_score += 30.0
            anomaly_flags.append("BATCH_METADATA_MISMATCH")
            risk_reasons.append(f"Submitted batch '{submitted_batch}' conflicts with registered batch '{matched_record['batch_number']}'.")

        # Cap risk score at 99.0
        risk_score = min(risk_score, 99.0)

        outcome = "warning" if (is_warning or model_conflict or brand_conflict or batch_conflict or risk_score >= 40.0) else "match"
        outcome_title = "Potential Inconsistency / Warning" if outcome == "warning" else "Registered Record Match Found"

        if outcome == "warning":
            risk_level = "Elevated Demo Signals"
            risk_explanation = " ".join(risk_reasons) or "The sample database returned configured warning signals for this record."
            recommended_actions = [
                "Treat the warning as a prompt to investigate, not as a verified counterfeit finding.",
                "Contact the manufacturer or retailer using contact details obtained independently.",
                "Compare the physical item with manufacturer-provided packaging guidance.",
                "Use the incident form to submit fictional demo details only."
            ]
        else:
            risk_level = "Fewer configured signals"
            risk_explanation = (
                f"The submitted identifier matched a record for {matched_record['brand_name']} in the fictional demo database. "
                "No configured warning signals were returned for this lookup; this is not a physical authenticity assessment."
            )
            recommended_actions = [
                "Check packaging and product details with the manufacturer through an independently verified contact channel.",
                "Confirm the seller and warranty terms directly with the manufacturer.",
                "Remember that copied identifiers can still match a registry record."
            ]

        # Consistency Matrix
        name_was_queried = match_type == "catalog_search" and norm_query in normalize_identifier(matched_record["product_name"])
        sku_was_queried = match_type == "sku"
        batch_was_queried = match_type == "batch"
        serial_was_queried = match_type == "serial"
        consistency_matrix = [
            ConsistencyField(
                field="Product Commercial Name",
                submitted=raw_query,
                registered=matched_record["product_name"],
                status="match" if name_was_queried else "unverified",
                diagnostic_rationale="Product name query matched this sample record." if name_was_queried else "Product name was not submitted; this is a field from the matched sample record."
            ),
            ConsistencyField(
                field="Brand Authority",
                submitted=submitted_brand or "Not submitted",
                registered=matched_record["brand_name"],
                status="conflict" if brand_conflict else ("match" if submitted_brand else "unverified"),
                diagnostic_rationale="Submitted brand conflicts with the stored field." if brand_conflict else ("Submitted brand matches the stored field; issuer credentials are not verified." if submitted_brand else "Brand was not submitted; issuer credentials are not verified.")
            ),
            ConsistencyField(
                field="Model SKU",
                submitted=submitted_model or (raw_query if sku_was_queried else "Not submitted"),
                registered=matched_record["model_sku"],
                status="conflict" if model_conflict else ("match" if submitted_model or sku_was_queried else "unverified"),
                diagnostic_rationale="Model identifier conflicts with the stored record." if model_conflict else ("Model identifier matched the stored record." if submitted_model or sku_was_queried else "Model SKU was not submitted; this is a field from the matched sample record.")
            ),
            ConsistencyField(
                field="Batch / Lot Code",
                submitted=submitted_batch or (raw_query if batch_was_queried else "Not submitted"),
                registered=matched_record["batch_number"] or "N/A",
                status="conflict" if (batch_status in ("flagged", "recalled") or batch_conflict) else ("match" if submitted_batch or batch_was_queried else "unverified"),
                diagnostic_rationale=(f"Sample batch status: {batch_status}. {matched_record['status_notes'] or ''}".strip() if batch_status != "active" else ("Submitted batch matches the stored sample field." if submitted_batch or batch_was_queried else "Batch was not submitted; production is not verified."))
            ),
            ConsistencyField(
                field="Unit Serial Number",
                submitted=raw_query if serial_was_queried else "Not submitted",
                registered=matched_record["serial_number"] or "Batch-Level Registration",
                status="conflict" if ident_status in ("flagged_cloned", "recalled") else ("match" if serial_was_queried else "unverified"),
                diagnostic_rationale=(f"Recorded lookup count: {current_scan_count}; configured identifier warning is present." if ident_status in ("flagged_cloned", "recalled") else (f"Serial matched the stored sample record; recorded lookup count: {current_scan_count}." if serial_was_queried else "Serial number was not submitted; this is a field from the matched sample record."))
            )
        ]

        # Record scan event in database
        cursor.execute("""
            INSERT INTO scan_events (id, identifier_id, product_id, user_id, submitted_query, query_type, outcome, risk_score, anomaly_flags, client_ip, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, identifier_id, product_id, user_id, raw_query, query_type, outcome, risk_score, json.dumps(anomaly_flags), client_ip, now_iso))

        return VerificationResponse(
            scan_id=scan_id,
            outcome=outcome,
            outcome_title=outcome_title,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_explanation=risk_explanation,
            scanned_at=now_iso,
            submitted_query=raw_query,
            product_id=product_id,
            product_name=matched_record["product_name"],
            brand_name=matched_record["brand_name"],
            brand_code=matched_record["brand_code"],
            category=matched_record["category"],
            model_sku=matched_record["model_sku"],
            batch_number=matched_record["batch_number"],
            serial_number=matched_record["serial_number"],
            production_facility=matched_record["facility"] or "Not specified",
            production_date=matched_record["production_date"] or "N/A",
            authorized_channels=matched_record["authorized_channels"],
            security_feature=matched_record["security_feature"],
            inspection_notes=matched_record["inspection_notes"],
            product_image_url=matched_record["image_url"],
            scan_count=current_scan_count,
            duplicate_alert=duplicate_alert,
            anomaly_flags=anomaly_flags,
            consistency_matrix=consistency_matrix,
            recommended_actions=recommended_actions,
            integrity_disclosure=INTEGRITY_DISCLOSURE
        )

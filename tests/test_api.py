"""
TruthTag Intelligence Platform — Comprehensive Automated Test Suite
Covers:
1. Valid registered product verification
2. Unknown/unregistered identifier (inconclusive)
3. Duplicate or suspicious identifier (warning + repeat scan tracking)
4. Mismatched product details / metadata conflict
5. Invalid and oversized image uploads
6. Product matching and catalog filtering
7. Multi-retailer price comparison and sorting (lowest price calculation)
8. Historical price tracking calculations (90-day trend, min, max, average, deal rating)
9. Price-drop alert conditions and watchlist operations
10. Authentication (registration, login, JWT issuance and token validation)
11. Role-based authorization & unauthorized modification prevention
12. Bulk record import validation and error handling
13. Health-check and analytics calculation from real stored data
"""

import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db
from backend.seed_data import seed_database
from PIL import Image

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    seed_database()

@pytest.fixture
def client():
    return TestClient(app)

# -----------------------------------------------------------------------------
# 1. System Health & Sanity
# -----------------------------------------------------------------------------
def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "sqlite3_wal_active"
    assert data["registered_products"] >= 6
    assert data["registered_identifiers"] >= 6

# -----------------------------------------------------------------------------
# 2. Product Authenticity Verification
# -----------------------------------------------------------------------------
def test_verify_valid_registered_product(client):
    """Test verification of a clean registered product (AuraSound Headphones)."""
    res = client.post("/api/verify", json={"query": "SN-772109"})
    assert res.status_code == 200
    data = res.json()
    assert data["outcome"] == "match"
    assert "Record Match" in data["outcome_title"]
    assert data["product_name"] == "AuraSound Apex Pro Wireless ANC Headphones"
    assert data["brand_name"] == "AuraSound Labs"
    assert data["model_sku"] == "AUD-9921-X"
    assert data["batch_number"] == "B24-8891"
    assert data["risk_score"] < 40.0
    assert len(data["consistency_matrix"]) == 5
    assert sum(c["status"] == "match" for c in data["consistency_matrix"]) == 1
    assert sum(c["status"] == "unverified" for c in data["consistency_matrix"]) == 4

def test_query_type_restricts_identifier_matching(client):
    wrong_type = client.post("/api/verify", json={"query": "AUD-9921-X", "query_type": "serial"})
    sku_match = client.post("/api/verify", json={"query": "AUD-9921-X", "query_type": "sku"})
    batch_match = client.post("/api/verify", json={"query": "B24-8891", "query_type": "batch"})

    assert wrong_type.status_code == 200
    assert wrong_type.json()["outcome"] == "inconclusive"
    assert sku_match.status_code == 200
    assert sku_match.json()["outcome"] == "match"
    assert batch_match.status_code == 200
    assert batch_match.json()["outcome"] == "match"

def test_verification_rejects_whitespace_only_query(client):
    res = client.post("/api/verify", json={"query": "   "})
    assert res.status_code == 422
    assert "Query must not be blank" in res.text

def test_verify_unknown_identifier_inconclusive(client):
    """Test verification of an unknown serial/barcode returns Inconclusive, not Genuine."""
    res = client.post("/api/verify", json={"query": "FAKE-UNKNOWN-BARCODE-9999"})
    assert res.status_code == 200
    data = res.json()
    assert data["outcome"] == "inconclusive"
    assert data["outcome_title"] == "Verification Inconclusive"
    assert data["product_id"] is None
    assert "IDENTIFIER_NOT_FOUND_IN_LEDGER" in data["anomaly_flags"]
    assert data["risk_score"] >= 60.0
    assert len(data["recommended_actions"]) > 0

def test_verify_flagged_counterfeit_batch(client):
    """Test verification of a known flagged counterfeit batch (NordicShield parka)."""
    res = client.post("/api/verify", json={"query": "NS-8800"})
    assert res.status_code == 200
    data = res.json()
    assert data["outcome"] == "warning"
    assert "SAMPLE_BATCH_FLAGGED" in data["anomaly_flags"]
    assert data["risk_score"] >= 50.0

def test_verify_duplicate_scan_tracking(client):
    """Test that scanning a unique serial number multiple times increments scan count and triggers duplicate alert."""
    # First query for Chronos watch
    res1 = client.post("/api/verify", json={"query": "SN-88203"})
    assert res1.status_code == 200
    count1 = res1.json()["scan_count"]

    # Second query for same serial
    res2 = client.post("/api/verify", json={"query": "SN-88203"})
    assert res2.status_code == 200
    count2 = res2.json()["scan_count"]
    assert count2 == count1 + 1
    assert res2.json()["duplicate_alert"] is True
    assert "DUPLICATE_SCAN_DETECTED" in res2.json()["anomaly_flags"]

def test_verify_metadata_mismatch_conflict(client):
    """Test that submitting an incorrect model SKU alongside a valid serial triggers metadata conflict."""
    res = client.post("/api/verify", json={
        "query": "SN-772109",
        "submitted_model": "INCORRECT-MODEL-999"
    })
    assert res.status_code == 200
    data = res.json()
    assert "MODEL_METADATA_MISMATCH" in data["anomaly_flags"]
    # Consistency matrix should have conflict for Model SKU
    sku_row = next(r for r in data["consistency_matrix"] if r["field"] == "Model SKU")
    assert sku_row["status"] == "conflict"
    assert data["outcome"] == "warning"

def test_verify_submitted_brand_mismatch_is_a_warning(client):
    res = client.post("/api/verify", json={
        "query": "SN-772109",
        "submitted_brand": "Different Brand"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["outcome"] == "warning"
    assert "BRAND_METADATA_MISMATCH" in data["anomaly_flags"]
    brand_row = next(r for r in data["consistency_matrix"] if r["field"] == "Brand Authority")
    assert brand_row["status"] == "conflict"

# -----------------------------------------------------------------------------
# 3. Product Image Identification
# -----------------------------------------------------------------------------
def test_image_identification_valid_image(client):
    """Validate that images are accepted without claiming unconfigured image matches."""
    img = Image.new("RGB", (200, 200), color=(30, 45, 35))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    res = client.post(
        "/api/verify/identify-image",
        files={"file": ("aurasound_test.jpg", buf, "image/jpeg")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "unavailable"
    assert data["candidates"] == []
    assert data["manual_search_recommended"] is True
    assert "no image match was attempted" in data["message"].lower()
    assert "IMAGE RECOGNITION DISCLAIMER" in data["disclaimer"]

def test_image_identification_invalid_file_type(client):
    """Test rejection of unsupported file types."""
    res = client.post(
        "/api/verify/identify-image",
        files={"file": ("malicious_script.exe", b"not-an-image", "application/x-msdownload")}
    )
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]

def test_image_identification_oversized_file(client):
    """Test rejection of oversized image files exceeding 10MB."""
    oversized_bytes = b"0" * (11 * 1024 * 1024) # 11MB
    res = client.post(
        "/api/verify/identify-image",
        files={"file": ("giant_photo.jpg", oversized_bytes, "image/jpeg")}
    )
    assert res.status_code == 400
    assert "exceeds maximum allowable size" in res.json()["detail"]

def test_image_identification_rejects_mismatched_content_type(client):
    """Reject payloads whose declared image type does not match their actual encoding."""
    img = Image.new("RGB", (20, 20), color=(30, 45, 35))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    res = client.post(
        "/api/verify/identify-image",
        files={"file": ("product.jpg", buf, "image/jpeg")}
    )
    assert res.status_code == 400
    assert "does not match" in res.json()["detail"]

# -----------------------------------------------------------------------------
# 4. Multi-Retailer Price Comparison & Historical Price Tracking
# -----------------------------------------------------------------------------
def test_retailer_pricing_and_history(client):
    """Test multi-retailer price comparison and 90-day historical tracking."""
    res = client.get("/api/products/prod-001/pricing")
    assert res.status_code == 200
    data = res.json()
    assert data["product_id"] == "prod-001"
    assert len(data["listings"]) >= 4
    # Ensure listings are sorted ascending by total price
    prices = [l["total_price"] for l in data["listings"]]
    assert prices == sorted(prices)
    # Check lowest price indicator
    lowest = [l for l in data["listings"] if l["is_lowest_price"]]
    assert len(lowest) == 1
    # Check historical chart observations
    assert data["total_observations_count"] > 20
    assert len(data["historical_chart_data"]) >= 2
    assert data["lowest_observed_price"] > 0
    assert data["average_observed_price"] > 0
    assert "Historical" in data["deal_rating"] or "Average" in data["deal_rating"] or "Fair" in data["deal_rating"]

def test_pricing_for_nonexistent_product(client):
    res = client.get("/api/products/non-existent-product-id/pricing")
    assert res.status_code == 404

# -----------------------------------------------------------------------------
# 5. Product Trust Report
# -----------------------------------------------------------------------------
def test_generate_product_trust_report(client):
    """Test generation of comprehensive product trust report combining verification and shopping intelligence."""
    res = client.get("/api/trust-report?query=AUD-9921-X")
    assert res.status_code == 200
    data = res.json()
    assert data["report_id"].startswith("TRUTH-REP-")
    assert data["cryptographic_digest"].startswith("SHA256: ")
    assert data["composite_trust_index"] > 50
    assert data["trust_category"] == "Registered Record Matched"
    assert data["pricing_summary"] is not None
    assert len(data["limitations_and_disclaimers"]) > 0
    assert len(data["next_steps"]) > 0

# -----------------------------------------------------------------------------
# 6. User Authentication & Authorization (RBAC)
# -----------------------------------------------------------------------------
def test_user_registration_and_login(client):
    """Test user registration, password hashing, and token issuance."""
    test_user = f"tester_{io.StringIO().getvalue() or '42'}"
    email = "tester_new@example.com"
    pwd = "New-User-Password@2026"

    # Register
    reg_res = client.post("/api/auth/register", json={
        "username": "tester_qa",
        "email": email,
        "password": pwd,
        "role": "user"
    })
    # If already exists from earlier run, login directly
    if reg_res.status_code == 400:
        login_res = client.post("/api/auth/login", json={
            "email_or_username": email,
            "password": pwd
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
    else:
        assert reg_res.status_code == 200
        token = reg_res.json()["access_token"]

    # Verify /api/auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

def test_public_registration_cannot_assign_privileged_roles(client):
    """Reject attempts to provision elevated roles through public registration."""
    res = client.post("/api/auth/register", json={
        "username": "role_escalation",
        "email": "role_escalation@example.com",
        "password": "Unprivileged-Password@2026",
        "role": "admin",
        "brand_id": "brand-001"
    })
    assert res.status_code == 422

def test_invalid_optional_bearer_token_is_rejected(client):
    """A malformed token must not silently downgrade an authenticated route to anonymous."""
    res = client.post(
        "/api/verify",
        json={"query": "SN-772109"},
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert res.status_code == 401

def test_brand_representative_is_limited_to_own_brand(client):
    """Brand representatives can manage their own brand but cannot cross tenant boundaries."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "partner@aurasound.com",
        "password": "Test-Partner-Only@2026"
    })
    assert login_res.status_code == 200
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    foreign_product = client.post("/api/admin/products", json={
        "brand_id": "brand-002",
        "name": "Unauthorized Product",
        "model_sku": "UNAUTH-001",
        "category": "Electronics"
    }, headers=headers)
    assert foreign_product.status_code == 403

    own_product = client.post("/api/admin/products", json={
        "brand_id": "brand-001",
        "name": "Partner Product",
        "model_sku": "PARTNER-001",
        "category": "Electronics"
    }, headers=headers)
    assert own_product.status_code == 200

    foreign_batch = client.post("/api/admin/batches", json={
        "product_id": "prod-002",
        "batch_number": "FOREIGN-BATCH",
        "facility": "Test facility",
        "production_date": "2026-10-08"
    }, headers=headers)
    assert foreign_batch.status_code == 403

    own_batch = client.post("/api/admin/batches", json={
        "product_id": own_product.json()["product_id"],
        "batch_number": "PARTNER-BATCH",
        "facility": "Test facility",
        "production_date": "2026-10-08",
        "serial_numbers": ["PARTNER-SERIAL-001"]
    }, headers=headers)
    assert own_batch.status_code == 200
    assert own_batch.json()["enrolled_units_count"] == 1

    foreign_import = client.post("/api/admin/bulk-import", json={
        "records": [{
            "name": "Foreign Brand Product",
            "model_sku": "VTL-402",
            "batch_number": "FOREIGN-IMPORT"
        }]
    }, headers=headers)
    assert foreign_import.status_code == 200
    assert foreign_import.json()["success_count"] == 0
    assert foreign_import.json()["error_count"] == 1

def test_batch_registration_rejects_an_already_registered_serial(client):
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "partner@aurasound.com",
        "password": "Test-Partner-Only@2026"
    })
    token = login_res.json()["access_token"]
    res = client.post("/api/admin/batches", json={
        "product_id": "prod-001",
        "batch_number": "DUPLICATE-SERIAL-TEST",
        "facility": "Test facility",
        "production_date": "2026-10-08",
        "serial_numbers": ["SN-772109"]
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"]

def test_brand_representative_incidents_are_scoped_to_brand(client):
    """Brand representatives only see incident reports linked to their own catalog."""
    client.post("/api/incidents", json={
        "reporter_name": "Aura Reporter",
        "reporter_email": "aura-reporter@example.com",
        "inquiry_type": "counterfeit_report",
        "product_identifier": "AUD-9921-X",
        "message": "This report is linked to the AuraSound catalog."
    })
    client.post("/api/incidents", json={
        "reporter_name": "Nordic Reporter",
        "reporter_email": "nordic-reporter@example.com",
        "inquiry_type": "counterfeit_report",
        "product_identifier": "NS-8800",
        "message": "This report is linked to the NordicShield catalog."
    })
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "partner@aurasound.com",
        "password": "Test-Partner-Only@2026"
    })
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.get("/api/admin/incidents", headers=headers)
    assert res.status_code == 200
    reporters = {incident["reporter_name"] for incident in res.json()}
    assert "Aura Reporter" in reporters
    assert "Nordic Reporter" not in reporters
    assert "Elena Rostova" not in reporters

def test_unauthorized_user_cannot_access_admin_endpoints(client):
    """Test that normal users are forbidden from accessing admin endpoints (RBAC)."""
    # Login as consumer user
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "user@example.com",
        "password": "Test-User-Only@2026"
    })
    assert login_res.status_code == 200
    user_token = login_res.json()["access_token"]

    # Attempt to access admin incidents list
    admin_res = client.get("/api/admin/incidents", headers={"Authorization": f"Bearer {user_token}"})
    assert admin_res.status_code == 403
    assert "Access denied" in admin_res.json()["detail"]

def test_admin_can_access_admin_endpoints(client):
    """Test that admin user has full access to admin incident portal."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "admin@truthtag.io",
        "password": "Test-Admin-Only@2026"
    })
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]

    admin_res = client.get("/api/admin/incidents", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200
    assert isinstance(admin_res.json(), list)

# -----------------------------------------------------------------------------
# 7. Watchlist & Price Alerts
# -----------------------------------------------------------------------------
def test_watchlist_operations(client):
    """Test adding product to watchlist, setting target price, and deleting."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "user@example.com",
        "password": "Test-User-Only@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add to watchlist with target price $350 (should trigger alert if price <= $350)
    add_res = client.post("/api/user/watchlist", json={
        "product_id": "prod-001",
        "target_price": 350.0
    }, headers=headers)
    assert add_res.status_code == 200
    assert add_res.json()["alert_triggered"] is True

    # Retrieve watchlist
    get_res = client.get("/api/user/watchlist", headers=headers)
    assert get_res.status_code == 200
    items = get_res.json()
    assert any(i["product_id"] == "prod-001" for i in items)

    # Delete from watchlist
    del_res = client.delete("/api/user/watchlist/prod-001", headers=headers)
    assert del_res.status_code == 200

# -----------------------------------------------------------------------------
# 8. Counterfeit Incident Reporting
# -----------------------------------------------------------------------------
def test_report_counterfeit_incident(client):
    """Test reporting a suspicious counterfeit incident."""
    res = client.post("/api/incidents", json={
        "reporter_name": "Marcus Vance",
        "reporter_email": "marcus@company.com",
        "inquiry_type": "counterfeit_report",
        "product_identifier": "AUD-9921-X",
        "message": "Encountered a duplicate serial number at a third-party discount kiosk."
    })
    assert res.status_code == 200
    data = res.json()
    assert data["id"].startswith("INC-")
    assert data["status"] == "pending"

# -----------------------------------------------------------------------------
# 9. Real Stored Data Analytics Dashboard
# -----------------------------------------------------------------------------
def test_analytics_dashboard_metrics(client):
    """Test that analytics are calculated from actual database records."""
    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total_verifications"] > 0
    assert data["active_registered_products"] >= 6
    assert data["total_price_observations"] > 20
    assert data["supported_retailers"] >= 6
    assert len(data["recent_scans"]) > 0
    assert isinstance(data["category_distribution"], dict)

# -----------------------------------------------------------------------------
# 10. Bulk Import Records
# -----------------------------------------------------------------------------
def test_bulk_import_validation(client):
    """Test bulk import with valid records and invalid records error handling."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "admin@truthtag.io",
        "password": "Test-Admin-Only@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    bulk_payload = {
        "records": [
            {
                "name": "Lumina Quantum Studio Monitors",
                "model_sku": "LUM-Q500",
                "category": "Electronics",
                "batch_number": "B-2026-LQ",
                "serial_number": "SN-LUM-001",
                "description": "High-fidelity studio reference monitors."
            },
            {
                # Missing required SKU to test error reporting
                "name": "Invalid Record Without SKU",
                "category": "Electronics"
            }
        ]
    }

    res = client.post("/api/admin/bulk-import", json=bulk_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success_count"] == 1
    assert data["error_count"] == 1
    assert "Missing required fields" in data["errors"][0]

def test_bulk_import_rejects_malformed_and_oversized_fields(client):
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "admin@truthtag.io",
        "password": "Test-Admin-Only@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/admin/bulk-import", json={
        "records": [
            {"name": "Malformed Category Product", "model_sku": "MALFORMED-001", "category": {"unexpected": "object"}},
            {"name": "Oversized SKU Product", "model_sku": "X" * 101}
        ]
    }, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["success_count"] == 0
    assert data["error_count"] == 2
    assert "Expected text values for category" in data["errors"][0]
    assert "maximum length for model_sku" in data["errors"][1]

def test_demo_seed_refuses_production_environment(monkeypatch):
    monkeypatch.setenv("TRUTHTAG_ENV", "production")
    with pytest.raises(RuntimeError, match="disabled outside development and test"):
        seed_database()

# -----------------------------------------------------------------------------
# 11. Security Headers & Rate Limiting Defense
# -----------------------------------------------------------------------------
def test_security_headers_enforced(client):
    """Test that all API responses include strict browser security headers."""
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"
    assert res.headers["x-xss-protection"] == "1; mode=block"
    assert res.headers["referrer-policy"] == "strict-origin-when-cross-origin"

def test_sliding_window_rate_limiter_unit_logic(monkeypatch):
    """Test that SlidingWindowRateLimiter correctly throttles after exceeding threshold."""
    from backend.main import SlidingWindowRateLimiter
    monkeypatch.setenv("TRUTHTAG_ENV", "production")
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60)
    assert limiter.is_allowed("192.168.1.100") is True
    assert limiter.is_allowed("192.168.1.100") is True
    assert limiter.is_allowed("192.168.1.100") is False
    # Different IP should still be allowed
    assert limiter.is_allowed("192.168.1.101") is True

# -----------------------------------------------------------------------------
# 12. Incident Filtering, Audit History & User Isolation
# -----------------------------------------------------------------------------
def test_incident_search_and_pagination(client):
    """Test that administrators can filter and paginate incidents."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "admin@truthtag.io",
        "password": "Test-Admin-Only@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Search existing seed incident for Elena
    res_search = client.get("/api/admin/incidents?search=Elena&limit=10&offset=0", headers=headers)
    assert res_search.status_code == 200
    incidents = res_search.json()
    assert len(incidents) >= 1
    assert any("Elena" in inc["reporter_name"] for inc in incidents)

    # Search with nonexistent term
    res_empty = client.get("/api/admin/incidents?search=NONEXISTENT_QUERY_9999", headers=headers)
    assert res_empty.status_code == 200
    assert len(res_empty.json()) == 0

def test_incident_status_update_with_audit_trail(client):
    """Test that updating an incident status persists an audit history log."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "admin@truthtag.io",
        "password": "Test-Admin-Only@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create new incident
    create_res = client.post("/api/incidents", json={
        "reporter_name": "Audit Trail Tester",
        "reporter_email": "audittrail@example.com",
        "inquiry_type": "counterfeit_report",
        "product_identifier": "AUD-9921-X",
        "message": "Testing incident status transition and history logging."
    })
    assert create_res.status_code == 200
    inc_id = create_res.json()["id"]

    # Update status to under_review
    update_res = client.patch(
        f"/api/admin/incidents/{inc_id}/status",
        json={"status": "under_review", "admin_notes": "Triage review started by senior auditor."},
        headers=headers
    )
    assert update_res.status_code == 200

    # Retrieve incident detail with audit trail
    detail_res = client.get(f"/api/admin/incidents/{inc_id}", headers=headers)
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["status"] == "under_review"
    assert data["admin_notes"] == "Triage review started by senior auditor."
    assert len(data["audit_history"]) >= 1
    audit_entry = data["audit_history"][0]
    assert audit_entry["old_status"] == "pending"
    assert audit_entry["new_status"] == "under_review"
    assert "Triage review" in audit_entry["admin_notes"]

def test_user_cannot_access_another_users_incident(client):
    """Verify that ordinary users cannot access private reports filed by others."""
    # User 1 registers and logs in
    user1_email = "owner_user@example.com"
    reg1 = client.post("/api/auth/register", json={
        "username": "owner_user",
        "email": user1_email,
        "password": "OwnerUser-Password@2026",
        "role": "user"
    })
    token1 = reg1.json()["access_token"] if reg1.status_code == 200 else client.post("/api/auth/login", json={
        "email_or_username": user1_email, "password": "OwnerUser-Password@2026"
    }).json()["access_token"]

    # User 1 files a report
    inc_res = client.post(
        "/api/incidents",
        json={
            "reporter_name": "Owner User",
            "reporter_email": user1_email,
            "inquiry_type": "counterfeit_report",
            "product_identifier": "AUD-9921-X",
            "message": "This is a private consumer report."
        },
        headers={"Authorization": f"Bearer {token1}"}
    )
    inc_id = inc_res.json()["id"]

    # User 2 registers and logs in
    user2_email = "intruder_user@example.com"
    reg2 = client.post("/api/auth/register", json={
        "username": "intruder_user",
        "email": user2_email,
        "password": "IntruderUser-Password@2026",
        "role": "user"
    })
    token2 = reg2.json()["access_token"] if reg2.status_code == 200 else client.post("/api/auth/login", json={
        "email_or_username": user2_email, "password": "IntruderUser-Password@2026"
    }).json()["access_token"]

    # User 2 attempts to fetch User 1's report directly
    unauth_res = client.get(f"/api/incidents/{inc_id}", headers={"Authorization": f"Bearer {token2}"})
    assert unauth_res.status_code == 403
    assert "Access denied" in unauth_res.json()["detail"]

    # User 1 can view their own report
    auth_res = client.get(f"/api/incidents/{inc_id}", headers={"Authorization": f"Bearer {token1}"})
    assert auth_res.status_code == 200
    assert auth_res.json()["id"] == inc_id

# -----------------------------------------------------------------------------
# 13. Admin Identifier Management & Scans
# -----------------------------------------------------------------------------
def test_admin_identifier_status_management(client):
    """Test that administrators can update identifier status and view scan history."""
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "admin@truthtag.io",
        "password": "Test-Admin-Only@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Update identifier status
    patch_res = client.patch(
        "/api/admin/identifiers/ident-001/status",
        json={"status": "flagged_cloned"},
        headers=headers
    )
    assert patch_res.status_code == 200

    # View scan history
    scans_res = client.get("/api/admin/identifiers/ident-001/scans", headers=headers)
    assert scans_res.status_code == 200
    assert "scans" in scans_res.json()

    # Revert to active
    revert_res = client.patch(
        "/api/admin/identifiers/ident-001/status",
        json={"status": "active"},
        headers=headers
    )
    assert revert_res.status_code == 200

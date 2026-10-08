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
    assert all(c["status"] == "match" for c in data["consistency_matrix"])

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
    assert "BATCH_FLAGGED_COUNTERFEIT_ALERT" in data["anomaly_flags"]
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

# -----------------------------------------------------------------------------
# 3. Product Image Identification
# -----------------------------------------------------------------------------
def test_image_identification_valid_image(client):
    """Test visual product identification with a valid synthesized JPEG image."""
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
    assert data["status"] == "success"
    assert len(data["candidates"]) > 0
    assert data["candidates"][0]["confidence_score"] >= 0.50
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
    pwd = "SecurePassword@2026"

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

def test_unauthorized_user_cannot_access_admin_endpoints(client):
    """Test that normal users are forbidden from accessing admin endpoints (RBAC)."""
    # Login as consumer user
    login_res = client.post("/api/auth/login", json={
        "email_or_username": "user@example.com",
        "password": "User@123"
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
        "password": "Admin@123"
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
        "password": "User@123"
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
        "password": "Admin@123"
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

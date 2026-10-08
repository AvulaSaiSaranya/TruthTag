"""
TruthTag Intelligence Platform — Master FastAPI Application
Production-style backend exposing REST APIs for authenticity verification,
image identification, multi-retailer price tracking, and administrative controls.
"""

import os
import uuid
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from .database import init_db, get_db
from .seed_data import seed_database
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_current_user,
    require_role
)
from .models import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthTokenResponse,
    VerifyRequest,
    VerificationResponse,
    ImageIdentificationResponse,
    ProductPricingResponse,
    TrustReportResponse,
    WatchlistCreateRequest,
    WatchlistResponse,
    IncidentCreateRequest,
    IncidentResponse,
    IncidentStatusUpdateRequest,
    ProductCreateRequest,
    BatchCreateRequest,
    BulkImportRequest,
    BulkImportResponse,
    AnalyticsDashboardResponse
)
from .verification_service import run_verification
from .image_service import identify_product_image
from .pricing_service import (
    get_product_pricing,
    add_to_watchlist,
    get_user_watchlist,
    remove_from_watchlist
)
from .trust_report_service import generate_product_trust_report

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB and seed dataset on startup
    init_db()
    seed_database()
    yield

app = FastAPI(
    title="TruthTag Intelligence API",
    description="Product Authenticity Verification and Shopping Intelligence Platform Engine",
    version="3.9.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# 1. System Health & Metadata
# -----------------------------------------------------------------------------
@app.get("/api/health", tags=["System"])
def get_health():
    """Health-check endpoint reporting node status and ledger operational state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        p_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM identifiers")
        i_count = cursor.fetchone()[0]
    return {
        "status": "healthy",
        "ledger_node": "TruthTag Cryptographic Node London-01",
        "version": "3.9.0-prod",
        "database": "sqlite3_wal_active",
        "registered_products": p_count,
        "registered_identifiers": i_count
    }

# -----------------------------------------------------------------------------
# 2. Authentication & User Profile
# -----------------------------------------------------------------------------
@app.post("/api/auth/register", response_model=AuthTokenResponse, tags=["Authentication"])
def register_user(req: UserRegisterRequest):
    """Register a new user account with secure password hashing."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (req.email, req.username))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already registered.")
        
        user_id = "usr-" + uuid.uuid4().hex[:10]
        hashed = hash_password(req.password)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, brand_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, req.username, req.email, hashed, req.role, req.brand_id))

        token = create_access_token({"sub": user_id, "role": req.role, "username": req.username})

        user_resp = UserResponse(
            id=user_id,
            username=req.username,
            email=req.email,
            role=req.role,
            brand_id=req.brand_id,
            created_at=str(datetime.now())
        )
        return AuthTokenResponse(access_token=token, user=user_resp)

@app.post("/api/auth/login", response_model=AuthTokenResponse, tags=["Authentication"])
def login_user(req: UserLoginRequest):
    """Authenticate user and return JWT bearer token."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, password_hash, role, brand_id, created_at
            FROM users
            WHERE email = ? OR username = ?
        """, (req.email_or_username, req.email_or_username))
        user = cursor.fetchone()

        if not user or not verify_password(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email/username or password.")

        token = create_access_token({"sub": user["id"], "role": user["role"], "username": user["username"]})
        user_resp = UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            brand_id=user["brand_id"],
            created_at=str(user["created_at"])
        )
        return AuthTokenResponse(access_token=token, user=user_resp)

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_current_user_profile(user: dict = Depends(get_current_user)):
    """Return profile of currently logged-in user."""
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        role=user["role"],
        brand_id=user["brand_id"],
        created_at=str(user["created_at"])
    )

# -----------------------------------------------------------------------------
# 3. Product Authenticity Verification
# -----------------------------------------------------------------------------
@app.post("/api/verify", response_model=VerificationResponse, tags=["Verification"])
def verify_identifier(
    req: VerifyRequest,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    """
    Verify submitted serial number, QR matrix payload, model SKU, or batch number.
    Tracks scan velocity, detects duplicate cloning anomalies, and evaluates consistency.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_id = current_user["id"] if current_user else None

    return run_verification(
        query=req.query,
        query_type=req.query_type,
        submitted_brand=req.submitted_brand,
        submitted_model=req.submitted_model,
        submitted_batch=req.submitted_batch,
        user_id=user_id,
        client_ip=client_ip
    )

# -----------------------------------------------------------------------------
# 4. Product Image Identification
# -----------------------------------------------------------------------------
@app.post("/api/verify/identify-image", response_model=ImageIdentificationResponse, tags=["Verification"])
async def upload_and_identify_image(file: UploadFile = File(...)):
    """
    Ingest a product image, validate file integrity and size, and perform perceptual
    visual product-matching to identify probable models and categories.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload JPEG, PNG, or WebP images."
        )

    file_bytes = await file.read()
    try:
        result = identify_product_image(
            file_bytes=file_bytes,
            file_name=file.filename or "uploaded_image.jpg",
            content_type=file.content_type
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

# -----------------------------------------------------------------------------
# 5. Multi-Retailer Price Comparison & Historical Tracking
# -----------------------------------------------------------------------------
@app.get("/api/products/{product_id}/pricing", response_model=ProductPricingResponse, tags=["Pricing"])
def get_product_pricing_endpoint(product_id: str):
    """
    Fetch multi-retailer listings with current observed prices, shipping,
    authorized status, deal ratings, and 90-day historical chart points.
    """
    pricing = get_product_pricing(product_id)
    if not pricing:
        raise HTTPException(status_code=404, detail="Product not found.")
    return pricing

# -----------------------------------------------------------------------------
# 6. Product Trust Report
# -----------------------------------------------------------------------------
@app.get("/api/trust-report", response_model=TrustReportResponse, tags=["Trust Report"])
def get_trust_report(
    query: str = Query(..., min_length=1, description="Serial number, SKU, or batch code"),
    request: Request = None,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    """
    Synthesize an executive-grade Product Trust Report combining verification evidence,
    retailer authorization, duplicate scan velocity, and historical price stability.
    """
    client_ip = request.client.host if request and request.client else "127.0.0.1"
    user_id = current_user["id"] if current_user else None
    return generate_product_trust_report(
        identifier_or_sku=query,
        user_id=user_id,
        client_ip=client_ip
    )

# -----------------------------------------------------------------------------
# 7. Products Catalog
# -----------------------------------------------------------------------------
@app.get("/api/products", tags=["Catalog"])
def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Browse all registered baseline products."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT p.id, p.name, p.model_sku, p.category, p.description, p.image_url,
                   p.security_feature, p.authorized_channels, p.inspection_notes, p.created_at,
                   b.name as brand_name, b.code as brand_code
            FROM products p
            JOIN brands b ON p.brand_id = b.id
            WHERE 1=1
        """
        params = []
        if category and category.lower() != "all":
            query += " AND LOWER(p.category) = LOWER(?)"
            params.append(category)
        if search:
            query += " AND (LOWER(p.name) LIKE ? OR LOWER(p.model_sku) LIKE ? OR LOWER(b.name) LIKE ?)"
            s = f"%{search.lower()}%"
            params.extend([s, s, s])
        
        query += " ORDER BY p.name ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@app.get("/api/products/{product_id}", tags=["Catalog"])
def get_product(product_id: str):
    """Get single product detail including active batches."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, b.name as brand_name, b.code as brand_code
            FROM products p
            JOIN brands b ON p.brand_id = b.id
            WHERE p.id = ?
        """, (product_id,))
        prod = cursor.fetchone()
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found.")
        
        cursor.execute("SELECT * FROM batches WHERE product_id = ?", (product_id,))
        batches = cursor.fetchall()
        
        d = dict(prod)
        d["batches"] = [dict(b) for b in batches]
        return d

# -----------------------------------------------------------------------------
# 8. User Watchlist & Price Alerts
# -----------------------------------------------------------------------------
@app.get("/api/user/watchlist", response_model=List[WatchlistResponse], tags=["User Dashboard"])
def get_watchlist(current_user: dict = Depends(get_current_user)):
    """Retrieve saved products and price drop alerts for authenticated user."""
    return get_user_watchlist(current_user["id"])

@app.post("/api/user/watchlist", tags=["User Dashboard"])
def add_watchlist_item(req: WatchlistCreateRequest, current_user: dict = Depends(get_current_user)):
    """Save product to user's watchlist with an optional target price."""
    try:
        result = add_to_watchlist(current_user["id"], req.product_id, req.target_price)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@app.delete("/api/user/watchlist/{product_id}", tags=["User Dashboard"])
def remove_watchlist_item(product_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a product from user's watchlist."""
    success = remove_from_watchlist(current_user["id"], product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found in watchlist.")
    return {"status": "success", "message": "Product removed from watchlist."}

@app.get("/api/user/history", tags=["User Dashboard"])
def get_user_scan_history(current_user: dict = Depends(get_current_user)):
    """Get scan and verification audit trail for the authenticated user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.submitted_query, s.query_type, s.outcome, s.risk_score,
                   s.anomaly_flags, s.scanned_at,
                   p.name as product_name, p.model_sku,
                   i.serial_number
            FROM scan_events s
            LEFT JOIN products p ON s.product_id = p.id
            LEFT JOIN identifiers i ON s.identifier_id = i.id
            WHERE s.user_id = ?
            ORDER BY s.scanned_at DESC
            LIMIT 50
        """, (current_user["id"],))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["anomaly_flags"] = json.loads(d["anomaly_flags"]) if d["anomaly_flags"] else []
            result.append(d)
        return result

# -----------------------------------------------------------------------------
# 9. Counterfeit Incidents & User Reports
# -----------------------------------------------------------------------------
@app.post("/api/incidents", response_model=IncidentResponse, tags=["Incidents"])
def report_counterfeit_incident(
    req: IncidentCreateRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    """File a suspicious packaging or cloned serial number incident report."""
    inc_id = "INC-" + uuid.uuid4().hex[:8].upper()
    now_str = str(datetime.now())
    user_id = current_user["id"] if current_user else None

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO incidents (id, user_id, reporter_name, reporter_email, inquiry_type, product_identifier, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (inc_id, user_id, req.reporter_name, req.reporter_email, req.inquiry_type, req.product_identifier, req.message))

    return IncidentResponse(
        id=inc_id,
        reporter_name=req.reporter_name,
        reporter_email=req.reporter_email,
        inquiry_type=req.inquiry_type,
        product_identifier=req.product_identifier,
        message=req.message,
        status="pending",
        admin_notes=None,
        created_at=now_str
    )

@app.get("/api/user/incidents", response_model=List[IncidentResponse], tags=["User Dashboard"])
def get_user_submitted_incidents(current_user: dict = Depends(get_current_user)):
    """Retrieve incidents reported by the logged-in user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
        rows = cursor.fetchall()
        return [IncidentResponse(**dict(r)) for r in rows]

# -----------------------------------------------------------------------------
# 10. Real Stored Data Analytics Dashboard
# -----------------------------------------------------------------------------
@app.get("/api/analytics/dashboard", response_model=AnalyticsDashboardResponse, tags=["Analytics"])
def get_analytics_dashboard():
    """
    Return comprehensive analytics calculated dynamically from actual stored database records.
    Never fabricates random data.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Total verification events
        cursor.execute("SELECT COUNT(*) FROM scan_events")
        total_scans = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scan_events WHERE outcome = 'match'")
        matches = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scan_events WHERE outcome = 'warning'")
        warnings = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scan_events WHERE outcome = 'inconclusive'")
        inconclusive = cursor.fetchone()[0]

        # Duplicate scan alerts
        cursor.execute("SELECT COUNT(*) FROM identifiers WHERE scan_count > 1")
        dupe_count = cursor.fetchone()[0]

        # Active products & batches
        cursor.execute("SELECT COUNT(*) FROM products")
        active_prods = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM batches WHERE status = 'active'")
        active_batches = cursor.fetchone()[0]

        # Retailer & price coverage
        cursor.execute("SELECT COUNT(*) FROM price_observations")
        total_obs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM retailers")
        retailers_count = cursor.fetchone()[0]

        # Recent 10 scans
        cursor.execute("""
            SELECT s.id, s.submitted_query, s.outcome, s.risk_score, s.scanned_at,
                   p.name as product_name
            FROM scan_events s
            LEFT JOIN products p ON s.product_id = p.id
            ORDER BY s.scanned_at DESC
            LIMIT 10
        """)
        recent_scans = [dict(r) for r in cursor.fetchall()]

        # Category distribution
        cursor.execute("SELECT category, COUNT(*) as count FROM products GROUP BY category")
        cat_dist = {r["category"]: r["count"] for r in cursor.fetchall()}

        # Top counterfeit risk models
        cursor.execute("""
            SELECT p.name, p.model_sku, COUNT(s.id) as alert_count
            FROM scan_events s
            JOIN products p ON s.product_id = p.id
            WHERE s.outcome = 'warning'
            GROUP BY p.id
            ORDER BY alert_count DESC
            LIMIT 5
        """)
        top_risks = [dict(r) for r in cursor.fetchall()]

        match_rate = round((matches / total_scans * 100), 1) if total_scans > 0 else 0.0
        warning_rate = round((warnings / total_scans * 100), 1) if total_scans > 0 else 0.0

        return AnalyticsDashboardResponse(
            total_verifications=total_scans,
            matched_count=matches,
            warning_count=warnings,
            inconclusive_count=inconclusive,
            match_rate_pct=match_rate,
            warning_rate_pct=warning_rate,
            duplicate_scan_alerts=dupe_count,
            active_registered_products=active_prods,
            active_batches=active_batches,
            total_price_observations=total_obs,
            supported_retailers=retailers_count,
            recent_scans=recent_scans,
            category_distribution=cat_dist,
            top_counterfeit_risk_models=top_risks
        )

# -----------------------------------------------------------------------------
# 11. Brand Portal & Administration Endpoints (RBAC Protected)
# -----------------------------------------------------------------------------
@app.post("/api/admin/products", tags=["Brand & Admin Portal"])
def create_product_admin(
    req: ProductCreateRequest,
    current_user: dict = Depends(require_role(["brand_rep", "admin"]))
):
    """Register a new product in the brand ledger."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Verify brand exists
        cursor.execute("SELECT id FROM brands WHERE id = ?", (req.brand_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Brand authority not found.")
        
        prod_id = "prod-" + uuid.uuid4().hex[:8]
        try:
            cursor.execute("""
                INSERT INTO products (id, brand_id, name, model_sku, category, description, image_url, security_feature, authorized_channels, inspection_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (prod_id, req.brand_id, req.name, req.model_sku, req.category, req.description, req.image_url, req.security_feature, req.authorized_channels, req.inspection_notes))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

        return {"status": "success", "product_id": prod_id, "message": f"Product '{req.name}' successfully enrolled."}

@app.post("/api/admin/batches", tags=["Brand & Admin Portal"])
def create_batch_admin(
    req: BatchCreateRequest,
    current_user: dict = Depends(require_role(["brand_rep", "admin"]))
):
    """Enroll a new manufacturing batch and generate serial unit records."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products WHERE id = ?", (req.product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Product ID does not exist.")

        batch_id = "batch-" + uuid.uuid4().hex[:8]
        cursor.execute("""
            INSERT INTO batches (id, product_id, batch_number, facility, production_date, status, status_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (batch_id, req.product_id, req.batch_number, req.facility, req.production_date, req.status, req.status_notes))

        created_serials = []
        for sn in req.serial_numbers:
            ident_id = "ident-" + uuid.uuid4().hex[:8]
            qr_payload = f"https://verify.truthtag.io/audit?code={sn}"
            cursor.execute("""
                INSERT INTO identifiers (id, product_id, batch_id, serial_number, qr_payload, scan_count, status)
                VALUES (?, ?, ?, ?, ?, 0, 'active')
            """, (ident_id, req.product_id, batch_id, sn, qr_payload))
            created_serials.append(sn)

        return {
            "status": "success",
            "batch_id": batch_id,
            "batch_number": req.batch_number,
            "enrolled_units_count": len(created_serials),
            "message": f"Batch '{req.batch_number}' and {len(created_serials)} unit serials enrolled."
        }

@app.post("/api/admin/bulk-import", response_model=BulkImportResponse, tags=["Brand & Admin Portal"])
def bulk_import_records(
    req: BulkImportRequest,
    current_user: dict = Depends(require_role(["brand_rep", "admin"]))
):
    """
    Bulk import products, batches, and serial records with validation and error reporting.
    """
    success_count = 0
    errors = []
    imported_products = []

    with get_db() as conn:
        cursor = conn.cursor()
        # Default brand for import if not specified
        cursor.execute("SELECT id FROM brands LIMIT 1")
        default_brand_id = cursor.fetchone()[0]

        for idx, rec in enumerate(req.records):
            name = rec.get("name")
            sku = rec.get("model_sku") or rec.get("sku")
            category = rec.get("category", "General")
            batch_num = rec.get("batch_number") or rec.get("batch")
            serial_num = rec.get("serial_number") or rec.get("serial")

            if not name or not sku:
                errors.append(f"Row {idx+1}: Missing required fields 'name' or 'model_sku'.")
                continue

            try:
                # Check if product exists
                cursor.execute("SELECT id FROM products WHERE model_sku = ?", (sku,))
                prod = cursor.fetchone()
                if not prod:
                    prod_id = "prod-" + uuid.uuid4().hex[:8]
                    cursor.execute("""
                        INSERT INTO products (id, brand_id, name, model_sku, category, description, security_feature)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (prod_id, default_brand_id, name, sku, category, rec.get("description", ""), rec.get("security_feature", "Holographic Seal")))
                    imported_products.append(name)
                else:
                    prod_id = prod["id"]

                # If batch specified
                if batch_num:
                    cursor.execute("SELECT id FROM batches WHERE product_id = ? AND batch_number = ?", (prod_id, batch_num))
                    batch = cursor.fetchone()
                    if not batch:
                        batch_id = "batch-" + uuid.uuid4().hex[:8]
                        cursor.execute("""
                            INSERT INTO batches (id, product_id, batch_number, facility, production_date)
                            VALUES (?, ?, ?, ?, ?)
                        """, (batch_id, prod_id, batch_num, rec.get("facility", "Central Production Facility"), rec.get("production_date", str(datetime.now().date()))))
                    else:
                        batch_id = batch["id"]

                    # If serial specified
                    if serial_num:
                        cursor.execute("SELECT id FROM identifiers WHERE serial_number = ?", (serial_num,))
                        if not cursor.fetchone():
                            ident_id = "ident-" + uuid.uuid4().hex[:8]
                            cursor.execute("""
                                INSERT INTO identifiers (id, product_id, batch_id, serial_number, qr_payload, scan_count)
                                VALUES (?, ?, ?, ?, ?, 0)
                            """, (ident_id, prod_id, batch_id, serial_num, f"https://verify.truthtag.io/audit?code={serial_num}"))

                success_count += 1
            except Exception as e:
                errors.append(f"Row {idx+1} ({sku}): {str(e)}")

    return BulkImportResponse(
        success_count=success_count,
        error_count=len(errors),
        errors=errors,
        imported_products=imported_products
    )

@app.get("/api/admin/incidents", response_model=List[IncidentResponse], tags=["Brand & Admin Portal"])
def list_all_incidents_admin(current_user: dict = Depends(require_role(["brand_rep", "admin"]))):
    """Triage counterfeit incidents and brand alerts."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [IncidentResponse(**dict(r)) for r in rows]

@app.patch("/api/admin/incidents/{incident_id}/status", tags=["Brand & Admin Portal"])
def update_incident_status(
    incident_id: str,
    req: IncidentStatusUpdateRequest,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Update incident status and administrative review notes."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE incidents
            SET status = ?, admin_notes = ?
            WHERE id = ?
        """, (req.status, req.admin_notes, incident_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Incident not found.")
    return {"status": "success", "message": f"Incident {incident_id} marked as {req.status}."}

@app.get("/api/admin/anomaly-telemetry", tags=["Brand & Admin Portal"])
def get_anomaly_telemetry(current_user: dict = Depends(require_role(["admin", "brand_rep"]))):
    """Get high-risk scan patterns and duplicate serial signals."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.serial_number, i.scan_count, i.last_scanned_at, i.status,
                   p.name as product_name, p.model_sku,
                   b.batch_number
            FROM identifiers i
            JOIN products p ON i.product_id = p.id
            JOIN batches b ON i.batch_id = b.id
            WHERE i.scan_count > 1 OR i.status != 'active'
            ORDER BY i.scan_count DESC
            LIMIT 50
        """)
        dupes = [dict(r) for r in cursor.fetchall()]
        return {"duplicate_signals": dupes}

# -----------------------------------------------------------------------------
# 12. Mount Static Files & Single-Page Application
# -----------------------------------------------------------------------------
STATIC_DIR = Path(__file__).parent.parent

@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/index.html", include_in_schema=False)
async def serve_index_html():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/style.css", include_in_schema=False)
async def serve_style():
    return FileResponse(STATIC_DIR / "style.css", media_type="text/css")

@app.get("/script.js", include_in_schema=False)
async def serve_script():
    return FileResponse(STATIC_DIR / "script.js", media_type="application/javascript")

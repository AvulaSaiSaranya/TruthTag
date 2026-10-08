"""
TruthTag Intelligence Platform — Pydantic Validation Models
Clean schemas for request validation, structured responses, and serialization.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Authentication Schemas ---
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[str] = Field("user", pattern="^(user|brand_rep|admin)$")
    brand_id: Optional[str] = None

class UserLoginRequest(BaseModel):
    email_or_username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    brand_id: Optional[str] = None
    created_at: str

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Verification Schemas ---
class VerifyRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Serial number, QR payload, SKU, or Batch number")
    query_type: Optional[str] = Field("auto", pattern="^(auto|serial|qr|sku|batch)$")
    submitted_brand: Optional[str] = None
    submitted_model: Optional[str] = None
    submitted_batch: Optional[str] = None

class ConsistencyField(BaseModel):
    field: str
    submitted: str
    registered: str
    status: str # 'match', 'conflict', 'unverified'
    diagnostic_rationale: str

class VerificationResponse(BaseModel):
    scan_id: str
    outcome: str # 'match', 'warning', 'inconclusive'
    outcome_title: str
    risk_score: float # 0.0 (Clean/Verified) to 100.0 (High Risk)
    risk_level: str # 'Low Risk', 'Moderate Risk', 'High Risk Anomaly'
    risk_explanation: str
    scanned_at: str
    submitted_query: str
    
    # Matched product data (null if inconclusive)
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    brand_code: Optional[str] = None
    category: Optional[str] = None
    model_sku: Optional[str] = None
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    production_facility: Optional[str] = None
    production_date: Optional[str] = None
    authorized_channels: Optional[str] = None
    security_feature: Optional[str] = None
    inspection_notes: Optional[str] = None
    product_image_url: Optional[str] = None
    
    # Anomaly / Duplicate Scan Signals
    scan_count: int = 1
    duplicate_alert: bool = False
    anomaly_flags: List[str] = []
    
    # Field-by-field consistency matrix
    consistency_matrix: List[ConsistencyField] = []
    
    # Recommended Next Steps & Transparency
    recommended_actions: List[str] = []
    integrity_disclosure: str

# --- Image Identification Schemas ---
class VisualMatchCandidate(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    model_sku: str
    confidence_score: float # 0.0 to 1.0
    similarity_percentage: int
    image_url: Optional[str] = None
    authorized_channels: Optional[str] = None

class ImageIdentificationResponse(BaseModel):
    status: str
    message: str
    uploaded_file_name: str
    candidates: List[VisualMatchCandidate] = []
    manual_search_recommended: bool = False
    disclaimer: str

# --- Retailer Price Comparison Schemas ---
class RetailerListingResponse(BaseModel):
    id: str
    retailer_name: str
    retailer_domain: str
    retailer_logo: Optional[str] = None
    product_url: str
    listing_title: str
    current_price: float
    currency: str
    shipping_price: float
    total_price: float
    availability: str
    warranty_info: Optional[str] = None
    return_policy: Optional[str] = None
    seller_name: str
    is_authorized_seller: bool
    match_confidence: str
    last_checked_at: str
    is_lowest_price: bool = False

class PriceHistoryPoint(BaseModel):
    date: str
    price: float

class ListingPriceHistory(BaseModel):
    retailer_name: str
    history: List[PriceHistoryPoint] = []

class ProductPricingResponse(BaseModel):
    product_id: str
    product_name: str
    model_sku: str
    lowest_observed_price: float
    highest_observed_price: float
    average_observed_price: float
    price_change_90d_pct: float
    deal_rating: str # 'Below Historical Range', 'Fair Market Price', 'Above Average'
    deal_description: str
    listings: List[RetailerListingResponse] = []
    historical_chart_data: List[ListingPriceHistory] = []
    total_observations_count: int
    last_observation_date: str

# --- Product Trust Report Schema ---
class TrustReportResponse(BaseModel):
    report_id: str
    generated_at: str
    cryptographic_digest: str
    
    # Verification dimension
    verification: VerificationResponse
    
    # Pricing dimension
    pricing_summary: Optional[Dict[str, Any]] = None
    
    # Risk Assessment
    composite_trust_index: int # 0 to 100
    trust_category: str # 'Verified Record Matched', 'Suspicious Signals Detected', 'Inconclusive Registry Lookup'
    scoring_methodology: Dict[str, Any]
    limitations_and_disclaimers: List[str]
    next_steps: List[str]

# --- Watchlist & Alerts ---
class WatchlistCreateRequest(BaseModel):
    product_id: str
    target_price: Optional[float] = None

class WatchlistResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    brand_name: str
    model_sku: str
    image_url: Optional[str] = None
    current_lowest_price: float
    target_price: Optional[float] = None
    alert_triggered: bool
    created_at: str

# --- Incidents / Counterfeit Reports ---
class IncidentCreateRequest(BaseModel):
    reporter_name: str = Field(..., min_length=2)
    reporter_email: EmailStr
    inquiry_type: str = Field("counterfeit_report", pattern="^(counterfeit_report|brand_enrollment|audit_request|general)$")
    product_identifier: Optional[str] = None
    message: str = Field(..., min_length=10)

class IncidentResponse(BaseModel):
    id: str
    reporter_name: str
    reporter_email: str
    inquiry_type: str
    product_identifier: Optional[str] = None
    message: str
    status: str
    admin_notes: Optional[str] = None
    created_at: str

class IncidentStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|under_review|resolved|dismissed)$")
    admin_notes: Optional[str] = None

# --- Product & Batch Registration (Brand / Admin) ---
class ProductCreateRequest(BaseModel):
    brand_id: str
    name: str = Field(..., min_length=2)
    model_sku: str = Field(..., min_length=2)
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    security_feature: Optional[str] = "Holographic Void Seal"
    authorized_channels: Optional[str] = None
    inspection_notes: Optional[str] = None

class BatchCreateRequest(BaseModel):
    product_id: str
    batch_number: str
    facility: str
    production_date: str
    status: Optional[str] = "active"
    status_notes: Optional[str] = None
    serial_numbers: List[str] = [] # Optional batch serials to generate

class BulkImportRequest(BaseModel):
    records: List[Dict[str, Any]]

class BulkImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str] = []
    imported_products: List[str] = []

# --- Analytics Dashboard Schema ---
class AnalyticsDashboardResponse(BaseModel):
    total_verifications: int
    matched_count: int
    warning_count: int
    inconclusive_count: int
    match_rate_pct: float
    warning_rate_pct: float
    duplicate_scan_alerts: int
    active_registered_products: int
    active_batches: int
    total_price_observations: int
    supported_retailers: int
    recent_scans: List[Dict[str, Any]] = []
    category_distribution: Dict[str, int] = {}
    top_counterfeit_risk_models: List[Dict[str, Any]] = []

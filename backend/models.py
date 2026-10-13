"""
TruthTag Intelligence Platform — Pydantic Validation Models
Clean schemas for request validation, structured responses, and serialization.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Annotated, Optional, List, Dict, Any
from datetime import datetime

# --- Authentication Schemas ---
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    role: str = Field("user", pattern="^user$")

    @field_validator("username", "email", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

class UserLoginRequest(BaseModel):
    email_or_username: str = Field(..., min_length=1, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email_or_username", mode="before")
    @classmethod
    def strip_login_identifier(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip()

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
    query: str = Field(..., min_length=1, max_length=256, description="Serial number, QR payload, SKU, or batch number")
    query_type: Optional[str] = Field("auto", pattern="^(auto|serial|qr|sku|batch)$")
    submitted_brand: Optional[str] = Field(None, max_length=200)
    submitted_model: Optional[str] = Field(None, max_length=100)
    submitted_batch: Optional[str] = Field(None, max_length=100)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        query = value.strip()
        if not query:
            raise ValueError("Query must not be blank.")
        return query

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
    anomaly_flags: List[str] = Field(default_factory=list)
    
    # Field-by-field consistency matrix
    consistency_matrix: List[ConsistencyField] = Field(default_factory=list)
    
    # Recommended Next Steps & Transparency
    recommended_actions: List[str] = Field(default_factory=list)
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
    candidates: List[VisualMatchCandidate] = Field(default_factory=list)
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
    history: List[PriceHistoryPoint] = Field(default_factory=list)

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
    listings: List[RetailerListingResponse] = Field(default_factory=list)
    historical_chart_data: List[ListingPriceHistory] = Field(default_factory=list)
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
    target_price: Optional[float] = Field(None, gt=0, allow_inf_nan=False)

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
    reporter_name: str = Field(..., min_length=2, max_length=200)
    reporter_email: EmailStr
    inquiry_type: str = Field("counterfeit_report", pattern="^(counterfeit_report|brand_enrollment|audit_request|general)$")
    product_identifier: Optional[str] = Field(None, max_length=256)
    message: str = Field(..., min_length=10, max_length=5000)

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
    admin_notes: Optional[str] = Field(None, max_length=5000)

class IncidentAuditLogResponse(BaseModel):
    id: str
    incident_id: str
    changed_by_user_id: Optional[str] = None
    old_status: str
    new_status: str
    admin_notes: Optional[str] = None
    created_at: str

class IncidentDetailResponse(IncidentResponse):
    audit_history: List[IncidentAuditLogResponse] = Field(default_factory=list)

class IdentifierStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(active|flagged_cloned|recalled)$")
    status_notes: Optional[str] = Field(None, max_length=1000)

# --- Product & Batch Registration (Brand / Admin) ---
class ProductCreateRequest(BaseModel):
    brand_id: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=2, max_length=200)
    model_sku: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=1000)
    security_feature: Optional[str] = Field("Holographic Void Seal", max_length=300)
    authorized_channels: Optional[str] = Field(None, max_length=1000)
    inspection_notes: Optional[str] = Field(None, max_length=2000)

class BatchCreateRequest(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=128)
    batch_number: str = Field(..., min_length=1, max_length=100)
    facility: str = Field(..., min_length=1, max_length=200)
    production_date: str = Field(..., min_length=1, max_length=32)
    status: Optional[str] = Field("active", pattern="^(active|flagged|recalled)$")
    status_notes: Optional[str] = Field(None, max_length=2000)
    serial_numbers: List[Annotated[str, Field(min_length=1, max_length=128)]] = Field(default_factory=list, max_length=1000)

class BulkImportRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., min_length=1, max_length=500)

class BulkImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str] = Field(default_factory=list)
    imported_products: List[str] = Field(default_factory=list)

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
    recent_scans: List[Dict[str, Any]] = Field(default_factory=list)
    category_distribution: Dict[str, int] = Field(default_factory=dict)
    top_counterfeit_risk_models: List[Dict[str, Any]] = Field(default_factory=list)

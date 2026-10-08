"""
TruthTag Intelligence Platform — Authentication & RBAC Engine
Secure password hashing using PBKDF2-HMAC-SHA256 and cryptographic JWT token processing.
Role-Based Access Control (RBAC): user, brand_rep, admin.
"""

import os
import hashlib
import hmac
import base64
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import get_db

SECRET_KEY = os.environ.get("TRUTHTAG_JWT_SECRET")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError("TRUTHTAG_JWT_SECRET must be configured with at least 32 characters.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

security = HTTPBearer(auto_error=False)
PASSWORD_HASH_ITERATIONS = 600_000

def hash_password(password: str) -> str:
    """Generate a PBKDF2-HMAC-SHA256 password hash with a random 16-byte salt."""
    salt = os.urandom(16)
    iterations = PASSWORD_HASH_ITERATIONS
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    derived_b64 = base64.b64encode(derived).decode("ascii")
    return f"pbkdf2:sha256:{iterations}${salt_b64}${derived_b64}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using constant-time comparison to prevent timing side-channels."""
    try:
        header, salt_b64, derived_b64 = hashed_password.split("$")
        iterations = int(header.split(":")[-1])
        salt = base64.b64decode(salt_b64)
        expected_derived = base64.b64decode(derived_b64)
        actual_derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual_derived, expected_derived)
    except Exception:
        return False

def _b64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def _b64_url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("ascii"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    now = int(time.time())
    if expires_delta:
        expire = now + int(expires_delta.total_seconds())
    else:
        expire = now + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {**to_encode, "iat": now, "exp": expire}

    header_b64 = _b64_url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64_url_encode(json.dumps(payload).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64_url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_access_token(token: str) -> dict:
    """Validate and decode signed JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        header_b64, payload_b64, signature_b64 = parts
        header = json.loads(_b64_url_decode(header_b64).decode("utf-8"))
        if not isinstance(header, dict) or header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
            raise ValueError("Unsupported token header")

        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64_url_decode(signature_b64)

        if not hmac.compare_digest(actual_sig, expected_sig):
            raise ValueError("Signature mismatch")
        
        payload = json.loads(_b64_url_decode(payload_b64).decode("utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("exp"), int):
            raise ValueError("Invalid token claims")
        if payload["exp"] <= int(time.time()):
            raise ValueError("Token expired")
        
        return payload
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Retrieve authenticated user if bearer token is present, else None."""
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, brand_id, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found")
        return dict(row)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """Strict authentication dependency returning the current user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, brand_id, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found")
        return dict(row)

def require_role(allowed_roles: List[str]):
    """Role-Based Access Control decorator/dependency."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

"""
TruthTag Intelligence Platform — Database Engine
High-performance SQLite database connection, schema setup, and migration.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(os.environ.get("TRUTHTAG_DB_PATH", Path(__file__).parent.parent / "truthtag.db"))

def get_connection():
    """Return an optimized SQLite connection with foreign keys and WAL enabled."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db():
    """Context manager for transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database tables and indexes."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user', -- 'user', 'brand_rep', 'admin'
            brand_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Brands table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            website TEXT,
            logo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            brand_id TEXT NOT NULL,
            name TEXT NOT NULL,
            model_sku TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            security_feature TEXT,
            authorized_channels TEXT,
            inspection_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE
        );
        """)

        # 4. Batches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            facility TEXT NOT NULL,
            production_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active', -- 'active', 'flagged', 'recalled'
            status_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """)

        # 5. Identifiers table (individual units or serial numbers)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS identifiers (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            batch_id TEXT NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            qr_payload TEXT NOT NULL,
            scan_count INTEGER NOT NULL DEFAULT 0,
            last_scanned_at TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'active', -- 'active', 'flagged_cloned', 'recalled'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
        );
        """)

        # 6. Scan & Verification Events (audit log of verification requests)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_events (
            id TEXT PRIMARY KEY,
            identifier_id TEXT,
            product_id TEXT,
            user_id TEXT,
            submitted_query TEXT NOT NULL,
            query_type TEXT NOT NULL, -- 'serial', 'qr', 'sku', 'batch', 'image'
            outcome TEXT NOT NULL, -- 'match', 'warning', 'inconclusive'
            risk_score REAL NOT NULL DEFAULT 0.0,
            anomaly_flags TEXT, -- JSON array of detected signals
            client_ip TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (identifier_id) REFERENCES identifiers(id) ON DELETE SET NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
        );
        """)

        # 7. Retailers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS retailers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT NOT NULL,
            is_authorized_partner INTEGER NOT NULL DEFAULT 1,
            logo_url TEXT,
            rating REAL DEFAULT 4.8,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 8. Retailer Listings table (price comparison)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS retailer_listings (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            retailer_id TEXT NOT NULL,
            product_url TEXT NOT NULL,
            listing_title TEXT NOT NULL,
            current_price REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            shipping_price REAL NOT NULL DEFAULT 0.0,
            availability TEXT NOT NULL DEFAULT 'in_stock', -- 'in_stock', 'limited', 'out_of_stock'
            warranty_info TEXT,
            return_policy TEXT,
            seller_name TEXT NOT NULL,
            is_authorized_seller INTEGER NOT NULL DEFAULT 1,
            match_confidence TEXT NOT NULL DEFAULT 'exact', -- 'exact', 'similar'
            last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (retailer_id) REFERENCES retailers(id) ON DELETE CASCADE
        );
        """)

        # 9. Historical Price Observations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_observations (
            id TEXT PRIMARY KEY,
            listing_id TEXT NOT NULL,
            observed_price REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            observed_at TIMESTAMP NOT NULL,
            FOREIGN KEY (listing_id) REFERENCES retailer_listings(id) ON DELETE CASCADE
        );
        """)

        # 10. Watchlist & Price Alerts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            target_price REAL,
            alert_triggered INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(user_id, product_id)
        );
        """)

        # 11. Incidents & Reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            reporter_name TEXT NOT NULL,
            reporter_email TEXT NOT NULL,
            inquiry_type TEXT NOT NULL, -- 'counterfeit_report', 'brand_enrollment', 'audit_request', 'general'
            product_identifier TEXT,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'under_review', 'resolved', 'dismissed'
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        """)

        # Indexes for ultra-fast query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_identifiers_serial ON identifiers(serial_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_identifiers_product ON identifiers(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(model_sku);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batches_batch_num ON batches(batch_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_events_identifier ON scan_events(identifier_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_events_timestamp ON scan_events(scanned_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_obs_listing_date ON price_observations(listing_id, observed_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listings_product ON retailer_listings(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id);")

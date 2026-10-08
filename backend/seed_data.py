"""
TruthTag Intelligence Platform — Seed Dataset Generator
Populates clean, realistic, and clearly labeled initial records into the database.
Includes authentic products, flagged counterfeit cases, multi-retailer listings,
90 days of historical price points, and demo user accounts.
"""

from datetime import datetime, timedelta, timezone
from .database import get_db
from .auth import hash_password

def seed_database():
    """Populate database with rich initial data if empty."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] > 0:
            return # Already seeded

        print("[TruthTag Seed] Seeding initial intelligence ledger records...")

        # 1. Users
        users = [
            ("usr-admin-01", "admin_sarah", "admin@truthtag.io", hash_password("Admin@123"), "admin", None),
            ("usr-brand-01", "brand_aurasound", "partner@aurasound.com", hash_password("Partner@123"), "brand_rep", "brand-001"),
            ("usr-demo-01", "consumer_alex", "user@example.com", hash_password("User@123"), "user", None)
        ]
        cursor.executemany("""
            INSERT INTO users (id, username, email, password_hash, role, brand_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, users)

        # 2. Brands
        brands = [
            ("brand-001", "AuraSound Labs", "AURASOUND", "United Kingdom", "https://aurasound.com", "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=100"),
            ("brand-002", "Vitalis Laboratories", "VITALIS", "France", "https://vitalislabs.com", "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=100"),
            ("brand-003", "AeroStride Athletics", "AEROSTRIDE", "South Korea", "https://aerostride.com", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=100"),
            ("brand-004", "NordicShield Outerwear", "NORDICSHIELD", "Norway", "https://nordicshield.com", "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=100"),
            ("brand-005", "OmniPower Global", "OMNIPOWER", "Taiwan", "https://omnipower.com", "https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=100"),
            ("brand-006", "Chronos Horology", "CHRONOS", "Switzerland", "https://chronoswatch.com", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=100")
        ]
        cursor.executemany("""
            INSERT INTO brands (id, name, code, country, website, logo_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, brands)

        # 3. Products
        products = [
            (
                "prod-001", "brand-001", "AuraSound Apex Pro Wireless ANC Headphones", "AUD-9921-X", "Electronics",
                "Flagship spatial audio active noise cancelling headphones with titanium drivers.",
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                "Holographic Void Seal & Micro-Engraved QR Matrix",
                "AuraSound Direct, BestBuy, Currys UK, B&H Photo",
                "Look for rainbow holographic sheen on inner seal and embossed serial tag on headband."
            ),
            (
                "prod-002", "brand-002", "Vitalis Botanical Glow Facial Serum", "VTL-402", "Skincare",
                "Ultra-hydrating botanical glow serum infused with cold-pressed rosehip seed extract.",
                "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500",
                "Tamper-Evident Breakaway Foil & Lot Stamp on Glass Base",
                "Vitalis Paris Flagship, Sephora, Nordstrom, Mecca",
                "Authentic bottles have lot code screen-printed in white ink on the base of the glass bottle."
            ),
            (
                "prod-003", "brand-003", "AeroStride Velocity Carbon Running Shoes", "AERO-900", "Footwear",
                "Marathon racing shoes with propulsive carbon plate and lightweight supercritical foam.",
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                "Encrypted NFC Tongue Tag & Embedded RFID Thread",
                "AeroStride Global, Fleet Feet, Dick's Sporting Goods",
                "Inner tongue tag features high-density woven label with crisp vector typography."
            ),
            (
                "prod-004", "brand-004", "NordicShield Extreme Weather Down Parka", "NS-8800", "Apparel",
                "850-fill power expedition parka engineered for Arctic conditions and severe sub-zero wind.",
                "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=500",
                "Suspected Counterfeit Cloned Hangtag Series",
                "Official NordicShield Stores Only (Unauthorized Gray-Market Sellers & Fake Pop-Up Stores Circulating)",
                "Counterfeiters have duplicated this hangtag barcode across hundreds of non-insulated synthetic garments."
            ),
            (
                "prod-005", "brand-005", "OmniCharge MagSafe 100W Power Bank", "OP-100W", "Electronics",
                "Compact high-density 25,000mAh magnetic portable battery pack with multi-port fast charging.",
                "https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=500",
                "Cloned Safety Certification Logo & Micro-Barcode",
                "Recall Notice: Authorization Revoked Globally",
                "Units with batch B-990-REC or duplicate serial SN-10901 are subject to official safety recall due to cell degradation risks."
            ),
            (
                "prod-006", "brand-006", "Chronos Heritage Automatic Diver Watch", "CRN-3301", "Luxury",
                "Certified Swiss chronometer diver rated to 300m with ceramic bezel and sapphire crystal.",
                "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500",
                "Laser-Etched Caseback Serial & Cryptographic Sapphire Card",
                "Chronos Boutiques, Watches of Switzerland, Bucherer",
                "Laser engraving on caseback has 0.15mm depth with certified Swiss chronometer seal."
            )
        ]
        cursor.executemany("""
            INSERT INTO products (id, brand_id, name, model_sku, category, description, image_url, security_feature, authorized_channels, inspection_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)

        # 4. Batches
        batches = [
            ("batch-001", "prod-001", "B24-8891", "AuraSound UK Engineering Facility, Oxford, UK", "August 14, 2025", "active", "Standard commercial production batch. Released after multi-point QA inspection."),
            ("batch-002", "prod-002", "LOT-2024-09", "Vitalis Clean Cosmetics Facility, Provence, France", "September 22, 2025", "active", "Certified organic harvest cosmetic release. Zero contamination notices."),
            ("batch-003", "prod-003", "B-7712", "AeroStride Technical Footwear Plant, Busan, South Korea", "January 10, 2026", "active", "Official Olympic marathon qualification shoe run."),
            ("batch-004", "prod-004", "BATCH-FLAGGED-01", "NordicShield Arctic Wear Ltd, Oslo, Norway", "Unverified / Flagged Counterfeit Series", "flagged", "🚨 HIGH RISK COUNTERFEIT WARNING: Identifier is linked to a widely reported counterfeit batch. Unlicensed factories have replicated this tag on low-grade garments."),
            ("batch-005", "prod-005", "B-990-REC", "OmniPower Hardware Labs, Taipei, Taiwan", "May 04, 2025 (Recalled Series)", "recalled", "⚠️ SAFETY RECALL NOTICE: Batch B-990-REC is officially flagged for high temperature cell degradation."),
            ("batch-006", "prod-006", "BATCH-CH-44", "Chronos Atelier, Geneva, Switzerland", "November 05, 2025", "active", "Individually numbered master horology batch.")
        ]
        cursor.executemany("""
            INSERT INTO batches (id, product_id, batch_number, facility, production_date, status, status_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, batches)

        # 5. Identifiers (Serial Numbers & QR Payloads)
        identifiers = [
            ("ident-001", "prod-001", "batch-001", "SN-772109", "https://verify.truthtag.io/audit?code=SN-772109", 1, "2026-09-20 14:22:00", "active"),
            ("ident-002", "prod-002", "batch-002", "SN-55412", "https://verify.truthtag.io/audit?code=SN-55412", 1, "2026-09-22 10:15:00", "active"),
            ("ident-003", "prod-003", "batch-003", "SN-33901", "https://verify.truthtag.io/audit?code=SN-33901", 1, "2026-09-24 16:45:00", "active"),
            ("ident-004", "prod-004", "batch-004", "SN-66601", "https://verify.truthtag.io/audit?code=SN-66601", 4, "2026-09-25 09:12:00", "flagged_cloned"),
            ("ident-005", "prod-005", "batch-005", "SN-10901", "https://verify.truthtag.io/audit?code=SN-10901", 14, "2026-09-26 21:03:00", "recalled"),
            ("ident-006", "prod-006", "batch-006", "SN-88203", "https://verify.truthtag.io/audit?code=SN-88203", 1, "2026-09-25 18:30:00", "active")
        ]
        cursor.executemany("""
            INSERT INTO identifiers (id, product_id, batch_id, serial_number, qr_payload, scan_count, last_scanned_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, identifiers)

        # 6. Retailers
        retailers = [
            ("ret-001", "AuraSound Direct", "aurasound.com", 1, "https://logo.clearbit.com/aurasound.com", 4.9),
            ("ret-002", "Best Buy", "bestbuy.com", 1, "https://logo.clearbit.com/bestbuy.com", 4.7),
            ("ret-003", "B&H Photo Video", "bhphotovideo.com", 1, "https://logo.clearbit.com/bhphotovideo.com", 4.8),
            ("ret-004", "Amazon (Authorized)", "amazon.com", 1, "https://logo.clearbit.com/amazon.com", 4.6),
            ("ret-005", "Sephora", "sephora.com", 1, "https://logo.clearbit.com/sephora.com", 4.9),
            ("ret-006", "Nordstrom", "nordstrom.com", 1, "https://logo.clearbit.com/nordstrom.com", 4.8),
            ("ret-007", "Fleet Feet Sports", "fleetfeet.com", 1, "https://logo.clearbit.com/fleetfeet.com", 4.7),
            ("ret-008", "Global Liquidation Hub (Unauthorized)", "liquidation-deals-cheap.com", 0, None, 2.8)
        ]
        cursor.executemany("""
            INSERT INTO retailers (id, name, domain, is_authorized_partner, logo_url, rating)
            VALUES (?, ?, ?, ?, ?, ?)
        """, retailers)

        # 7. Retailer Listings (Price Comparison)
        listings = [
            # AuraSound Headphones (prod-001)
            ("list-001", "prod-001", "ret-001", "https://aurasound.com/products/apex-pro", "AuraSound Apex Pro Wireless ANC Headphones - Charcoal Black", 349.00, "USD", 0.0, "in_stock", "2-Year Official Manufacturer Warranty", "30-Day Free Return Window", "AuraSound Labs Direct", 1, "exact"),
            ("list-002", "prod-001", "ret-002", "https://bestbuy.com/site/aurasound-apex-pro", "AuraSound - Apex Pro Wireless Noise Cancelling Over-Ear Headphones", 329.99, "USD", 0.0, "in_stock", "2-Year Manufacturer Warranty + GeekSquad eligible", "14-Day Return Policy", "Best Buy Co.", 1, "exact"),
            ("list-003", "prod-001", "ret-003", "https://bhphotovideo.com/c/product/aurasound-apex", "AuraSound Apex Pro ANC Wireless Headphones (Black)", 339.00, "USD", 0.0, "in_stock", "2-Year Authorized USA Warranty", "30-Day Return Window", "B&H Authorized Audio", 1, "exact"),
            ("list-004", "prod-001", "ret-004", "https://amazon.com/dp/B09AURASOUND", "AuraSound Apex Pro Wireless Headphones ANC Pro Audio", 319.95, "USD", 5.99, "in_stock", "1-Year Limited Warranty", "Amazon 30-Day Return", "Amazon Direct Fulfillment", 1, "exact"),
            ("list-005", "prod-001", "ret-008", "https://liquidation-deals-cheap.com/apex-pro-sale", "NEW AuraSound APEX Pro Headphone (Bulk Packaging / OEM)", 189.00, "USD", 15.00, "limited", "No Manufacturer Warranty (As-Is)", "Final Sale / No Returns", "Shenzhen Discounter Hub", 0, "similar"),

            # Vitalis Botanical Serum (prod-002)
            ("list-006", "prod-002", "ret-005", "https://sephora.com/product/vitalis-botanical-glow", "Vitalis Laboratories Botanical Glow Facial Serum 50ml", 88.00, "USD", 0.0, "in_stock", "Authenticity Guaranteed / Fresh Stock Batch", "60-Day Return / Exchange", "Sephora USA", 1, "exact"),
            ("list-007", "prod-002", "ret-006", "https://nordstrom.com/s/vitalis-glow-serum", "Vitalis Botanical Glow Facial Serum - 1.7 oz", 88.00, "USD", 0.0, "in_stock", "Authorized Retailer Guarantee", "Nordstrom Flexible Return Policy", "Nordstrom Cosmetics", 1, "exact"),
            ("list-008", "prod-002", "ret-008", "https://liquidation-deals-cheap.com/vitalis-serum-cheap", "Vitalis Serum Glow (Factory Surplus - Unboxed)", 39.00, "USD", 8.50, "limited", "None", "No Returns Accepted", "Cosmetic Surplus Warehouse", 0, "similar"),

            # AeroStride Running Shoes (prod-003)
            ("list-009", "prod-003", "ret-007", "https://fleetfeet.com/products/aerostride-velocity", "AeroStride Velocity Carbon Running Shoes - Mens/Womens", 250.00, "USD", 0.0, "in_stock", "Manufacturer Defect Coverage (1 Year)", "60-Day Happy Fit Guarantee", "Fleet Feet Official", 1, "exact"),
            ("list-010", "prod-003", "ret-004", "https://amazon.com/dp/B09AEROSTRIDE", "AeroStride Velocity Carbon Super Shoes", 239.99, "USD", 0.0, "in_stock", "Standard Manufacturer Guarantee", "30-Day Amazon Return", "AeroStride Athletics Store", 1, "exact")
        ]
        cursor.executemany("""
            INSERT INTO retailer_listings (id, product_id, retailer_id, product_url, listing_title, current_price, currency, shipping_price, availability, warranty_info, return_policy, seller_name, is_authorized_seller, match_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, listings)

        # 8. Dated Historical Price Observations (90 days of daily/weekly records)
        print("[TruthTag Seed] Generating 90-day dated historical price observations...")
        base_date = datetime.now(timezone.utc) - timedelta(days=90)
        price_observations = []

        # List-001 (AuraSound Direct: $349 standard, had a $329 holiday promo 30 days ago)
        for d in range(0, 91, 5):
            obs_dt = (base_date + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
            p = 349.00
            if 40 <= d <= 55: # 40 days ago promotional sale
                p = 329.00
            price_observations.append((f"obs-001-{d}", "list-001", p, "USD", obs_dt))

        # List-002 (Best Buy: Started $359, dropped to $339, current $329.99)
        for d in range(0, 91, 5):
            obs_dt = (base_date + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
            if d < 30:
                p = 359.99
            elif d < 65:
                p = 339.99
            else:
                p = 329.99
            price_observations.append((f"obs-002-{d}", "list-002", p, "USD", obs_dt))

        # List-004 (Amazon: Fluctuation between $315 and $340)
        for d in range(0, 91, 5):
            obs_dt = (base_date + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
            cycle = [339.00, 335.50, 329.00, 319.95, 324.00, 315.00, 319.95][(d // 5) % 7]
            price_observations.append((f"obs-004-{d}", "list-004", cycle, "USD", obs_dt))

        # List-006 (Sephora Vitalis Serum: Steady $88.00)
        for d in range(0, 91, 10):
            obs_dt = (base_date + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
            price_observations.append((f"obs-006-{d}", "list-006", 88.00, "USD", obs_dt))

        # List-009 (AeroStride Velocity: Steady $250.00)
        for d in range(0, 91, 10):
            obs_dt = (base_date + timedelta(days=d)).strftime("%Y-%m-%d %H:%M:%S")
            price_observations.append((f"obs-009-{d}", "list-009", 250.00, "USD", obs_dt))

        cursor.executemany("""
            INSERT INTO price_observations (id, listing_id, observed_price, currency, observed_at)
            VALUES (?, ?, ?, ?, ?)
        """, price_observations)

        # 9. Initial Scan Events (Populates Intelligence Bento & Audit Trail)
        scan_events = [
            ("scan-seed-01", "ident-001", "prod-001", "usr-demo-01", "AUD-9921-X", "sku", "match", 5.0, '["CLEAN_LEDGER_MATCH"]', "192.168.1.10", (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")),
            ("scan-seed-02", "ident-004", "prod-004", "usr-demo-01", "NS-8800", "sku", "warning", 85.0, '["BATCH_FLAGGED_COUNTERFEIT_ALERT"]', "192.168.1.12", (datetime.now(timezone.utc) - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
            ("scan-seed-03", "ident-002", "prod-002", "usr-demo-01", "VTL-402", "sku", "match", 5.0, '["CLEAN_LEDGER_MATCH"]', "192.168.1.14", (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")),
            ("scan-seed-04", "ident-005", "prod-005", None, "SN-10901", "serial", "warning", 92.0, '["BATCH_OFFICIALLY_RECALLED", "HIGH_VELOCITY_SERIAL_CLONING"]', "10.0.0.8", (datetime.now(timezone.utc) - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S")),
            ("scan-seed-05", None, None, None, "UNKNOWN-LOT-992", "auto", "inconclusive", 65.0, '["IDENTIFIER_NOT_FOUND_IN_LEDGER"]', "10.0.0.21", (datetime.now(timezone.utc) - timedelta(hours=22)).strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
            INSERT INTO scan_events (id, identifier_id, product_id, user_id, submitted_query, query_type, outcome, risk_score, anomaly_flags, client_ip, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, scan_events)

        # 10. Sample Counterfeit Incident
        incidents = [
            (
                "inc-001", "usr-demo-01", "Elena Rostova", "elena@example.com", "counterfeit_report",
                "NS-8800",
                "Purchased a NordicShield Extreme Weather Down Parka from a pop-up marketplace stall in London. "
                "The barcode matches NS-8800, but the inner insulation is cheap polyester batting instead of goose down. "
                "The jacket tore along the seam immediately in sub-zero wind.",
                "under_review",
                "Investigating seller marketplace entity with brand enforcement counsel."
            )
        ]
        cursor.executemany("""
            INSERT INTO incidents (id, user_id, reporter_name, reporter_email, inquiry_type, product_identifier, message, status, admin_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, incidents)

        print("[TruthTag Seed] Initial dataset successfully populated.")

if __name__ == "__main__":
    from .database import init_db
    init_db()
    seed_database()

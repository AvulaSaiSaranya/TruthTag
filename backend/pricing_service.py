"""
TruthTag Intelligence Platform — Multi-Retailer Pricing & Price History Service
Tracks retailer listings, dated historical price observations, deal analytics,
and user price-drop alert conditions.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .database import get_db
from .models import (
    ProductPricingResponse,
    RetailerListingResponse,
    ListingPriceHistory,
    PriceHistoryPoint,
    WatchlistResponse
)

def get_product_pricing(product_id: str) -> Optional[ProductPricingResponse]:
    """
    Retrieve multi-retailer price comparison and dated historical observations
    for a specific registered product.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Product Details
        cursor.execute("SELECT id, name, model_sku FROM products WHERE id = ? OR model_sku = ?", (product_id, product_id))
        prod = cursor.fetchone()
        if not prod:
            return None

        real_product_id = prod["id"]

        # 2. Retailer Listings
        cursor.execute("""
            SELECT l.id, l.product_url, l.listing_title, l.current_price, l.currency,
                   l.shipping_price, l.availability, l.warranty_info, l.return_policy,
                   l.seller_name, l.is_authorized_seller, l.match_confidence, l.last_checked_at,
                   r.name as retailer_name, r.domain as retailer_domain, r.logo_url as retailer_logo
            FROM retailer_listings l
            JOIN retailers r ON l.retailer_id = r.id
            WHERE l.product_id = ?
            ORDER BY (l.current_price + l.shipping_price) ASC
        """, (real_product_id,))
        listing_rows = cursor.fetchall()

        if not listing_rows:
            return ProductPricingResponse(
                product_id=prod["id"],
                product_name=prod["name"],
                model_sku=prod["model_sku"],
                lowest_observed_price=0.0,
                highest_observed_price=0.0,
                average_observed_price=0.0,
                price_change_90d_pct=0.0,
                deal_rating="No Active Listings",
                deal_description="No commercial listings currently tracked for this model.",
                listings=[],
                historical_chart_data=[],
                total_observations_count=0,
                last_observation_date="N/A"
            )

        # Find absolute lowest total price among available listings
        min_total_price = float("inf")
        lowest_listing_id = None
        for r in listing_rows:
            tot = r["current_price"] + r["shipping_price"]
            if r["availability"] != "out_of_stock" and tot < min_total_price:
                min_total_price = tot
                lowest_listing_id = r["id"]

        listings_output = []
        for r in listing_rows:
            total_price = round(r["current_price"] + r["shipping_price"], 2)
            listings_output.append(
                RetailerListingResponse(
                    id=r["id"],
                    retailer_name=r["retailer_name"],
                    retailer_domain=r["retailer_domain"],
                    retailer_logo=r["retailer_logo"],
                    product_url=r["product_url"],
                    listing_title=r["listing_title"],
                    current_price=round(r["current_price"], 2),
                    currency=r["currency"],
                    shipping_price=round(r["shipping_price"], 2),
                    total_price=total_price,
                    availability=r["availability"],
                    warranty_info=r["warranty_info"],
                    return_policy=r["return_policy"],
                    seller_name=r["seller_name"],
                    is_authorized_seller=bool(r["is_authorized_seller"]),
                    match_confidence=r["match_confidence"],
                    last_checked_at=str(r["last_checked_at"]),
                    is_lowest_price=(r["id"] == lowest_listing_id)
                )
            )

        # 3. Fetch Historical Observations for these listings
        listing_ids = [r["id"] for r in listing_rows]
        placeholders = ",".join(["?"] * len(listing_ids))
        cursor.execute(f"""
            SELECT o.listing_id, o.observed_price, o.observed_at, r.name as retailer_name
            FROM price_observations o
            JOIN retailer_listings l ON o.listing_id = l.id
            JOIN retailers r ON l.retailer_id = r.id
            WHERE o.listing_id IN ({placeholders})
            ORDER BY o.observed_at ASC
        """, listing_ids)
        obs_rows = cursor.fetchall()

        # Group observations by retailer
        retailer_charts: Dict[str, List[PriceHistoryPoint]] = {}
        all_prices: List[float] = []
        first_price = None
        latest_price = None
        last_obs_date = "N/A"

        for row in obs_rows:
            r_name = row["retailer_name"]
            p = row["observed_price"]
            dt_str = str(row["observed_at"])[:10]
            if r_name not in retailer_charts:
                retailer_charts[r_name] = []
            retailer_charts[r_name].append(PriceHistoryPoint(date=dt_str, price=p))
            all_prices.append(p)
            if first_price is None:
                first_price = p
            latest_price = p
            last_obs_date = dt_str

        # Calculate metrics
        lowest_obs = min(all_prices) if all_prices else (min_total_price if min_total_price != float("inf") else 0.0)
        highest_obs = max(all_prices) if all_prices else (min_total_price if min_total_price != float("inf") else 0.0)
        avg_obs = (sum(all_prices) / len(all_prices)) if all_prices else lowest_obs

        # Calculate 90-day price trend percentage
        price_change_pct = 0.0
        if first_price and latest_price and first_price > 0:
            price_change_pct = round(((latest_price - first_price) / first_price) * 100, 1)

        # Deal rating logic
        current_active_lowest = min_total_price if min_total_price != float("inf") else lowest_obs
        if current_active_lowest <= lowest_obs * 1.01:
            deal_rating = "Historical Low Price"
            deal_desc = f"Current price (${current_active_lowest:.2f}) matches or is within 1% of the all-time observed low (${lowest_obs:.2f})."
        elif current_active_lowest < avg_obs * 0.95:
            deal_rating = "Below Historical Average"
            deal_desc = f"Current price is {round((1 - (current_active_lowest / avg_obs)) * 100, 1)}% lower than the 90-day average (${avg_obs:.2f})."
        elif current_active_lowest > avg_obs * 1.05:
            deal_rating = "Above Historical Average"
            deal_desc = f"Current price is higher than historical average (${avg_obs:.2f}). Waiting for a price drop is recommended."
        else:
            deal_rating = "Fair Market Range"
            deal_desc = f"Current price is in line with the steady 90-day average (${avg_obs:.2f})."

        chart_data = [
            ListingPriceHistory(retailer_name=k, history=v)
            for k, v in retailer_charts.items()
        ]

        return ProductPricingResponse(
            product_id=prod["id"],
            product_name=prod["name"],
            model_sku=prod["model_sku"],
            lowest_observed_price=round(lowest_obs, 2),
            highest_observed_price=round(highest_obs, 2),
            average_observed_price=round(avg_obs, 2),
            price_change_90d_pct=price_change_pct,
            deal_rating=deal_rating,
            deal_description=deal_desc,
            listings=listings_output,
            historical_chart_data=chart_data,
            total_observations_count=len(obs_rows),
            last_observation_date=last_obs_date
        )

def add_to_watchlist(user_id: str, product_id: str, target_price: Optional[float] = None) -> Dict[str, Any]:
    """Save product to user's watchlist and evaluate price alert."""
    import uuid
    pricing = get_product_pricing(product_id)
    if not pricing:
        raise ValueError("Product not found.")

    current_lowest = pricing.lowest_observed_price
    alert_triggered = False
    if target_price and current_lowest <= target_price:
        alert_triggered = True

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM watchlists WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE watchlists
                SET target_price = ?, alert_triggered = ?
                WHERE id = ?
            """, (target_price, 1 if alert_triggered else 0, existing["id"]))
            item_id = existing["id"]
        else:
            item_id = "W-" + uuid.uuid4().hex[:8]
            cursor.execute("""
                INSERT INTO watchlists (id, user_id, product_id, target_price, alert_triggered)
                VALUES (?, ?, ?, ?, ?)
            """, (item_id, user_id, product_id, target_price, 1 if alert_triggered else 0))

    return {
        "id": item_id,
        "product_id": product_id,
        "product_name": pricing.product_name,
        "target_price": target_price,
        "current_lowest_price": current_lowest,
        "alert_triggered": alert_triggered,
        "message": "Product saved to your watchlist." if not alert_triggered else f"Price alert! Current price (${current_lowest:.2f}) is already at or below your target (${target_price:.2f})."
    }

def get_user_watchlist(user_id: str) -> List[WatchlistResponse]:
    """Retrieve all products in a user's watchlist."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.id, w.product_id, w.target_price, w.alert_triggered, w.created_at,
                   p.name as product_name, p.model_sku, p.image_url,
                   b.name as brand_name
            FROM watchlists w
            JOIN products p ON w.product_id = p.id
            JOIN brands b ON p.brand_id = b.id
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()

    result = []
    for r in rows:
        pricing = get_product_pricing(r["product_id"])
        lowest = pricing.lowest_observed_price if pricing else 0.0
        result.append(
            WatchlistResponse(
                id=r["id"],
                product_id=r["product_id"],
                product_name=r["product_name"],
                brand_name=r["brand_name"],
                model_sku=r["model_sku"],
                image_url=r["image_url"],
                current_lowest_price=lowest,
                target_price=r["target_price"],
                alert_triggered=bool(r["alert_triggered"]),
                created_at=str(r["created_at"])
            )
        )
    return result

def remove_from_watchlist(user_id: str, product_id: str) -> bool:
    """Remove a product from user's watchlist."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlists WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        return cursor.rowcount > 0

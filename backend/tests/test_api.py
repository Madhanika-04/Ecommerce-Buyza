"""
FastAPI Backend Integration Tests
=================================
Validates API endpoints for health, categories, catalog pagination,
content-based recommendations, search, cart, wishlist, and simulated orders.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    """Create test client with triggered lifespan startup events."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    """GET /api/health"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ml_engine"]["ready"] is True
    assert data["ml_engine"]["catalog_products"] == 76327


def test_get_categories(client):
    """GET /api/categories"""
    response = client.get("/api/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 9
    cat_names = [c["category"] for c in categories]
    assert "Laptops & Computers" in cat_names
    assert "Men's Fashion" in cat_names


def test_list_products_pagination_and_filter(client):
    """GET /api/products with pagination and category filtering"""
    response = client.get("/api/products?page=1&page_size=15&category=Laptops%20%26%20Computers")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 15
    assert data["total"] == 2178
    assert data["page"] == 1
    assert data["total_pages"] > 1
    for item in data["items"]:
        assert item["category"] == "Laptops & Computers"
        assert item["formatted_price"].startswith("₹")


def test_get_product_by_id(client):
    """GET /api/products/{product_id}"""
    response = client.get("/api/products/IN-PROD-000001")
    assert response.status_code == 200
    prod = response.json()
    assert prod["product_id"] == "IN-PROD-000001"
    assert "price_inr" in prod
    assert "title" in prod

    # Non-existent product
    bad_resp = client.get("/api/products/NON_EXISTENT_ID_999999")
    assert bad_resp.status_code == 404


def test_product_recommendations(client):
    """GET /api/products/{product_id}/recommendations"""
    response = client.get("/api/products/IN-PROD-000001/recommendations?top_n=5")
    assert response.status_code == 200
    recs = response.json()
    assert len(recs) <= 5
    for r in recs:
        assert r["product_id"] != "IN-PROD-000001"  # No self recommendation
        assert 0.0 <= r["similarity_score"] <= 1.0
        assert r["formatted_price"].startswith("₹")


def test_semantic_search(client):
    """GET /api/search?q=laptop"""
    response = client.get("/api/search?q=laptop&top_n=6")
    assert response.status_code == 200
    recs = response.json()
    assert len(recs) > 0
    assert recs[0]["similarity_score"] > 0.0


def test_cart_operations(client):
    """Cart flow: add -> get -> update -> remove"""
    test_user = "test_user_cart_1"
    
    # 1. Clear cart
    client.delete(f"/api/cart?user_id={test_user}")
    
    # 2. Add item
    add_resp = client.post("/api/cart", json={
        "product_id": "IN-PROD-000001",
        "quantity": 2,
        "user_id": test_user
    })
    assert add_resp.status_code == 200
    cart = add_resp.json()
    assert cart["total_items"] == 2
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 2
    
    # 3. Update quantity
    upd_resp = client.patch(
        "/api/cart/IN-PROD-000001",
        json={"quantity": 3, "user_id": test_user}
    )
    assert upd_resp.status_code == 200
    assert upd_resp.json()["total_items"] == 3
    
    # 4. Remove item
    del_resp = client.delete(f"/api/cart/IN-PROD-000001?user_id={test_user}")
    assert del_resp.status_code == 200
    assert del_resp.json()["total_items"] == 0


def test_wishlist_operations(client):
    """Wishlist flow: add -> list -> delete"""
    test_user = "test_user_wishlist_1"
    
    # 1. Add item
    add_resp = client.post("/api/wishlist", json={
        "product_id": "IN-PROD-000005",
        "user_id": test_user
    })
    assert add_resp.status_code == 200
    assert add_resp.json()["total_items"] >= 1
    
    # 2. Get wishlist
    get_resp = client.get(f"/api/wishlist?user_id={test_user}")
    assert get_resp.status_code == 200
    items = get_resp.json()["items"]
    assert any(i["product_id"] == "IN-PROD-000005" for i in items)
    
    # 3. Delete from wishlist
    del_resp = client.delete(f"/api/wishlist/IN-PROD-000005?user_id={test_user}")
    assert del_resp.status_code == 200
    items_after = del_resp.json()["items"]
    assert not any(i["product_id"] == "IN-PROD-000005" for i in items_after)


def test_order_simulated_checkout(client):
    """Simulated checkout flow with Indian Address and PIN Code validation"""
    test_user = "test_user_checkout_1"
    
    # 1. Attempt checkout with empty cart -> 400
    client.delete(f"/api/cart?user_id={test_user}")
    empty_order_resp = client.post("/api/orders", json={
        "user_id": test_user,
        "delivery_address": {
            "full_name": "Rohan Sharma",
            "phone": "9876543210",
            "address_line": "Flat 402, Green Glen Layout, Bellandur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pin_code": "560103"
        }
    })
    assert empty_order_resp.status_code == 400
    
    # 2. Add item to cart
    client.post("/api/cart", json={
        "product_id": "IN-PROD-000010",
        "quantity": 1,
        "user_id": test_user
    })
    
    # 3. Place order with invalid PIN code -> 422
    bad_pin_resp = client.post("/api/orders", json={
        "user_id": test_user,
        "delivery_address": {
            "full_name": "Rohan Sharma",
            "phone": "9876543210",
            "address_line": "Flat 402, Green Glen Layout",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pin_code": "0123"  # Invalid!
        }
    })
    assert bad_pin_resp.status_code == 422
    
    # 4. Place valid simulated order
    order_resp = client.post("/api/orders", json={
        "user_id": test_user,
        "delivery_address": {
            "full_name": "Rohan Sharma",
            "phone": "9876543210",
            "address_line": "Flat 402, Green Glen Layout, Bellandur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pin_code": "560103"
        },
        "payment_method": "Cash on Delivery (Simulated)"
    })
    assert order_resp.status_code == 201
    order = order_resp.json()
    assert order["order_id"].startswith("IN-ORD-")
    assert order["status"] == "Confirmed (Simulated)"
    assert order["delivery_address"]["pin_code"] == "560103"
    
    # 5. Verify cart is now empty
    cart_after = client.get(f"/api/cart?user_id={test_user}").json()
    assert cart_after["total_items"] == 0
    
    # 6. Verify order appears in order history
    history_resp = client.get(f"/api/orders?user_id={test_user}")
    assert history_resp.status_code == 200
    orders_list = history_resp.json()
    assert any(o["order_id"] == order["order_id"] for o in orders_list)

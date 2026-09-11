import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
ZENDROP_API_KEY = os.getenv("SUPPLIER_API_KEY") or os.getenv("ZENDROP_API_KEY")
ZENDROP_API_URL = os.getenv("SUPPLIER_API_URL") or "https://api.zendrop.com/v1"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# Rules from gemini.md
MIN_RATING = 4.5
MAX_SHIPPING_DAYS = 10

def fetch_zendrop_products():
    """
    Attempts to fetch products from Zendrop.
    Falls back to mock data if the API is restricted or fails.
    """
    print("[*] Fetching products from Supplier API...")
    headers = {"Authorization": f"Bearer {ZENDROP_API_KEY}"}
    
    try:
        response = requests.get(f"{ZENDROP_API_URL}/products", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"[-] Real API call failed or restricted: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"    Response body: {response.text}")
        return []

def filter_products(products):
    """Applies strict B.L.A.S.T. rules to products."""
    filtered = []
    print(f"[*] Total raw products fetched: {len(products)}")
    
    for p in products:
        rating = p.get("rating", 0.0)
        shipping = p.get("shipping_time_days", 99)
        
        if rating >= MIN_RATING and shipping <= MAX_SHIPPING_DAYS:
            filtered.append(p)
        else:
            print(f"    [-] Rejected '{p['title']}': Rating {rating}, Shipping {shipping} days")
            
    print(f"[+] Products passing strict filter: {len(filtered)}")
    return filtered

def push_to_airtable(products):
    """Pushes valid products to Airtable staging."""
    if not products:
        print("[-] No products to push.")
        return

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Airtable allows batch creation of up to 10 records at a time
    records = []
    for p in products:
        image_url = p.get("images", [""])[0] if isinstance(p.get("images"), list) else p.get("images", "")
        
        records.append({
            "fields": {
                "product_id": str(p["product_id"]),
                "title": str(p["title"]),
                "description_html": str(p["description_html"]),
                "supplier_cost": float(p["supplier_cost"]),
                "recommended_price": float(p["recommended_price"]),
                "images": str(image_url),
                "shipping_time_days": int(p["shipping_time_days"]),
                "rating": float(p["rating"]),
                "Approved": False,
                "Published": False
            }
        })
        
    payload = {"records": records}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("[+] Successfully pushed products to Airtable!")
        else:
            print(f"[-] Failed to push to Airtable: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[-] Request failed: {e}")

if __name__ == "__main__":
    raw_products = fetch_zendrop_products()
    valid_products = filter_products(raw_products)
    push_to_airtable(valid_products)

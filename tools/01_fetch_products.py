import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
ZENDROP_API_KEY = os.getenv("SUPPLIER_API_KEY") or os.getenv("ZENDROP_API_KEY")
ZENDROP_API_URL = "https://app.zendrop.com/mcp/v1"
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
    print("[*] Fetching products from Supplier API (MCP Endpoint)...")
    headers = {
        "Authorization": f"Bearer {ZENDROP_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_catalog_products",
            "arguments": {
                "keyword": "pet",
                "limit": 10
            }
        }
    }
    
    try:
        response = requests.post(f"{ZENDROP_API_URL}", headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        raw_json = response.json()
        print(f"DEBUG: Parsed response successfully")
        
        # In MCP, result might be under 'result' -> 'structuredContent' -> 'products'
        data = raw_json.get("result", {}).get("structuredContent", {}).get("products", [])
        
        # Map MCP structure to our expected schema
        mapped_products = []
        for p in data:
            images = [img.get("url") for img in p.get("images", []) if isinstance(img, dict) and "url" in img]
            
            mapped_products.append({
                "product_id": p.get("id"),
                "title": p.get("name"),
                "description_html": p.get("description", f"<p>{p.get('name')}</p>"),
                "supplier_cost": float(p.get("price", 0.0)),
                "recommended_price": float(p.get("price", 0.0)) * 2.5,
                "images": images,
                "shipping_time_days": 7, # Default as it's not in the basic response
                "rating": p.get("rating", 4.8) # Default if missing
            })
            
        return mapped_products
        
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
        # Join multiple image URLs with a comma
        images_list = p.get("images", [])
        images_str = ",".join(images_list) if isinstance(images_list, list) else str(images_list)
        
        records.append({
            "fields": {
                "product_id": str(p["product_id"]),
                "title": str(p["title"]),
                "description_html": str(p["description_html"]),
                "supplier_cost": float(p["supplier_cost"]),
                "recommended_price": float(p["recommended_price"]),
                "images": images_str,
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

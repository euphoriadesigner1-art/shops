import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

MARKUP_MULTIPLIER = 2.5  # Rule 4: 40% margin

def get_approved_products():
    """Fetches records from Airtable where Approved is True and Published is False."""
    print("[*] Checking Airtable for Approved products...")
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    
    # Filter using Airtable formula syntax
    formula = "AND({Approved} = TRUE(), {Published} != TRUE())"
    params = {"filterByFormula": formula}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        records = response.json().get("records", [])
        print(f"[+] Found {len(records)} approved, unpublished product(s).")
        return records
    except Exception as e:
        print(f"[-] Failed to fetch from Airtable: {e}")
        return []

def publish_to_shopify(record):
    """Pushes a single product to Shopify based on B.L.A.S.T. schemas."""
    fields = record.get("fields", {})
    title = fields.get("title", "Unknown Product")
    print(f"[*] Publishing '{title}' to Shopify...")
    
    # Calculate selling price (Rule 4)
    supplier_cost = float(fields.get("supplier_cost", 0.0))
    selling_price = round(supplier_cost * MARKUP_MULTIPLIER, 2)
    
    # Prepare Shopify Payload
    product_payload = {
        "product": {
            "title": title,
            "body_html": fields.get("description_html", ""),
            "vendor": "PawVation",
            "product_type": "Pet Tech",
            "status": "draft",
            "variants": [
                {
                    "price": str(selling_price),
                    "inventory_management": "shopify"
                }
            ]
        }
    }
    
    image_url = fields.get("images", "")
    if image_url:
        product_payload["product"]["images"] = [{"src": image_url}]
        
    url = f"{SHOPIFY_STORE_URL}/admin/api/2024-01/products.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=product_payload)
        if response.status_code == 201:
            print(f"    [+] Success! Price set to ${selling_price} (Cost: ${supplier_cost})")
            return True
        else:
            print(f"    [-] Shopify API Error: {response.status_code}")
            print(f"    {response.text}")
            return False
    except Exception as e:
        print(f"    [-] Request failed: {e}")
        return False

def mark_as_published(record_id):
    """Updates the Airtable record to set Published = True."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "fields": {
            "Published": True
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"    [+] Marked record {record_id} as Published in Airtable.")
        else:
            print(f"    [-] Failed to update Airtable: {response.status_code}")
    except Exception as e:
        print(f"    [-] Failed to update Airtable: {e}")

if __name__ == "__main__":
    records = get_approved_products()
    
    for record in records:
        success = publish_to_shopify(record)
        if success:
            mark_as_published(record["id"])

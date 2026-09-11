import os
import sys
import requests
from dotenv import load_dotenv

def check_shopify():
    store_url = os.getenv("SHOPIFY_STORE_URL")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not store_url or not access_token or "your_" in store_url:
        print("[-] Shopify credentials missing or invalid in .env.")
        return False
        
    url = f"{store_url}/admin/api/2024-01/shop.json"
    headers = {"X-Shopify-Access-Token": access_token}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("[+] Shopify connection successful.")
            return True
        else:
            print(f"[-] Shopify connection failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[-] Shopify request exception: {e}")
        return False

def check_airtable():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    table_name = os.getenv("AIRTABLE_TABLE_NAME")
    
    if not api_key or not base_id or not table_name or "your_" in api_key:
        print("[-] Airtable credentials missing or invalid in .env.")
        return False
        
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}?maxRecords=1"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("[+] Airtable connection successful.")
            return True
        else:
            print(f"[-] Airtable connection failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[-] Airtable request exception: {e}")
        return False

def main():
    print("=== B.L.A.S.T. Link Phase: Handshake Verification ===")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("[-] .env file not found. Please create one based on the template.")
        sys.exit(1)
        
    load_dotenv()
    
    success = True
    if not check_shopify():
        success = False
    if not check_airtable():
        success = False
        
    # Supplier API requires a specific supplier to verify, checking for existence.
    if not os.getenv("SUPPLIER_API_KEY") or "your_" in os.getenv("SUPPLIER_API_KEY"):
        print("[-] Supplier API credentials missing or invalid in .env.")
        success = False
    else:
        print("[+] Supplier API credentials found.")
        
    if not success:
        print("\n[!] Handshake Failed. Please update your .env file with real credentials.")
        sys.exit(1)
    else:
        print("\n[+] Handshake Successful. All external services are connected!")
        sys.exit(0)

if __name__ == "__main__":
    main()

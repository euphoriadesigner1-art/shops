import os
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")
STORE = os.getenv("SHOPIFY_STORE_URL", "pawvation.myshopify.com").replace("https://", "")
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "read_products,write_products,read_inventory,write_inventory"

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if "code" in query_components:
            auth_code = query_components["code"][0]
            
            token_url = f"https://{STORE}/admin/oauth/access_token"
            payload = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": auth_code
            }
            
            try:
                response = requests.post(token_url, json=payload)
                data = response.json()
                
                if "access_token" in data:
                    access_token = data["access_token"]
                    set_key(".env", "SHOPIFY_ACCESS_TOKEN", access_token)
                    
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>Success!</h1><p>Shopify Admin Token successfully saved to .env file! You can close this window.</p>")
                    print(f"\n[+] SUCCESS! Token retrieved and saved to .env")
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Failed to get token")
                    print(f"[-] Failed: {data}")
            except Exception as e:
                print(f"[-] Error exchanging token: {e}")
                
        raise KeyboardInterrupt

def main():
    if not CLIENT_ID or not CLIENT_SECRET or "your_" in CLIENT_ID:
        print("[-] Please add SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET to .env")
        return
        
    auth_url = f"https://{STORE}/admin/oauth/authorize?client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URI}"
    
    print(f"Opening browser to authenticate with Shopify...")
    print(f"If it doesn't open automatically, click this link:\n{auth_url}\n")
    
    webbrowser.open(auth_url)
    
    print("Waiting for callback on port 8080...")
    server = HTTPServer(("localhost", 8080), AuthHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Authentication complete.")

if __name__ == "__main__":
    main()

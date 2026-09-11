# SOP 01: API Handshake (Link Phase)

## Goal
Verify that all external services (Shopify, Zendrop/CJ Dropshipping, Airtable) are accessible before building complex business logic.

## Inputs
- `.env` file containing API keys and endpoints.

## Tool Logic
1. Load environment variables.
2. Send a minimal, non-destructive request (e.g., `GET /shop.json` for Shopify) to each service.
3. Assert that the response status code is 200 OK.
4. If any service fails, halt execution and raise a clear error indicating which service failed.

## Edge Cases
- Missing `.env` variables.
- Invalid or expired tokens (401/403).
- Service downtime (5xx).

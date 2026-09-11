# SOP: Automation Pipeline

This document defines the Standard Operating Procedure for running the automated dropshipping pipeline for PawVation.

## Overview
The pipeline consists of two deterministic scripts located in the `tools/` directory. These scripts enforce the rules defined in `gemini.md`.

## Prerequisites
- A populated `.env` file with Shopify, Airtable, and Supplier credentials.
- An Airtable Base with a table named `tblP3OudYn08v2DyM` (or whichever ID is in `.env`).
- The Airtable table MUST contain the following exact columns:
  - `product_id` (Single line text)
  - `title` (Single line text)
  - `description_html` (Long text)
  - `supplier_cost` (Currency)
  - `recommended_price` (Currency)
  - `images` (Single line text)
  - `shipping_time_days` (Number)
  - `rating` (Number)
  - `Approved` (Checkbox)
  - `Published` (Checkbox)

## Step 1: Fetch and Filter (Supplier -> Airtable)
Run the following command to pull products from Zendrop, filter them based on our strict criteria, and stage them in Airtable:

```bash
source venv/bin/activate
python tools/01_fetch_products.py
```

**Rules Applied:**
- Filters out any product with `rating < 4.5`.
- Filters out any product with `shipping_time_days > 10`.

## Step 2: Human Approval
- Open Airtable in your browser.
- Review the staged products.
- Check the **Approved** checkbox for products you want to sell.

## Step 3: Publish (Airtable -> Shopify)
Run the following command to take approved products, calculate the selling price, and push them to your Shopify store as drafts:

```bash
source venv/bin/activate
python tools/02_publish_shopify.py
```

**Rules Applied:**
- Queries only records where `Approved = TRUE` and `Published = FALSE`.
- Calculates Shopify selling price using a minimum 40% margin: `supplier_cost * 2.5`.
- Creates the product as a Draft in Shopify.
- Marks the Airtable record as `Published = TRUE` so it isn't duplicated on future runs.

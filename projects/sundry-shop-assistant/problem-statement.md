# Sundry Shop Assistant — Problem Statement

**Date:** 2026-04-16
**Template base:** `analytics-agent/retail-analytics` (`C:\Users\Lenovo\Documents\02_Pau-AI\template\analytics-agent\retail-analytics\`)
**Reference quality bar:** Bright Path Tuition

---

## The Problem

Pak Ahmad is a 52-year-old Malay-speaking sundry shop owner in Kajang who runs his kedai runcit alone from 7am to 10pm. His POS records every sale — around 40 to 80 transactions a day across groceries, snacks, dairy, vegetables, and bakery — but he never opens the dashboard because he cannot stop serving customers to type on a phone screen. By the time he closes at 10pm, he is too tired to review anything, so every reorder, every loyalty decision, and every judgement about which category is actually paying his rent is made on gut feel.

The tools currently in the market do not fit his reality. Loyverse and StoreHub dashboards are English-only and visual, requiring him to stop work to read charts. Delivery platforms like Grab Merchant only cover delivery revenue. A bookkeeper costs RM 300–800 a month and only produces monthly reports — no help for a question asked on a Tuesday afternoon. No existing option lets him ask his own sales data a question aloud in Malay and get a spoken answer in seconds, with a text fallback for moments when a customer is standing right in front of him.

## Who It Is For

- Role: Solo sundry shop (kedai runcit) owner-operator
- Location: Kajang, Selangor (primarily Malay-speaking)
- Age: ~52, Malay-first with working English for brand names
- Business size: ~800 sqft, ~200 SKUs, 40–80 transactions/day, RM 2,500–4,500 daily revenue
- Hours: 7am–10pm, seven days a week, mostly alone behind the counter
- Existing tools: basic POS (Loyverse-style), loyalty stamp card, accepts Cash + DuitNow QR + some credit card
- Operational constraint: hands-busy all day, cannot type into a dashboard during working hours

## Market Fit Verdict

**Upgrades existing**

Delta over incumbents: voice-first Malay interaction over the owner's own sales data, with four I/O modes (voice-in/voice-out, voice-in/text-out, text-in/voice-out, text-in/text-out) the owner can switch between as the shop's noise level and customer proximity change through the day — something no POS dashboard, delivery platform analytics, or generic voice assistant currently offers for this persona.

## Dataset

- Source: `C:\Users\Lenovo\Documents\03_Portfolios\AI-Project\sundry shop assistant\dataset.csv`
- Row count: 150 (March 2024 window)
- Columns: Invoice ID, Date, Customer Type (Member/Visitor), Gender, Product Category, Unit Price, Quantity, Total Sales, Payment Method
- Known data quality issues to address before MCP exposure:
  - Null values in Gender and Payment Method columns — MCP tools must handle "unknown" cleanly
  - Row 1 shows `Total Sales` inconsistent with `Unit Price × Quantity` (24.72 × 3 ≠ 323.78) — needs validation pass
- Malaysian localization: Product Category values (Snacks, Vegetables, Fruits, Dairy, Bakery, Beverages) map directly to kedai runcit vocabulary; Payment Method values (Cash, Credit Card, Mobile Payment) cover the three modes Pak Ahmad accepts (add DuitNow QR mapping under Mobile Payment)
- Demo window caveat: 150 rows covers March 2024 only; multi-month trend questions ("compare to last month") have no data to answer and must be handled gracefully in the agent's response

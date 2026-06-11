# Lead Source Intelligence Dataset — README

**Project:** Property Rental Lead Source Analytics (Pau Analytics portfolio build)
**Window:** 1 Dec 2025 to 31 May 2026 (6 months) · **Generated:** 11 Jun 2026 · Seed: 2026 (reproducible)
**Fictional client:** Adeline Khoo (PEA 9183), Klang Valley Homes Realty. All listings, agents, and figures are synthetic. Listing structures modeled on real KL rental market patterns.

## Files

| File | Grain | Rows | Purpose |
|---|---|---|---|
| listings.csv | 1 row per listing | 10 | Portfolio dimension table |
| enquiries.csv | 1 row per enquiry | ~1,140 | Main fact table: source, method, funnel flags, outcome |
| ad_spend.csv | month x campaign | 30 | Campaign-level spend (Google Ads, Meta Ads) |
| platform_costs.csv | month x platform | 12 | Portfolio-level subscriptions (PropertyGuru, Mudah) |

## Key schema notes

- **source** = where the lead came from (propertyguru / mudah / google_ads / meta_ads / referral)
- **contact_method** = how it arrived (portal_chat / whatsapp / phone_call / lead_form). Source and method are deliberately separate columns.
- **qualified** = requirement matches listing (incl. gender rule) AND move_in_days <= 30 AND responsive past first exchange
- **Cost allocation:** campaign spend attributes to target_segment listings; platform subscriptions spread across active listings weighted by days listed.

## Cost model (stated assumptions, RM/month)

PropertyGuru 450 · Mudah 60 · Google Ads 600 · Meta Ads 400 · Referral 0. Total RM9,060 over 6 months.

## Planted insights (what the dashboard should find)

1. **Mudah inversion:** 40% of enquiry volume, 15% qualified rate, 5% viewing rate, zero tenancies.
2. **Google Ads pays off:** highest CPE (~RM31) but ~50% qualified, best paid viewing rate, 2 tenancies at RM1,800 each.
3. **Referral champion:** 9% of volume, 67% qualified, 2 tenancies at RM0.
4. **Stale listing L09 (Sunway Velocity Two, RM3,400):** enquiry velocity collapses ~70% after week 2; comparable L05 at RM2,999 keeps moving. Recommend reprice.
5. **After-hours leak:** unanswered rate 20% after-hours vs 7% office hours (~3x).
6. **Channel x segment:** Meta works for rooms only; Google works for whole units/studios; running every listing everywhere wastes spend.
7. **Star performer L07 (Lavile):** signed in ~3 weeks via Google Ads.
8. **Portfolio sell-through:** monthly volume declines Dec (202) to May (64) as 7 of 10 listings sign. Restock warning for the agent.

## Cost per tenancy (the headline table)

PropertyGuru RM1,350 · Google Ads RM1,800 · Meta Ads RM2,400 · Referral RM0 · Mudah undefined (0 signings).

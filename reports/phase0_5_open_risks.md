# Phase 0.5 Open Risks & Policy Alignment Report

**Date:** 2026-10-10  
**Project:** LIDO AI Meditation Music Factory  
**Status:** Verified Open Risks & Mitigations  

---

## 1. Verified Policy & Compliance Risks

### 1.1 YouTube API Caching & Data Retention Compliance
- **Policy Reference:** YouTube Developer Policies Section III.E (Data Caching and Storage).
- **Rule:** Data obtained via YouTube API v3 must not be cached for more than 30 calendar days. If a video/channel is removed from YouTube, local records must be purged or updated.
- **Verification Result:** System includes `purge_stale_api_cache()` routine specification in `docs/data_retention.md`.
- **Open Action item for Phase 1:** Automate an explicit 30-day TTL index check in `src/ingestion.py` upon initial API integration.

### 1.2 Intellectual Property & Content Rights Certification
- **Policy Reference:** LIDO Channel Originality Guidelines.
- **Rule:** All creative briefs generated must be 100% original and certified free of third-party melody copying or sample infringement.
- **Verification Result:** Unit test `test_rights_review_blocking` in `tests/test_phase0.py` verified that uncertified or melody-infringing briefs raise `RightsReviewFailure` and fail ingestion.

---

## 2. Risk Tracking Table

| Risk ID | Title | Verified Status | Mitigation / Guardrail | Remaining Exposure |
| :--- | :--- | :--- | :--- | :--- |
| **RSK-P0.5-01** | API Quota Exhaustion | Controlled | Batching `videos.list` (1 unit per 50 videos). Fixture fallback when offline. | Low |
| **RSK-P0.5-02** | Secret Leakage | Controlled | `.env` git exclusion + secret scanner test `P0_TEST_08`. | Zero |
| **RSK-P0.5-03** | Copyright Infringement | Controlled | Mandatory `rights_records` table certification prior to brief approval. | Low |
| **RSK-P0.5-04** | Stale Cache Violation | Controlled | 30-day retention schedule documented in `docs/data_retention.md`. | Low |

---

## 3. Unverified Claims Audit

- **Claim:** YouTube API v3 key rate limit performance under live production load.
  - **Status:** *Unverified Hypothesis*. In Phase 0/0.5, execution was conducted exclusively via offline synthetic fixtures (`SYNTHETIC_FIXTURE`). Real API throughput will be empirically measured upon Phase 1 key activation.

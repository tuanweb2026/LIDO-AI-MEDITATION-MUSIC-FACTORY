# Phase 0 Data-Source Audit Report

**Date:** 2026-10-10  
**Project:** LIDO AI Meditation Music Factory  
**Status:** Completed  
**Operating Mode:** RESEARCH + DRY-RUN ONLY  

---

## 1. Executive Summary

This data-source audit evaluates official YouTube API capabilities, data accessibility, quota restrictions, legal terms of service, and compliance constraints for the LIDO AI Meditation Music Factory research engine.

---

## 2. YouTube Data API v3 Analysis

### 2.1 Available Public Endpoint & Data Matrix

| Endpoint | Data Provided | Quota Cost (Units) | Access Requirements | Reliability |
| :--- | :--- | :--- | :--- | :--- |
| `search.list` | Video IDs, Title, Description, Channel ID, Publish Time | 100 per request | API Key | High |
| `videos.list` (snippet, statistics, contentDetails) | Views, Likes, Duration, Tags, Category, View Count, Topic Categories | 1 unit per resource (~1-3 per request) | API Key | High |
| `channels.list` (snippet, statistics) | Subscriber count, Total views, Video count, Custom URL | 1 unit per resource | API Key | High |
| `commentThreads.list` | Top-level comments, User sentiments, Keywords | 1 unit per request | API Key | Medium (Depends on comment settings) |

### 2.2 Authorized / Channel-Owner Data Matrix

| Data Metric | Endpoint | Access Requirements |
| :--- | :--- | :--- |
| Revenue / RPM / CPM | YouTube Analytics API | OAuth 2.0 (Channel Owner) |
| Audience Demographics (Age/Gender/Geo) | YouTube Analytics API | OAuth 2.0 (Channel Owner) |
| Traffic Sources & Search Terms | YouTube Analytics API | OAuth 2.0 (Channel Owner) |
| Retention & Click-Through-Rate (CTR) | YouTube Analytics API | OAuth 2.0 (Channel Owner) |

### 2.3 Unobtainable or Unreliable Data

| Data Item | Technical Status | Policy / Compliance Constraint | Alternative Strategy |
| :--- | :--- | :--- | :--- |
| Competitor RPM / Revenue | Unobtainable via API | Strict Privacy Policy | Model estimates based on public views & niche benchmark RPMs |
| Exact Audio Frequency / Musical Key | Cannot obtain via YouTube metadata | Audio downloading strictly forbidden by hard policy | Analyze title/tags/descriptions for key terms (e.g., "432Hz", "528Hz", "Delta Waves") |
| Competitor Retention Curves | Unobtainable | Private channel analytics | Proxy metric using engagement ratio `(Likes + Comments) / Views` |

---

## 3. API Quota & Usage Economics

- **Default Daily Quota Limit:** 10,000 units / day (free tier).
- **Search Heavy Strategy:** 100 `search.list` calls = 10,000 units (exhausts daily quota quickly).
- **Optimized Batching Strategy:**
  1. Maintain seed list of channel IDs / video IDs.
  2. Use `videos.list(id="id1,id2,...50", part="snippet,statistics,contentDetails")` = 1-3 units per 50 videos.
  3. Daily capacity with batching: ~150,000 video records updated daily within free quota limits.

---

## 4. Policy & Terms Compliance

1. **Scraping Prohibition:** Scraping YouTube HTML pages or reverse-engineering internal APIs is strictly prohibited under YouTube Terms of Service and project hard restrictions.
2. **Data Caching & Retention Rules:**
  - YouTube API Developer Policies allow caching data for performance, but stale data must be refreshed or purged after **30 days**.
  - If a video or channel is deleted or made private on YouTube, local cache must purge corresponding data upon notification or re-fetch failure.
3. **No Direct Audio/Video Downloading:** Downloading YouTube audio/video files violates YouTube Terms of Service section 5.B and project hard restrictions.

---

## 5. Seed & Synthetic Fixture Protocol

When no active YouTube API credentials are supplied in the environment (`YOUTUBE_API_KEY` is null/empty):
- System strictly defaults to **Offline Synthetic Fixture Mode**.
- Synthetic fixtures (`fixtures/seed_data.json`) supply realistic, deterministic channel and video metadata for Vietnamese and International meditation music niches.
- All fixture-derived records in SQLite are explicitly tagged with `source_provenance = 'SYNTHETIC_FIXTURE'` to prevent data contamination.

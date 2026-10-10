# Data Retention & Compliance Specification

**Version:** 1.0.0  
**Date:** 2026-10-10  
**Status:** Approved  

---

## 1. Compliance Alignment with YouTube API Developer Policies

In accordance with YouTube API Developer Policies (specifically Section III.E - Data Caching and Storage):

1. **30-Day Maximum Cache Window:** Public YouTube data fetched via API v3 (video stats, channel counts) must not be retained locally for more than 30 consecutive days without re-validation or refresh from the API.
2. **Platform Deletion Compliance:** If a video or channel is deleted or set to private on YouTube, local cached records (`videos`, `video_snapshots`) must be deleted or marked as inactive during subsequent synchronization runs.
3. **Synthetic Fixture Exemption:** Locally generated synthetic fixtures (`MANUAL_SEED` or `SYNTHETIC_FIXTURE`) are exempt from YouTube API 30-day purging rules, as they do not constitute API-derived platform metrics.

---

## 2. Retention Matrix by Table

| Table Name | Data Class | Retention Policy | Automatic Cleanup Routine |
| :--- | :--- | :--- | :--- |
| `research_runs` | Audit History | Retain Indefinitely | Manual Archive |
| `sources` | Metadata | Retain Indefinitely | N/A |
| `channels` | Platform Data | Max 30 Days without refresh | Purge/Update on Sync Run |
| `videos` | Platform Data | Max 30 Days without refresh | Purge/Update on Sync Run |
| `video_snapshots` | Historical Metrics | 90 Days for Trend Analysis | Prune snapshots > 90 days |
| `research_scores` | Analytical Results | Retain with Research Run | Tied to `research_runs` |
| `creative_briefs` | IP Asset Specification | Retain Indefinitely | Core LIDO IP Storage |
| `rights_records` | Legal Certification | Retain Indefinitely | Compliance Evidence |
| `audit_events` | System Logs | Retain 365 Days | Truncate > 365 days |

---

## 3. Automated Retention Cleanup Command

The system provides an automated pruning function in `src/database.py`:
- `purge_stale_api_cache(db_conn, max_days=30)`: Deletes API-derived video snapshots older than 30 days that have not been re-verified.
- Writes an event to `audit_events` whenever records are purged.

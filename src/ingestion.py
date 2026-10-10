import json
import datetime
import uuid

class IngestionError(Exception):
    pass

def validate_and_normalize_fixture(fixture_path):
    with open(fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if "channels" not in data or "videos" not in data:
        raise IngestionError("Invalid fixture format: missing channels or videos array")
    
    normalized_channels = []
    for ch in data["channels"]:
        if not ch.get("channel_id") or not ch.get("channel_title"):
            raise IngestionError(f"Missing required channel fields in {ch}")
        normalized_channels.append({
            "channel_id": str(ch["channel_id"]).strip(),
            "source_id": str(ch.get("source_id", "SRC_SYNTHETIC_01")).strip(),
            "channel_title": str(ch["channel_title"]).strip(),
            "custom_url": ch.get("custom_url"),
            "country": ch.get("country", "VN"),
            "published_at": ch.get("published_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            "subscriber_count": int(ch.get("subscriber_count", 0)),
            "total_views": int(ch.get("total_views", 0)),
            "video_count": int(ch.get("video_count", 0))
        })
        
    normalized_videos = []
    for vid in data["videos"]:
        if not vid.get("video_id") or not vid.get("channel_id") or not vid.get("title"):
            raise IngestionError(f"Missing required video fields in {vid}")
        
        # ISO-8601 validation
        pub_at = vid.get("published_at")
        try:
            datetime.datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
        except Exception as e:
            raise IngestionError(f"Invalid published_at date format in {vid['video_id']}: {pub_at}") from e

        normalized_videos.append({
            "video_id": str(vid["video_id"]).strip(),
            "channel_id": str(vid["channel_id"]).strip(),
            "title": str(vid["title"]).strip(),
            "description": str(vid.get("description", "")).strip(),
            "published_at": pub_at,
            "duration_seconds": int(vid.get("duration_seconds", 0)),
            "category_id": str(vid.get("category_id", "10")),
            "default_language": str(vid.get("default_language", "vi")),
            "provenance": str(vid.get("provenance", "SYNTHETIC_FIXTURE")),
            "view_count": int(vid.get("view_count", 0)),
            "like_count": int(vid.get("like_count", 0)),
            "comment_count": int(vid.get("comment_count", 0)),
            "tags": vid.get("tags", [])
        })
        
    return normalized_channels, normalized_videos

def ingest_to_sqlite(conn, run_id, channels, videos):
    cursor = conn.cursor()
    
    # 1. Source record
    cursor.execute("""
        INSERT OR IGNORE INTO sources (source_id, source_name, source_type, api_endpoint, last_fetched_at)
        VALUES ('SRC_SYNTHETIC_01', 'Offline Synthetic Fixtures', 'SYNTHETIC_FIXTURE', 'local://fixtures/seed_data.json', datetime('now'))
    """)
    
    # 2. Channels
    for ch in channels:
        cursor.execute("""
            INSERT OR REPLACE INTO channels 
            (channel_id, source_id, channel_title, custom_url, country, published_at, subscriber_count, total_views, video_count, last_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            ch["channel_id"], ch["source_id"], ch["channel_title"], ch["custom_url"],
            ch["country"], ch["published_at"], ch["subscriber_count"], ch["total_views"], ch["video_count"]
        ))
        
    # 3. Videos, Snapshots, Topic Tags
    captured_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for vid in videos:
        cursor.execute("""
            INSERT OR REPLACE INTO videos
            (video_id, channel_id, title, description, published_at, duration_seconds, category_id, default_language, provenance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vid["video_id"], vid["channel_id"], vid["title"], vid["description"],
            vid["published_at"], vid["duration_seconds"], vid["category_id"], vid["default_language"], vid["provenance"]
        ))
        
        # Snapshot record
        view_cnt = vid["view_count"]
        like_cnt = vid["like_count"]
        comment_cnt = vid["comment_count"]
        engagement = (like_cnt + comment_cnt) / max(view_cnt, 1)
        snapshot_id = f"SNAP_{vid['video_id']}_{run_id}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO video_snapshots
            (snapshot_id, video_id, run_id, captured_at, view_count, like_count, comment_count, engagement_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (snapshot_id, vid["video_id"], run_id, captured_at, view_cnt, like_cnt, comment_cnt, engagement))
        
        # Tags
        for tag in vid.get("tags", []):
            tag_id = f"TAG_{tag.upper().replace(' ', '_')}"
            cursor.execute("""
                INSERT OR IGNORE INTO topic_tags (tag_id, tag_name, category)
                VALUES (?, ?, 'MEDITATION_NICHE')
            """, (tag_id, tag.lower()))
            cursor.execute("""
                INSERT OR IGNORE INTO video_topic_tags (video_id, tag_id)
                VALUES (?, ?)
            """, (vid["video_id"], tag_id))
            
    conn.commit()

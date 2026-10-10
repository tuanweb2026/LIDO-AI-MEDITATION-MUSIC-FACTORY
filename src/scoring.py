import json
import datetime

def load_scoring_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_research_scores(conn, run_id, config_path):
    config = load_scoring_config(config_path)
    weights = config["weights"]
    formula_version = config.get("formula_version", "v1.0.0")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.video_id, v.published_at, s.view_count, s.like_count, s.comment_count, s.engagement_ratio
        FROM videos v
        JOIN video_snapshots s ON v.video_id = s.video_id
        WHERE s.run_id = ?
    """, (run_id,))
    rows = cursor.fetchall()
    
    scored_items = []
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for row in rows:
        video_id, pub_at_str, views, likes, comments, engagement = row
        
        # Momentum score based on views vs recency
        pub_dt = datetime.datetime.fromisoformat(pub_at_str.replace("Z", "+00:00"))
        days_old = max((now - pub_dt).days, 1)
        daily_views = views / days_old
        momentum_score = min(daily_views / 5000.0, 1.0) * 100.0
        
        # Engagement score
        engagement_score = min(engagement / 0.05, 1.0) * 100.0
        
        # Evergreen score (higher for videos older than 30 days maintaining steady ratio)
        evergreen_score = min(days_old / 90.0, 1.0) * 100.0
        
        # Saturation penalty (too many identical high view videos reduce opportunity score)
        saturation_penalty = min(views / 1500000.0, 1.0) * 50.0
        
        # Composite calculation
        composite = (
            weights["momentum"] * momentum_score +
            weights["engagement"] * engagement_score +
            weights["evergreen"] * evergreen_score -
            weights["saturation_penalty"] * saturation_penalty
        )
        composite = max(round(composite, 2), 0.0)
        
        scored_items.append({
            "video_id": video_id,
            "momentum_score": round(momentum_score, 2),
            "engagement_score": round(engagement_score, 2),
            "evergreen_score": round(evergreen_score, 2),
            "saturation_penalty": round(saturation_penalty, 2),
            "composite_score": composite
        })
        
    # Sort by composite_score descending
    scored_items.sort(key=lambda x: x["composite_score"], reverse=True)
    
    for rank, item in enumerate(scored_items, start=1):
        score_id = f"SCORE_{item['video_id']}_{run_id}"
        cursor.execute("""
            INSERT OR REPLACE INTO research_scores
            (score_id, run_id, video_id, formula_version, momentum_score, engagement_score, evergreen_score, saturation_penalty, composite_score, score_rank, scored_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            score_id, run_id, item["video_id"], formula_version,
            item["momentum_score"], item["engagement_score"], item["evergreen_score"],
            item["saturation_penalty"], item["composite_score"], rank
        ))
        
    conn.commit()
    return scored_items

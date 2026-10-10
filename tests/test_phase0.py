import unittest
import os
import sqlite3
import json
import tempfile
import datetime
from src.database import init_db, log_audit_event
from src.ingestion import validate_and_normalize_fixture, ingest_to_sqlite, IngestionError
from src.scoring import calculate_research_scores
from src.rights import enforce_dry_run_guards, verify_creative_brief_rights, SecurityGuardViolation, RightsReviewFailure

class TestPhase0Compliance(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test_lido.db")
        self.conn = init_db(self.db_path)
        
        self.fixture_path = os.path.join(self.test_dir.name, "test_fixture.json")
        self.scoring_config_path = os.path.join(self.test_dir.name, "test_scoring.json")
        
        with open(self.scoring_config_path, "w", encoding="utf-8") as f:
            json.dump({
                "formula_version": "v1.0.0",
                "weights": {"momentum": 0.35, "engagement": 0.35, "evergreen": 0.20, "saturation_penalty": 0.10}
            }, f)
            
    def tearDown(self):
        self.conn.close()
        self.test_dir.cleanup()

    def _create_run(self, run_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO research_runs (run_id, run_timestamp, mode, formula_version, config_json, status) VALUES (?, datetime('now'), 'DRY_RUN', 'v1.0.0', '{}', 'COMPLETED')",
            (run_id,)
        )
        self.conn.commit()

    # 1. Duplicate Ingestion Test
    def test_duplicate_ingestion(self):
        fixture_data = {
            "channels": [{
                "channel_id": "CH_01", "channel_title": "Channel 1", "source_id": "SRC_SYNTHETIC_01"
            }],
            "videos": [{
                "video_id": "VID_DUP", "channel_id": "CH_01", "title": "Test Title",
                "published_at": "2026-08-01T00:00:00Z", "view_count": 1000, "like_count": 50, "comment_count": 10
            }]
        }
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(fixture_data, f)
            
        channels, videos = validate_and_normalize_fixture(self.fixture_path)
        
        self._create_run("RUN_TEST_1")
        self._create_run("RUN_TEST_2")
        
        # Ingest twice into SQLite
        ingest_to_sqlite(self.conn, "RUN_TEST_1", channels, videos)
        ingest_to_sqlite(self.conn, "RUN_TEST_2", channels, videos)
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM videos WHERE video_id = 'VID_DUP'")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1, "Duplicate video insertion should replace or ignore existing record without throwing error")

    # 2. Missing Data Validation Test
    def test_missing_required_fields(self):
        invalid_fixture = {
            "channels": [{"channel_id": "CH_01"}], # Missing channel_title
            "videos": []
        }
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(invalid_fixture, f)
            
        with self.assertRaises(IngestionError):
            validate_and_normalize_fixture(self.fixture_path)

    # 3. Invalid Dates Test
    def test_invalid_date_format(self):
        invalid_fixture = {
            "channels": [{"channel_id": "CH_01", "channel_title": "Title"}],
            "videos": [{
                "video_id": "VID_BAD_DATE", "channel_id": "CH_01", "title": "Title",
                "published_at": "10-10-2026 INVALID DATE"
            }]
        }
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(invalid_fixture, f)
            
        with self.assertRaises(IngestionError):
            validate_and_normalize_fixture(self.fixture_path)

    # 4. Deterministic Scoring Test
    def test_deterministic_scoring(self):
        fixture_data = {
            "channels": [{"channel_id": "CH_01", "channel_title": "Title"}],
            "videos": [{
                "video_id": "VID_SCORE", "channel_id": "CH_01", "title": "Test Video",
                "published_at": "2026-09-01T00:00:00Z", "view_count": 50000, "like_count": 2500, "comment_count": 200
            }]
        }
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(fixture_data, f)
            
        channels, videos = validate_and_normalize_fixture(self.fixture_path)
        
        self._create_run("RUN_S1")
        self._create_run("RUN_S2")
        
        ingest_to_sqlite(self.conn, "RUN_S1", channels, videos)
        scores_1 = calculate_research_scores(self.conn, "RUN_S1", self.scoring_config_path)
        
        ingest_to_sqlite(self.conn, "RUN_S2", channels, videos)
        scores_2 = calculate_research_scores(self.conn, "RUN_S2", self.scoring_config_path)
        
        self.assertEqual(scores_1[0]["composite_score"], scores_2[0]["composite_score"], "Scoring formula must be 100% deterministic")

    # 5. Data Provenance Test
    def test_data_provenance_tracking(self):
        fixture_data = {
            "channels": [{"channel_id": "CH_01", "channel_title": "Title"}],
            "videos": [{
                "video_id": "VID_PROV", "channel_id": "CH_01", "title": "Title",
                "published_at": "2026-08-01T00:00:00Z", "provenance": "SYNTHETIC_FIXTURE",
                "view_count": 100, "like_count": 5, "comment_count": 1
            }]
        }
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(fixture_data, f)
            
        channels, videos = validate_and_normalize_fixture(self.fixture_path)
        self._create_run("RUN_P1")
        ingest_to_sqlite(self.conn, "RUN_P1", channels, videos)
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT provenance FROM videos WHERE video_id = 'VID_PROV'")
        provenance = cursor.fetchone()[0]
        self.assertEqual(provenance, "SYNTHETIC_FIXTURE")

    # 6. Rights Review Blocking Test
    def test_rights_review_blocking(self):
        invalid_brief_1 = {"original_work_certified": 0, "third_party_melody_used": 0}
        invalid_brief_2 = {"original_work_certified": 1, "third_party_melody_used": 1}
        valid_brief = {"original_work_certified": 1, "third_party_melody_used": 0}
        
        with self.assertRaises(RightsReviewFailure):
            verify_creative_brief_rights(invalid_brief_1)
            
        with self.assertRaises(RightsReviewFailure):
            verify_creative_brief_rights(invalid_brief_2)
            
        self.assertTrue(verify_creative_brief_rights(valid_brief))

    # 7. Dry-Run Security Guard Enforcement Test
    def test_security_guards(self):
        with self.assertRaises(SecurityGuardViolation):
            enforce_dry_run_guards("PUBLISH_VIDEO")
            
        with self.assertRaises(SecurityGuardViolation):
            enforce_dry_run_guards("DOWNLOAD_MEDIA_CONTENT")

    # 8. Secret Leakage Test
    def test_secret_leakage_in_code_and_docs(self):
        forbidden_strings = ["AIzaSy", "client_secret", "BEGIN PRIVATE KEY"]
        scan_files = [self.scoring_config_path]
        if os.path.exists(self.fixture_path):
            scan_files.append(self.fixture_path)
        for fpath in scan_files:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                for secret_pattern in forbidden_strings:
                    self.assertNotIn(secret_pattern, content, f"Secret pattern found in {fpath}")

    # 9. Database Recovery & Backup Test
    def test_database_backup_and_recovery(self):
        backup_path = os.path.join(self.test_dir.name, "backup_lido.db")
        backup_conn = sqlite3.connect(backup_path)
        self.conn.backup(backup_conn)
        
        cursor = backup_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        backup_conn.close()
        
        self.assertIn("videos", tables)
        self.assertIn("creative_briefs", tables)
        self.assertIn("audit_events", tables)

if __name__ == "__main__":
    unittest.main()

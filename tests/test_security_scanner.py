import unittest
import os
import tempfile
import json
from scripts.pre_push_check import run_secret_scan_on_content, scan_files_content, run_privacy_scan

class TestSecurityScannerNegativeAndPrivacy(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()

    # 1. Negative Test: Secret API Key Detection
    def test_negative_google_api_key_detection(self):
        fake_key = "AIza" + "Sy" + "A" * 35
        content = f"YOUTUBE_API_KEY = '{fake_key}'"
        violations = run_secret_scan_on_content(content, "Test Content")
        self.assertTrue(len(violations) > 0, "Scanner must detect fake Google API key")
        self.assertIn("Google API Key", violations[0])
        self.assertIn("[VALUE REDACTED]", violations[0])
        self.assertNotIn(fake_key, violations[0], "Actual secret value must never be printed in violation message")

    # 2. Negative Test: GitHub Personal Access Token Detection
    def test_negative_github_pat_detection(self):
        fake_pat = "ghp_" + "B" * 36
        content = f"TOKEN = '{fake_pat}'"
        violations = run_secret_scan_on_content(content, "Test Content")
        self.assertTrue(len(violations) > 0, "Scanner must detect fake GitHub PAT")
        self.assertIn("GitHub Personal Access Token", violations[0])
        self.assertIn("[VALUE REDACTED]", violations[0])

    # 3. Negative Test: Unsanitized Absolute Path Privacy Gate Failure
    def test_negative_privacy_gate_failure(self):
        bad_file = os.path.join(self.test_dir.name, "bad_report.md")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("Secret directory at /Users/unauthorized_user/Documents/secret_project")
            
        violations = run_privacy_scan([bad_file])
        self.assertTrue(len(violations) > 0, "Privacy gate must fail on unwhitelisted absolute user paths")
        self.assertIn("Unsanitized absolute path detected", violations[0])

    # 4. Whitelist Test: Whitelisted Path Exception Allowed
    def test_whitelisted_privacy_exception(self):
        whitelist_file = "reports/phase0_environment_audit.md"
        violations = run_privacy_scan([whitelist_file])
        self.assertEqual(len(violations), 0, "Whitelisted audit report should be permitted without raising privacy gate failure")

if __name__ == "__main__":
    unittest.main()

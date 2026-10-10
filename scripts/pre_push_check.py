#!/usr/bin/env python3
"""
Pre-Push & Security Verification Script
LIDO AI Meditation Music Factory — Phase 0.6 Bridge
"""

import sys
import os
import re
import json
import subprocess
import datetime

FORBIDDEN_PATTERNS = [
    (re.compile(r"AIzaSy[A-Za-z0-9_-]{35}"), "Google API Key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"gho_[A-Za-z0-9]{36}"), "GitHub OAuth Token"),
    (re.compile(r"-----BEGIN " + r"PRIVATE KEY-----"), "PEM Private Key"),
]

def get_git_commit_sha():
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"

def get_tracked_files():
    try:
        res = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
        return [f for f in res.stdout.splitlines() if os.path.isfile(f)]
    except Exception:
        files = []
        for root, _, fnames in os.walk("."):
            if ".git" in root:
                continue
            for f in fnames:
                files.append(os.path.relpath(os.path.join(root, f), "."))
        return files

def run_secret_scan(files):
    violations = []
    for filepath in files:
        # Exclude self-scanning of security rule patterns in pre_push_check.py and test_phase0.py
        if filepath in ["scripts/pre_push_check.py", "tests/test_phase0.py"]:
            continue
        if filepath.endswith(".db") or filepath.endswith(".png") or filepath.endswith(".jpg"):
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pattern, desc in FORBIDDEN_PATTERNS:
                    if pattern.search(content):
                        violations.append(f"Secret detected ({desc}) in file: {filepath}")
        except Exception as e:
            violations.append(f"Could not scan file {filepath}: {e}")
    return violations

def run_path_privacy_scan(files):
    warnings = []
    user_path_pattern = re.compile(r"/Users/[A-Za-z0-9_-]+/")
    for filepath in files:
        if filepath in ["reports/phase0_environment_audit.md"]:
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if user_path_pattern.search(content):
                    warnings.append(f"Absolute local path detected in: {filepath}")
        except Exception:
            pass
    return warnings

def run_tests():
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return res.returncode == 0, res.stdout + res.stderr

def update_bridge_status(commit_sha, test_passed, secret_passed, privacy_warnings):
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status_data = {
        "timestamp": timestamp,
        "commit_sha": commit_sha,
        "phase": "PHASE_0.6_BRIDGE",
        "phase_1_authorized": False,
        "test_status": "PASSED" if test_passed else "FAILED",
        "secret_scan_status": "PASSED" if secret_passed else "FAILED",
        "privacy_warnings": privacy_warnings,
        "sync_status": "VERIFIED_LOCAL",
        "review_status": "AWAITING_CHATGPT_REVIEW"
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/bridge_status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

def main():
    print("=== LIDO AI MEDITATION MUSIC FACTORY — PRE-PUSH CHECK ===")
    commit_sha = get_git_commit_sha()
    print(f"Commit SHA: {commit_sha}")
    
    files = get_tracked_files()
    print(f"Tracked Files Scanned: {len(files)}")
    
    secret_violations = run_secret_scan(files)
    privacy_warnings = run_path_privacy_scan(files)
    
    if secret_violations:
        print("\n[ERROR] Secret scanning failed:")
        for v in secret_violations:
            print(f"  - {v}")
    else:
        print("[PASS] Secret scan clean.")
        
    if privacy_warnings:
        print("\n[WARNING] Absolute path privacy scan found items:")
        for w in privacy_warnings:
            print(f"  - {w}")
    else:
        print("[PASS] Privacy scan clean.")
        
    print("\nExecuting Unit Test Suite...")
    test_passed, test_output = run_tests()
    
    if test_passed:
        print("[PASS] Unit tests passed.")
    else:
        print("[FAIL] Unit tests failed:\n" + test_output)
        
    secret_passed = len(secret_violations) == 0
    update_bridge_status(commit_sha, test_passed, secret_passed, privacy_warnings)
    
    if secret_passed and test_passed:
        print("\nSUCCESS: All pre-push checks passed cleanly.")
        sys.exit(0)
    else:
        print("\nFAILURE: Pre-push checks failed. Push blocked.")
        sys.exit(1)

if __name__ == "__main__":
    main()

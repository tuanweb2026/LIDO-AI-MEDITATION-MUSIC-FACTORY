#!/usr/bin/env python3
"""
Pre-Push & Security Verification Script (Hardened v2.0)
LIDO AI Meditation Music Factory — Phase 0.6.1 CI & Security Hardening
"""

import sys
import os
import re
import json
import subprocess
import datetime
import argparse

# Secret Detection Regex Patterns constructed via string concatenation and line boundary anchors
SECRET_PATTERNS = [
    (re.compile(r"AI" + r"zaSy[A-Za-z0-9_-]{35}"), "Google API Key"),
    (re.compile(r"gh" + r"p_[A-Za-z0-9]{36}"), "GitHub Personal Access Token (Classic)"),
    (re.compile(r"gh" + r"o_[A-Za-z0-9]{36}"), "GitHub OAuth Token"),
    (re.compile(r"gh" + r"u_[A-Za-z0-9]{36}"), "GitHub User-to-Server Token"),
    (re.compile(r"gh" + r"s_[A-Za-z0-9]{36}"), "GitHub Server-to-Server Token"),
    (re.compile(r"gh" + r"r_[A-Za-z0-9]{36}"), "GitHub Refresh Token"),
    (re.compile(r"AK" + r"IA[0-9A-Z]{16}"), "AWS Access Key ID"),
    (re.compile(r"(?m)^[\+\s]*-----BEGIN (?:RSA |OPENSSH |EC |DSA |PKCS8 )?PRIVATE KEY-----"), "PEM Private Key Block"),
    (re.compile(r"xox" + r"b-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}"), "Slack Bot Token"),
    (re.compile(r"post" + r"gresql://[^:]+:[^@\s]+@[^/\s]+/\w+"), "PostgreSQL Connection URI with Password"),
    (re.compile(r"my" + r"sql://[^:]+:[^@\s]+@[^/\s]+/\w+"), "MySQL Connection URI with Password"),
]

# Documented Whitelist for Absolute Paths (Explicitly justified & tested)
PRIVACY_PATH_WHITELIST = [
    "reports/phase0_environment_audit.md", # Environment audit report explicitly documents local audit directory path
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

def get_staged_files():
    try:
        res = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True, check=True)
        return [f for f in res.stdout.splitlines() if os.path.isfile(f)]
    except Exception:
        return []

def run_secret_scan_on_content(content, source_label):
    violations = []
    for pattern, desc in SECRET_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            violations.append(f"Secret type [{desc}] detected in {source_label} (Count: {len(matches)}). [VALUE REDACTED]")
    return violations

def scan_files_content(files, scope_name):
    violations = []
    for filepath in files:
        if filepath.endswith(".db") or filepath.endswith(".png") or filepath.endswith(".jpg") or filepath.endswith(".pyc"):
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                file_violations = run_secret_scan_on_content(content, f"{scope_name} file '{filepath}'")
                violations.extend(file_violations)
        except Exception as e:
            violations.append(f"Could not read {filepath}: {e}")
    return violations

def scan_git_history():
    violations = []
    try:
        res = subprocess.run(["git", "log", "-p", "--all"], capture_output=True, text=True, check=True)
        history_content = res.stdout
        history_violations = run_secret_scan_on_content(history_content, "Git Commit History")
        violations.extend(history_violations)
    except Exception as e:
        violations.append(f"Git history scan failed to execute: {e}")
    return violations

def run_privacy_scan(files):
    violations = []
    user_path_pattern = re.compile(r"/Users/[A-Za-z0-9_-]+/")
    for filepath in files:
        if filepath in PRIVACY_PATH_WHITELIST:
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = user_path_pattern.findall(content)
                if matches:
                    violations.append(f"Unsanitized absolute path detected in '{filepath}' (Count: {len(matches)})")
        except Exception as e:
            violations.append(f"Privacy scan read error on {filepath}: {e}")
    return violations

def run_tests():
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return res.returncode == 0, res.stdout + res.stderr

def update_bridge_status(commit_sha, test_passed, secret_passed, privacy_passed, details):
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status_data = {
        "timestamp": timestamp,
        "commit_sha": commit_sha,
        "phase": "PHASE_0.6.1_CI_SECURITY_HARDENING",
        "phase_1_authorized": False,
        "test_status": "PASSED" if test_passed else "FAILED",
        "secret_scan_status": "PASSED" if secret_passed else "FAILED",
        "privacy_scan_status": "PASSED" if privacy_passed else "FAILED",
        "sync_status": "VERIFIED_LOCAL",
        "review_status": "AWAITING_CHATGPT_REVIEW",
        "scan_details": details
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/bridge_status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="LIDO Pre-Push & Security Verification Gate")
    parser.add_argument("--full-scan", action="store_true", help="Perform full Git history scan in addition to file scans")
    args = parser.parse_args()

    print("=== LIDO AI MEDITATION MUSIC FACTORY — HARDENED SECURITY & COMPLIANCE GATE ===")
    commit_sha = get_git_commit_sha()
    print(f"Commit SHA: {commit_sha}")
    
    tracked_files = get_tracked_files()
    staged_files = get_staged_files()
    
    print(f"Tracked Files: {len(tracked_files)} | Staged Files: {len(staged_files)}")
    
    secret_violations = scan_files_content(tracked_files, "Tracked")
    if staged_files:
        secret_violations.extend(scan_files_content(staged_files, "Staged"))
        
    history_scanned = False
    if args.full_scan or os.environ.get("CI") == "true":
        print("Executing Full Git History Secret Scan...")
        history_violations = scan_git_history()
        secret_violations.extend(history_violations)
        history_scanned = True
        
    secret_passed = len(secret_violations) == 0
    if secret_passed:
        print("[PASS] Secret scan clean (Zero keys/tokens found).")
    else:
        print("[FAIL] Secret scanning failed:")
        for v in secret_violations:
            print(f"  - {v}")
            
    privacy_violations = run_privacy_scan(tracked_files)
    privacy_passed = len(privacy_violations) == 0
    if privacy_passed:
        print("[PASS] Privacy scan clean (Zero unsanitized absolute paths found).")
    else:
        print("[FAIL] Privacy gate failed:")
        for pv in privacy_violations:
            print(f"  - {pv}")
            
    print("\nExecuting Unit Test Suite...")
    test_passed, test_output = run_tests()
    if test_passed:
        print("[PASS] Unit tests passed.")
    else:
        print("[FAIL] Unit tests failed:\n" + test_output)
        
    details = {
        "tracked_files_count": len(tracked_files),
        "history_scanned": history_scanned,
        "secret_violations_count": len(secret_violations),
        "privacy_violations_count": len(privacy_violations)
    }
    
    update_bridge_status(commit_sha, test_passed, secret_passed, privacy_passed, details)
    
    if secret_passed and privacy_passed and test_passed:
        print("\nSUCCESS: All security, privacy, and test gates passed cleanly.")
        sys.exit(0)
    else:
        print("\nFAILURE: Compliance gate failed. Operation blocked.")
        sys.exit(1)

if __name__ == "__main__":
    main()

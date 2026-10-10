#!/usr/bin/env python3
"""
Git Pre-Push Hook Installer & Verification Utility
LIDO AI Meditation Music Factory — Phase 0.6.1
"""

import os
import sys
import stat

HOOK_SCRIPT = """#!/bin/sh
# Git Pre-Push Hook for LIDO AI Meditation Music Factory
# Runs security scan, privacy audit, and unit tests before allowing git push

echo "Executing pre-push compliance check..."
PYTHONPATH=. python3 scripts/pre_push_check.py

if [ $? -ne 0 ]; then
    echo "Git push aborted due to failed pre-push security/compliance check."
    exit 1
fi
"""

def install_hook():
    git_dir = ".git"
    if not os.path.exists(git_dir):
        print("[ERROR] .git directory not found. Please run inside git repository root.")
        sys.exit(1)
        
    hooks_dir = os.path.join(git_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    
    hook_path = os.path.join(hooks_dir, "pre-push")
    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(HOOK_SCRIPT)
        
    # Make executable
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)
    
    print(f"[SUCCESS] Git pre-push hook installed successfully at {hook_path}")

if __name__ == "__main__":
    install_hook()

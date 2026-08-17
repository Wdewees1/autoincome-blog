#!/usr/bin/env python3
"""
AutoIncome Blog — Git Deploy Script
Builds the site and pushes to GitHub for GitHub Pages deployment.
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path("/opt/data/autoincome-blog")
OUTPUT_DIR = BASE_DIR / "output"
GH_BIN = os.path.expanduser("~/.local/bin/gh")

def run(cmd, check=True, capture=False):
    """Run a shell command."""
    print(f"  $ {cmd}")
    env = os.environ.copy()
    env["PATH"] = os.path.expanduser("~/.local/bin:") + env.get("PATH", "")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True, env=env, cwd=str(BASE_DIR))
    if check and result.returncode != 0:
        print(f"  ❌ Error (exit {result.returncode})")
        if capture:
            print(result.stderr)
        sys.exit(1)
    return result

def main():
    git_remote = os.environ.get("GIT_REMOTE_URL", "")

    if not git_remote:
        print("❌ No GIT_REMOTE_URL set.")
        print("   Run: export GIT_REMOTE_URL='https://github.com/YOUR_USERNAME/autoincome-blog.git'")
        print("   Then re-run this script.")
        sys.exit(1)

    # Set git identity if not set
    run("git config user.name 'AI Tools Daily' || true", check=False)
    run("git config user.email 'aitoolsdaily@users.noreply.github.com' || true", check=False)

    # Init repo if needed
    if not (BASE_DIR / ".git").exists():
        run("git init")
        run("git branch -M main")

    # Add remote if not present
    run(f"git remote remove origin 2>/dev/null || true", check=False)
    run(f"git remote add origin {git_remote}")

    # Build the site
    print("🔨 Building site...")
    run("python3 build_site.py")

    # Stage everything
    print("📦 Staging files...")
    run("git add -A")

    # Commit
    print("💾 Committing...")
    run("git commit -m 'Auto-deploy: rebuild site with latest articles' || true", check=False)

    # Push
    print("🚀 Pushing to GitHub...")
    run("git push -u origin main --force")

    print()
    print("✅ Deploy complete!")
    print(f"   Your site will be live at the GitHub Pages URL you configured.")
    print(f"   (Settings → Pages in your repo)")


if __name__ == "__main__":
    main()

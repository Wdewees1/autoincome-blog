#!/usr/bin/env python3
"""
AutoIncome Blog — Git Deploy Script
Builds the site and pushes to GitHub for GitHub Pages deployment.

Requires GITHUB_TOKEN environment variable to be set.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def run(cmd, check=True):
    """Run a shell command."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(BASE_DIR))
    if check and result.returncode != 0:
        print(f"  ❌ Error (exit {result.returncode})")
        if result.stderr:
            print(f"  {result.stderr.strip()}")
        return False
    return True


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set!")
        sys.exit(1)

    remote_url = f"https://Wdewees1:{token}@github.com/Wdewees1/autoincome-blog.git"
    python_bin = sys.executable

    # Set git identity
    run('git config user.name "Wdewees1"', check=False)
    run('git config user.email "317993808+wdewees1@users.noreply.github.com"', check=False)

    # Set remote URL
    run(f'git remote set-url origin "{remote_url}"', check=False)
    run(f'git remote add origin "{remote_url}"', check=False)

    # Build the site
    print("🔨 Building site...")
    run(f'"{python_bin}" build_site.py')

    # Copy output to docs/ for GitHub Pages
    print("📋 Copying output to docs/...")
    docs_dir = BASE_DIR / "docs"
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    shutil.copytree(OUTPUT_DIR, docs_dir)

    # Stage everything
    print("📦 Staging files...")
    run("git add -A")

    # Commit
    print("💾 Committing...")
    run('git commit -m "Auto-deploy: rebuild site with latest articles"', check=False)

    # Push
    print("🚀 Pushing to GitHub...")
    if run("git push -u origin main"):
        print()
        print("✅ Deploy complete!")
        print("   Site: https://wdewees1.github.io/autoincome-blog/")
    else:
        print()
        print("❌ Push failed. Check errors above.")


if __name__ == "__main__":
    main()

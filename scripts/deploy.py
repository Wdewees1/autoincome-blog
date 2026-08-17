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
    git_remote = "https://github.com/Wdewees1/autoincome-blog.git"

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

    # Copy output to docs/ for GitHub Pages (serves from /docs folder)
    print("📋 Copying output to docs/...")
    import shutil
    docs_dir = BASE_DIR / "docs"
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    shutil.copytree(OUTPUT_DIR, docs_dir)

    # Stage everything
    print("📦 Staging files...")
    run("git add -A")

    # Commit
    print("💾 Committing...")
    run("git commit -m 'Auto-deploy: rebuild site with latest articles' || true", check=False)

    # Push
    print("🚀 Pushing to GitHub...")
    run("git push -u origin main")

    # Trigger Pages rebuild
    print("🔄 Triggering Pages rebuild...")
    run("gh api -X POST repos/Wdewees1/autoincome-blog/pages/builds || true", check=False)

    print()
    print("✅ Deploy complete!")
    print("   Site: https://wdewees1.github.io/autoincome-blog/")


if __name__ == "__main__":
    main()

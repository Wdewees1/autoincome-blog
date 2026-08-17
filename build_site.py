#!/usr/bin/env python3
"""
AutoIncome Blog — Static Site Generator
Generates a professional, SEO-optimized blog site from Markdown posts.
No dependencies — pure Python 3.
"""

import os
import re
import json
import html
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
POSTS_DIR = BASE_DIR / "posts"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = BASE_DIR / "static"
CONFIG_PATH = BASE_DIR / "config.json"

# ─── Config ───────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "site_name": "AI Tools Daily",
    "site_tagline": "Your daily source for AI tools, reviews, and tutorials",
    "site_url": "https://yourusername.github.io/autoincome-blog",
    "site_description": "Discover the best AI tools, tutorials, and reviews updated daily. Stay ahead of the AI revolution.",
    "site_author": "AI Tools Daily",
    "social_twitter": "@aitoolsdaily",
    "affiliate_id": "YOUR_AFFILIATE_ID",
    "posts_per_page": 10,
    "footer_text": "© 2026 AI Tools Daily. All rights reserved.",
    "nav_links": [
        {"label": "Home", "url": "/"},
        {"label": "AI Tools", "url": "/category/ai-tools.html"},
        {"label": "Tutorials", "url": "/category/tutorials.html"},
        {"label": "Reviews", "url": "/category/reviews.html"},
        {"label": "News", "url": "/category/news.html"},
    ],
}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        merged = {**DEFAULT_CONFIG, **cfg}
        return merged
    return DEFAULT_CONFIG


CONFIG = load_config()


# ─── Markdown to HTML (minimal parser) ───────────────────────────────────────

def md_to_html(text):
    """Convert a subset of Markdown to HTML."""
    lines = text.strip().split("\n")
    html_lines = []
    in_list = False
    in_ol = False
    in_paragraph = False

    def close_lists():
        nonlocal in_list, in_ol
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    def close_paragraph():
        nonlocal in_paragraph
        if in_paragraph:
            html_lines.append("</p>")
            in_paragraph = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            close_paragraph()
            close_lists()
            continue
        # Headings
        if stripped.startswith("### "):
            close_paragraph()
            close_lists()
            html_lines.append(f"<h3>{inline_md(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_paragraph()
            close_lists()
            html_lines.append(f"<h2>{inline_md(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_paragraph()
            close_lists()
            html_lines.append(f"<h1>{inline_md(stripped[2:])}</h1>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            close_paragraph()
            if not in_list:
                close_lists()
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{inline_md(stripped[2:])}</li>")
        elif re.match(r"^\d+\. ", stripped):
            close_paragraph()
            if not in_ol:
                close_lists()
                html_lines.append("<ol>")
                in_ol = True
            cleaned = re.sub(r'^\d+\. ', '', stripped)
            html_lines.append(f"<li>{inline_md(cleaned)}</li>")
        else:
            close_lists()
            if not in_paragraph:
                html_lines.append("<p>")
                in_paragraph = True
            html_lines.append(inline_md(stripped) + " ")

    close_paragraph()
    close_lists()
    return "\n".join(html_lines)


def inline_md(text):
    """Process inline markdown: bold, italic, links, code."""
    # Code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Links [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


# ─── Post parsing ───────────────────────────────────────────────────────────

def parse_post(filepath):
    """Parse a Markdown file with YAML-like frontmatter."""
    with open(filepath, "r") as f:
        content = f.read()

    # Extract frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
        else:
            frontmatter = ""
            body = content
    else:
        frontmatter = ""
        body = content

    post = {}
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",")]
            post[key] = val

    post["content"] = body
    post["html"] = md_to_html(body)
    post["slug"] = filepath.stem

    # Date handling
    date_str = post.get("date", "")
    try:
        post["date_obj"] = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        post["date_obj"] = datetime.datetime.now()

    post["date_display"] = post["date_obj"].strftime("%B %d, %Y")
    post["iso_date"] = post["date_obj"].strftime("%Y-%m-%d")

    # Excerpt (first ~200 chars of plain text)
    plain = re.sub(r"[#*`\[\]()]|\([^)]+\)", "", body)
    plain = re.sub(r"\s+", " ", plain).strip()
    post["excerpt"] = plain[:200] + "..." if len(plain) > 200 else plain

    return post


def get_all_posts():
    posts = []
    if not POSTS_DIR.exists():
        return posts
    for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        try:
            post = parse_post(f)
            posts.append(post)
        except Exception as e:
            print(f"  ⚠ Error parsing {f.name}: {e}")
    # Sort by date descending
    posts.sort(key=lambda p: p["date_obj"], reverse=True)
    return posts


# ─── HTML templates ──────────────────────────────────────────────────────────

def render_head(title, description, canonical="", extra=""):
    og_url = canonical or CONFIG["site_url"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(description)}">
    <meta name="author" content="{html.escape(CONFIG['site_author'])}">
    <link rel="canonical" href="{og_url}">
    <!-- Open Graph -->
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(description)}">
    <meta property="og:url" content="{og_url}">
    <meta property="og:site_name" content="{html.escape(CONFIG['site_name'])}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(title)}">
    <meta name="twitter:description" content="{html.escape(description)}">
    <meta name="twitter:site" content="{CONFIG['social_twitter']}">
    <!-- RSS -->
    <link rel="alternate" type="application/rss+xml" title="{html.escape(CONFIG['site_name'])}" href="/feed.xml">
    <link rel="sitemap" type="application/xml" href="/sitemap.xml">
    {extra}
    <style>{get_css()}</style>
</head>"""


def render_nav():
    nav_items = ""
    for link in CONFIG["nav_links"]:
        nav_items += f'<a href="{link["url"]}" class="nav-link">{link["label"]}</a>'
    return f"""<header class="site-header">
    <div class="container">
        <div class="header-inner">
            <a href="/" class="logo">
                <span class="logo-icon">🤖</span>
                <span class="logo-text">{html.escape(CONFIG['site_name'])}</span>
            </a>
            <nav class="main-nav">
                {nav_items}
            </nav>
            <button class="menu-toggle" onclick="document.querySelector('.main-nav').classList.toggle('open')">☰</button>
        </div>
    </div>
</header>"""


def render_footer():
    return f"""<footer class="site-footer">
    <div class="container">
        <div class="footer-inner">
            <div class="footer-col">
                <h3>{html.escape(CONFIG['site_name'])}</h3>
                <p>{html.escape(CONFIG['site_description'])}</p>
            </div>
            <div class="footer-col">
                <h4>Explore</h4>
                {''.join(f'<a href="{l["url"]}">{l["label"]}</a>' for l in CONFIG['nav_links'])}
            </div>
            <div class="footer-col">
                <h4>Stay Updated</h4>
                <p>Subscribe via <a href="/feed.xml">RSS</a></p>
                <p class="footer-text">{html.escape(CONFIG['footer_text'])}</p>
            </div>
        </div>
    </div>
</footer>
<script>
document.querySelectorAll('a[href^="/"]').forEach(a => {{
    a.addEventListener('click', function(e) {{
        // Smooth scroll for internal anchors
        if (this.getAttribute('href').startsWith('/#')) {{
            e.preventDefault();
            document.querySelector(this.getAttribute('href').slice(1)).scrollIntoView({{behavior:'smooth'}});
        }}
    }});
}});
</script>"""


def get_css():
    return """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f1117;--surface:#1a1d27;--surface2:#222632;--border:#2d3141;--text:#e4e6eb;--text-muted:#9ca3af;--primary:#6c5ce7;--primary-hover:#7f70ef;--accent:#00cec9;--link:#74b9ff;--danger:#e74c3c;--success:#00b894;--warning:#fdcb6e}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:16px}
.container{max-width:1100px;margin:0 auto;padding:0 20px}
a{color:var(--link);text-decoration:none;transition:color .2s}
a:hover{color:var(--primary-hover)}
.site-header{background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filter:blur(10px)}
.header-inner{display:flex;align-items:center;justify-content:space-between;padding:16px 20px}
.logo{display:flex;align-items:center;gap:8px;font-size:1.4rem;font-weight:800;color:var(--text)}
.logo:hover{color:var(--text)}
.logo-icon{font-size:1.6rem}
.main-nav{display:flex;gap:24px}
.nav-link{color:var(--text-muted);font-weight:500;font-size:.95rem;padding:6px 0;position:relative}
.nav-link:hover{color:var(--text)}
.nav-link::after{content:'';position:absolute;bottom:0;left:0;width:0;height:2px;background:var(--primary);transition:width .2s}
.nav-link:hover::after{width:100%}
.menu-toggle{display:none;background:none;border:none;color:var(--text);font-size:1.5rem;cursor:pointer}
.hero{padding:60px 0 40px;text-align:center;background:linear-gradient(135deg,var(--surface) 0%,var(--bg) 100%)}
.hero h1{font-size:2.5rem;margin-bottom:12px;background:linear-gradient(135deg,var(--primary) 0%,var(--accent) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{color:var(--text-muted);font-size:1.1rem;max-width:600px;margin:0 auto}
.post-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:24px;padding:40px 0}
.post-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;transition:transform .2s,border-color .2s}
.post-card:hover{transform:translateY(-4px);border-color:var(--primary)}
.post-card-content{padding:20px}
.post-card-category{display:inline-block;font-size:.75rem;color:var(--accent);font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.post-card-title{font-size:1.15rem;font-weight:700;margin-bottom:8px;line-height:1.4}
.post-card-title a{color:var(--text)}
.post-card-excerpt{color:var(--text-muted);font-size:.9rem;margin-bottom:12px}
.post-card-meta{display:flex;gap:12px;font-size:.8rem;color:var(--text-muted)}
.post-card-meta span{display:flex;align-items:center;gap:4px}
.article{max-width:760px;margin:0 auto;padding:40px 20px}
.article-header{margin-bottom:32px;text-align:center}
.article-header h1{font-size:2rem;line-height:1.3;margin-bottom:16px}
.article-meta{color:var(--text-muted);font-size:.9rem}
.article-meta span{margin:0 8px}
.article-body{font-size:1.05rem;line-height:1.8}
.article-body h2{margin:32px 0 12px;font-size:1.5rem}
.article-body h3{margin:24px 0 10px;font-size:1.2rem}
.article-body p{margin-bottom:16px}
.article-body ul,.article-body ol{margin:0 0 16px 24px}
.article-body li{margin-bottom:6px}
.article-body code{background:var(--surface2);padding:2px 6px;border-radius:4px;font-size:.9em}
.article-body a{color:var(--link);text-decoration:underline}
.cta-box{background:linear-gradient(135deg,var(--primary) 0%,var(--accent) 100%);border-radius:12px;padding:24px;text-align:center;margin:32px 0}
.cta-box h3{color:#fff;margin-bottom:8px}
.cta-box p{color:rgba(255,255,255,.9);margin-bottom:16px}
.cta-box a{display:inline-block;background:#fff;color:var(--primary);padding:10px 24px;border-radius:8px;font-weight:700;text-decoration:none}
.pagination{display:flex;justify-content:center;gap:8px;padding:20px 0 40px}
.pagination a,.pagination span{padding:8px 14px;border-radius:6px;font-size:.9rem}
.pagination a{background:var(--surface);border:1px solid var(--border);color:var(--text)}
.pagination a:hover{background:var(--primary);color:#fff}
.pagination .current{background:var(--primary);color:#fff}
.site-footer{background:var(--surface);border-top:1px solid var(--border);padding:40px 0;margin-top:60px}
.footer-inner{display:grid;grid-template-columns:2fr 1fr 1fr;gap:32px}
.footer-col h3{font-size:1.1rem;margin-bottom:12px}
.footer-col h4{font-size:.9rem;margin-bottom:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted)}
.footer-col a{display:block;color:var(--text-muted);font-size:.9rem;margin-bottom:6px}
.footer-col p{color:var(--text-muted);font-size:.9rem}
.footer-text{margin-top:12px;font-size:.8rem;color:var(--text-muted);opacity:.6}
.category-header{padding:40px 0 20px}
.category-header h1{font-size:1.8rem;margin-bottom:8px}
.category-header p{color:var(--text-muted)}
@media(max-width:768px){.main-nav{display:none;position:absolute;top:100%;left:0;right:0;background:var(--surface);flex-direction:column;padding:16px;gap:12px}.menu-toggle{display:block}.post-grid{grid-template-columns:1fr}.footer-inner{grid-template-columns:1fr}.hero h1{font-size:1.8rem}}
    """


def render_cta_box():
    """Affiliate CTA box included at the bottom of every article."""
    return """
<div class="cta-box">
    <h3>⚡ Get Started with AI Tools Today</h3>
    <p>Join thousands of professionals using AI to boost productivity. Start your free trial now!</p>
    <a href="#" onclick="alert('Replace this link with your affiliate link!');return false;">Try Free →</a>
</div>"""


# ─── Page generators ─────────────────────────────────────────────────────────

def generate_homepage(posts, page=1):
    per_page = CONFIG["posts_per_page"]
    total_pages = max(1, (len(posts) + per_page - 1) // per_page)
    start = (page - 1) * per_page
    page_posts = posts[start : start + per_page]

    cards = ""
    for post in page_posts:
        category = post.get("category", "General")
        tags = post.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        cards += f"""<article class="post-card">
    <div class="post-card-content">
        <span class="post-card-category">{html.escape(category)}</span>
        <h2 class="post-card-title"><a href="/posts/{post['slug']}.html">{html.escape(post.get('title', 'Untitled'))}</a></h2>
        <p class="post-card-excerpt">{html.escape(post['excerpt'])}</p>
        <div class="post-card-meta">
            <span>📅 {post['date_display']}</span>
            <span>⏱ {post.get('read_time', '5 min')} read</span>
        </div>
    </div>
</article>"""

    pagination = ""
    if total_pages > 1:
        pagination = '<div class="pagination">'
        for i in range(1, total_pages + 1):
            if i == page:
                pagination += f'<span class="current">{i}</span>'
            elif i == 1:
                pagination += f'<a href="/index.html">{i}</a>'
            else:
                pagination += f'<a href="/page/{i}.html">{i}</a>'
        pagination += "</div>"

    content = f"""<section class="hero">
    <div class="container">
        <h1>{html.escape(CONFIG['site_name'])}</h1>
        <p>{html.escape(CONFIG['site_tagline'])}</p>
    </div>
</section>
<div class="container">
    <div class="post-grid">
        {cards}
    </div>
    {pagination}
</div>"""

    page_title = f"{CONFIG['site_name']} — {CONFIG['site_tagline']}" if page == 1 else f"Page {page} — {CONFIG['site_name']}"
    return f"""{render_head(page_title, CONFIG['site_description'], CONFIG['site_url'])}
<body>
{render_nav()}
{content}
{render_footer()}
</body>
</html>"""


def generate_article_page(post):
    canonical = f"{CONFIG['site_url']}/posts/{post['slug']}.html"
    tags = post.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tags_html = " ".join(f'<span style="display:inline-block;background:var(--surface2);padding:4px 10px;border-radius:4px;font-size:.8rem;margin:2px">{html.escape(t)}</span>' for t in tags)

    body = f"""<article class="article">
    <div class="article-header">
        <span class="post-card-category">{html.escape(post.get('category', 'General'))}</span>
        <h1>{html.escape(post.get('title', 'Untitled'))}</h1>
        <div class="article-meta">
            <span>📅 {post['date_display']}</span>
            <span>·</span>
            <span>⏱ {post.get('read_time', '5 min')} read</span>
            <span>·</span>
            <span>✍️ {html.escape(CONFIG['site_author'])}</span>
        </div>
    </div>
    <div class="article-body">
        {post['html']}
        {render_cta_box()}
        <div style="margin-top:24px">{tags_html}</div>
    </div>
</article>"""

    return f"""{render_head(post.get('title', 'Untitled'), post.get('excerpt', ''), canonical)}
<body>
{render_nav()}
{body}
{render_footer()}
</body>
</html>"""


def generate_category_page(category, posts):
    filtered = [p for p in posts if p.get("category", "General").lower() == category.lower()]
    cards = ""
    for post in filtered:
        cards += f"""<article class="post-card">
    <div class="post-card-content">
        <span class="post-card-category">{html.escape(post.get('category', 'General'))}</span>
        <h2 class="post-card-title"><a href="/posts/{post['slug']}.html">{html.escape(post.get('title', 'Untitled'))}</a></h2>
        <p class="post-card-excerpt">{html.escape(post['excerpt'])}</p>
        <div class="post-card-meta"><span>📅 {post['date_display']}</span></div>
    </div>
</article>"""

    content = f"""<section class="category-header">
    <div class="container">
        <h1>{html.escape(category.title())}</h1>
        <p>{len(filtered)} article(s) in this category</p>
    </div>
</section>
<div class="container"><div class="post-grid">{cards}</div></div>"""

    slug = category.lower().replace(" ", "-")
    canonical = f"{CONFIG['site_url']}/category/{slug}.html"
    return f"""{render_head(f"{category.title()} — {CONFIG['site_name']}", f"Articles about {category}", canonical)}
<body>
{render_nav()}
{content}
{render_footer()}
</body>
</html>"""


def generate_rss_feed(posts):
    items = ""
    for post in posts[:20]:
        url = f"{CONFIG['site_url']}/posts/{post['slug']}.html"
        items += f"""<item>
    <title>{html.escape(post.get('title', ''))}</title>
    <link>{url}</link>
    <guid isPermaLink="true">{url}</guid>
    <description>{html.escape(post['excerpt'])}</description>
    <pubDate>{post['date_obj'].strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
    <category>{html.escape(post.get('category', 'General'))}</category>
</item>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>{html.escape(CONFIG['site_name'])}</title>
    <link>{CONFIG['site_url']}</link>
    <description>{html.escape(CONFIG['site_description'])}</description>
    <language>en-us</language>
    {items}
</channel>
</rss>"""


def generate_sitemap(posts):
    urls = f"""<url><loc>{CONFIG['site_url']}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>"""
    for post in posts:
        urls += f"\n<url><loc>{CONFIG['site_url']}/posts/{post['slug']}.html</loc><lastmod>{post['iso_date']}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>"

    categories = set(p.get("category", "General") for p in posts)
    for cat in categories:
        slug = cat.lower().replace(" ", "-")
        urls += f"\n<url><loc>{CONFIG['site_url']}/category/{slug}.html</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""


def generate_robots_txt():
    return f"""User-agent: *
Allow: /
Sitemap: {CONFIG['site_url']}/sitemap.xml"""


# ─── Main build ──────────────────────────────────────────────────────────────

def build():
    print("🔨 Building site...")
    posts = get_all_posts()
    print(f"  📄 Found {len(posts)} posts")

    # Clean output
    if OUTPUT_DIR.exists():
        import shutil
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    (OUTPUT_DIR / "posts").mkdir()
    (OUTPUT_DIR / "category").mkdir()
    (OUTPUT_DIR / "page").mkdir()

    # Homepage
    home = generate_homepage(posts, page=1)
    (OUTPUT_DIR / "index.html").write_text(home)
    print("  ✅ Homepage")

    # Pagination
    per_page = CONFIG["posts_per_page"]
    total_pages = max(1, (len(posts) + per_page - 1) // per_page)
    for p in range(2, total_pages + 1):
        page_html = generate_homepage(posts, page=p)
        (OUTPUT_DIR / "page" / f"{p}.html").write_text(page_html)
    print(f"  ✅ {total_pages} page(s)")

    # Article pages
    for post in posts:
        page = generate_article_page(post)
        (OUTPUT_DIR / "posts" / f"{post['slug']}.html").write_text(page)
    print(f"  ✅ {len(posts)} article page(s)")

    # Category pages
    categories = set(p.get("category", "General") for p in posts)
    for cat in categories:
        slug = cat.lower().replace(" ", "-")
        page = generate_category_page(cat, posts)
        (OUTPUT_DIR / "category" / f"{slug}.html").write_text(page)
    print(f"  ✅ {len(categories)} category page(s)")

    # RSS feed
    (OUTPUT_DIR / "feed.xml").write_text(generate_rss_feed(posts))
    print("  ✅ RSS feed")

    # Sitemap
    (OUTPUT_DIR / "sitemap.xml").write_text(generate_sitemap(posts))
    print("  ✅ Sitemap")

    # Robots.txt
    (OUTPUT_DIR / "robots.txt").write_text(generate_robots_txt())
    print("  ✅ robots.txt")

    # Copy static files if any
    if STATIC_DIR.exists():
        import shutil
        for f in STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy2(f, OUTPUT_DIR / f.name)
        print("  ✅ Static files")

    print(f"\n✨ Build complete! Output in: {OUTPUT_DIR}")
    print(f"   Open with: python3 -m http.server -d {OUTPUT_DIR} 8000")
    return True


if __name__ == "__main__":
    build()

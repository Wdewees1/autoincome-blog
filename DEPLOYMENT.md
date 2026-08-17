# 🚀 AutoIncome Blog — Deployment Guide

## What You Have

A fully automated AI blog that:
- Generates SEO-optimized articles daily (automated)
- Builds a professional, responsive website (dark theme, mobile-friendly)
- Includes RSS feed, sitemap, robots.txt for SEO
- Has affiliate CTA boxes baked into every article
- Runs 100% on free tools

## Project Structure

```
autoincome-blog/
├── build_site.py              # Static site generator (builds HTML from posts)
├── config.json                # Site configuration (name, URL, affiliate ID)
├── posts/                     # Markdown articles (5 initial + daily auto-generated)
├── scripts/
│   └── generate_article.py    # Daily article generator
├── static/                    # Static assets
├── output/                    # Generated HTML site (deploy this folder)
└── DEPLOYMENT.md              # This file
```

---

## Step 1: Deploy to GitHub Pages (FREE)

1. **Create a GitHub account** at [github.com](https://github.com) (if you don't have one)

2. **Create a new repository:**
   - Go to https://github.com/new
   - Name it `autoincome-blog`
   - Set to **Public**
   - Click "Create repository"

3. **Upload your site:**
   ```bash
   cd /opt/data/autoincome-blog
   git init
   git add .
   git commit -m "Initial blog setup"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/autoincome-blog.git
   git push -u origin main
   ```

4. **Enable GitHub Pages:**
   - Go to your repo → Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main` / folder: `/output`
   - Click Save
   - Your site will be live at: `https://YOUR_USERNAME.github.io/autoincome-blog/`

5. **Update config.json** with your real URL:
   ```json
   "site_url": "https://YOUR_USERNAME.github.io/autoincome-blog"
   ```

---

## Step 2: Alternative — Deploy to Cloudflare Pages (FREE, faster)

1. **Create a Cloudflare account** at [cloudflare.com](https://cloudflare.com)

2. **Go to Pages:**
   - Dashboard → Pages → Create a project
   - Connect your GitHub repo
   - Build command: `python3 build_site.py`
   - Build output directory: `output`
   - Click "Save and Deploy"

3. Your site will be live at: `https://autoincome-blog.pages.dev/`

---

## Step 3: Set Up Daily Auto-Posting (Cron)

The article generator runs daily to create fresh content. On this Hermes instance:

```bash
# The cron job is already configured via Hermes
# It runs daily and generates a new article + rebuilds the site
```

To set it up on your own server:
```bash
crontab -e
# Add this line (runs daily at 9 AM):
0 9 * * * cd /opt/data/autoincome-blog && python3 scripts/generate_article.py
```

---

## Step 4: Monetize with Affiliate Links

### Update Affiliate Links

1. **Edit `config.json`** and replace `YOUR_AFFILIATE_ID` with your actual affiliate ID

2. **Edit the CTA box** in `build_site.py` (search for `render_cta_box`):
   - Replace the `href="#"` with your actual affiliate link
   - Example: `https://openai.com/chatgpt/?ref=YOUR_AFFILIATE_ID`

### Best Affiliate Programs for AI Niche

| Program | Commission | Signup URL |
|---------|-----------|------------|
| **OpenAI / ChatGPT** | Varies | https://openai.com |
| **Jasper AI** | 30% recurring | https://.jasper.ai/affiliate |
| **Grammarly** | $0.20-$25 per signup | https://grammarly.com/affiliates |
| **Writesonic** | 30% recurring | https://writesonic.com/affiliate |
| **Copy.ai** | 45% recurring | https://copy.ai/affiliate |
| **Notion** | 50% recurring | https://notion.so/affiliates |
| **Semrush** | $0.01-$200 per sale | https://semrush.com/affiliate |
| **Amazon Associates** | 1-10% | https://affiliate-program.amazon.com |

### Add Google AdSense (Optional)

1. Go to [Google AdSense](https://www.google.com/adsense)
2. Add your site URL
3. Get verified (may take a few days)
4. Add the AdSense code to `build_site.py` in the `render_head()` function

---

## Step 5: Drive Traffic (SEO)

### Already Included:
- ✅ SEO-optimized meta tags (title, description, Open Graph, Twitter Cards)
- ✅ XML sitemap (`/sitemap.xml`)
- ✅ RSS feed (`/feed.xml`)
- ✅ Robots.txt (`/robots.txt`)
- ✅ Semantic HTML structure
- ✅ Mobile-responsive design
- ✅ Clean URL slugs

### Submit to Search Engines:
1. **Google Search Console:** https://search.google.com/search-console
   - Add your site URL
   - Submit your sitemap: `https://YOURSITE/sitemap.xml`

2. **Bing Webmaster Tools:** https://www.bing.com/webmasters
   - Add your site
   - Submit sitemap

### Social Media:
- Share each new article on Twitter/X, LinkedIn, Reddit
- The RSS feed can be connected to automation tools like IFTTT or Zapier
- Create a Twitter account for your blog and auto-post via RSS

---

## Step 6: Monitor and Grow

### Key Metrics to Track:
- **Google Search Console** — Search rankings, impressions, clicks
- **Google Analytics** — Visitor count, bounce rate, popular pages
- **Affiliate dashboards** — Clicks, conversions, earnings

### Growth Tips:
- The daily article generator creates fresh content automatically
- Each article targets different AI keywords for SEO
- Aim for 100+ articles over 3 months (the cron job does this for you)
- Review and edit auto-generated articles weekly for quality
- Respond to comments and engage on social media

---

## Quick Start Summary

```bash
# 1. Preview locally
python3 -m http.server -d /opt/data/autoincome-blog/output 8000
# Open http://localhost:8000

# 2. Generate a new article manually
python3 /opt/data/autoincome-blog/scripts/generate_article.py

# 3. Rebuild the site
python3 /opt/data/autoincome-blog/build_site.py

# 4. Deploy (push to GitHub)
cd /opt/data/autoincome-blog
git add . && git commit -m "New articles" && git push
```

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Hosting (GitHub Pages/Cloudflare) | $0 |
| Domain (optional, use free .github.io subdomain) | $0 or $12/year |
| Article generation | $0 (automated by Hermes) |
| SEO tools | $0 (Google Search Console is free) |
| **Total monthly cost** | **$0** |

---

## Revenue Potential

| Traffic Level | Monthly Revenue (est.) |
|---------------|----------------------|
| 1,000 visitors/mo | $10-50 (affiliate + ads) |
| 10,000 visitors/mo | $100-500 |
| 50,000 visitors/mo | $500-2,500 |
| 100,000+ visitors/mo | $2,000-10,000+ |

Revenue comes from:
- **Affiliate commissions** (30-50% recurring for AI tools)
- **Google AdSense** ($2-10 per 1,000 pageviews)
- **Sponsored content** (once you have traffic)
- **Newsletter** (monetize with premium content)

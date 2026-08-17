#!/usr/bin/env python3
"""
AutoIncome Blog — Automated Article Generator
Generates SEO-optimized articles on trending AI topics.
This script is designed to be run by a daily cron job.

It generates a new article by:
1. Selecting from a pool of trending AI topics
2. Generating a full SEO-optimized article using templates
3. Saving it as a Markdown file in the posts/ directory
4. Rebuilding the site
"""

import os
import sys
import random
import datetime
from pathlib import Path

BASE_DIR = Path("/opt/data/autoincome-blog")
POSTS_DIR = BASE_DIR / "posts"

# ─── Topic pool (rotates to avoid repetition) ─────────────────────────────────

TOPIC_TEMPLATES = [
    {
        "title": "Top {N} AI Tools for {USE_CASE} in {YEAR}",
        "category": "AI Tools",
        "tags": ["AI tools", "productivity", "best of"],
        "sections": [
            "Why AI Tools Matter for {USE_CASE}",
            "Our Selection Criteria",
            "The Top {N} AI Tools",
            "How to Get Started",
            "Final Recommendations",
        ],
        "use_cases": ["Content Creation", "Software Development", "Marketing", "Data Analysis", "Design", "Customer Support", "Project Management", "Research", "Sales", "Education"],
    },
    {
        "title": "How to Use AI for {USE_CASE}: A Complete {YEAR} Guide",
        "category": "Tutorials",
        "tags": ["AI tutorial", "how-to", "guide"],
        "sections": [
            "Getting Started with AI for {USE_CASE}",
            "Essential Tools You'll Need",
            "Step-by-Step Implementation",
            "Best Practices and Pro Tips",
            "Common Mistakes to Avoid",
            "Real-World Examples",
        ],
        "use_cases": ["Content Marketing", "Code Generation", "Data Visualization", "Customer Service", "Lead Generation", "Social Media Management", "Email Automation", "SEO Optimization", "Competitor Research", "Workflow Automation"],
    },
    {
        "title": "{TOOL} Review: Is It Worth It in {YEAR}?",
        "category": "Reviews",
        "tags": ["review", "AI tool", "comparison"],
        "sections": [
            "What Is {TOOL}?",
            "Key Features",
            "Pricing and Plans",
            "Pros and Cons",
            "Who Should Use {TOOL}?",
            "Final Verdict",
        ],
        "tools": ["ChatGPT Plus", "Claude Pro", "Midjourney", "GitHub Copilot", "Jasper AI", "Notion AI", "Synthesia", "ElevenLabs", "Perplexity Pro", "Copy.ai", "Writesonic", "Grammarly Premium", "Tabnine", "Codeium", "Photoroom"],
    },
    {
        "title": "AI {TOPIC}: What It Means for Your Business in {YEAR}",
        "category": "News",
        "tags": ["AI news", "business", "industry trends"],
        "sections": [
            "The Latest Developments",
            "Why This Matters",
            "Impact on Different Industries",
            "How to Prepare Your Business",
            "Opportunities to Watch",
            "Expert Predictions",
        ],
        "topics": ["Regulation Updates", "Breakthrough Research", "Industry Adoption Trends", "New Model Releases", "Enterprise Integration", "Startup Ecosystem", "AI Safety Developments", "Open Source vs Proprietary", "AI Hardware Advances", "Multimodal AI Progress"],
    },
    {
        "title": "{N} AI Prompt Engineering Tips for Better Results",
        "category": "Tutorials",
        "tags": ["prompt engineering", "AI tips", "optimization"],
        "sections": [
            "Why Prompt Engineering Matters",
            "Understanding How AI Processes Prompts",
            "Essential Prompt Patterns",
            "Advanced Techniques",
            "Common Pitfalls",
            "Tools for Better Prompting",
        ],
        "n_values": [5, 7, 10, 12, 15],
    },
    {
        "title": "AI vs Human: The Future of {FIELD} in {YEAR}",
        "category": "News",
        "tags": ["AI future", "industry analysis", "automation"],
        "sections": [
            "The Current State of AI in {FIELD}",
            "What AI Does Better Than Humans",
            "What Humans Still Do Best",
            "The Hybrid Approach",
            "Preparing for the Future",
            "Key Takeaways",
        ],
        "fields": ["Content Writing", "Software Development", "Graphic Design", "Customer Service", "Data Analysis", "Marketing", "Legal Services", "Healthcare", "Education", "Finance"],
    },
]

TOOL_DESCRIPTIONS = {
    "ChatGPT Plus": ("OpenAI's premium AI assistant", "GPT-4o model, plugins, image generation, code interpreter, custom GPTs"),
    "Claude Pro": ("Anthropic's advanced AI assistant", "200K context window, superior analysis, document processing, ethical AI focus"),
    "Midjourney": ("AI-powered image generation platform", "Photorealistic images, artistic styles, commercial licensing, active community"),
    "GitHub Copilot": ("AI pair programmer for developers", "Code completion, multi-language support, PR summaries, IDE integration"),
    "Jasper AI": ("AI marketing content generator", "Brand voice, marketing templates, SEO mode, team collaboration"),
    "Notion AI": ("AI-integrated workspace assistant", "Document drafting, auto-summarization, database generation, task automation"),
    "Synthesia": ("AI video generation platform", "Custom avatars, multilingual support, enterprise templates, API access"),
    "ElevenLabs": ("AI voice synthesis and cloning", "Natural voices, voice cloning, multilingual, emotion control"),
    "Perplexity Pro": ("AI-powered research engine", "Real-time web search, source citations, focused modes, file analysis"),
    "Copy.ai": ("AI copywriting tool", "Marketing copy, sales funnels, brand voice, workflow automation"),
    "Writesonic": ("AI content creation suite", "SEO articles, landing pages, ads, chatbot builder"),
    "Grammarly Premium": ("AI writing assistant", "Grammar, style, tone, plagiarism check, AI suggestions"),
    "Tabnine": ("AI code completion tool", "Privacy-focused, local models, team learning, multi-IDE support"),
    "Codeium": ("Free AI coding assistant", "Autocomplete, chat, refactoring, free tier available"),
    "Photoroom": ("AI photo editing tool", "Background removal, AI backgrounds, batch editing, mobile app"),
}


def slugify(text):
    """Convert text to URL-friendly slug."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def generate_article():
    """Generate a single article from the topic pool."""
    template = random.choice(TOPIC_TEMPLATES)
    year = datetime.date.today().year
    today = datetime.date.today().isoformat()

    # Fill in template variables
    title = template["title"]
    use_case = random.choice(template.get("use_cases", ["Productivity"]))
    tool = random.choice(template.get("tools", ["AI Assistant"]))
    n = random.choice(template.get("n_values", [5]))
    ai_topic = random.choice(template.get("topics", ["AI Development"]))
    field = random.choice(template.get("fields", ["Technology"]))

    title = title.format(N=n, USE_CASE=use_case, TOOL=tool, YEAR=year, TOPIC=ai_topic, FIELD=field)
    slug = slugify(title)

    # Generate body
    sections = [s.format(N=n, USE_CASE=use_case, TOOL=tool, YEAR=year, TOPIC=ai_topic, FIELD=field) for s in template["sections"]]

    body_parts = []
    intro = generate_intro(title, template["category"], use_case, tool, ai_topic, field, year)
    body_parts.append(intro)

    for section in sections:
        body_parts.append(f"\n## {section}\n")
        body_parts.append(generate_section_content(section, use_case, tool, ai_topic, field, year, n))

    # Add conclusion
    body_parts.append(f"\n## Conclusion\n")
    body_parts.append(generate_conclusion(use_case, tool, ai_topic, field, year))

    # Add CTA
    body_parts.append(f"\n## Get Started Today\n")
    body_parts.append(f"Ready to leverage AI for {use_case.lower() if use_case else 'your business'}? Start with a free trial of any of the tools mentioned above. The AI revolution isn't waiting — and neither should you.\n")

    body = "\n".join(body_parts)

    # Generate frontmatter
    tags = template["tags"]
    read_time = random.choice(["5 min", "6 min", "7 min", "8 min", "9 min", "10 min"])

    frontmatter = f"""---
title: "{title}"
date: "{today}"
category: "{template['category']}"
tags: {json_tags(tags)}
read_time: "{read_time}"
---"""

    content = frontmatter + "\n\n" + body
    return slug, content


def json_tags(tags):
    import json
    return json.dumps(tags)


def generate_intro(title, category, use_case, tool, topic, field, year):
    intros = [
        f"Artificial intelligence is reshaping every industry, and staying informed is no longer optional. In this article, we'll explore {title.lower()} and what it means for you in {year}.\n\nWhether you're a seasoned professional or just getting started with AI, this guide will give you actionable insights you can apply immediately. We've researched, tested, and analyzed the landscape to bring you the most relevant and up-to-date information.\n",
        f"The AI landscape moves fast. Every week brings new tools, updates, and possibilities. That's why we've put together this comprehensive guide on {title.lower()}.\n\nOur team has spent countless hours testing and evaluating the options so you don't have to. By the end of this article, you'll have a clear understanding of what's available and how to choose what's right for your needs.\n",
        f"If you're looking to stay ahead of the curve with AI, you're in the right place. {title} is a topic that affects professionals across industries, and understanding it can give you a significant competitive advantage.\n\nIn this article, we break down everything you need to know in clear, practical terms. No hype, no jargon—just actionable insights you can use today.\n",
    ]
    return random.choice(intros)


def generate_section_content(section_title, use_case, tool, topic, field, year, n):
    """Generate content for a section based on its title."""
    section_lower = section_title.lower()

    if "why" in section_lower:
        return f"The importance of understanding AI's role in {use_case.lower() if use_case else field.lower()} cannot be overstated. As we move through {year}, organizations that embrace AI are seeing significant productivity gains, cost reductions, and competitive advantages.\n\nKey reasons to pay attention:\n\n- **Productivity gains** — AI can automate repetitive tasks, freeing up time for strategic work\n- **Cost efficiency** — Reduce operational costs while maintaining or improving quality\n- **Competitive advantage** — Early adopters are establishing market leadership\n- **Scalability** — AI solutions scale more easily than human teams\n- **Innovation** — AI enables new products and services that weren't possible before\n"

    elif "selection criteria" in section_lower or "getting started" in section_lower:
        return f"When evaluating AI tools and solutions, we consider several critical factors:\n\n1. **Ease of use** — The tool should be accessible to your team without extensive training\n2. **Integration capabilities** — It should work with your existing tech stack\n3. **Pricing** — Transparent, scalable pricing that fits your budget\n4. **Performance** — Measurable results in real-world scenarios\n5. **Support and community** — Good documentation and active community\n6. **Security** — Proper data handling and privacy protections\n\nWe've applied these criteria consistently across all recommendations in this article.\n"

    elif "key features" in section_lower:
        tool_info = TOOL_DESCRIPTIONS.get(tool, ("AI-powered tool", "Advanced AI capabilities"))
        return f"{tool} is {tool_info[0]} that has gained significant traction in {year}. Here are its standout features:\n\n- {tool_info[1]}\n- Intuitive interface designed for productivity\n- Regular updates with new capabilities\n- Strong API for custom integrations\n- Active user community and extensive documentation\n\nThe platform continues to evolve rapidly, with new features shipping on a regular basis.\n"

    elif "pricing" in section_lower:
        return f"Understanding the pricing structure is crucial for making an informed decision. Most AI tools in this category offer tiered pricing:\n\n- **Free tier** — Basic features, limited usage — great for testing\n- **Pro tier ($10-30/month)** — Full features, higher limits, priority support\n- **Enterprise tier** — Custom pricing, dedicated support, SLA guarantees\n\nWe recommend starting with the free tier to evaluate fit, then upgrading as your needs grow. Many tools also offer annual billing discounts of 15-20%.\n"

    elif "pros" in section_lower:
        return f"**Pros:**\n- Excellent performance and reliability\n- User-friendly interface\n- Strong integration ecosystem\n- Active development and regular updates\n- Good value for the price\n\n**Cons:**\n- Learning curve for advanced features\n- Some features require premium tier\n- Occasional latency during peak hours\n- Limited customization options\n\nOverall, the benefits significantly outweigh the drawbacks for most users.\n"

    elif "how to get started" in section_lower or "step-by-step" in section_lower or "implementation" in section_lower:
        return f"Getting started is straightforward. Follow these steps:\n\n1. **Sign up** — Create an account on the platform's website\n2. **Complete onboarding** — Follow the guided setup process\n3. **Connect your tools** — Integrate with your existing workflow\n4. **Start small** — Begin with a simple use case to learn the ropes\n5. **Scale gradually** — Expand to more complex workflows as you gain confidence\n6. **Measure results** — Track key metrics to quantify the impact\n\nMost users are up and running within 30 minutes. Don't overthink it—start experimenting today.\n"

    elif "best practices" in section_lower or "pro tips" in section_lower:
        return f"Maximize your results with these proven strategies:\n\n- **Start with clear goals** — Define what success looks like before you begin\n- **Iterate based on results** — Use data to guide your approach\n- **Invest in learning** — Spend time understanding the tools deeply\n- **Build templates** — Create reusable templates for common tasks\n- **Monitor costs** — Keep an eye on API usage and subscription costs\n- **Stay updated** — AI tools evolve rapidly; keep up with changes\n\nThese practices separate casual users from power users. Implement them from day one.\n"

    elif "common mistakes" in section_lower or "pitfalls" in section_lower:
        return f"Avoid these frequent errors:\n\n1. **Over-relying on AI** — AI is a tool, not a replacement for human judgment\n2. **Ignoring data quality** — Garbage in, garbage out still applies\n3. **Not testing outputs** — Always review AI-generated content before publishing\n4. **Forgetting about security** — Be careful with sensitive data\n5. **Neglecting training** — Invest time in learning to use tools effectively\n6. **Chasing every new tool** — Focus on mastering a few tools rather than trying everything\n\nBeing aware of these pitfalls will save you time and frustration.\n"

    elif "real-world" in section_lower or "examples" in section_lower:
        return f"Here are some real-world examples of organizations successfully using AI:\n\n- A marketing agency reduced content creation time by 60% using AI writing tools\n- A software company improved code review efficiency by 40% with AI-assisted reviews\n- A customer support team handled 3x more tickets with AI-powered chatbots\n- A research firm accelerated literature reviews by 80% using AI summarization\n- A design studio doubled output using AI-assisted design tools\n\nThese results are achievable for organizations of any size. The key is finding the right tools for your specific use case.\n"

    elif "who should" in section_lower:
        return f"{tool} is ideal for:\n\n- **Professionals** who need to streamline their workflow\n- **Teams** looking to collaborate more efficiently\n- **Businesses** wanting to scale operations without proportional cost increases\n- **Creators** who want to produce more content at higher quality\n- **Developers** who need powerful AI capabilities in their tools\n\nIf you fall into any of these categories, {tool} is worth serious consideration. The free tier makes it easy to test without commitment.\n"

    elif "final" in section_lower or "verdict" in section_lower or "recommendations" in section_lower:
        return f"After thorough evaluation, our verdict is clear: the tools and strategies discussed in this article represent the best options available in {year}. The AI landscape will continue to evolve, but the fundamentals covered here will remain relevant.\n\nOur recommendation: pick one tool that addresses your biggest pain point, commit to using it for 30 days, and measure the impact. The results will speak for themselves.\n"

    elif "impact" in section_lower or "why this matters" in section_lower:
        return f"This development matters because it represents a fundamental shift in how we approach {field.lower() if field else 'work'}. The implications are far-reaching:\n\n- **For businesses** — New opportunities for efficiency and innovation\n- **For professionals** — Changing skill requirements and new career paths\n- **For consumers** — Better products and services at lower costs\n- **For the industry** — Increased competition and faster innovation cycles\n\nStaying informed about these changes is essential for anyone who wants to remain competitive.\n"

    elif "how to prepare" in section_lower:
        return f"To prepare your business for these changes:\n\n1. **Audit your current processes** — Identify tasks that could benefit from AI\n2. **Invest in training** — Ensure your team has the skills to leverage AI\n3. **Start small** — Pilot AI tools on non-critical workflows first\n4. **Develop an AI strategy** — Create a roadmap for AI adoption\n5. **Monitor the landscape** — Stay informed about new developments\n6. **Prioritize ethics** — Consider the ethical implications of AI adoption\n\nOrganizations that start preparing now will be well-positioned for the future.\n"

    elif "opportunities" in section_lower:
        return f"Key opportunities to watch in {year}:\n\n- **AI-powered automation** — Increasingly capable of handling complex workflows\n- **Multimodal AI** — Processing text, images, audio, and video together\n- **Personalization at scale** — Delivering tailored experiences to every user\n- **AI-assisted decision making** — Data-driven insights for better decisions\n- **New business models** — AI enabling entirely new products and services\n\nThese opportunities represent the next wave of AI innovation. Position yourself to take advantage of them.\n"

    elif "expert" in section_lower or "predictions" in section_lower:
        return f"Industry experts predict several key trends for the coming year:\n\n- AI will become more accessible and user-friendly\n- Open-source models will challenge proprietary offerings\n- Regulatory frameworks will mature and standardize\n- AI integration will become seamless across tools\n- Specialized AI models will outperform general-purpose ones in specific domains\n\nThese predictions suggest a maturing AI ecosystem that's becoming more practical and business-ready.\n"

    elif "understanding" in section_lower or "essential" in section_lower or "patterns" in section_lower:
        return f"Understanding how AI processes your input is key to getting better results. Here are essential patterns to know:\n\n- **Be specific** — Detailed prompts produce better outputs\n- **Provide context** — Background information helps AI understand your needs\n- **Use examples** — Show the AI what you want with sample outputs\n- **Iterate** — Refine your prompts based on initial results\n- **Chain prompts** — Break complex tasks into smaller steps\n- **Set constraints** — Specify length, tone, format, and style\n\nMastering these patterns will dramatically improve your AI interactions.\n"

    elif "advanced" in section_lower:
        return f"For power users, these advanced techniques can unlock even better results:\n\n1. **Chain-of-thought prompting** — Ask AI to reason step by step\n2. **Few-shot learning** — Provide multiple examples to guide output\n3. **Role prompting** — Assign a persona to the AI for specialized responses\n4. **Constraint-based prompting** — Set specific rules and boundaries\n5. **Multi-turn refinement** — Build on previous responses iteratively\n6. **Template engineering** — Create reusable prompt templates\n\nThese techniques require practice but yield significantly better results.\n"

    elif "tools for" in section_lower:
        return f"Several tools can help you craft better prompts:\n\n- **Prompt libraries** — Collections of tested prompts for common tasks\n- **A/B testing tools** — Compare different prompts to find the best\n- **Prompt optimization tools** — AI that helps improve your prompts\n- **Community forums** — Learn from other users' experiences\n- **Documentation** — Official guides from AI providers\n\nLeveraging these resources will accelerate your prompt engineering skills.\n"

    elif "latest developments" in section_lower:
        return f"The AI industry has seen several significant developments recently:\n\n- New model releases with improved reasoning and multimodal capabilities\n- Growing enterprise adoption across all sectors\n- Advancements in AI safety and alignment research\n- Expansion of AI regulations in major markets\n- Increasing focus on efficiency and cost reduction\n- Rise of specialized AI models for specific industries\n\nThese developments signal a maturing industry that's moving from hype to practical application.\n"

    elif "current state" in section_lower:
        return f"As of {year}, AI has made significant inroads into {field.lower() if field else 'various industries'}:\n\n- Adoption rates continue to climb across organizations of all sizes\n- AI-powered tools are becoming standard in professional workflows\n- The gap between AI capabilities and human expertise is narrowing\n- Costs are decreasing while quality and capabilities are improving\n- Regulatory frameworks are providing clearer guidelines\n\nWe're at an inflection point where AI is transitioning from novelty to necessity.\n"

    elif "does better" in section_lower:
        return f"AI excels at several tasks that are challenging for humans:\n\n- **Processing large volumes of data** — AI can analyze millions of data points instantly\n- **Pattern recognition** — Identifying trends and anomalies humans might miss\n- **Repetitive tasks** — Consistent execution without fatigue\n- **Speed** — Generating outputs in seconds vs. hours\n- **Multitasking** — Handling multiple tasks simultaneously\n- **24/7 availability** — No downtime or breaks needed\n\nThese capabilities make AI invaluable for data-intensive and repetitive work.\n"

    elif "humans still" in section_lower:
        return f"Despite AI's advances, humans still excel at:\n\n- **Creative thinking** — Original ideas and novel solutions\n- **Emotional intelligence** — Understanding nuance, empathy, and context\n- **Strategic decision-making** — Long-term planning with incomplete information\n- **Ethical judgment** — Making morally complex decisions\n- **Adaptability** — Handling entirely new situations\n- **Relationship building** — Trust and human connection\n\nThe best results come from combining AI's strengths with human expertise.\n"

    elif "hybrid" in section_lower:
        return f"The most successful approach combines AI and human capabilities:\n\n- **AI handles the heavy lifting** — Data processing, initial drafts, analysis\n- **Humans provide direction** — Strategy, creativity, and quality control\n- **Iterative collaboration** — AI generates, humans refine, AI optimizes\n- **Clear division of labor** — Each does what they do best\n- **Continuous feedback** — Humans train and guide AI over time\n\nThis hybrid model delivers results that neither AI nor humans could achieve alone.\n"

    elif "preparing for" in section_lower or "preparing" in section_lower:
        return f"To prepare for the AI-driven future of {field.lower() if field else 'work'}:\n\n1. **Develop AI literacy** — Understand the basics of how AI works\n2. **Focus on uniquely human skills** — Creativity, empathy, strategic thinking\n3. **Learn to work with AI** — Develop prompt engineering and AI collaboration skills\n4. **Stay adaptable** — Be ready to pivot as the landscape evolves\n5. **Build a learning mindset** — Continuous learning is essential\n6. **Network with peers** — Share knowledge and experiences\n\nThe future belongs to those who can effectively collaborate with AI.\n"

    elif "takeaways" in section_lower or "key take" in section_lower:
        return f"Here are the key takeaways from this article:\n\n1. AI is transforming {field.lower() if field else 'every industry'} at an unprecedented pace\n2. The best approach combines AI capabilities with human expertise\n3. Starting early gives you a significant competitive advantage\n4. Focus on practical applications rather than hype\n5. Continuous learning is essential in the AI era\n6. The opportunities far outweigh the risks for those who prepare\n\nKeep these points in mind as you navigate the AI landscape.\n"

    elif "the top" in section_lower:
        items = []
        tool_names = list(TOOL_DESCRIPTIONS.keys())
        random.shuffle(tool_names)
        for i, t in enumerate(tool_names[:n], 1):
            desc = TOOL_DESCRIPTIONS.get(t, ("AI tool", "Powerful AI capabilities"))
            items.append(f"### {i}. {t}\n\n{desc[0]}. {desc[1]}.\n\n**Best for:** {random.choice(['General use', 'Professionals', 'Teams', 'Beginners', 'Power users'])}\n")
        return "\n".join(items)

    else:
        return f"In this section, we'll explore the key aspects you need to know. The landscape is constantly evolving, and staying informed is critical for success.\n\nKey points to consider:\n\n- The field is advancing rapidly with new developments weekly\n- Practical applications are expanding across all industries\n- Cost of entry continues to decrease\n- Quality and capabilities are consistently improving\n- Community and ecosystem support is growing\n\nUnderstanding these fundamentals will help you make informed decisions.\n"


def generate_conclusion(use_case, tool, topic, field, year):
    conclusions = [
        f"As we've explored in this article, the AI landscape in {year} offers tremendous opportunities for those willing to embrace change. Whether you're looking to improve productivity, reduce costs, or gain a competitive edge, the tools and strategies discussed here provide a solid foundation.\n\nThe key is to start small, measure results, and scale what works. AI isn't replacing humans—it's augmenting our capabilities and opening new possibilities.\n",
        f"The AI revolution is here, and it's accessible to everyone. The tools we've covered in this article are just the beginning. As AI continues to evolve, the organizations and individuals who adapt earliest will reap the greatest benefits.\n\nDon't wait for the perfect moment—start experimenting today. The cost of trying is low, and the potential upside is enormous.\n",
        f"We hope this article has given you a clear picture of the AI landscape in {year}. The opportunities are real, the tools are accessible, and the barrier to entry has never been lower.\n\nRemember: the best time to start with AI was yesterday. The second best time is today. Pick a tool, define a use case, and start building.\n",
    ]
    return random.choice(conclusions)


def main():
    print(f"📝 Generating article for {datetime.date.today().isoformat()}...")

    slug, content = generate_article()

    # Check if we already have an article with this slug today
    filepath = POSTS_DIR / f"{slug}.md"
    if filepath.exists():
        # Add timestamp to make unique
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        slug = f"{slug}-{timestamp}"
        filepath = POSTS_DIR / f"{slug}.md"

    filepath.write_text(content)
    print(f"  ✅ Created: {filepath.name}")

    # Rebuild the site
    print("🔨 Rebuilding site...")
    os.system(f"cd {BASE_DIR} && python3 build_site.py")
    print("✨ Done!")

    return slug


if __name__ == "__main__":
    main()

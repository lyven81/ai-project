import json
import os
from datetime import datetime

import anthropic


class BuilderAgent:
    """
    Runs every Monday.
    1. Uses Claude to pick a product idea not yet in the catalogue.
    2. Generates a 50-prompt pack (5 categories × 10 prompts each).
    3. Saves a clean Markdown file to products/{slug}.md
    4. Saves a listing.txt with ready-to-paste Gumroad copy.
    5. Saves product to state.json with status 'pending_upload'.

    Manual upload step (you do this):
      - Convert products/{slug}.md to PDF (Notion, Google Docs, Typora)
      - Go to gumroad.com → New Product
      - Upload the PDF and paste copy from products/{slug}-listing.txt
      - Publish and copy the product URL
      - Run: python main.py --register {slug} https://your-gumroad-url
    """

    def __init__(self, config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config["claude_api_key"])
        self.products_dir = config.get("products_dir", "products")
        self.state_file = config.get("state_file", "state.json")
        os.makedirs(self.products_dir, exist_ok=True)

    def run(self):
        print("[Builder] Starting build cycle...")

        state = self._load_state()
        idea = self._research_idea(state)
        print(f"[Builder] Idea: {idea['title']}")

        prompts = self._generate_prompts(idea)
        print(f"[Builder] Generated {len(prompts)} prompts")

        md_path = self._create_markdown(idea, prompts)
        print(f"[Builder] Markdown saved: {md_path}")

        listing_path = self._save_listing_file(idea, md_path)
        print(f"[Builder] Listing copy saved: {listing_path}")

        # Add to state as pending_upload
        product = {
            "id": idea["slug"],
            "title": idea["title"],
            "slug": idea["slug"],
            "description": idea["description"],
            "price": idea["price"],
            "what_inside": idea["what_inside"],
            "gumroad_url": "",
            "status": "pending_upload",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "sales": 0,
            "weeks_live": 0,
            "promoted_count": 0,
            "last_promoted": None
        }
        state["products"].append(product)
        state["last_builder_run"] = datetime.now().isoformat()
        self._save_state(state)

        print()
        print("=" * 55)
        print("NEXT STEP — Manual Gumroad Upload")
        print("=" * 55)
        print(f"1. Convert to PDF:  products/{idea['slug']}.md")
        print(f"2. Go to gumroad.com → New Product")
        print(f"3. Upload the converted PDF")
        print(f"4. Paste listing copy from:  {listing_path}")
        print(f"5. Set price to:  ${idea['price']}")
        print(f"6. Publish the product and copy its URL")
        print(f"7. Run this command to register it:")
        print(f"   python main.py --register {idea['slug']} YOUR_GUMROAD_URL")
        print("=" * 55)

        return idea

    def register(self, slug, gumroad_url):
        """Called via --register to attach a Gumroad URL to a pending product."""
        state = self._load_state()
        matched = False
        for p in state["products"]:
            if p["slug"] == slug:
                p["gumroad_url"] = gumroad_url
                p["status"] = "live"
                matched = True
                break
        if not matched:
            print(f"[Builder] ERROR: no product found with slug '{slug}'")
            return False
        self._save_state(state)
        print(f"[Builder] Registered: {slug} → {gumroad_url}")
        return True

    # ------------------------------------------------------------------ #

    def _research_idea(self, state):
        existing = [p["title"] for p in state.get("products", [])]

        prompt = f"""You are the product researcher for Banana Lab, a store selling AI prompt packs for small business owners.

Existing products (do not duplicate):
{json.dumps(existing, indent=2) if existing else "None yet"}

Pick ONE high-demand prompt pack idea for small business owners. Good niches:
- F&B / restaurant / cafe owners
- Retail shop owners
- Freelancers and consultants
- E-commerce sellers
- Service businesses (salons, clinics, workshops, tutors)
- Social media managers
- Property agents

Return ONLY valid JSON, no markdown fences:
{{
  "title": "e.g. 50 ChatGPT Prompts for Restaurant Owners",
  "slug": "url-friendly-slug-here",
  "description": "2-3 sentence listing description that sells the pack",
  "niche": "target niche label",
  "price": 9.00,
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "what_inside": ["bullet 1", "bullet 2", "bullet 3", "bullet 4"]
}}"""

        msg = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    def _generate_prompts(self, idea):
        """Generate 50 prompts in two batches of 25 to avoid output token limits."""

        # First decide the 5 categories
        cat_msg = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content":
                f"List exactly 5 category names for a ChatGPT prompt pack targeting "
                f"{idea['niche']} owners. Return ONLY a JSON array of 5 strings, no markdown: "
                f'["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]'
            }]
        )
        raw = cat_msg.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1].lstrip("json").strip().rstrip("```")
        categories = json.loads(raw)

        all_prompts = []
        number = 1

        def _batch(cats, start_number):
            batch_cats = "\n".join(f"- {c} (10 prompts)" for c in cats)
            p = f"""Create ChatGPT prompts for: {idea['title']}
Niche: {idea['niche']} owners.

Write 10 prompts for EACH of these categories:
{batch_cats}

Rules for every prompt:
- Full, complete instruction the owner pastes directly into ChatGPT
- Specific to {idea['niche']} — not generic
- Use [PLACEHOLDERS IN CAPS] for business-specific details
- Detailed enough that ChatGPT returns immediately useful output
- Number prompts starting from {start_number}

Return ONLY a valid JSON array, no markdown fences:
[{{"number": {start_number}, "category": "...", "prompt": "..."}}, ...]"""

            msg = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                messages=[{"role": "user", "content": p}]
            )
            raw = msg.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1].lstrip("json").strip().rstrip("```")
            return json.loads(raw.strip())

        # Batch 1: categories 0-2 (30 prompts), Batch 2: categories 3-4 (20 prompts)
        all_prompts += _batch(categories[0:3], 1)
        all_prompts += _batch(categories[3:5], len(all_prompts) + 1)

        return all_prompts

    def _create_markdown(self, idea, prompts):
        """Write a clean, complete Markdown file the owner converts to PDF."""
        # Group prompts by category
        categories = {}
        for item in prompts:
            cat = item.get("category", "General")
            categories.setdefault(cat, []).append(item)

        lines = []

        # --- Title block ---
        lines += [
            f"# {idea['title']}",
            "",
            f"*by Banana Lab — AI prompt packs for real business work*",
            "",
            "---",
            "",
        ]

        # --- About this pack ---
        lines += [
            "## About This Pack",
            "",
            idea["description"],
            "",
            "This pack contains **50 ready-to-use prompts** organised into "
            f"{len(categories)} categories. Each prompt is written specifically "
            f"for {idea['niche']} owners — not generic advice.",
            "",
            "---",
            "",
        ]

        # --- What's inside ---
        lines += ["## What's Inside", ""]
        for bullet in idea["what_inside"]:
            lines.append(f"- {bullet}")
        lines += ["", "---", ""]

        # --- How to use ---
        lines += [
            "## How to Use These Prompts",
            "",
            "1. Find the prompt that matches what you need.",
            "2. Copy the full prompt text.",
            "3. Replace every `[PLACEHOLDER IN CAPS]` with your actual details.",
            "4. Paste into ChatGPT or Claude.",
            "5. Review the output and adjust to match your brand voice.",
            "",
            "> **Tip:** The more specific your placeholders, the better the output. "
            "Include your business name, location, target customer, and tone of voice.",
            "",
            "---",
            "",
        ]

        # --- Prompts by category ---
        lines.append("## Prompts")
        lines.append("")

        for cat, items in categories.items():
            lines += [f"### {cat}", ""]
            for item in items:
                lines += [
                    f"**Prompt {item['number']}**",
                    "",
                    f"> {item['prompt']}",
                    "",
                ]
            lines += ["---", ""]

        # --- Footer ---
        lines += [
            "## About Banana Lab",
            "",
            "Banana Lab publishes a new AI prompt pack every week for a different "
            "small business niche. Each pack is written to be immediately useful — "
            "no marketing degree required.",
            "",
            f"*© {datetime.now().year} Banana Lab. For personal and business use. "
            "Do not resell or redistribute.*",
        ]

        md_path = os.path.join(self.products_dir, f"{idea['slug']}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return md_path

    def _save_listing_file(self, idea, md_path):
        """Save ready-to-paste Gumroad listing copy alongside the Markdown."""
        lines = [
            "BANANA LAB — GUMROAD LISTING COPY",
            "=" * 40,
            "",
            f"TITLE:       {idea['title']}",
            f"PRICE:       ${idea['price']}",
            f"TAGS:        {', '.join(idea.get('tags', []))}",
            "",
            "DESCRIPTION (paste into Gumroad description box):",
            "-" * 40,
            idea["description"],
            "",
            "What's inside:",
        ] + [f"  • {b}" for b in idea["what_inside"]] + [
            "",
            "How to use:",
            "  1. Copy the prompt you need.",
            "  2. Replace [PLACEHOLDERS] with your business details.",
            "  3. Paste into ChatGPT or Claude and get your output.",
            "",
            "-" * 40,
            "",
            "YOUR PRODUCT FILE:",
            f"  Convert to PDF:  {md_path}",
            "  Recommended tool: Notion (paste MD → Export as PDF)",
            "                    or: Word, Google Docs, Typora, Pandoc",
            "",
            "AFTER UPLOAD — register with:",
            f"  python main.py --register {idea['slug']} YOUR_GUMROAD_URL",
        ]

        path = os.path.join(self.products_dir, f"{idea['slug']}-listing.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    def _load_state(self):
        if not os.path.exists(self.state_file):
            return {"products": [], "twitter_log": [], "last_builder_run": None,
                    "last_reporter_run": None, "week_number": 0}
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self, data):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

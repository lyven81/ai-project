import os
import json
from datetime import datetime

from utils.state_manager import StateManager


PRODUCT_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Banana Lab</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <header>
    <a href="../index.html" class="logo">🍌 Banana Lab</a>
    <nav><a href="../index.html">All Packs</a><a href="../about.html">About</a></nav>
  </header>

  <main class="product-page">
    <div class="product-hero">
      <div class="product-badge">AI Prompt Pack</div>
      <h1>{title}</h1>
      <p class="product-desc">{description}</p>
      <div class="product-meta">
        <span class="price">${price}</span>
        <span class="prompt-count">50 ready-to-use prompts</span>
      </div>
      <a href="{gumroad_url}" class="btn-buy" target="_blank">Get It Now →</a>
    </div>

    <div class="product-inside">
      <h2>What's Inside</h2>
      <ul>
        {what_inside_items}
      </ul>
    </div>

    <div class="product-how">
      <h2>How to Use</h2>
      <ol>
        <li>Buy and download the PDF.</li>
        <li>Open it and find the prompt you need.</li>
        <li>Replace <strong>[PLACEHOLDERS]</strong> with your business details.</li>
        <li>Paste into ChatGPT or Claude and get your output.</li>
      </ol>
    </div>

    <div class="cta-block">
      <a href="{gumroad_url}" class="btn-buy" target="_blank">Get It Now — ${price}</a>
    </div>
  </main>

  <footer>
    <p>© {year} Banana Lab · AI prompt packs for real business work.</p>
  </footer>
</body>
</html>"""


class SiteAgent:
    """
    Runs every Monday after BuilderAgent.
    1. Reads the latest product from state.json.
    2. Generates a product landing page HTML.
    3. Rebuilds index.html with all products.
    """

    def __init__(self, config):
        self.config = config
        self.state = StateManager(config["state_file"])
        self.website_dir = config.get("website_dir", "website")
        self.products_dir = os.path.join(self.website_dir, "products")
        os.makedirs(self.products_dir, exist_ok=True)

    def run(self):
        products = self.state.get_products()
        if not products:
            print("[Site] No products found. Skipping.")
            return

        latest = products[-1]
        self._build_product_page(latest)
        self._rebuild_homepage(products)
        print(f"[Site] Website updated. {len(products)} product(s) live.")

    # ------------------------------------------------------------------ #

    def _build_product_page(self, product):
        what_inside_items = "\n        ".join(
            f"<li>{item}</li>" for item in product.get("what_inside", [])
        )
        html = PRODUCT_PAGE_TEMPLATE.format(
            title=product["title"],
            description=product["description"],
            price=product["price"],
            gumroad_url=product["gumroad_url"],
            what_inside_items=what_inside_items,
            year=datetime.now().year
        )
        path = os.path.join(self.products_dir, f"{product['slug']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[Site] Product page saved: {path}")

    def _rebuild_homepage(self, products):
        cards = ""
        for p in reversed(products):
            cards += f"""
      <div class="product-card">
        <div class="card-badge">AI Prompt Pack</div>
        <h3><a href="products/{p['slug']}.html">{p['title']}</a></h3>
        <p>{p['description']}</p>
        <div class="card-footer">
          <span class="price">${p['price']}</span>
          <a href="{p['gumroad_url']}" class="btn-buy-small" target="_blank">Get It Now</a>
        </div>
      </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Banana Lab — AI Prompt Packs for Business Owners</title>
  <meta name="description" content="Ready-to-use ChatGPT prompt packs for small business owners. Save time, write better, grow faster.">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <a href="index.html" class="logo">🍌 Banana Lab</a>
    <nav><a href="index.html">All Packs</a><a href="about.html">About</a></nav>
  </header>

  <section class="hero">
    <h1>AI Prompt Packs<br>for Business Owners</h1>
    <p>Stop staring at a blank screen. Get 40 ready-to-use ChatGPT prompts for your exact business type — copy, fill in your details, and go.</p>
  </section>

  <section class="products-grid">
    <h2>All Packs ({len(products)} available)</h2>
    <div class="grid">
      {cards}
    </div>
  </section>

  <footer>
    <p>© {datetime.now().year} Banana Lab · AI prompt packs for real business work.</p>
  </footer>
</body>
</html>"""

        path = os.path.join(self.website_dir, "index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[Site] Homepage rebuilt: {path}")

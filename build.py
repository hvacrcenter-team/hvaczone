#!/usr/bin/env python3
"""
HVAC Zone — content build script
Reads articles/index.json (source of truth) and regenerates:
  - the article grid in hub.html (between <!--ARTICLE-GRID--> markers)
  - the latest-3 preview in index.html (between <!--HUB-PREVIEW--> markers)

Run after adding/editing an article:
    python3 build.py
Then redeploy the site.
"""
import json
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "articles", "index.json")

# Category -> illustration SVG (viewBox 0 0 400 225). Shared, scalable visuals.
CAT_SVG = {
    "smart": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Smart thermostat"><rect width="400" height="225" fill="var(--color-surface-offset)"/><rect x="140" y="45" width="120" height="150" rx="18" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="3"/><circle cx="200" cy="110" r="42" fill="none" stroke="var(--color-primary)" stroke-width="4"/><text x="200" y="118" text-anchor="middle" font-family="Space Grotesk" font-size="20" fill="var(--color-primary)" font-weight="700">72&#176;</text><circle cx="200" cy="158" r="5" fill="var(--color-accent)"/></svg>''',
    "iaq": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Air quality monitor"><rect width="400" height="225" fill="var(--color-surface-offset)"/><rect x="130" y="50" width="140" height="125" rx="14" fill="var(--color-surface)" stroke="var(--color-cool)" stroke-width="2.5"/><text x="200" y="110" text-anchor="middle" font-family="Space Grotesk" font-size="30" fill="var(--color-cool)" font-weight="700">AQI</text><text x="200" y="145" text-anchor="middle" font-family="Space Grotesk" font-size="26" fill="var(--color-text)">18</text><path d="M150 175 h100" stroke="var(--color-success)" stroke-width="4" stroke-linecap="round"/></svg>''',
    "tools": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="HVAC tools"><rect width="400" height="225" fill="var(--color-surface-offset)"/><rect x="80" y="120" width="240" height="14" rx="4" fill="var(--color-accent)" transform="rotate(-20 200 127)"/><rect x="150" y="60" width="40" height="60" rx="6" fill="var(--color-primary)"/><rect x="210" y="60" width="40" height="60" rx="6" fill="var(--color-primary)" opacity="0.6"/></svg>''',
    "building": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="House thermal envelope"><rect width="400" height="225" fill="var(--color-surface-offset)"/><path d="M90 180 L90 110 L200 60 L310 110 L310 180 Z" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="2.5"/><path d="M90 180 L310 180" stroke="var(--color-accent)" stroke-width="4"/><path d="M120 130 h30 v30 h-30z M250 130 h30 v30 h-30z" fill="var(--color-primary-highlight)" stroke="var(--color-primary)" stroke-width="1.5"/></svg>''',
    "equipment": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="HVAC equipment"><rect width="400" height="225" fill="var(--color-surface-offset)"/><rect x="140" y="60" width="120" height="110" rx="10" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="2.5"/><g stroke="var(--color-primary)" stroke-width="2" opacity="0.5"><path d="M150 75 v80 M165 75 v80 M180 75 v80 M195 75 v80 M210 75 v80 M225 75 v80 M240 75 v80 M255 75 v80"/></g><circle cx="200" cy="135" r="14" fill="none" stroke="var(--color-accent)" stroke-width="3"/></svg>''',
    "trends": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Product trends"><rect width="400" height="225" fill="var(--color-surface-offset)"/><path d="M60 170 L120 140 L180 150 L240 100 L300 80 L340 50" fill="none" stroke="var(--color-accent)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="340" cy="50" r="6" fill="var(--color-accent)"/><path d="M50 190 h300" stroke="var(--color-border-strong)" stroke-width="1.5"/></svg>''',
    "outlook": '''<svg viewBox="0 0 400 225" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Weekly weather outlook"><rect width="400" height="225" fill="var(--color-surface-offset)"/><circle cx="155" cy="105" r="34" fill="var(--color-accent)" opacity="0.9"/><path d="M150 180 a42 42 0 0 1 84 0" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="2.5"/><path d="M150 180 h84" stroke="var(--color-primary)" stroke-width="2.5"/><g stroke="var(--color-cool)" stroke-width="2.5" stroke-linecap="round"><path d="M175 195 v8 M195 195 v8 M215 195 v8"/></g></svg>''',
}
CAT_SVG_WIDE = {
    "smart": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Smart thermostat"><rect width="600" height="340" fill="var(--color-surface-offset)"/><circle cx="300" cy="170" r="150" fill="var(--color-primary-highlight)"/><rect x="240" y="90" width="120" height="160" rx="20" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="3"/><circle cx="300" cy="170" r="50" fill="none" stroke="var(--color-primary)" stroke-width="4"/><text x="300" y="178" text-anchor="middle" font-family="Space Grotesk" font-size="22" fill="var(--color-primary)" font-weight="700">72&#176;</text><circle cx="300" cy="222" r="6" fill="var(--color-accent)"/></svg>''',
    "iaq": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Indoor air quality"><rect width="600" height="340" fill="var(--color-surface-offset)"/><circle cx="300" cy="170" r="130" fill="var(--color-cool-highlight)"/><path d="M300 90 a55 55 0 0 1 0 160 a45 45 0 0 1 0 -160z" fill="var(--color-cool)" opacity="0.85"/><text x="300" y="180" text-anchor="middle" font-family="Space Grotesk" font-size="28" fill="#fff" font-weight="700">AQI 18</text></svg>''',
    "building": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Building envelope"><rect width="600" height="340" fill="var(--color-surface-offset)"/><path d="M150 280 L150 150 L300 70 L450 150 L450 280 Z" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="2.5"/><path d="M150 280 L450 280" stroke="var(--color-accent)" stroke-width="5"/><path d="M210 180 h60 v70 h-60z M330 180 h60 v70 h-60z" fill="var(--color-primary-highlight)" stroke="var(--color-primary)" stroke-width="1.5"/></svg>''',
    "tools": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Tools"><rect width="600" height="340" fill="var(--color-surface-offset)"/><rect x="120" y="180" width="360" height="16" rx="5" fill="var(--color-accent)" transform="rotate(-18 300 188)"/><rect x="220" y="90" width="60" height="90" rx="8" fill="var(--color-primary)"/><rect x="320" y="90" width="60" height="90" rx="8" fill="var(--color-primary)" opacity="0.6"/></svg>''',
    "equipment": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Equipment"><rect width="600" height="340" fill="var(--color-surface-offset)"/><rect x="220" y="80" width="160" height="180" rx="12" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="2.5"/><g stroke="var(--color-primary)" stroke-width="2.5" opacity="0.45"><path d="M235 100 v140 M255 100 v140 M275 100 v140 M295 100 v140 M315 100 v140 M335 100 v140 M355 100 v140"/></g><circle cx="300" cy="170" r="20" fill="none" stroke="var(--color-accent)" stroke-width="4"/></svg>''',
    "trends": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Trends"><rect width="600" height="340" fill="var(--color-surface-offset)"/><path d="M80 260 L160 220 L240 230 L320 170 L420 130 L520 80" fill="none" stroke="var(--color-accent)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="520" cy="80" r="8" fill="var(--color-accent)"/><path d="M70 280 h470" stroke="var(--color-border-strong)" stroke-width="2"/></svg>''',
    "outlook": '''<svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Weekly weather outlook"><rect width="600" height="340" fill="var(--color-surface-offset)"/><circle cx="240" cy="150" r="52" fill="var(--color-accent)" opacity="0.9"/><path d="M230 250 a64 64 0 0 1 128 0" fill="var(--color-surface)" stroke="var(--color-primary)" stroke-width="3"/><path d="M230 250 h128" stroke="var(--color-primary)" stroke-width="3"/><g stroke="var(--color-cool)" stroke-width="3" stroke-linecap="round"><path d="M255 268 v12 M290 268 v12 M325 268 v12"/></g></svg>''',
}


def load_articles():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        arts = json.load(f)
    # sort newest first by date
    arts.sort(key=lambda a: a.get("date", ""), reverse=True)
    return arts


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def card_html(a, feature=False):
    cat = a.get("category", "equipment")
    svg = CAT_SVG_WIDE.get(cat, CAT_SVG_WIDE["equipment"]) if feature else CAT_SVG.get(cat, CAT_SVG["equipment"])
    cls = "card card--feature" if feature else "card"
    title = esc(a["title"])
    excerpt_html = f'<p class="card-excerpt">{esc(a["excerpt"])}</p>' if a.get("excerpt") else ""
    meta = f'<div class="card-meta"><span class="author">{esc(a.get("author","HVAC Zone Team"))}</span><span>&#8226;</span><span>{esc(a.get("readTime",""))}</span><span>&#8226;</span><span>{esc(a.get("dateLabel",""))}</span></div>'
    return f'''          <a href="{a["file"]}" class="{cls}" data-cat="{cat}">
            <div class="card-media">
              {svg}
              <span class="card-cat">{esc(a.get("categoryLabel", cat))}</span>
            </div>
            <div class="card-body">
              <h3 class="card-title">{title}</h3>
              {excerpt_html}
              {meta}
            </div>
          </a>'''


def replace_between(text, start_marker, end_marker, new_inner):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"Markers not found: {start_marker} / {end_marker}")
    return pattern.sub(start_marker + "\n" + new_inner + "\n          " + end_marker, text)


def build_hub_grid(arts):
    # newest = feature, rest normal
    cards = []
    if arts:
        cards.append(card_html(arts[0], feature=True))
        for a in arts[1:]:
            cards.append(card_html(a, feature=False))
    return "\n".join(cards)


def build_home_preview(arts):
    # 3 newest: first feature, next two normal
    cards = []
    top = arts[:3]
    if top:
        cards.append(card_html(top[0], feature=True))
        for a in top[1:]:
            cards.append(card_html(a, feature=False))
    return "\n".join(cards)


def main():
    arts = load_articles()
    print(f"Loaded {len(arts)} articles from manifest.")

    hub_path = os.path.join(ROOT, "hub.html")
    with open(hub_path, "r", encoding="utf-8") as f:
        hub = f.read()
    hub = replace_between(hub, "<!--ARTICLE-GRID-START-->", "<!--ARTICLE-GRID-END-->", build_hub_grid(arts))
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(hub)
    print("Regenerated hub.html article grid.")

    home_path = os.path.join(ROOT, "index.html")
    with open(home_path, "r", encoding="utf-8") as f:
        home = f.read()
    home = replace_between(home, "<!--HUB-PREVIEW-START-->", "<!--HUB-PREVIEW-END-->", build_home_preview(arts))
    with open(home_path, "w", encoding="utf-8") as f:
        f.write(home)
    print("Regenerated index.html hub preview.")

    print("Build complete. Redeploy the site to publish changes.")


if __name__ == "__main__":
    main()

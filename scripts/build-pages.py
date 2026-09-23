"""Builds every HTML page from shared partials, the portfolio data and the Vermont map.

Run from the site folder:  python3 scripts/build-pages.py

- Page bodies live in pages/*.html. Markers inside them are expanded here:
    <!--tile:slug:classes:note-->   a video tile (add "note" to print the blurb)
    <!--waves:seed-->               a pop-art wave band (scripts/waves.py)
    <!--vmap:full-->                the interactive Vermont map
- One case-study page per project is generated into work/<slug>.html from PROJECTS.
- File names match the old Wix slugs (/about, /our-work, /services, /contact-us).
- Paths are root-absolute (/assets/...) so pages in work/ resolve the same way.
"""
import json
import re
from html import escape
from pathlib import Path

from waves import waves

ROOT = Path(__file__).resolve().parent.parent
V = "8"  # bump to bust caches after CSS/JS edits
CONTACT = "/contact-us.html"
IG = "https://www.instagram.com/inspirecampaigns/"
LI_JAVI = "https://www.linkedin.com/in/javier-matos-rodriguez-aa202a249/"

# ---------------------------------------------------------------- portfolio
# Order follows the old /our-work page. Goals and results are the client's own statements from that page;
# nothing here should claim a number or outcome they did not.
PROJECTS = {
    "jhc-better-vermont": dict(
        title="A better Vermont", client="The Johnson Health Center", cat="nonprofit", orient="tall", dur="1:17",
        format="Motion graphics", places=["burlington", "johnson"],
        blurb="An animated explainer on harm reduction with one clear call to action. Monthly social views and donations went up after it ran.",
        goal="Help The Johnson Health Center spread its harm-reduction message and grow support for the work.",
        made="A 77-second motion graphic built on the numbers, ending on one clear ask: share the post, give to the center.",
        result="Monthly social media views and donations increased after it ran.",
        alt="Motion graphic of five figures, one in red, above the word Vermont."),
    "popup-food": dict(
        title="Food showcase", client="Local food pop-up", cat="food", orient="tall", dur="0:21",
        format="Short-form video", places=[],
        blurb="The cook, shot up close, to build hype before a pop-up.",
        goal="Build anticipation for a local food pop-up before the doors opened.",
        made="A 21-second close-up of the cook: into the fryer, onto the waffle, finished with whipped cream.",
        result="",
        alt="Whipped cream piped onto a fried chicken and waffle."),
    "festival-of-fools": dict(
        title="Festival of Fools", client="Burlington community", cat="community", orient="wide", dur="0:40",
        format="Event film", places=["burlington"],
        blurb="Burlington's street festival, shot for the love of it. No brief, just the crowd.",
        goal="No client and no goal. We went because we love this city and wanted to capture how many people showed up.",
        made="A 40-second widescreen cut of the street performers and the crowd on Burlington's streets.",
        result="",
        alt="A street performer in front of a packed crowd on a Burlington street."),
    "mechayeh-product": dict(
        title="Product showcase", client="Mechayeh", cat="local", orient="tall", dur="0:18",
        format="Animation", places=[],
        blurb="An animated product piece for a local cultivation brand, showing what they make and why.",
        goal="Show what Mechayeh makes, a Vermont craft brand working with cultivators across the state, and what sets it apart.",
        made="An 18-second animated piece: bold type, product renders and a comment-thread punchline.",
        result="",
        alt="Animated product frame reading Pure Gasss on a dark background."),
    "market-vendor": dict(
        title="Farmers' market vendor", client="Local food vendor", cat="food", orient="tall", dur="0:17",
        format="Short-form video", places=[],
        blurb="A vendor's story, made to get them into more farmers' markets. It worked.",
        goal="Help a local food vendor land spots at more farmers' markets.",
        made="A 17-second vendor story shot at the griddle, with bold captions in the vendor's own words.",
        result="The vendor got into more farmers' markets.",
        alt="A burger on a griddle at a market stall, with a yellow caption across the top."),
    "propready-estimate": dict(
        title="From estimate to end", client="Prop Ready", cat="local", orient="tall", dur="0:22",
        format="Short-form series", places=["winooski"],
        blurb="A series of short videos explaining how Prop Ready works, built to grow trust in the local market.",
        goal="Grow awareness of and trust in Prop Ready across the local community, organically.",
        made="A series of short-form videos that walk through a project, from the first site visit and estimate to the finished job.",
        result="",
        alt="Prop Ready team member speaking to camera in the company workshop."),
    "propready-walkthrough": dict(
        title="Prop Ready walk-through", client="Prop Ready", cat="local", orient="tall", dur="0:20",
        format="Brand film", places=["winooski"],
        blurb="A tour of the office and the values behind the work, for clients deciding who to hire.",
        goal="Build trust and recognition with people choosing a contractor.",
        made="A 20-second walk through the Prop Ready office and shop, and the values behind the work.",
        result="",
        alt="A Prop Ready carpenter cutting a board on a miter saw."),
    "popup-drinks": dict(
        title="Brand showcase", client="Local food pop-up", cat="food", orient="tall", dur="0:15",
        format="Short-form video", places=[],
        blurb="How the drinks get made, to set the vibe ahead of the next pop-up.",
        goal="Establish the pop-up's look and feel, and build hype for the next one.",
        made="A 15-second look at how the drinks get made, from the espresso shot to the whipped cream.",
        result="",
        alt="Whipped cream piped onto an iced coffee."),
}
ORDER = list(PROJECTS)
CATS = {"nonprofit": ("Nonprofit", "red"), "food": ("Food and drink", "yellow"), "local": ("Local business", "blue"), "community": ("Community", "red")}

# ---------------------------------------------------------------- Vermont map
VT = json.loads((ROOT / "data" / "vermont.json").read_text())
PLACES = {p["id"]: p for p in VT["places"]}
SERVED = {"Chittenden", "Lamoille"}


def vmap(kind="full"):
    """Census county outlines with Inspire's places pinned. kind="full" is the interactive map;
    kind="mini:<place ids>" is a static crop used on case-study pages."""
    ids = list(PLACES) if kind == "full" else kind.split(":", 1)[1].split(",")
    pts = [PLACES[i] for i in ids]
    if kind == "full":
        vb = VT["viewBox"]
    else:  # frame the pins, keeping the state's portrait feel
        cx = sum(p["x"] for p in pts) / len(pts); cy = sum(p["y"] for p in pts) / len(pts)
        w = max(340, max(p["x"] for p in pts) - min(p["x"] for p in pts) + 260); h = w * 0.8
        vb = f"{cx - w / 2:.0f} {cy - h / 2:.0f} {w:.0f} {h:.0f}"
    fills = "".join(
        f'<path d="{c["d"]}" class="vmap__c{" is-served" if c["name"] in SERVED else ""}" data-county="{c["name"]}"/>'
        for c in VT["counties"])
    lines = "".join(f'<path d="{c["d"]}"/>' for c in VT["counties"])
    # pins are drawn in screen pixels and scaled by k = viewBox units per pixel (main.js keeps k current)
    k = 2.3 if kind == "full" else round(float(vb.split()[2]) / 460, 2)
    pins = "".join(
        f'<g class="pin" data-pin="{p["id"]}" transform="translate({p["x"]} {p["y"]})"><g class="pin__in" transform="scale({k})">'
        f'<circle class="pin__pulse" r="9"/><circle class="pin__dot" r="6"/>'
        f'<text class="pin__label" x="11" y="5">{p["town"]}</text></g></g>' for p in pts)
    towns = ", ".join(p["town"] for p in pts)
    data = ' data-vmap' if kind == "full" else ""
    return (f'<svg class="vmap vmap--{"full" if kind == "full" else "mini"}" viewBox="{vb}" role="img"{data} '
            f'aria-label="Map of Vermont\'s fourteen counties with pins at {towns}.">'
            f'<g class="vmap__fills">{fills}</g><g class="vmap__lines" aria-hidden="true">{lines}</g>'
            f'<g class="vmap__pins" aria-hidden="true">{pins}</g></svg>')


# ---------------------------------------------------------------- partials
HEAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="/assets/posters/{og}.webp">
  <meta name="theme-color" content="#0F2A3F">
  <script>
    /* theme before first paint: the visitor's saved choice, else Trippy (pop) */
    (function () {{
      var t = null; try {{ t = localStorage.getItem('ic-mode'); }} catch (e) {{}}
      if (t !== 'light' && t !== 'dark' && t !== 'pop') t = 'pop';
      document.documentElement.dataset.theme = t;
      document.documentElement.classList.add('js');
    }})();
  </script>
  <link rel="icon" href="/assets/favicon.png" type="image/png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800&family=Geist:wght@400;500;600&family=Geist+Mono:wght@500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.1/src/regular/style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.1/src/fill/style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lenis@1.3.26/dist/lenis.css">
  {preload}<link rel="stylesheet" href="/styles.css?v={v}">
  <script src="https://cdn.jsdelivr.net/npm/lenis@1.3.26/dist/lenis.min.js" defer></script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"ProfessionalService","name":"Inspire Campaigns",
   "description":"Video production, brand storytelling and paid advertising for Vermont businesses.",
   "url":"https://www.inspirecampaigns.com/","areaServed":{{"@type":"State","name":"Vermont"}},
   "founder":{{"@type":"Person","name":"Javi Matos Rodriguez"}},
   "sameAs":["{ig}","{li_javi}"]}}
  </script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <span class="sentinel" data-top-sentinel aria-hidden="true"></span>
"""

MODES = """<div class="modes" data-modes>
          <button class="modes__btn" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="modes-menu" data-modes-btn>
            <span class="modes__cur" data-modes-cur aria-hidden="true">&#9728;&#65039;</span><span class="sr-only">Change colour mode</span><i class="ph ph-caret-down" aria-hidden="true"></i>
          </button>
          <div class="modes__menu" id="modes-menu" role="menu" aria-label="Colour mode" hidden data-modes-menu>
            <button type="button" role="menuitemradio" aria-checked="false" data-mode="light"><span class="modes__emoji" aria-hidden="true">&#9728;&#65039;</span>Light</button>
            <button type="button" role="menuitemradio" aria-checked="false" data-mode="dark"><span class="modes__emoji" aria-hidden="true">&#127769;</span>Dark</button>
            <button type="button" role="menuitemradio" aria-checked="false" data-mode="pop"><span class="modes__emoji" aria-hidden="true">&#127744;</span>Trippy</button>
          </div>
        </div>"""

NAV = [("/our-work.html", "Work", "work"), ("/services.html", "Services", "services"),
       ("/vermont.html", "Vermont", "vermont"), ("/about.html", "About", "about")]


def header(active):
    links = "\n        ".join(
        f'<a href="{h}"{" aria-current=page" if k == active else ""}>{label}</a>' for h, label, k in NAV)
    sheet = "\n    ".join(f'<a href="{h}">{label}</a>' for h, label, _ in NAV)
    return f"""
  <header class="nav" data-nav>
    <div class="nav__inner wrap">
      <a href="/" class="mark" aria-label="Inspire Campaigns, home"><span class="mark__img" aria-hidden="true"></span></a>
      <nav class="nav__links" aria-label="Primary">
        {links}
      </nav>
      <div class="nav__actions">
        {MODES}
        <a class="btn btn--primary nav__cta" href="{CONTACT}">Start a project</a>
        <button class="burger" type="button" data-burger aria-expanded="false" aria-controls="sheet" aria-label="Open menu"><i class="ph ph-list" aria-hidden="true"></i></button>
      </div>
    </div>
  </header>
  <div class="sheet" id="sheet" data-sheet hidden data-lenis-prevent>
    <span class="art art--sheet" aria-hidden="true"></span>
    {sheet}
    <a class="btn btn--primary btn--lg" href="{CONTACT}">Start a project<i class="ph ph-arrow-right" aria-hidden="true"></i></a>
    <div class="sheet__meta">
      <a class="link" href="{IG}" target="_blank" rel="noopener">Instagram</a>
      <span>Video and marketing for Vermont brands</span>
    </div>
  </div>
"""


FOOTER = f"""
  <footer class="foot" data-hide-dock>
    <span class="art art--foot" aria-hidden="true"></span>
    <div class="wrap foot__inner">
      <div class="foot__col foot__brand">
        <a href="/" class="mark mark--foot" aria-label="Inspire Campaigns, home"><span class="mark__img" aria-hidden="true"></span></a>
        <p>Video, social and paid ads for Vermont brands that are done blending in.</p>
      </div>
      <div class="foot__col">
        <h2>Explore</h2>
        <a href="/our-work.html">Work</a>
        <a href="/services.html">Services</a>
        <a href="/vermont.html">Vermont</a>
        <a href="/about.html">About</a>
        <a href="{CONTACT}">Start a project</a>
      </div>
      <div class="foot__col">
        <h2>Connect</h2>
        <a href="{IG}" target="_blank" rel="noopener"><i class="ph ph-instagram-logo" aria-hidden="true"></i>Instagram</a>
        <a href="{LI_JAVI}" target="_blank" rel="noopener"><i class="ph ph-linkedin-logo" aria-hidden="true"></i>Javi on LinkedIn</a>
      </div>
      <p class="foot__credit">&copy; 2026 Inspire Campaigns. Artwork: Eadweard Muybridge, <i>The Horse in Motion</i> (1878), and Thomas Edison's patent drawings for the electric lamp (1880) and Kinetoscope (1902), all public domain. Map: U.S. Census Bureau county boundaries.</p>
    </div>
  </footer>

  <div class="dock" data-dock>
    <a class="btn btn--primary dock__cta" href="{CONTACT}">Start a project<i class="ph ph-arrow-right" aria-hidden="true"></i></a>
  </div>

  <dialog class="player" data-player aria-label="Video player">
    <div class="player__frame">
      <video data-player-video controls playsinline preload="none"></video>
    </div>
    <div class="player__bar">
      <p class="player__title" data-player-title></p>
      <button class="player__close" type="button" data-player-close aria-label="Close video"><i class="ph ph-x" aria-hidden="true"></i></button>
    </div>
  </dialog>

  <script src="/main.js?v={V}" type="module"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- tiles
def dims(p):
    return (432, 768, "9 / 16") if p["orient"] == "tall" else (768, 345, "1024 / 460")  # wide = cinemascope crop


def tile(slug, cls="", note=False):
    p = PROJECTS[slug]
    w, h, ar = dims(p)
    tall = " data-tall" if p["orient"] == "tall" else ""
    note_html = f'\n      <p class="tile__note">{p["blurb"]}</p>' if note else ""
    tone = CATS[p["cat"]][1]
    return f"""<article class="tile reveal {cls}" data-tile data-cat="{p["cat"]}" data-tone="{tone}">
    <div class="tile__media" style="--ar:{ar}; view-transition-name:v-{slug}">
      <img src="/assets/posters/{slug}.webp" width="{w}" height="{h}" alt="{p["alt"]}" loading="lazy">
      <video data-src="/assets/video/{slug}-preview.mp4" muted loop playsinline preload="none" aria-hidden="true"></video>
      <a class="tile__link" href="/work/{slug}.html" tabindex="-1" aria-hidden="true"></a>
      <button class="tile__play" type="button" data-play="/assets/video/{slug}.mp4" data-title="{p["title"]}, {p["client"]}"{tall} aria-label="Play {p["title"]}, {p["dur"]}"><i class="ph-fill ph-play" aria-hidden="true"></i>{p["dur"]}</button>
    </div>
    <div class="tile__meta">
      <h3 class="h3"><a href="/work/{slug}.html">{p["title"]}</a></h3>
      <p class="tile__client">{p["client"]}</p>{note_html}
    </div>
  </article>"""


# ---------------------------------------------------------------- case-study pages
def case_page(slug):
    p = PROJECTS[slug]
    i = ORDER.index(slug)
    nxt = PROJECTS[ORDER[(i + 1) % len(ORDER)]]; nslug = ORDER[(i + 1) % len(ORDER)]
    w, h, ar = dims(p)
    tone = CATS[p["cat"]][1]
    tall = " data-tall" if p["orient"] == "tall" else ""
    where = " and ".join(PLACES[x]["town"] for x in p["places"]) if p["places"] else "Vermont"
    frames = "".join(
        f'<li class="reveal" style="--d:{k}"><img src="/assets/frames/{slug}-{k + 1}.webp" loading="lazy" alt="" '
        f'width="{480 if p["orient"] == "tall" else 720}" height="{853 if p["orient"] == "tall" else 323}"></li>' for k in range(4))
    result = (f'<div class="story-row reveal"><h2 class="story-row__k">What happened</h2>'
              f'<p class="story-row__v">{p["result"]}</p></div>') if p["result"] else ""
    mapblock = ""
    if p["places"]:
        mapblock = f"""
    <section class="case-map" aria-labelledby="where-title" data-tone="blue">
      <div class="wrap case-map__inner">
        <div class="case-map__art reveal">{vmap("mini:" + ",".join(p["places"]))}</div>
        <div class="case-map__copy">
          <h2 id="where-title" class="h2 reveal">Filmed in <em>{where}.</em></h2>
          <p class="lede reveal" style="--d:1">One of the Vermont places we've worked. See them all on the map.</p>
          <a class="btn btn--ghost reveal" style="--d:2" href="/vermont.html">Open the Vermont map<i class="ph ph-arrow-right" aria-hidden="true"></i></a>
        </div>
      </div>
    </section>"""
    body = f"""
  <main id="main" class="case case--{p["orient"]}">
    <section class="case-hero" data-tone="{tone}">
      <div class="wrap case-hero__inner">
        <div class="case-hero__copy">
          <a class="back reveal" href="/our-work.html"><i class="ph ph-arrow-left" aria-hidden="true"></i>All work</a>
          <p class="case-hero__client reveal">{p["client"]}</p>
          <h1 class="h1 reveal" style="--d:1">{p["title"]}</h1>
          <p class="lede reveal" style="--d:2">{p["blurb"]}</p>
          <dl class="facts reveal" style="--d:3">
            <div><dt>Format</dt><dd>{p["format"]}</dd></div>
            <div><dt>Length</dt><dd>{p["dur"]}</dd></div>
            <div><dt>Where</dt><dd>{where}</dd></div>
            <div><dt>Category</dt><dd>{CATS[p["cat"]][0]}</dd></div>
          </dl>
          <div class="case-hero__ctas reveal" style="--d:4" data-hide-dock>
            <button class="btn btn--primary btn--lg" type="button" data-play="/assets/video/{slug}.mp4" data-title="{p["title"]}, {p["client"]}"{tall}><i class="ph-fill ph-play" aria-hidden="true"></i>Watch with sound</button>
          </div>
        </div>
        <div class="case-hero__media" style="--ar:{ar}; view-transition-name:v-{slug}">
          <video src="/assets/video/{slug}-preview.mp4" poster="/assets/posters/{slug}.webp" muted loop playsinline autoplay preload="metadata" aria-hidden="true"></video>
        </div>
      </div>
    </section>

    <section class="filmstrip" aria-label="Stills from the video">
      <ul class="filmstrip__row filmstrip__row--{p["orient"]}">{frames}</ul>
    </section>

    <section class="story" aria-label="The project" data-tone="{tone}">
      <div class="wrap story__rows">
        <div class="story-row reveal"><h2 class="story-row__k">The goal</h2><p class="story-row__v">{p["goal"]}</p></div>
        <div class="story-row reveal"><h2 class="story-row__k">What we made</h2><p class="story-row__v">{p["made"]}</p></div>
        {result}
      </div>
    </section>
{mapblock}
    <a class="next" href="/work/{nslug}.html" data-tone="{CATS[nxt["cat"]][1]}">
      <span class="wrap next__inner">
        <span class="next__label">Next project</span>
        <span class="next__title">{nxt["title"]}<i class="ph ph-arrow-right" aria-hidden="true"></i></span>
        <span class="next__client">{nxt["client"]}</span>
      </span>
      <img class="next__img" src="/assets/posters/{nslug}.webp" alt="" loading="lazy">
    </a>

    <!--waves:{i + 11}-->
    <section class="cta" aria-labelledby="cta-title" data-tone="red">
      <div class="wrap cta__inner">
        <h2 id="cta-title" class="cta__title reveal">Want one <em>like this?</em></h2>
        <a class="btn btn--primary btn--lg reveal" style="--d:1" href="{CONTACT}" data-hide-dock>Start a project<i class="ph ph-arrow-right" aria-hidden="true"></i></a>
      </div>
    </section>
  </main>
"""
    return (f"{p['title']} for {p['client']} | Inspire Campaigns", f"{p['blurb']} A {p['format'].lower()} by Inspire Campaigns.", body, slug)


# ---------------------------------------------------------------- pages
PAGES = [
    ("index.html", "home", "Inspire Campaigns | Video & Visual Marketing in Vermont",
     "Short-form video, brand storytelling and paid ads for Vermont businesses. Inspire Campaigns makes visuals that stop the scroll and campaigns that close."),
    ("our-work.html", "work", "Our Work | Inspire Campaigns",
     "Video work for The Johnson Health Center, Prop Ready, Mechayeh, local food pop-ups and Burlington's Festival of Fools."),
    ("services.html", "services", "Services | Inspire Campaigns",
     "Videography, brand storytelling and paid advertising. We plan it, shoot it, post it and track what it earns."),
    ("vermont.html", "vermont", "Made in Vermont | Inspire Campaigns",
     "Where Inspire Campaigns has filmed and worked across Vermont: Burlington, Winooski, Colchester and Johnson."),
    ("about.html", "about", "About | Inspire Campaigns",
     "Meet Javi Matos Rodriguez, founder and creative lead of Inspire Campaigns: strategy, storytelling and video for Vermont brands."),
    ("contact-us.html", "contact", "Start a Project | Inspire Campaigns",
     "Tell Inspire Campaigns what you're working on: a launch, a pop-up, a campaign or a video you've been meaning to make."),
]

TILE_RE = re.compile(r"<!--tile:([\w-]+):([^:]*):(note|)-->")
WAVES_RE = re.compile(r"<!--waves:(\d+)-->")
VMAP_RE = re.compile(r"<!--vmap:([\w:,]+)-->")


def expand(body):
    body = TILE_RE.sub(lambda m: tile(m[1], m[2], m[3] == "note"), body)
    body = WAVES_RE.sub(lambda m: waves(int(m[1])), body)
    return VMAP_RE.sub(lambda m: vmap(m[1]), body)


def render(title, desc, key, body, og="popup-food", preload=""):
    return (HEAD.format(title=escape(title, quote=True), desc=escape(desc, quote=True), og=og, preload=preload,
                        v=V, ig=IG, li_javi=LI_JAVI)
            + header(key) + expand(body) + FOOTER)


for out, key, title, desc in PAGES:
    body = (ROOT / "pages" / out).read_text()
    pre = '<link rel="preload" as="image" href="/assets/posters/popup-food.webp">\n  ' if key == "home" else ""
    (ROOT / out).write_text(render(title, desc, key, body, preload=pre))
    print("wrote", out)

(ROOT / "work").mkdir(exist_ok=True)
for slug in ORDER:
    title, desc, body, og = case_page(slug)
    (ROOT / "work" / f"{slug}.html").write_text(render(title, desc, "work", body, og=og))
    print("wrote", f"work/{slug}.html")

# Security Review — hvaczone (pre-publish to *.pplx.app)

Scope: static HTML/CSS/JS marketing site for HVAC Zone Inc. No backend, no database,
no accounts, no LLM/connector usage. Client-side weather widget calls Open-Meteo
(no API key). Reviewed at /home/user/workspace/hvaczone.

## Security Review Results

### BLOCK (must fix before publishing)

**1. Reflected-XSS-shaped pattern in weather widget — FIXED**
- File: `js/weather.js:104-112` (render function), root cause `js/weather.js:131`
- Issue: The visible location `label` is built from the Open-Meteo **geocoding**
  API response (`geo.name`, `geo.admin1`, `geo.country_code`), which is influenced
  by the free-text city/postal search the visitor types into `#outlook-city`
  (`js/weather.js:120-131`). That `label` was concatenated, unescaped, directly
  into `result.innerHTML` (`js/weather.js:104-105`). If Open-Meteo ever echoes
  back attacker-supplied text unmodified (e.g. a crafted search string), or is
  itself compromised/spoofed, arbitrary HTML/JS could execute in the visitor's
  browser. This is a classic "trusted API, untrusted-influenced field into
  innerHTML" mistake and is treated as BLOCK given zero risk tolerance for a
  public marketing site.
- **Fix applied:** added an `escHtml()` helper (HTML-entity escaping for
  `& < > " '`) and wrapped `label` with it before insertion:
  `'<h3 class="outlook-loc">' + escHtml(label) + '</h3>'`. All other values
  interpolated into that `innerHTML` block are numeric (temps, degree-days) or
  hardcoded copy strings (`flags[].text`), so no other escaping was needed.
  Verified with `node -c js/weather.js` — no syntax errors introduced.
- Status: **Fixed in this review.** No further action needed unless you want to
  also switch the whole render function to DOM `textContent`/`createElement`
  construction instead of string-built HTML (more defense-in-depth, optional).

### WARN (inform user, let them decide)

**2. No dependency manifest / package manager audit possible**
- No `package.json`, `requirements.txt`, or lockfile found anywhere in the
  project (confirmed via filesystem search). This is expected for a pure static
  HTML/CSS/JS site with no build tooling dependencies (the one Python script,
  `build.py`, uses only the standard library — `json`, `os`, `re`, `datetime`).
  No third-party npm/pip packages are pulled in, so there is nothing to audit
  and no supply-chain exposure from dependencies. No action needed, just noting
  for the record.

**3. "Contact form" is not a data-collecting form — links only**
- File: `index.html:606-618` (`<section id="contact">`)
- There is **no `<form>` element** in the contact section at all. It's a CTA
  band with a `mailto:info@hvaczonenj.com` link and a `tel:+19736876386` link
  (`index.html:612-613`). Clicking either simply opens the visitor's email
  client or dialer — nothing is transmitted, stored, or processed by the site
  itself. This is safe (no injection/storage surface) but means there's no
  actual lead-capture mechanism yet; purely a UX/product note, not a security
  issue.

**4. Newsletter form is a non-functional UI demo**
- File: `hub.html:147` (`<form class="newsletter-form" data-demo>`), handled by
  `js/main.js:80-97`
- On submit, `main.js` calls `preventDefault()`, shows a fake "Subscribed ✓"
  button state, sets a note ("This is a preview — email delivery connects once
  your list/ESP is wired up."), and resets the form. No `action=`, no `fetch`,
  no network call — the email address the visitor types is discarded client-side
  and never sent anywhere. Confirmed no `action=` attribute exists anywhere in
  the project (`grep` across all `*.html`). Safe, but visitors could be misled
  into thinking they subscribed; consider wiring to a real ESP or removing the
  "Subscribed" copy before launch (product decision, not a security block).

**5. Weather widget calls two third-party APIs directly from the browser**
- File: `js/weather.js:7-8` (`GEOCODE`, `FORECAST` constants → `open-meteo.com`)
  and `:135-147` (uses `navigator.geolocation`)
- No API key is present or required (Open-Meteo free tier), consistent with the
  brief. Visitor's typed search query and, if they opt in via the "use my
  location" button, coarse lat/lon are sent to Open-Meteo's public endpoints
  over HTTPS. No first-party server is involved, so there's no first-party
  logging/storage of this data. Recommend disclosing this third-party call in
  a privacy note if the site has (or later adds) a privacy policy, since
  geolocation data leaves the browser to a third party — low risk but worth a
  one-line disclosure for transparency.

### PASS

**6. No hardcoded secrets**
- Grepped all `*.js *.json *.html *.env *.py *.css *.md` (excluding `.git`,
  `node_modules`, `dist`) for `sk-…`, `AKIA…`, `ghp_…`, `glpat-…`, `xox[baprs]-…`,
  `BEGIN PRIVATE KEY`, `api_key=`, `password=`, `secret=` patterns. No matches.
  No `.env` files present anywhere in the project. The weather widget confirmed
  to use Open-Meteo with **no API key** (`js/weather.js:7-8`), matching the
  provided context exactly.

**7. No dangerous eval/injection sinks with untrusted control flow**
- Grepped all `*.js`/`*.html` for `eval(`, `new Function(`, `dangerouslySetInnerHTML`,
  `document.write(`, `.html(`, `outerHTML=`, `insertAdjacentHTML`. None found.
  Only two `innerHTML=` assignments exist site-wide:
  - `js/main.js:16` — hardcoded inline SVG markup for a theme toggle icon, no
    variable/user input involved. Safe as-is.
  - `js/weather.js:104` — addressed above (now escapes the one user-influenced
    field).

**8. No open CORS / permissive server config**
- Grepped for `Access-Control-Allow-Origin`, `cors(`. No matches — expected,
  since this is a static site with no server component that could emit such
  headers. Nothing to fix.

**9. No backend, database, or credential surface**
- Confirmed via file listing: no `package.json`, no server code, no `.env`,
  no database config. `build.py` is a local content-generation script (run
  manually by a developer to regenerate article grids from
  `articles/index.json`) — it does not run in production or on the published
  site, and ships no secrets.

## Summary
- **1 BLOCK finding — fixed during this review** (unescaped geocoding label in
  `js/weather.js`, now HTML-escaped).
- **4 WARN items** — all informational/product-decision items (no dependency
  manifest to audit, contact section is mailto/tel only, newsletter form is a
  cosmetic demo, third-party weather API calls could use a privacy disclosure).
  None block publishing.
- **4 PASS checks** — no secrets, no other injection sinks, no open CORS, no
  backend/credential surface.

The site is safe to publish to a public `*.pplx.app` URL after this review's fix.

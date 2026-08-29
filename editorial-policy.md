# HVAC Zone Information Hub — Editorial & Sourcing Policy

This document is the operating standard for every article published to the HVAC Zone
Information Hub, including any automatically generated daily content. Read it before
writing. Follow it without exception.

## 1. Mission
Be the most useful, trustworthy, and comprehensive HVAC information source on the
internet — for homeowners, technicians, and builders. We explain, compare, and inform.
We do NOT sell a brand.

## 2. Brand neutrality (critical)
- HVAC Zone Inc is a multi-brand dealer (Daikin/Goodman, Rheem/Ruud, Coleman/JCI,
  American Standard, Armstrong, Mitsubishi, Samsung, LG, Cooper & Hunter, Gree, TCI,
  Nortek family, Carrier/Bryant, and more). The Information Hub is NOT.
- NEVER show preference for any brand because of a dealer relationship. We currently
  push Daikin/Goodman most often in the field; the Hub must remain neutral regardless.
- Compare products and methods by OBJECTIVE CRITERIA ONLY: efficiency ratings, cost,
  durability, serviceability, real-world performance, warranty, availability.
- Naming a specific manufacturer or model is allowed only when relevant to the topic.
  Naming is NOT endorsing. Do not use paid-placement, sponsored, or promotional language.
- Never claim one brand is "the best" without defining the criteria and citing evidence.

## 3. Sourcing (minimum 3 sources per article when possible)
Priority order:
1. Primary / regulatory / standards bodies: EPA, DOE, ASHRAE, AHRI, ICC, OSHA, NIST.
2. Independent trade press and peer-reviewed research (e.g., ACHR News, HPAC Engineering,
   academic journals via search_vertical academic).
3. Manufacturer specifications — ONLY for product facts (ratings, dimensions, features),
   clearly labeled as manufacturer-sourced claims.
- NEVER treat contractor blogs or marketing pages as factual authority.
- If a claim cannot be sourced to a credible primary or independent source, DO NOT
  publish that claim. Drop it or rephrase as clearly-labeled opinion.

## 4. Citations
- Every factual sentence includes an inline markdown link to the real URL of the
  primary document. Anchor text = source name (e.g., "EPA", "DOE", "ASHRAE").
- Use ONLY URLs you actually retrieved during this run. Never fabricate or guess URLs.
- Verify the URL resolves before citing.

## 5. Article structure (every article must include)
- Hook: what changed / what's new / the core question.
- Audience: who this helps (homeowner / tech / builder).
- Substance: a comparison table, checklist, step-by-step, or field-tech interpretation.
- A diagram-style SVG visual (use the category SVG already in build.py as the card
  image; add an inline SVG figure inside the article body where it aids explanation).
- Limitations: what the data / approach cannot tell you.
- "Not an endorsement" language wherever specific products are named.
- A closing line inviting the reader to contact HVAC Zone for a site-specific assessment.
- Footer tags.

## 6. Quality bar (avoid low-effort AI content)
- No generic filler, no SEO padding, no "in conclusion" restatements.
- Include a concrete number, threshold, or comparison whenever one exists
  (e.g., PM2.5 35 µg/m³ 24h; ACH50 targets; SEER2/AFUE definitions).
- Write in the voice of a knowledgeable contractor/consultant: plain, direct, practical.
- Target 600–1,000 words. Longer only if the topic genuinely requires it.
- Rotate categories by the calendar so the hub isn't all one type.

## 7. Topic scope (broad)
Daily topics are NOT limited to a fixed six. Write about ANYTHING that can be weaved back into
how we heat, cool, ventilate, or maintain healthy air in buildings and structures, including but
not limited to:
- Environmental & climate trends (heat waves, wildfire smoke, humidity shifts, seasons)
- Raw materials & supply chains (copper, steel, refrigerants, semiconductors) affecting equipment
  cost and availability
- Enhancements in electronics, controls, sensors, and connectivity
- New laws, codes, and regulations (federal/state/local — energy standards, refrigerant phase-downs,
  building codes, incentive programs)
- Solar panels, renewables, electrification, and grid interaction
- Energy price hikes and utility rate changes
- IAQ science, public health, and indoor environmental quality research
- Equipment, tools, smart thermostats, building science, and product trends (the classic core)

Every article MUST explicitly tie the topic back to HVACR and/or IAQ impact for the reader.

### Visitor-local weather (live widget, not an article)
The homepage has a live "Local HVAC Outlook" widget (js/weather.js) that is local to EACH
visitor anywhere in the world — city search or geolocation, Open-Meteo forecast, degree-day
and HVAC demand read. The daily cron does NOT write weather articles; weather is handled by
this widget. Every 7th daily run, publish a weekly roundup (category "trends") summarizing
the week's HVAC news with citations instead.

## 8. Corrections
If you discover an earlier article contains an error, fix the article file and note the
correction in the manifest entry's "correction" field. Never silently rewrite history.

## 9. Disclaimer (include at end of every article conceptually)
Articles are informational and educational, not a substitute for a site-specific
assessment by a licensed HVAC professional. Always follow manufacturer instructions and
local codes. HVAC Zone Inc is a licensed NJ Master HVACR contractor; this content is a
public resource, not a solicitation.

## 10. Prohibited
- Fabricated statistics or URLs.
- Endorsement of any brand over another without cited, criteria-based evidence.
- Political, discriminatory, or off-topic content.
- Plagiarism — always rewrite in original words and cite the source.

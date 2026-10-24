# Google Search TODO — erechnung-smart.de

Status: 24 October 2026.

- `[x]` — already in the repository
- `[ ]` — still to do

## Goal

Appear in Google.de for the queries people use when they need to **open, read, check, and export** an incoming XRechnung or ZUGFeRD file.

The product does not edit an issued invoice. Do not optimize for **erechnung bearbeiten**.

Realistic outcome: show up for narrow phrases such as «ZUGFeRD öffnen» and «E-Rechnung für den Steuerberater exportieren». Ranking above ELSTER, easybill, or dedicated validators for the broad query «XRechnung prüfen» needs links from other German sites, not only on-page text.

## Baseline (Google.de, logged out, 24 October 2026)

- `site:erechnung-smart.de` returned **one** URL: the homepage.
- «erechnung bearbeiten» — not in the top 30.
- «XRechnung und ZUGFeRD prüfen» — not in the top 30.
- The exact sentence «E-Rechnungen kommen als XML» was about position 6. That sentence is no longer the homepage headline.
- Homepage title in the repo and on production is `XRechnung und ZUGFeRD öffnen, prüfen und exportieren | eInvoice`. Google was asked to recrawl it on 24 October 2026.

---

## 1. Already in the repo

Checked against the repo on 24 October 2026. The wording commit `817eb85` is on `origin/main` and is live. Indexing of the homepage was requested the same day.

- [x] `frontend/public/robots.txt`: allow public pages, disallow account pages (including `/statistik`) and `/api/`, point at the sitemap
- [x] `frontend/public/sitemap.xml`: homepage, upload, tarife, hilfe, impressum, datenschutz, five topic pages, and each FAQ URL
- [x] Nginx serves `robots.txt`, `sitemap.xml`, and the Google verification file as real files (`deploy/nginx-spa-snippet.conf`)
- [x] SPA fallback: unknown paths return `index.html` (so `/hilfe` is not a server 404)
- [x] Canonical URL, `index,follow` on public pages, `noindex,nofollow` on account pages (`frontend/src/seo.ts`)
- [x] Unique title and description for `/`, `/upload`, `/tarife`, `/hilfe`, `/impressum`, `/datenschutz`
- [x] Homepage H1, document title, meta description, and Open Graph use the same words: öffnen, prüfen, exportieren
- [x] `lang="de"` and WebApplication JSON-LD on the homepage shell (`frontend/index.html`)
- [x] Google verification file `frontend/public/googlea13d2b84aeb444f1.html`

---

## 2. Publish the new homepage wording

- [x] Deploy the current frontend so production title, H1, and description match the repo
- [x] After deploy, open the live homepage and confirm the visible H1 is `XRechnung und ZUGFeRD öffnen, prüfen und exportieren`
- [x] In Google Search Console, request indexing of `https://erechnung-smart.de/` (requested 24 October 2026; URL was already in the index)

---

## 3. Let Google follow real links

Today the menu, footer, and landing buttons call JavaScript (`PageNav`, `SiteFooter`, landing CTAs). A crawler that does not run that click handler never sees `/hilfe`, `/tarife`, or `/upload` as links. That matches the Search result: only `/` is indexed.

- [x] Replace public navigation buttons with `<a href="...">` for `/`, `/upload`, `/tarife`, `/hilfe`, `/impressum`, `/datenschutz`
- [x] Keep account actions (`Anmelden`, `Verlauf`, `Organisation`, `Statistik`) as buttons; they stay out of the sitemap
- [x] Put the same public URLs in the footer as normal links
- [x] On the homepage, link the words «prüfen» and «exportieren» to `/upload` and `/hilfe`
- [ ] After the next deploy, check that each new public URL returns HTTP 200 on production and that the canonical points at itself

---

## 4. One public page per search query

One homepage cannot rank for every phrase. Each page below needs its own path, its own `<title>`, H1, short answer, and a link to upload.

Do not create a page for «E-Rechnung bearbeiten».

- [x] `/xrechnung-oeffnen` — query: XRechnung öffnen
- [x] `/zugferd-oeffnen` — query: ZUGFeRD öffnen
- [x] `/e-rechnung-lesen` — query: E-Rechnung lesen
- [x] `/xrechnung-zugferd-pruefen` — query: XRechnung und ZUGFeRD prüfen
- [x] `/steuerberater-export` — query: E-Rechnung für den Steuerberater exportieren

For each page:

- [x] German title with the query, then `| eInvoice`
- [x] H1 repeats the query in normal language
- [x] Two or three short paragraphs: what the file is, what eInvoice shows, what the user can export
- [x] One primary action: Rechnung hochladen (`/upload`)
- [x] Canonical URL on that path
- [x] Entry in `sitemap.xml`
- [x] A normal link from `/hilfe` and from the homepage
- [x] `seoForPath` entry and a test that the title and canonical are stable

---

## 5. Help and FAQ as indexable answers

`/hilfe` exists, but its questions are not separate URLs, and Google has not indexed the page.

- [x] Give each FAQ item its own path under `/hilfe/...`
- [x] Add `FAQPage` JSON-LD that matches the visible questions and answers
- [x] Link each new topic page from the matching FAQ answer
- [x] Keep `/faq` as a redirect to `/hilfe` (static refresh page plus canonical)

---

## 6. HTML Google can read before JavaScript

`index.html` always ships the homepage title. Other routes change the title only after React runs. Google rendered the homepage once, but `/upload`, `/tarife`, and `/hilfe` are still absent from the index.

- [x] For every public URL, the built HTML already contains that page's `<title>`, meta description, canonical, and H1 (`frontend/scripts/prerender.mjs`, runs at the end of `vite build`)
- [x] Prerender covers landing, upload, tarife, hilfe, impressum, datenschutz, topic pages, and FAQ pages
- [x] Account pages stay client-only and `noindex`
- [x] The built files in `frontend/dist` contain the H1 in the HTML body (checked 24 October 2026)
- [ ] After deploy, repeat that check against `https://erechnung-smart.de`

---

## 7. Google Search Console

The verification file is in the repo. The console steps are outside the repo.

- [ ] Confirm the property `https://erechnung-smart.de/` is verified
- [ ] Submit `https://erechnung-smart.de/sitemap.xml`
- [ ] Inspect URL for `/`, `/upload`, `/tarife`, `/hilfe` and fix any «Discovered – currently not indexed» or «Crawled – currently not indexed» cause
- [ ] After each new topic page is deployed, request indexing for that exact URL
- [ ] Check Coverage / Pages weekly until the public URLs are indexed

---

## 8. Mentions on other sites

On-page text does not outrank ELSTER, DATEV, easybill, or validator landing pages. Those results have links.

- [ ] Ask pilot Steuerberater to link to one specific page (for example `/steuerberater-export`), not only to the homepage
- [ ] List the tool once in a relevant German directory or «kostenlose E-Rechnung Tools» article, with the matching URL
- [ ] When answering a public question (forum, blog comment), link to the page that answers that question
- [ ] Do not buy links and do not publish the same text on many sites

---

## 9. Checks after each change

- [ ] `site:erechnung-smart.de` lists the homepage and the new public pages
- [ ] Search the exact H1 of a new page in quotes; the page should be the first result
- [ ] Search the target query without quotes and record the position (logged out, google.de)
- [ ] Re-check these queries: «XRechnung öffnen», «ZUGFeRD öffnen», «E-Rechnung lesen», «XRechnung und ZUGFeRD prüfen», «E-Rechnung Steuerberater exportieren»
- [ ] Leave «erechnung bearbeiten» untargeted

## Out of scope

- Ads (Google Ads can sit above the organic results; they do not change organic rank)
- Keyword stuffing the homepage with every query
- A page that promises invoice editing
- English or Russian public pages (`lang` stays `de`)

# NWGS Grid™ — National Wastewater Genomics Smart Grid

### 🌐 Live site: **[nwgsgrid.com](https://nwgsgrid.com/)**

**Full website file (download and open in a browser):** [snapshot/NWGS_Grid_website.html](snapshot/NWGS_Grid_website.html) · Page source: [site_src/template.html](site_src/template.html)

Weekly, validated wastewater surveillance of respiratory and emerging pathogens across U.S. counties,
rebuilt every Saturday by GitHub Actions. Sign in on the site to save alerts.

## About

NWGS Grid™ shows what wastewater testing can detect across the United States, and which communities it cannot see.
Every Saturday it gathers CDC wastewater results for six pathogens, along with emergency department visits, county
health measures, social vulnerability, sewer service and genomic records, runs its validation checks and rebuilds the
site from one snapshot. If any check fails, nothing is published and the previous week's results stay up.

- **Timeliness:** separates how early a signal appears from how long it takes to reach the public.
- **Coverage:** measures how much of each county testing actually reaches.
- **Reproducibility:** every weekly run is saved and citable, so any figure can be checked later.

**Developer:** Victoria Love Franklin, PhD Data Science Student. Featured as an Inspiring Black Scientist through
[Wiley's Inspiring Black Scientists initiative](https://www.wiley.com/en-us/research/inspiring-black-scientists), 2026.

## The website

One static HTML page. No framework, no bundler, no build step for the browser, and nothing
queried at page load: every figure is precomputed, so any page can be reproduced exactly from
the archived release for its run. `scripts/build_site.py` substitutes one JSON payload into
`site_src/template.html` and writes `site/index.html`.

**Nineteen views, grouped into six sections in the header:**

| Section | Views |
|---|---|
| Overview | Start here · Dashboard |
| Surveillance | Surveillance map · Trends & timing · Lead time · Predictive models · Alerts · My alerts |
| Coverage & equity | Where monitoring happens · Coverage & equity · Global coverage · Tennessee |
| Research & genomics | Genomics & AMR · Protein structures |
| Data & methods | Data & reports · Audit log · Methods & sources · Glossary |
| About | About the developer |

**Data & reports** lets a reader choose an area and pathogens and take away a written report —
narrative, figures, maps and figure descriptions for that selection — rather than a bare table.

The grouping is presentation only. Every view key and `#hash` route is unchanged, so existing
links keep working. Below roughly 760px the header collapses to a menu button and the groups
become one stacked list, so no view is more than one tap away.

**Design rules the page keeps to:**

- Navy carries the text, rose marks selected state and accents, teal pairs with rose on charts.
  No text on the site is grey.
- Three type sizes and no more: 32px page titles, 20px section headings, 16px for anything
  written to be read, plus 15px captions and 12px field labels. A component that sets its own
  size is a bug.
- Each pathogen has one colour, defined once and used on its card, sparkline, trend line, map
  and chips. A colour identifies the pathogen; it never signals severity.
- Panels size to their own content rather than stretching to the tallest card in the row.
- An empty panel always says which source did not load and why, so a missing source can never
  be mistaken for a measurement of zero.
- Monospace is reserved for run identifiers, dataset codes and audit output.

The front end reference documents the data object, the view functions, the chart helpers and
the theme tokens in full.

**Author:** Victoria Love Franklin · PhD Data Science Student · Published Research Scholar · Developer

**Contact, license requests and beta feedback:** alerts@nwgsgrid.com

**Copyright © 2026 Victoria Love Franklin. All rights reserved.** No reuse without written
permission; see [LICENSE](LICENSE). To cite, use **Cite this repository** on GitHub (from
[CITATION.cff](CITATION.cff)) and name the weekly release your numbers come from.

```
CDC / NCBI / RCSB APIs → pipeline/nwgs_pipeline.py → scripts/nwgs_app_export.py → scripts/build_site.py → GitHub Pages
                          (tables)                    (validation gate)              (index.html)
```

## Documentation

Generated from the code and from a run's export, so they describe what the project
actually does rather than what it did when someone last wrote them down.

| Document | For | Covers |
|---|---|---|
| [User guide](docs/USER_GUIDE.md) | Anyone reading the site | What each page answers, how to read a level, how to set an alert, what the numbers do not mean |
| [Front end reference](docs/FRONTEND.md) | Developers | How the page is built, the data object, views, chart helpers, theme tokens, how to add a page |
| [Back end reference](docs/BACKEND.md) | Developers | Pipeline stages, the validation gate, database and row-level security, automation, secrets, releases |
| [Data reference](docs/DATA_REFERENCE.md) | Researchers and developers | Every upstream dataset and every exported column, with type, nullability and meaning |
| [Runbook](docs/RUNBOOK.md) | Whoever operates it | Publishing, reading a failed run, rotating a secret, adding a pathogen, reproducing a figure |
| [Dashboard audit](docs/DASHBOARD_AUDIT.md) | Review and record | Per-run audit: what the dashboard collects, validates, publishes and cannot claim |

Each one is also kept as a Word file in `docs/`, named `NWGS_Grid_<DOCUMENT>.docx`.

One document is hand-maintained rather than generated, because it records how
external services are configured rather than what the code does:

| Document | For | Covers |
|---|---|---|
| [Domain, email and sign-in](docs/DOMAIN_AND_EMAIL.md) | Whoever operates it | The custom domain end to end, the sending mailbox, Supabase redirects, and the registrar behaviour that makes each of them fail |

Regenerate all of them from any run's export:

```
python3 scripts/build_docs.py      <export_dir>
python3 scripts/build_audit_doc.py <export_dir> docs/DASHBOARD_AUDIT.md
node scripts/md_to_docx.js docs/BACKEND.md docs/NWGS_Grid_BACKEND.docx   # needs: npm install docx
```

`<export_dir>` is a run's app export: the folder holding `manifest.json` and the
entity CSVs. Use a full export from a release, not `sample_export/`, which holds
a subset and will produce a shorter data reference.

## Weekly run
`.github/workflows/weekly-update.yml` runs every Saturday at 13:17 UTC (8:17 a.m. Central), and
from **Actions → Weekly NWGS Grid update → Run workflow** at any time.

1. Verifies the build inputs are present. A missing pipeline, script or template fails the run
   here rather than being worked around later, so the previous week stays published.
2. Runs the pipeline with the API keys stored as repository secrets.
3. Exports app data. If a blocking check fails, or tables come from different runs, the job
   stops, the live site keeps last week's data, and GitHub emails you about the failed run.
4. Commits the forecast ledger back, so each prediction is timestamped in git history before
   the week it predicted.
5. Builds `site/index.html` and publishes it to GitHub Pages.
6. Saves the export, pipeline tables and log as a run artifact for 90 days (failed runs too).
7. Publishes a permanent **Release** named after the run (e.g. `run_20261017T1317Z-r12`) with
   zipped tables, figures, app export, manifest and log. Cite each paper's numbers from a
   single release.

## Accounts and alerts (Supabase)
The site's sign-in, **My alerts**, feedback and license-request forms use a Supabase project
(`site_src/supabase.json` holds its public URL and publishable key; both are safe to publish).
- Database tables and security rules: `supabase/schema.sql` (run once in the SQL Editor).
- Weekly alert emails: `scripts/send_alerts.py`, run by the workflow after each passing run.
  Secrets: `SUPABASE_SECRET_KEY`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_HOST` when the
  mailbox is not on the default host. One mailbox, `alerts@nwgsgrid.com`, both sends the
  automated mail and receives replies: it is the sender, the Reply-To, and the contact
  address published on the site, in LICENSE and in CITATION.cff.
- Sign-in links are sent by Supabase itself, not by this repository, so its own SMTP settings
  and redirect URLs have to be configured too. Both are in
  [docs/DOMAIN_AND_EMAIL.md](docs/DOMAIN_AND_EMAIL.md).
- Read feedback and license requests in Supabase → **Table Editor**.

## One-time setup
1. **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. **Settings → Actions → General → Workflow permissions → Read and write permissions**
   (the run publishes a Release and commits the forecast ledger back)
3. **Settings → Secrets and variables → Actions → New repository secret**
   - `SOCRATA_KEY_ID` and `SOCRATA_KEY_SECRET` (data.cdc.gov → Developer Settings → API Keys)
   - `SOCRATA_APP_TOKEN`, `NCBI_API_KEY` (optional, raise rate limits)
   - `SUPABASE_SECRET_KEY`, `SMTP_USER`, `SMTP_PASSWORD` (weekly alert email)
4. Custom domain. `site_src/CNAME` contains `nwgsgrid.com` and the build copies it into the
   published output, so the domain survives every deploy. To change or remove it, edit that
   file. Three things have to agree: that file, **Settings → Pages**, and four `A` records on
   the apex at the DNS host. Nothing is published on `www`. Sign-in also needs the domain
   added to Supabase under **Authentication → URL Configuration**, or links keep pointing at
   the old host. Full procedure, including the registrar behaviour that breaks it:
   [docs/DOMAIN_AND_EMAIL.md](docs/DOMAIN_AND_EMAIL.md).

## Folders
| Path | Contents |
|---|---|
| `pipeline/` | The surveillance script (`nwgs_pipeline.py`) |
| `scripts/` | Export (validation gate), site build, alert emails, documentation generators |
| `site_src/` | Page template, images and U.S. county map (us-atlas, ISC license) |
| `static_inputs/` | Files the pipeline doesn't download: SVI county and tract, USDA rural-urban codes, EPA sewershed crosswalks, AMR panel. The forecast ledger is not seeded here; the workflow creates it on the first run that produces one. Provenance and caveats in `static_inputs/README.md`; TIGER is downloaded each run |
| `supabase/` | Database tables and security rules for accounts and alerts |
| `docs/` | Generated documentation (see above), in Markdown and Word |
| `references/` | Every source the project cites, with links and access terms, plus BibTeX for manuscripts |
| `sample_export/` | A saved export, used as a fixture for running the scripts offline |
| `LICENSE`, `CITATION.cff` | Copyright terms and citation details |
| `.gitattributes` | Pins LF line endings, so a Windows round-trip cannot rewrite every line of a data file |

## Urbanicity layer
`load_rucc()` and `rucc_coverage()` join USDA Economic Research Service
[Rural-Urban Continuum Codes](https://www.ers.usda.gov/data-products/rural-urban-continuum-codes)
(2023 vintage) to the county surveillance roster, giving coverage equity a second axis beside
social vulnerability: codes 1–3 metropolitan, 4–9 nonmetropolitan graded by urban population
and metro adjacency. Results go to `Table06d_RUCC_County_Coverage.csv`, and county identifiers
the national county file does not contain go to `Table06e_RUCC_Unmatched_Counties.csv` rather
than being dropped — a retired or invalid FIPS is worth seeing.

Two properties of the published file are handled rather than assumed: it is distributed in
Windows-1252, not UTF-8, because seventeen county names carry accented characters, and it is in
long form with three rows per county, so it is pivoted before the join. The file is committed to
`static_inputs/` rather than downloaded each run, because the published download URL carries a
cache-busting token that changes when ERS republishes; the codes are revised about once a
decade, so pinning the file also freezes provenance for every release.

Because CDC's own description of NWSS reports the same metropolitan split, the result is
checkable against a published figure rather than standing alone. The page states both numbers
and says why they are not expected to match exactly.

## Structural annotation layer
`pull_uniprot_functional_regions()` in the pipeline imports UniProtKB's curated feature table
for each representative structure's protein and maps the residue ranges onto that structure's
author numbering via RCSB's 1D-coordinates alignment, writing
`Table11d_UniProt_Functional_Regions.csv`. The app shows only rows with `mapping_status=MAPPED`
and marks them `pending_expert_review` until a structural biology collaborator signs off.
It is a descriptive, cited reference layer: nothing is predicted, scored or ranked.

## Build locally
```
pip install pandas numpy
python scripts/build_site.py sample_export site
```
Then open `site/index.html`.

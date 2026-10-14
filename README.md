# NWGS Grid™ site

### 🌐 Live site: **[victorialovefranklin.github.io/nwgs-grid-site](https://victorialovefranklin.github.io/nwgs-grid-site/)**

Weekly, validated wastewater surveillance of respiratory and emerging pathogens across U.S. counties,
rebuilt every Saturday by GitHub Actions. Sign in on the site to save alerts.

**Author:** Victoria Love Franklin · Developer · PhD Student, Data Science · Research Scholar

**Contact, license requests and beta feedback:** victorialovefranklin@gmail.com

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
  Secrets: `SUPABASE_SECRET_KEY`, `SMTP_USER`, `SMTP_PASSWORD` (Gmail App Password).
- Read feedback and license requests in Supabase → **Table Editor**.

## One-time setup
1. **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. **Settings → Actions → General → Workflow permissions → Read and write permissions**
   (the run publishes a Release and commits the forecast ledger back)
3. **Settings → Secrets and variables → Actions → New repository secret**
   - `SOCRATA_KEY_ID` and `SOCRATA_KEY_SECRET` (data.cdc.gov → Developer Settings → API Keys)
   - `SOCRATA_APP_TOKEN`, `NCBI_API_KEY` (optional, raise rate limits)
   - `SUPABASE_SECRET_KEY`, `SMTP_USER`, `SMTP_PASSWORD` (weekly alert email)
4. Custom domain: create `site_src/CNAME` containing `nwgsgrid.com`, set the same domain under
   **Settings → Pages**, and point the domain's DNS to GitHub Pages.

## Folders
| Path | Contents |
|---|---|
| `pipeline/` | The surveillance script (`nwgs_pipeline.py`) |
| `scripts/` | Export (validation gate), site build, alert emails, documentation generators |
| `site_src/` | Page template, images and U.S. county map (us-atlas, ISC license) |
| `static_inputs/` | Files the pipeline doesn't download (SVI, AMR, forecast ledger seed); TIGER is downloaded each run |
| `supabase/` | Database tables and security rules for accounts and alerts |
| `docs/` | Generated documentation (see above) |
| `sample_export/` | A saved export, used as a fixture for running the scripts offline |
| `LICENSE`, `CITATION.cff` | Copyright terms and citation details |

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

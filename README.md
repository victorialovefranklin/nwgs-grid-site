# NWGS Grid™ site

### 🌐 Live site: **[victorialovefranklin.github.io/nwgs-grid-site](https://victorialovefranklin.github.io/nwgs-grid-site/)**

Weekly, validated wastewater surveillance of respiratory and emerging pathogens across U.S. counties,
rebuilt every Saturday by GitHub Actions. Sign in on the site to save alerts.

**Author:** Victoria Love Franklin — Developer · PhD Student, Data Science · Research Scholar

**Contact, license requests and beta feedback:** victorialovefranklin@gmail.com

**Copyright © 2026 Victoria Love Franklin. All rights reserved.** No reuse without written
permission; see [LICENSE](LICENSE). To cite, use **Cite this repository** on GitHub (from
[CITATION.cff](CITATION.cff)) and name the weekly release your numbers come from.

```
CDC / NCBI / RCSB APIs → pipeline/nwgs_pipeline.py → scripts/nwgs_app_export.py → scripts/build_site.py → GitHub Pages
                          (tables)                    (validation gate)              (index.html)
```

## Weekly run
`.github/workflows/weekly-update.yml` runs every Saturday at 13:17 UTC (8:17 a.m. Central), and
from **Actions → Weekly NWGS Grid update → Run workflow** at any time.

1. Runs the pipeline with the API keys stored as repository secrets.
2. Exports app data. If any Table13 check is FAIL, or tables come from different runs, the job
   stops, the live site keeps last week's data, and GitHub emails you about the failed run.
3. Builds `site/index.html` and publishes it to GitHub Pages.
4. Saves the export, pipeline tables and log as a run artifact for 90 days (failed runs too).
5. If the run passes, publishes a permanent **Release** named after the run
   (e.g. `run_20261017T1317Z-r12`) with zipped tables, figures, app export, manifest and log.
   All weekly snapshots are listed under **Releases** on the repo page. Cite each paper's
   numbers from a single release.

Until `pipeline/nwgs_pipeline.py` is added, the workflow publishes the saved Oct 9, 2026 export in
`sample_export/`.

## Accounts and alerts (Supabase)
The site's sign-in, **My alerts**, feedback and license-request forms use a Supabase project
(`site_src/supabase.json` holds its public URL and publishable key; both are safe to publish).
- Database tables and security rules: `supabase/schema.sql` (run once in the SQL Editor).
- Weekly alert emails: `scripts/send_alerts.py`, run by the workflow after each passing run.
  Secrets: `SUPABASE_SECRET_KEY`, `SMTP_USER`, `SMTP_PASSWORD` (Gmail App Password).
- Read feedback and license requests in Supabase → **Table Editor**.

## One-time setup
1. **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. **Settings → Secrets and variables → Actions → New repository secret**
   - `SOCRATA_KEY_ID` and `SOCRATA_KEY_SECRET` (data.cdc.gov → Developer Settings → API Keys)
   - `NCBI_API_KEY` (optional)
3. Add the pipeline script and any manual input files (see `pipeline/README.md`).
4. Custom domain: create `site_src/CNAME` containing `nwgsgrid.com`, set the same domain under
   **Settings → Pages**, and point the domain's DNS to GitHub Pages.

## Folders
| Path | Contents |
|---|---|
| `pipeline/` | The surveillance script (`nwgs_pipeline.py`) |
| `static_inputs/` | Files the pipeline doesn't download (SVI, AMR); TIGER is downloaded each run |
| `scripts/` | Export (validation gate), site build, weekly alert emails |
| `supabase/` | Database tables and security rules for accounts and alerts |
| `site_src/` | Page template and U.S. county map (us-atlas, ISC license) |
| `sample_export/` | Oct 9, 2026 export used until the pipeline runs here |
| `LICENSE`, `CITATION.cff` | Copyright terms and citation details |

## Build locally
```
pip install pandas numpy
python scripts/build_site.py sample_export site
```
Then open `site/index.html`.

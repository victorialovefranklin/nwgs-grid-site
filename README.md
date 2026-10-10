# NWGS Grid™ site

Static site for nwgsgrid.com, rebuilt every week by GitHub Actions.

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
4. Saves the export (CSVs + manifest) as a run artifact for 90 days.

Until `pipeline/nwgs_pipeline.py` is added, the workflow publishes the saved Oct 9, 2026 export in
`sample_export/`.

## One-time setup
1. **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. **Settings → Secrets and variables → Actions → New repository secret**
   - `SOCRATA_APP_TOKEN` (free from data.cdc.gov → Developer Settings)
   - `NCBI_API_KEY` (optional)
3. Add the pipeline script and any manual input files (see `pipeline/README.md`).
4. Custom domain: create `site_src/CNAME` containing `nwgsgrid.com`, set the same domain under
   **Settings → Pages**, and point the domain's DNS to GitHub Pages.

## Folders
| Path | Contents |
|---|---|
| `pipeline/` | The surveillance script (`nwgs_pipeline.py`) |
| `static_inputs/` | Files the pipeline doesn't download (SVI, TIGER, AMR) |
| `scripts/` | Export, site build, Base44 schema generator |
| `site_src/` | Page template and U.S. county map (us-atlas, ISC license) |
| `sample_export/` | Oct 9, 2026 export used until the pipeline runs here |

## Build locally
```
pip install pandas numpy
python scripts/build_site.py sample_export site
```
Then open `site/index.html`.

# Pipeline

Put the surveillance script here as **`nwgs_pipeline.py`** (export the Colab notebook with
File → Download → Download .py).

Before the first automated run, check four things in the script:

1. **No Colab-only code.** Remove or guard `from google.colab import drive`, `drive.mount(...)`,
   `!pip install ...` lines and `files.download(...)`. The workflow installs packages from
   `requirements.txt` instead.
2. **Paths.** The workflow creates `/content/NWGS_GRID` exactly like Colab, so existing paths work.
   Tables must end up in `/content/NWGS_GRID/outputs/tables`.
3. **API keys.** Read them from the environment, never type them into the script:
   `SOCRATA_APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN")`
   (and `NCBI_API_KEY` the same way if the script uses one).
4. **Input files.** Already in `static_inputs/` (copied to `/content/NWGS_GRID/data/`):
   `SVI_2022_US_COUNTY.csv` and `US_Wastewater_AMR_ARG_2024.csv`.
   The TIGER/Line 2025 county shapefile (`tl_2025_us_county.*`, ~130 MB) is too big for GitHub,
   so the workflow downloads it from the Census Bureau into the same folder on each run.
   CDC NWSS data (such as the RSV file) comes from the API, so no CSV copy is needed.
   If the script expects these files under different names or folders, change its paths to match.

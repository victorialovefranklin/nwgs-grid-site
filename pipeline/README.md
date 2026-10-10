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
4. **Manual input files** (SVI, TIGER shapefiles, the AMR/ARG file, anything not downloaded by the
   script) go in `static_inputs/`. The workflow copies them to `/content/NWGS_GRID/data/`.

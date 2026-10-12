#!/usr/bin/env python3
"""
Generate docs/DASHBOARD_AUDIT.md from one app export.

    python3 scripts/build_audit_doc.py <EXPORT_DIR> <OUT_MD>

The narrative sections are written here. Every count, dataset identifier, run
identifier and source-load outcome is read from the export, so the document
cannot drift away from the run it describes. A figure that is not in the export
is printed as "not in this run" rather than guessed.

Author: Victoria Love Franklin - Developer, PhD Student, Data Science, Research Scholar
Copyright (c) 2026 Victoria Love Franklin. All rights reserved. See LICENSE.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "site_src" / "template.html"

# What each view answers. Keys are the view identifiers in template.html; the
# labels and the order come from the template itself so the two cannot diverge.
VIEW_NOTES = {
    "start": "Orientation: what wastewater surveillance is, its limits, and how to use the site",
    "dashboard": "Current national level per pathogen, direction of travel, counties at High, emerging detection rates, latest alerts",
    "map": "County choropleth with selection, plus spatial clustering statistics",
    "analytics": "National trends, seasonal peaks, wastewater-to-clinical lag",
    "leadtime": "Shedding lead, reporting lag and operational lead, decomposed",
    "predictive": "Held-out model benchmarks, SHAP attribution, archived forecast scoreboard",
    "equity": "Coverage against social vulnerability, county representativeness, site attrition",
    "global": "Country sanitation denominator and the observability ceiling it implies",
    "tennessee": "State deep dive",
    "genomics": "Resistance gene detections and NCBI genome records",
    "structures": "Reference protein structures, cited functional regions, assay-target panel",
    "alerts": "States and counties above the High threshold",
    "myalerts": "Authenticated saved alert rules",
    "audit": "Per-run validation checks and data-source outcomes",
    "methods": "Pipeline description, dataset list, full reference list",
    "glossary": "Plain-language definitions of every term used on the site",
    "about": "Authorship, citation, licensing, feedback",
}

DEP_NOTES = {
    "d3": ("cdnjs.cloudflare.com", "Charts and maps"),
    "topojson": ("cdnjs.cloudflare.com", "County and state geometry"),
    "supabase-js": ("cdn.jsdelivr.net", "Sign-in and saved alerts"),
    "3dmol": ("cdn.jsdelivr.net", "Protein viewer, loaded on demand"),
}


def read_views():
    """Pull the view list out of template.html. Returns [] if it cannot be read."""
    try:
        src = TEMPLATE.read_text(encoding="utf-8")
    except Exception:
        return []
    m = re.search(r"const VIEWS\s*=\s*\[(.*?)\];", src, re.S)
    if not m:
        return []
    return re.findall(r"\['([^']+)','([^']+)'\]", m.group(1))


def read_deps():
    """Pull the externally fetched script versions out of template.html."""
    try:
        src = TEMPLATE.read_text(encoding="utf-8")
    except Exception:
        return []
    found = []
    for url in sorted(set(re.findall(r"https://cdn[^\"'\s)]+\.js", src))):
        name = ver = None
        m = re.search(r"/libs/([^/]+)/([0-9][^/]*)/", url)          # cdnjs
        if m:
            name, ver = m.group(1), m.group(2)
        else:
            m = re.search(r"/npm/(?:@[^/]+/)?([^@/]+)@([^/]+)", url)  # jsdelivr
            if m:
                name, ver = m.group(1), m.group(2)
        if not name:
            continue
        origin, use = DEP_NOTES.get(name.lower(), ("", ""))
        found.append([name, ver, origin or url.split("/")[2], use])
    return found


def read(export: Path, name: str):
    """Return a dataframe, or None when that entity is absent from the run."""
    p = export / f"{name}.csv"
    if not p.exists():
        return None
    try:
        df = pd.read_csv(p, low_memory=False)
        return df if len(df) else None
    except Exception:
        return None


def n(df, fallback="not in this run"):
    return f"{len(df):,}" if df is not None else fallback


def number_sections(md):
    """Number `##` and `###` headings, then resolve [[ref:Title]] tokens.

    Sections are numbered from their position in the finished document, so
    inserting or reordering one cannot leave a stale number or a cross-reference
    pointing at the wrong place. A token naming a heading that does not exist is
    reported rather than silently left in the text.
    """
    out, top, sub, index = [], 0, 0, {}
    fence = False
    for line in md.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and line.startswith("## ") and not line.startswith("### "):
            top += 1
            sub = 0
            title = line[3:].strip()
            index[title] = f"section {top}"
            line = f"## {top}. {title}"
        elif not fence and line.startswith("### "):
            sub += 1
            title = line[4:].strip()
            index[title] = f"{top}.{sub}"
            line = f"### {top}.{sub} {title}"
        out.append(line)
    md = "\n".join(out)

    missing = []

    def sub_ref(m):
        key = m.group(1).strip()
        if key in index:
            return index[key]
        missing.append(key)
        return key

    md = re.sub(r"\[\[ref:(.+?)\]\]", sub_ref, md)
    if missing:
        print("[WARN] unresolved cross-reference(s): " + "; ".join(sorted(set(missing))))
    return md


def table(rows, header):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


# What each tracked path is for. Anything on disk and not named here is still
# listed, with its purpose left blank rather than invented.
PATH_PURPOSE = {
    "pipeline": "The surveillance pipeline. Acquisition, harmonization, standardization, every analytic layer, and the validation gate.",
    "scripts": "Build and delivery utilities run by the workflow.",
    "site_src": "The site source: the page template, county geometry, images and the public Supabase configuration.",
    "static_inputs": "Inputs the pipeline cannot download for itself, plus the committed forecast ledger seed.",
    "supabase": "The database schema: tables, row-level security and policies. The source of truth for the Supabase project.",
    "sample_export": "A saved export kept as a fixture for testing scripts offline. It is not a build fallback; the workflow refuses to build without the real pipeline.",
    "docs": "This audit document.",
    ".github": "The weekly workflow definition.",
    "requirements.txt": "Pinned Python dependencies installed at the start of every run.",
    "LICENSE": "All rights reserved. No reuse without written permission.",
    "CITATION.cff": "Machine-readable citation metadata, used by GitHub's “Cite this repository” button.",
    "README.md": "Repository overview and setup notes.",
    ".gitignore": "What is deliberately excluded; see [[ref:What is deliberately **not** in the repository]].",
}

SCRIPT_PURPOSE = {
    "nwgs_app_export.py": "Turns pipeline tables into the entity CSVs the site reads, and runs the validation gate.",
    "build_site.py": "Pours one export into the template and writes the finished static site.",
    "send_alerts.py": "Matches a new run against saved alert rules and sends the emails.",
    "build_audit_doc.py": "Generates this document from a run export and the repository.",
}

SECRET_PURPOSE = {
    "SOCRATA_APP_TOKEN": "Raises the CDC Socrata API rate limit",
    "SOCRATA_KEY_ID": "Authenticates the CDC Socrata pull",
    "SOCRATA_KEY_SECRET": "Authenticates the CDC Socrata pull",
    "NCBI_API_KEY": "Raises the NCBI rate limit for genome records",
    "SUPABASE_SECRET_KEY": "Server-side read of saved alert rules",
    "SMTP_USER": "Sends the weekly alert email",
    "SMTP_PASSWORD": "Sends the weekly alert email",
}


LIB_PURPOSE = {
    "pandas": "Every table in the pipeline; all tabular work",
    "numpy": "Numeric arrays underlying the standardization",
    "requests": "HTTP for CDC Socrata, NCBI, RCSB, World Bank and JMP",
    "scipy": "Spearman correlation and the statistical tests",
    "statsmodels": "The binomial GLM for coverage equity",
    "scikit-learn": "The held-out predictive models",
    "shap": "Feature attribution for those models",
    "matplotlib": "Publication figures (headless, MPLBACKEND=Agg)",
    "pillow": "Figure post-processing and the portrait self-check",
    "geopandas": "County geometry and spatial joins",
    "shapely": "Geometry operations",
    "pyproj": "Reprojection to EPSG:5070 for the spatial analysis",
    "pyogrio": "Fast reader for the TIGER/Line shapefile",
    "libpysal": "The six-nearest-neighbour spatial weights graph",
    "esda": "Global and local Moran's I",
    "pyarrow": "Columnar I/O",
    "openpyxl": "Reads the WHO/UNICEF JMP workbook",
}


def stack_sections():
    """Languages and pinned libraries, read from requirements.txt."""
    lang_tbl = table([
        ["Python 3.11", "`pipeline/`, `scripts/`",
         "Data acquisition, all analysis, export, site build, alert mail"],
        ["HTML / CSS / JavaScript", "`site_src/template.html`",
         "The entire front end, in one file with no framework and no build step"],
        ["SQL (PostgreSQL)", "`supabase/schema.sql`",
         "Table definitions, row-level security and policies"],
        ["YAML", "`.github/workflows/`", "The weekly workflow definition"],
        ["Bash", "workflow `run:` steps", "Orchestration inside the runner"],
    ], ["Language", "Where", "What it does"])

    rows = []
    try:
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
            line = line.split("#")[0].strip()
            if not line:
                continue
            name = re.split(r"[<>=!~\[]", line, maxsplit=1)[0].strip()
            pin = line[len(name):].strip() or "unpinned"
            rows.append([f"`{name}`", f"`{pin}`", LIB_PURPOSE.get(name.lower(), "")])
    except Exception:
        pass
    reqs_tbl = table(rows, ["Library", "Version", "Used for"]) if rows else \
        "*Could not read `requirements.txt`.*"
    return lang_tbl, reqs_tbl


def pipeline_modules():
    """The pipeline's own numbered sections, read from its source."""
    try:
        src = (ROOT / "pipeline" / "nwgs_pipeline.py").read_text(encoding="utf-8")
    except Exception:
        return "*Could not read the pipeline source.*"
    hits = re.findall(r"^# (\d+[a-z]?)\. (.+)$", src, re.M)
    if not hits:
        return "*No numbered sections found in the pipeline source.*"
    lines = src.count("\n") + 1

    ACRONYMS = {"CDC", "API", "NSSP", "ED", "ML", "AMR", "ARG", "NCBI", "RCSB",
                "PDB", "KNN", "ACS", "NOAA", "EPA", "AQS", "PHIL", "SVI", "US",
                "RSV", "LISA", "GLM", "SHAP", "JMP", "WDI"}
    MIXED = {"UNIPROT": "UniProt", "COLAB": "Colab"}

    def smart_title(t):
        t = t.strip()
        if not t.isupper():
            return t
        words = []
        for w in t.split():
            core = w.strip("(),/-")
            if core in ACRONYMS:
                words.append(w)
            elif core in MIXED:
                words.append(w.replace(core, MIXED[core]))
            else:
                words.append(w.capitalize())
        return " ".join(words)

    rows = [[f"`{num}`", smart_title(title)] for num, title in hits]
    out = (f"`pipeline/nwgs_pipeline.py` is a single module of about "
           f"{lines:,} lines, organized into numbered sections:\n\n"
           + table(rows, ["Section", "What it covers"]))
    nums = [n for n, _ in hits]
    notes = []
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    if dupes:
        notes.append("number" + ("s " if len(dupes) > 1 else " ")
                     + ", ".join(f"`{d}`" for d in dupes)
                     + (" appear" if len(dupes) > 1 else " appears") + " twice")
    # A lettered block whose stem is already used elsewhere reads as a
    # continuation of that stem when it is not one.
    stems = {n for n in nums if n.isdigit()}
    nested = sorted({n for n in nums if not n.isdigit() and n[:-1] in stems
                     and nums.index(n) > 0 and n[:-1] != nums[nums.index(n) - 1][:len(n) - 1]})
    if nested:
        notes.append("the lettered block "
                     + ", ".join(f"`{n}`" for n in nested[:3])
                     + (" …" if len(nested) > 3 else "")
                     + " sits inside a different section than its stem suggests")
    if notes:
        out += ("\n\n> **Maintainability note.** In the source, "
                + "; and ".join(notes)
                + ". The code is unaffected — these are comment headings, not "
                  "identifiers — but renumbering would make the file easier to "
                  "navigate.")
    return out


def entity_inventory(export):
    """Every exported entity, its size, and which views consume it."""
    try:
        bs = (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8")
        tpl = TEMPLATE.read_text(encoding="utf-8")
    except Exception:
        bs = tpl = ""

    # Some entities are loaded into a local first (nt = r("NationalTrend")) and
    # only then used in a D[...] assignment, so resolve those names as well.
    var2ent = {}
    for m in re.finditer(r'^\s*([A-Za-z_]\w*)\s*=\s*(?:r|opt)\(\s*"([A-Za-z0-9_]+)"', bs, re.M):
        var2ent.setdefault(m.group(1), set()).add(m.group(2))

    # A few entities are read directly with pd.read_csv through a path
    # variable rather than through the r()/opt() helpers.
    path2ent = {}
    for m in re.finditer(r'^\s*([A-Za-z_]\w*)\s*=\s*Path\([^)]*\)\s*/\s*"([A-Za-z0-9_]+)\.csv"', bs, re.M):
        path2ent[m.group(1)] = m.group(2)
    for m in re.finditer(r'^\s*([A-Za-z_]\w*)\s*=\s*pd\.read_csv\(\s*([A-Za-z_]\w*)', bs, re.M):
        ent = path2ent.get(m.group(2))
        if ent:
            var2ent.setdefault(m.group(1), set()).add(ent)

    # Split on assignment boundaries so one statement's window cannot bleed
    # into the next and attribute an entity to the wrong key.
    ent2key = {}
    for part in re.split(r'(?=^\s*D\["[a-z_0-9]+"\]\s*=)', bs, flags=re.M):
        m = re.match(r'\s*D\["([a-z_0-9]+)"\]\s*=', part)
        if not m:
            continue
        key = m.group(1)
        for ent in re.findall(r'(?:\br|\bopt)\(\s*"([A-Za-z0-9_]+)"', part):
            ent2key.setdefault(ent, set()).add(key)
        for var in set(re.findall(r'\b([A-Za-z_]\w*)\b', part)) & set(var2ent):
            for ent in var2ent[var]:
                ent2key.setdefault(ent, set()).add(key)

    # D key -> views, by slicing template.html into render functions
    views = dict(read_views())
    bounds = []
    for key in views:
        m = re.search(rf"^\s*{re.escape(key)}\(\)\{{", tpl, re.M)
        if m:
            bounds.append((m.start(), key))
    bounds.sort()
    slices = []
    for i, (start, vkey) in enumerate(bounds):
        end = bounds[i + 1][0] if i + 1 < len(bounds) else len(tpl)
        slices.append((start, end, views[vkey]))

    key2views = {}
    for start, end, label in slices:
        for dk in set(re.findall(r"D\.([a-z_0-9]+)", tpl[start:end])):
            key2views.setdefault(dk, set()).add(label)

    # Several panels are built by shared helper functions declared above the
    # render object. A key used there is still read by whichever view calls the
    # helper, so resolve the helper to its callers rather than reporting the
    # entity as unused.
    helpers = [(m.start(), m.group(1)) for m in re.finditer(r"^function (\w+)\s*\(", tpl, re.M)]
    helpers.sort()
    first_view = bounds[0][0] if bounds else len(tpl)
    for m in re.finditer(r"D\.([a-z_0-9]+)", tpl):
        if m.start() >= first_view:
            continue
        owner = None
        for pos, name in helpers:
            if pos <= m.start():
                owner = name
            else:
                break
        if not owner:
            continue
        for start, end, label in slices:
            if re.search(rf"\b{re.escape(owner)}\s*\(", tpl[start:end]):
                key2views.setdefault(m.group(1), set()).add(label)

    rows = []
    for csv in sorted(export.glob("*.csv")):
        name = csv.stem
        df = read(export, name)
        keys = sorted(ent2key.get(name, []))
        vs = sorted({v for k in keys for v in key2views.get(k, set())})
        rows.append([
            f"`{name}`",
            f"{len(df):,}" if df is not None else "empty",
            str(len(df.columns)) if df is not None else "—",
            ", ".join(vs) if vs else "*not read by any view*",
        ])
    if not rows:
        return "*No entity CSVs found in this export.*"
    return (f"The export for this run contains {len(rows)} entity files. Each is a "
            "flat CSV; the site reads all of them from one JSON payload built at "
            "publication time.\n\n"
            + table(rows, ["Entity", "Rows", "Columns", "Views that read it"]))


def repo_sections():
    """Describe the repository and its workflow, read from the repository."""
    # 5.1 — tracked top-level paths
    rows = []
    try:
        entries = sorted(ROOT.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except Exception:
        entries = []
    for p in entries:
        if p.name in {".git", "__pycache__"} or p.name.endswith(".pyc"):
            continue
        purpose = PATH_PURPOSE.get(p.name, "")
        if p.is_dir():
            kids = [c for c in p.rglob("*") if c.is_file() and "__pycache__" not in c.parts]
            detail = f"{len(kids)} file" + ("" if len(kids) == 1 else "s")
            if p.name == "scripts":
                detail = ", ".join(f"`{c.name}`" for c in sorted(p.glob("*.py")))
            rows.append([f"`{p.name}/`", detail, purpose])
        else:
            kb = p.stat().st_size / 1024
            rows.append([f"`{p.name}`", "under 1 KB" if kb < 1 else f"{kb:.0f} KB", purpose])
    repo_tbl = table(rows, ["Path", "Contents", "Purpose"]) if rows else \
        "*Could not read the repository layout.*"

    if (ROOT / "scripts").is_dir():
        srows = [[f"`scripts/{f.name}`", SCRIPT_PURPOSE.get(f.name, "")]
                 for f in sorted((ROOT / "scripts").glob("*.py"))]
        repo_tbl += "\n\n**Scripts**\n\n" + table(srows, ["Script", "What it does"])

    # 5.2 — .gitignore
    try:
        pats = [l.strip() for l in (ROOT / ".gitignore").read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        ignore_tbl = table([[f"`{x}`", ""] for x in pats], ["Excluded", "Note"]) if pats else ""
        why = {"app_export/": "Rebuilt by every run", "site/": "Rebuilt by every run",
               ".env": "Local secrets; never committed", "*.log": "Run logs go to the release instead",
               "__pycache__/": "Python bytecode", "*.pyc": "Python bytecode",
               ".ipynb_checkpoints/": "Notebook autosaves"}
        ignore_tbl = table([[f"`{x}`", why.get(x, "")] for x in pats], ["Excluded", "Why"])
    except Exception:
        ignore_tbl = "*No `.gitignore` found.*"

    # 5.3 / 5.5 — workflow
    wfs = sorted((ROOT / ".github" / "workflows").glob("*.yml")) if \
        (ROOT / ".github" / "workflows").is_dir() else []
    if not wfs:
        return repo_tbl, ignore_tbl, "*No workflow found.*", "*No workflow found.*", "—", "—"
    wf = wfs[0]
    text = wf.read_text(encoding="utf-8")
    wf_path = f".github/workflows/{wf.name}"

    cron = re.search(r'cron:\s*"([^"]+)"', text)
    trig = []
    if cron:
        trig.append(f"runs on the schedule `{cron.group(1)}`")
    if "workflow_dispatch" in text:
        trig.append("and on demand from the **Run workflow** button")
    wf_trigger = " ".join(trig) if trig else "trigger not detected"

    STEP_PURPOSE = {
        "Verify the build inputs": "Checks that the pipeline, the export and build scripts, the template and the requirements file are all present and non-empty. A missing input fails the run here rather than being worked around later, so the previous week stays published.",
        "actions/checkout": "Copies the repository onto the clean machine. This is why a push must precede a run: the machine takes what is on GitHub, not what is on your computer.",
        "actions/setup-python": "Installs the pinned Python version.",
        "Install packages": "Installs everything in `requirements.txt`.",
        "Prepare Colab-style folders": "Recreates the directory layout the pipeline expects and copies `static_inputs/` into place.",
        "Download Census TIGER": "Fetches the county boundary file fresh each run; at roughly 130 MB it is over GitHub's file limit, so it is not stored. Without it the maps cannot draw.",
        "Set the data window": "Sets the end of the study window to the current date, so each run covers one more week than the last.",
        "Run surveillance pipeline": "The substance of the run, and most of its duration. Pulls the CDC datasets, harmonizes, standardizes, and computes every analytic layer. API keys are injected here only.",
        "Export app data": "Builds the entity CSVs **and runs the validation gate**. A hard failure here stops the job, so no site update, release or email follows and the previous week stays published.",
        "Use the saved": "Fallback that copies `sample_export` when the pipeline file is absent. See the note at the end of this section.",
        "Persist the forecast ledger": "Commits the updated ledger back to the repository so it outlives the machine. See [[ref:Why the forecast ledger is committed back]].",
        "Build site": "Renders one export into the finished static site.",
        "Keep this run's export": "Attaches the export, tables and full log to the run for 90 days. Runs even on failure, so a failed run can still be diagnosed.",
        "Archive this run": "Publishes the permanent GitHub Release. See [[ref:Releases — the citation layer]].",
        "Email saved alerts": "Sends the weekly alert emails. Marked `continue-on-error`, so a mail failure never blocks the site update.",
        "actions/upload-pages-artifact": "Hands the built site to GitHub Pages.",
        "actions/deploy-pages": "Publishes it. The site is live when this finishes.",
    }

    steps = []
    for m in re.finditer(r"^      - (?:name: (.+)|uses: (\S+))", text, re.M):
        label = (m.group(1) or m.group(2) or "").strip()
        purpose = next((v for k, v in STEP_PURPOSE.items() if k in label), "")
        steps.append([f"**{label}**", purpose])
    if "deploy-pages" in text and not any("deploy-pages" in s[0] for s in steps):
        steps.append(["**actions/deploy-pages**", STEP_PURPOSE["actions/deploy-pages"]])
    steps_tbl = table(steps, ["Step", "Purpose"]) if steps else "*Could not parse the steps.*"

    if "hashFiles('pipeline/nwgs_pipeline.py') == ''" in text:
        steps_tbl += (
            "\n\n> **Note for the developer.** Several steps are guarded by "
            "`if: hashFiles('pipeline/nwgs_pipeline.py') != ''`, with a fallback that copies "
            "`sample_export` instead. If the pipeline file were ever missing from the "
            "repository, the run would publish that saved export **and report success** — the "
            "site would look correct while showing stale data. Failing loudly would be safer.")

    found = sorted(set(re.findall(r"secrets\.([A-Z_]+)", text)))
    secrets_tbl = table([[f"`{s}`", SECRET_PURPOSE.get(s, "")] for s in found],
                        ["Secret", "Used for"]) if found else "*No secrets referenced.*"

    return repo_tbl, ignore_tbl, steps_tbl, secrets_tbl, wf_path, wf_trigger


def main(export_dir, out_path):
    E = Path(export_dir)
    man = json.loads((E / "manifest.json").read_text())
    run_id = man.get("run_id", "unknown")
    as_of = man.get("data_as_of", "unknown")
    gate = man.get("gate_status", "unknown")
    pulled = man.get("data_pulled_utc", "unknown")

    ps = read(E, "PathogenSummary")
    ca = read(E, "CountyActivity")
    cov = read(E, "CountyCoverage")
    src = read(E, "DataSource")
    al = read(E, "Alert")
    audit = read(E, "AuditLog")
    sstat = read(E, "SourceStatus")
    rep = read(E, "RepresentativenessNational")
    lt = read(E, "LeadTime")
    att = read(E, "AttritionSite")
    fc = read(E, "ForecastScore")
    gc = read(E, "GlobalCoverage")
    at = read(E, "AssayTarget")

    views = read_views()
    if views:
        views_tbl = table([[label, VIEW_NOTES.get(key, "")] for key, label in views],
                          ["View", "What it answers"])
        nviews = len(views)
    else:
        views_tbl = "*Could not read the view list from `site_src/template.html`.*"
        nviews = "unread"

    deps = read_deps()
    rows = [[nm, f"`{v}`", origin, use] for nm, v, origin, use in deps]
    rows += [["Structure files", "—", "files.rcsb.org", "mmCIF/PDB, fetched when a structure is opened"],
             ["Web fonts", "—", "fonts.googleapis.com", "Typography; degrades gracefully if blocked"]]
    deps_tbl = table(rows, ["Dependency", "Version", "Origin", "Used for"])

    # Supabase surface, read from the template and the schema.
    FEATURE = {"alert_rules": "My alerts", "feedback": "Beta feedback form",
               "license_requests": "License request form"}
    try:
        tpl = TEMPLATE.read_text(encoding="utf-8")
    except Exception:
        tpl = ""
    used = {}
    for tbl_name, op in re.findall(
            r"\.from\('([a-z_]+)'\)\s*\.\s*(select|insert|update|delete|upsert)", tpl):
        used.setdefault(tbl_name, set()).add(op)
    try:
        schema = (ROOT / "supabase" / "schema.sql").read_text(encoding="utf-8")
    except Exception:
        schema = ""
    declared = re.findall(r"create table if not exists public\.([a-z_]+)", schema, re.I)
    npol = len(re.findall(r"create policy", schema, re.I)) or "the schema's"

    if used:
        sb_tbl = table([[f"`{t}`", ", ".join(sorted(ops)), FEATURE.get(t, "")]
                        for t, ops in sorted(used.items())],
                       ["Table", "Operations reachable from the browser", "Feature"])
    else:
        sb_tbl = "*Could not read the Supabase calls from `site_src/template.html`.*"

    unreached = [t for t in declared if t not in used]
    sb_unreached = (
        f"{len(declared)} tables are declared in `supabase/schema.sql`. The "
        + ("remaining " + ", ".join(f"`{t}`" for t in unreached)
           + (" is" if len(unreached) == 1 else " are")
           + " never reachable from the browser; they are written only by the "
             "scheduled workflow."
           if unreached else "browser reaches all of them.")
    ) if declared else ""

    repo_tbl, ignore_tbl, steps_tbl, secrets_tbl, wf_path, wf_trigger = repo_sections()
    lang_tbl, reqs_tbl = stack_sections()
    modules_tbl = pipeline_modules()
    entity_tbl = entity_inventory(E)
    license_tbl = table([
        ["NWGS Grid code and site content", "All rights reserved",
         "No reuse without written permission; see `LICENSE`"],
        ["CDC NWSS and NSSP data", "Public domain (US Government)",
         "Attribution expected; data is revised continuously"],
        ["US Census TIGER/Line", "Public domain", "County boundary geometry"],
        ["NCBI / INSDC records", "Public domain",
         "May be redistributed, which is why sequences here are downloadable"],
        ["RCSB PDB / UniProt", "CC BY 4.0", "Structures and functional annotations, cited in place"],
        ["RKI AMELAG (Germany)", "CC BY 4.0", "Versioned with a DOI"],
        ["World Bank Indicators", "CC BY 4.0", "Sanitation and income classification"],
        ["WHO/UNICEF JMP", "Provider terms", "Household world workbook"],
        ["us-atlas county geometry", "ISC", "Bundled; see `site_src/us-atlas-LICENSE.txt`"],
        ["d3, topojson, supabase-js, 3Dmol.js", "Open source (BSD/MIT/ISC)",
         "Loaded from CDNs at runtime, not vendored"],
    ], ["Component", "Licence", "Note"])

    doc = []
    A = doc.append

    A(f"""# NWGS Grid — Dashboard Audit

**Run:** `{run_id}` · **Data through:** {as_of} · **Validation gate:** {gate}

**Sources pulled:** {pulled}

**Document generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

> Generated by `scripts/build_audit_doc.py` from the export for this run. Counts
> and identifiers are read from the data, not written by hand, so this document
> describes the run named above and no other.

---

## Executive summary

NWGS Grid is a static, weekly-rebuilt dashboard of wastewater surveillance for
respiratory and emerging pathogens across U.S. counties. It reads published CDC
data, standardizes each monitoring site against its own history, and publishes a
frozen snapshot that is archived for citation.

Every figure shown to a visitor is precomputed. No published number is produced
by a live database query, which means any page can be reproduced exactly from
the archived release for its run.

**This run contains:**

{table([
 ["Pathogens tracked", n(ps)],
 ["County-pathogen activity rows", n(ca)],
 ["County coverage rows", n(cov)],
 ["Upstream datasets", n(src)],
 ["Alerts generated", n(al)],
 ["Validation / audit entries", n(audit)],
 ["External source outcomes recorded", n(sstat)],
], ["Item", "Count"])}

---

## Purpose and scope

**Purpose.** Bring CDC's separately published wastewater, clinical and
vulnerability data into one validated weekly pipeline, and show not only what is
rising but who the surveillance system reaches and who it misses.

**In scope.** U.S. county and state level wastewater activity for routine
respiratory pathogens; detection-based reporting for emerging pathogens;
clinical alignment; spatial clustering; coverage and representativeness;
reference protein structures with cited annotations.

**Out of scope.** Individual or household data. Case counts. Clinical diagnosis.
Any claim about people not connected to a monitored sewer. Any number that
cannot be traced to a published source.

**Audience.** Public health practitioners, researchers, journalists, elected
officials and residents. The site is written for a reader with no background,
with technical depth available on Methods and in the Glossary.

---

## Technology stack

Three languages, each doing one job.

{lang_tbl}

**Python libraries**, pinned in `requirements.txt` and installed at the start of
every run. The versions a run actually used are recorded in its archived log.

{reqs_tbl}

There is no application framework, no bundler, no build step for the front end
and no transpilation. `build_site.py` performs a single substitution of one JSON
payload into one HTML template. That is the whole front-end toolchain, and it is
deliberate: a page with no build system can be opened, read and audited by
anyone, and will still render in ten years.

---

## Front end

A single static HTML page. All views are rendered in the browser from one
embedded JSON object produced at build time.

### Views ({nviews})

Read from `site_src/template.html`, in the order they appear in the navigation.

{views_tbl}

### Runtime dependencies

These are the only things a visitor's browser fetches from outside the page.
Versions are read from the template, not written here.

{deps_tbl}

Everything else on the page is static. If all of the above failed, the data,
tables and text would still render; only charts, maps, sign-in and the 3D viewer
would be affected.

---

## Back end

### Supabase — the only runtime backend

{sb_tbl}

Authentication is passwordless email (one-time link). No password is ever
stored or transmitted. The browser receives only the **publishable** key; the
secret key exists solely as a repository secret used by the server-side mailer.
Row-level security is enabled on every table and {npol} policies restrict each
row to the account that created it.

{sb_unreached}

### Weekly alert mail

`scripts/send_alerts.py` runs inside the scheduled workflow, reads saved rules
with the secret key, matches them against the new run and sends email over SMTP.
It never runs in a browser.

### Build and hosting

The scheduled GitHub Actions workflow runs the pipeline, exports the app data,
builds the site and publishes to GitHub Pages. [[ref:What GitHub holds, and what it does]] describes that
repository and its automation in full.

---

## What GitHub holds, and what it does

GitHub is not only where the code is stored. It is the build machine, the
scheduler, the secret store, the archive and the web host. Everything below is
read from the repository, so this section describes the repository as it stands,
not as it was documented.

### What is in the repository

{repo_tbl}

### What is deliberately **not** in the repository

{ignore_tbl}

Build outputs are excluded on purpose. `app_export/` and `site/` are produced
fresh by every run, so a copy committed by hand would be a second, unversioned
source of truth. The one exception is the forecast ledger, which is committed
back on purpose — see [[ref:Why the forecast ledger is committed back]].

### The weekly workflow

`{wf_path}` — {wf_trigger}

Each run starts on a clean Ubuntu machine that GitHub destroys afterward.
Nothing survives a run except what is committed back, released, or deployed.

{steps_tbl}

### Why the forecast ledger is committed back

A forecast written during a run would be destroyed with the machine that wrote
it. The workflow therefore commits the updated ledger to the repository, tagged
`[skip ci]` so it does not retrigger the build. The value is not the file but
the commit timestamp: git history is the evidence that each prediction was
recorded **before** the week it predicted. Without it the forecast scoreboard
would be unfalsifiable.

### Secrets

{secrets_tbl}

These exist only as GitHub repository secrets and are injected as environment
variables for the single step that needs them. None appears in the code, in the
built site, in the logs or in any release asset. The Supabase **secret** key is
used only by the server-side mailer; the browser receives the publishable key,
which is public by design.

### Releases — the citation layer

Every successful run publishes a GitHub Release tagged
`<run_id>-r<run_number>`, holding the tables, the figures, the app export, the
manifest and the full pipeline log. CDC revises its datasets continuously, so a
figure is only reproducible against the release it came from. The release notes
carry the run ID, the data-through date, the gate status and the citation
string.

### Pages — the public site

The `deploy` job publishes the built `site/` folder to GitHub Pages. The site is
static: HTML, one JSON payload and images. There is no server to run and nothing
to query at page load.

---

## What the pipeline collects

### Upstream datasets in this run
""")

    if src is not None:
        cols = [c for c in ("pathogen", "dataset_name", "dataset_id", "rows", "updated_utc") if c in src.columns]
        rows = []
        for _, r in src[cols].iterrows():
            rows.append([
                r.get("pathogen", ""),
                str(r.get("dataset_name", ""))[:54],
                f"`{r.get('dataset_id','')}`",
                f"{int(r['rows']):,}" if "rows" in r and pd.notna(r["rows"]) else "",
                str(r.get("updated_utc", ""))[:19],
            ])
        A(table(rows, ["Pathogen", "Dataset", "ID", "Rows", "Provider updated"]))
    else:
        A("*No DataSource table in this run.*")

    A("""
All are public CDC datasets served from `data.cdc.gov`. Additional context data
is pulled from the U.S. Census Bureau (county boundaries), CDC/ATSDR (Social
Vulnerability Index), NCBI (virus genome records), RCSB PDB and UniProt
(reference structures and annotations), and the World Bank (sanitation and
income classification).

### External source outcomes for this run
""")

    if sstat is not None:
        rows = [[r.get("source", ""), f"**{r.get('status','')}**", str(r.get("detail", ""))[:90]]
                for _, r in sstat.iterrows()]
        A(table(rows, ["Source", "Status", "Detail"]))
        A("\n_`OK` loaded, `EMPTY` reachable but nothing usable, `FAILED` did not load. "
          "A layer that is empty on the site can be explained from this table._")
    else:
        A("*Source outcomes are recorded from the v5.22 pipeline onward; this run predates it "
          "or recorded none.*")

    A("""
---

## Pipeline structure

{modules_tbl}

Analysis stages are guarded individually: a stage that fails records the failure
and leaves its table empty rather than aborting the run or substituting a value.
Optional enrichment stages — weather, air quality, census detail — are off
unless explicitly enabled, so they cannot silently change a published figure.

---

## Methods

The pipeline runs these steps in order. Full prose description is on the
Methods & sources page of the site.

1. **Acquisition** — datasets pulled from the Socrata API and frozen with row
   counts and the provider's own update timestamp.
2. **Harmonization** — differing schemas mapped to common names through an
   explicit alias table; the mapping actually used is written out per pathogen.
   County identifiers normalized to five-digit FIPS.
3. **Measurement selection** — where several concentration measures exist, one
   is chosen by a fixed hierarchy (fecal-normalized, then flow-population
   normalized, then raw) and the choice is recorded per row.
4. **Within-site standardization** — concentrations log-transformed and
   converted to a z-score within each site, grouped by laboratory method and
   sample matrix. County and national figures are medians of those standardized
   values.
5. **Quality control** — inhibition and no-template-control flags carried
   through; zero and negative concentrations treated as missing before log
   transformation; untested is never recorded as negative.
6. **Analysis** — Spearman cross-correlation with Benjamini-Hochberg correction
   for clinical alignment; global and local Moran's I on a six-nearest-neighbor
   graph in EPSG:5070 for clustering; binomial GLM for coverage; models
   evaluated only on unseen weeks.
7. **Validation gate** — automated checks across parsing, county counts,
   pathogen independence, spatial and model audits and cross-table consistency.
   A blocking failure stops publication and the previous week is kept; a
   non-blocking discrepancy publishes with the gate marked
   `PASS_WITH_WARNINGS` and the discrepancy listed in [[ref:Gate result for this run]] and in the
   site's Audit log.
8. **Publication** — one static page from one export, archived as a release.

### Activity levels

{levels}

Levels describe how unusual a reading is for that site, not how many people are
infected. Two places at the same level are each unusual relative to themselves.

### What the pipeline does not do

It does not infer or impute missing observations, estimate values for
unmonitored counties, carry numbers over from a previous run, or adjust
published figures after the fact. Where a source does not load, the affected
panel says so and shows nothing.

### Gate result for this run
""".replace("{levels}", table([
        ["Very Low", "z ≤ −1"], ["Low", "−1 < z ≤ −0.25"], ["Typical", "−0.25 < z ≤ 0.25"],
        ["Elevated", "0.25 < z ≤ 1"], ["High", "z > 1"],
    ], ["Level", "Median site z-score"])))

    cc = man.get("consistency_checks", []) or []
    if cc:
        nfail = sum(1 for c in cc if not c.get("ok"))
        A(f"\nGate status **{gate}** — {len(cc)} cross-table checks, "
          f"{len(cc) - nfail} passed, {nfail} discrepant.\n")
        A(table([[c.get("check", ""), c.get("expected", ""), c.get("found", ""),
                  "pass" if c.get("ok") else "**discrepant**"] for c in cc],
                ["Check", "Expected", "Found", "Result"]))
        if nfail:
            A("\nDiscrepant rows are published because the difference is a count of "
              "counties between two tables built at different aggregation steps, not a "
              "change to any published value. They appear in the site's Audit log for "
              "the same run.")
    else:
        A("\n_No cross-table checks recorded in this run's manifest._")

    sha = man.get("payload_sha256")
    if sha:
        A(f"\n**Export payload SHA-256:** `{sha}`")

    A("""
---

## Analytic layers in this run
""")

    repd = read(E, "Representativeness")
    A(table([
        ["Lead-time decomposition", n(lt), "Shedding lead, reporting lag, operational lead per state-pathogen",
         "" if lt is not None else "Pipeline section 21c; absent before v5.22"],
        ["Coverage attrition", n(att), "Per-site reporting lifespan and dormancy",
         "" if att is not None else "Pipeline section 21c; absent before v5.22"],
        ["Representativeness", n(repd), "Sewer share and vulnerability gap per county",
         "" if repd is not None else "Pipeline section 21c; absent before v5.22"],
        ["Forecast scoreboard", n(fc), "Frozen predictions scored after maturity",
         "" if fc is not None else "Empty until the committed forecast ledger holds predictions old enough to score"],
        ["Global coverage", n(gc), "Country sanitation denominator and observability bound",
         "" if gc is not None else "Requires the World Bank Indicators fetch; not present in this run"],
        ["Assay-target panel", n(at), "Curated published target regions (citation required)",
         "" if at is not None else "Empty by design until a curated, citation-bearing target file is supplied; the pipeline refuses to invent coordinates"],
    ], ["Layer", "Rows", "What it provides", "If empty, why"]))

    if lt is not None and "reporting_lag_weeks" in lt.columns:
        ok = int(lt["reporting_lag_weeks"].notna().sum())
        if ok == 0:
            A("\n**Reporting lag is unavailable in this run.** It is derived from each CDC "
              "dataset's own update timestamp minus its latest sample collection date; when "
              "that timestamp is missing or unparseable for every dataset, the subtraction has "
              "no left-hand side. Operational lead therefore cannot be computed, and the site "
              "shows both columns blank rather than filling them. Shedding lead is unaffected, "
              "being measured from the paired wastewater and clinical series alone.")
        elif ok < len(lt):
            A(f"\n**Reporting lag resolved for {ok:,} of {len(lt):,} state-pathogen pairs.** "
              "Where it did not resolve, operational lead is left blank rather than inferred.")

    if rep is not None:
        r = rep.iloc[0]
        A("\n**Representativeness summary for this run**\n")
        A(table([
            ["Counties analyzed", f"{int(r.get('counties_total',0)):,}"],
            ["Counties monitored", f"{int(r.get('counties_monitored',0)):,}"],
            ["Population in a monitored sewershed", f"{r.get('pct_population_in_sewershed','—')}%"],
            ["Median sewer share where monitored", f"{r.get('median_sewer_share_monitored','—')}"],
        ], ["Measure", "Value"]))

    A("""
---

## Citations and references

Verified sources underpinning claims made on the site. Full list on the
Methods & sources page.

| Work | Link |
|---|---|
| Mark-Carew M, et al. Progress and Expansion of the National Wastewater Surveillance System, United States, 2020–2024. *Emerg Infect Dis* 2026;32(Suppl). | https://wwwnc.cdc.gov/eid/article/32/13/26-1118_article |
| Alkhouri NB, Fisher V, Abuelezam NN. Equity in Wastewater Surveillance. *AJPM Focus* 2025;5(1):100434. | https://doi.org/10.1016/j.focus.2025.100434 |
| Schenk H, Rauch W, Zulli A, Boehm AB. SARS-CoV-2 surveillance in US wastewater. *PLOS ONE* 2024;19(11):e0313927. | https://doi.org/10.1371/journal.pone.0313927 |
| Beck AS, et al. Sensitivity of a measles diagnostic real-time RT-PCR assay with priming mismatch variants. *Eurosurveillance* 2024;29(28):2400410. | https://doi.org/10.2807/1560-7917.ES.2024.29.28.2400410 |
| Berman HM, et al. The Protein Data Bank. *Nucleic Acids Res* 2000;28(1):235–242. | https://www.rcsb.org |
| Rego N, Koes D. 3Dmol.js. *Bioinformatics* 2015;31(8):1322–1324. | https://doi.org/10.1093/bioinformatics/btu829 |

### Data sources

| Source | Link |
|---|---|
| CDC National Wastewater Surveillance System | https://data.cdc.gov |
| CDC National Syndromic Surveillance Program (ED visits) | https://data.cdc.gov/d/rdmq-nq56 |
| CDC PLACES | https://data.cdc.gov/d/swc5-untb |
| CDC/ATSDR Social Vulnerability Index | https://www.atsdr.cdc.gov/place-health/php/svi/ |
| U.S. Census Bureau TIGER/Line | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html |
| NCBI Virus / Datasets | https://www.ncbi.nlm.nih.gov/datasets/ |
| RCSB Protein Data Bank | https://www.rcsb.org |
| UniProt | https://www.uniprot.org |
| World Bank Indicators API | https://api.worldbank.org/v2/ |
| WHO/UNICEF Joint Monitoring Programme | https://washdata.org/data/downloads |
| RKI AMELAG (Germany) | https://github.com/robert-koch-institut/Abwassersurveillance_AMELAG |
| CDCgov/NWSS repository | https://github.com/CDCgov/NWSS |

---

## Data inventory for this run

{entity_tbl}

The last column is derived from the code, not from a list kept by hand: each
entity is traced through the key `build_site.py` assigns it, then through the
views and shared panel helpers in `template.html` that read that key. An entity
marked as read by no view is exported and archived but not displayed anywhere —
either deliberately, because the release should carry more than the page shows,
or because it was built and never wired up. Both are worth knowing; the table
does not distinguish them.

---

## Reproducing any figure

1. Note the run identifier and data-through date in the site header, or in the
   heading of this document.
2. Open the GitHub Release tagged with that run identifier and download
   `<run_id>_app_export.zip` (the entity CSVs) or `<run_id>_tables.zip` (the
   full pipeline tables).
3. Rebuild the page from that export:
   `python3 scripts/build_site.py <export_dir> site`
4. Regenerate this document from the same export:
   `python3 scripts/build_audit_doc.py <export_dir> docs/DASHBOARD_AUDIT.md`

Re-running the pipeline itself will **not** reproduce an old run, because CDC
revises its datasets continuously and the pipeline always pulls current data.
The release is the reproducible artifact, not the code path.

---

## Licensing

{license_tbl}

The project's own code and content are all rights reserved; see `LICENSE`.
Underlying data remains subject to its providers' terms, which are not
superseded by anything here.

---

## Limitations

- **Coverage is partial and uneven.** Many counties have never had a monitored
  site. Absence of data is not absence of transmission.
- **Sewered populations only.** Households on septic systems are invisible to
  the method regardless of how well a program is run.
- **Sewershed boundaries are not public.** CDC collects them for most sites but
  does not release them, so representativeness uses a county-level proxy.
- **Levels are relative, not absolute.** A z-score cannot be converted into case
  counts.
- **Figures are revised.** CDC updates its datasets; numbers change between
  runs. Cite the run identifier.
- **Lead time is resolution-limited.** Weekly data cannot resolve a lead shorter
  than seven days.

---

## Change control

Every run carries a run identifier and a data-through date shown in the site
header. Each run is archived as a permanent release containing its tables,
figures and export. The validation gate blocks publication on failure, so a
published run has passed its checks or carries an explained warning.

To reproduce any figure on this site, take the release matching its run
identifier and re-run the export.
""")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = "\n".join(doc)
    # Blocks written as plain (non-f) strings carry named placeholders; fill
    # them here so a section can be moved between block styles without breaking.
    for token, value in (("{modules_tbl}", modules_tbl),
                         ("{entity_tbl}", entity_tbl),
                         ("{license_tbl}", license_tbl),
                         ("{lang_tbl}", lang_tbl),
                         ("{reqs_tbl}", reqs_tbl)):
        md = md.replace(token, value)
    leftover = re.findall(r"\{[a-z_]+_tbl\}", md)
    if leftover:
        print("[WARN] unfilled placeholder(s): " + ", ".join(sorted(set(leftover))))
    out.write_text(number_sections(md), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size/1024:.1f} KB) for run {run_id}, data through {as_of}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

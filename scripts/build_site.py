#!/usr/bin/env python3
"""
Build the static NWGS Grid site from one app export.

    python3 scripts/build_site.py <EXPORT_DIR> <SITE_DIR>

EXPORT_DIR is the output of scripts/nwgs_app_export.py.
Writes SITE_DIR/index.html (data and county map embedded) and SITE_DIR/data.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "site_src" / "template.html"
TOPO = ROOT / "site_src" / "counties-albers-10m.json"


def R(x, n=3):
    return None if x is None or pd.isna(x) else round(float(x), n)


def recs(df, drop=("run_id", "data_as_of")):
    df = df.drop(columns=[c for c in drop if c in df.columns])
    return json.loads(df.replace({np.nan: None}).to_json(orient="records"))


def main(export_dir, site_dir):
    E, out = Path(export_dir), Path(site_dir)
    out.mkdir(parents=True, exist_ok=True)
    r = lambda n: pd.read_csv(E / f"{n}.csv", dtype={"county_fips": str}, low_memory=False)

    D = {}
    D["run"] = json.loads(r("PipelineRun").replace({np.nan: None}).to_json(orient="records"))[0]
    D["sources"] = recs(r("DataSource")[["pathogen", "dataset_id", "dataset_name", "rows", "updated_utc", "source_url"]])
    D["summary"] = recs(r("PathogenSummary"))

    nt = r("NationalTrend")
    D["trend"] = {p: [[w, R(z)] for w, z in zip(q.week_end, q.median_site_z)] for p, q in nt.groupby("pathogen")}
    et = r("EmergingTrend")
    D["emerging"] = {p: [[w, R(z, 4), int(n)] for w, z, n in zip(q.week_end, q.detection_rate, q.n_sites_tested)]
                     for p, q in et.groupby("pathogen")}

    ca, cc = r("CountyActivity"), r("CountyCoverage")
    names = {}
    for f, n, s in list(zip(cc.county_fips, cc.county_name, cc.state_code)) + list(zip(ca.county_fips, ca.county_name, ca.state_code)):
        if isinstance(n, str):
            names[f] = [n, s]
    D["names"] = names
    D["activity"] = {p: {f: [R(z), int(n)] for f, z, n in zip(q.county_fips, q.activity_z, q.n_sites)}
                     for p, q in ca.groupby("pathogen")}
    D["activity_end"] = ca.activity_end_week.max()

    cl = r("CountyCluster")
    D["clusters"] = {p: dict(zip(q.county_fips, q.lisa_cluster)) for p, q in cl.groupby("pathogen")}
    cov = (cc[cc.pathogen.isin(["SARS-CoV-2", "RSV", "Influenza A"])]
           .groupby("county_fips").agg(w=("n_weeks", "max"), ready=("analysis_ready", "max"), svi=("svi", "first"))
           .reset_index())
    D["coverage"] = {f: [int(w), bool(rd), R(s)] for f, w, rd, s in zip(cov.county_fips, cov.w, cov.ready, cov.svi)}

    D["spatial"] = recs(r("SpatialSummary"))
    D["statelag"] = recs(r("StateLag"))
    D["seasonal"] = recs(r("SeasonalPeak"))
    D["variability"] = recs(r("SeasonalVariability"))
    sps = r("SeasonalPeakState")
    by = sps.groupby("pathogen").agg(n=("season", "size"), flagged=("implausible_lead_flag", "sum")).reset_index()
    D["state_seasons"] = {"n": len(sps), "flagged": int(sps.implausible_lead_flag.sum()), "by": recs(by)}
    D["equity"] = recs(r("EquitySummary"))
    D["models"] = recs(r("ModelPerformance"))
    D["shap"] = recs(r("ShapFeature")[["pathogen", "model", "feature", "rank", "mean_abs_shap"]])
    D["amr"] = recs(r("AmrTarget"))
    D["amr_state"] = recs(r("AmrState")[["state", "state_code", "sites", "mean_detection_rate_pct", "unique_site_population_sum"]])
    D["genomic"] = recs(r("GenomicSummary"))
    D["genomic_year"] = recs(r("GenomicByYear"))
    gr = r("GenomicRecord")
    D["genomic_hosts"] = {p: q.host.fillna("Not reported").value_counts().head(4).to_dict() for p, q in gr.groupby("pathogen")}
    D["genomic_places"] = {p: q.geographic_location.fillna("Not reported").value_counts().head(4).to_dict() for p, q in gr.groupby("pathogen")}
    D["structures"] = recs(r("ProteinStructure").drop(columns=["image_url"], errors="ignore"))
    D["tn_county"] = recs(r("TennesseeCounty"))
    D["tn_align"] = recs(r("TennesseeAlignment"))
    D["tn_equity"] = recs(r("TennesseeEquity"))
    D["tn_seasonal"] = recs(r("TennesseeSeasonal"))
    D["audit"] = recs(r("AuditLog")[["component", "status", "detail", "source"]])
    D["alerts"] = recs(r("Alert")[["alert_type", "severity", "pathogen", "geography", "message", "evidence"]])

    data = json.dumps(D, separators=(",", ":"), allow_nan=False)
    (out / "data.json").write_text(data)
    html = TEMPLATE.read_text().replace("__DATA__", data.replace("</", "<\\/")).replace("__TOPO__", TOPO.read_text())
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>[hidden]{display:none!important}body{margin:0}</style></head><body>' + html + "</body></html>")
    (out / "index.html").write_text(page)
    print(f"Built {out/'index.html'} ({len(page)/1e6:.2f} MB), run {D['run']['run_id']}, data through {D['run']['data_as_of']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

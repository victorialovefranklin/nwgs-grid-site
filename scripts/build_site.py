#!/usr/bin/env python3
"""
Build the static NWGS Grid site from one app export.
Author: Victoria Love Franklin — Ph.D. Data Science Student · GIS · AI & ML · Developer · Published Researcher
Copyright © 2026 Victoria Love Franklin. All rights reserved. See LICENSE.


    python3 scripts/build_site.py <EXPORT_DIR> <SITE_DIR>

EXPORT_DIR is the output of scripts/nwgs_app_export.py.
Writes SITE_DIR/index.html (data and county map embedded) and SITE_DIR/data.json.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "site_src" / "template.html"
TOPO = ROOT / "site_src" / "counties-albers-10m.json"
SUPA = ROOT / "site_src" / "supabase.json"   # public project URL + publishable key (safe to publish)


def R(x, n=3):
    return None if x is None or pd.isna(x) else round(float(x), n)


def recs(df, drop=("run_id", "data_as_of")):
    df = df.drop(columns=[c for c in drop if c in df.columns])
    return json.loads(df.replace({np.nan: None}).to_json(orient="records"))


def D_summary_latest(ps):
    """Most recent sample date across pathogens (the analysis window can end later than the last sample)."""
    s = pd.to_datetime(ps.get("latest_observation"), errors="coerce").dropna() if "latest_observation" in ps else pd.Series(dtype="datetime64[ns]")
    return s.max() if len(s) else None


def copy_assets(out):
    """Copy site images, the custom-domain file, and (when the pipeline ran
    here) small copies of its rendered protein structures."""
    import shutil
    img = ROOT / "site_src" / "img"
    if img.exists():
        shutil.copytree(img, out / "img", dirs_exist_ok=True)
    # GitHub Pages reads the custom domain from a CNAME file in the published
    # output. Without this copy the domain is cleared on every deploy and the
    # site silently reverts to the github.io address.
    cname = ROOT / "site_src" / "CNAME"
    if cname.exists():
        shutil.copyfile(cname, out / "CNAME")
        print(f"Custom domain: {cname.read_text(encoding='utf-8').strip()}")
    # .nojekyll stops GitHub Pages running Jekyll, which would drop any file
    # or folder whose name begins with an underscore.
    (out / ".nojekyll").write_text("", encoding="utf-8")
    sdir = os.getenv("NWGS_STRUCTURE_DIR")
    if sdir and Path(sdir).exists():
        from PIL import Image
        dest = out / "img" / "structures"
        dest.mkdir(parents=True, exist_ok=True)
        for f in Path(sdir).glob("ProteinStructure_*.png"):
            im = Image.open(f).convert("RGB")
            im.thumbnail((640, 640))
            im.save(dest / (f.stem.replace("ProteinStructure_", "") + ".png"), optimize=True)


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
    ec_path = Path(export_dir) / "EmergingCounty.csv"
    if ec_path.exists():
        ec = pd.read_csv(ec_path, dtype={"county_fips": str})
        ec["county_fips"] = ec["county_fips"].str.zfill(5)
        for f, n, s in zip(ec.county_fips, ec.county_name, ec.state_code):
            if isinstance(n, str) and f not in names:
                names[f] = [n, s]
        D["emerging_county"] = {p: {f: [int(t), int(d), (str(l)[:10] if isinstance(l, str) else None)]
                                    for f, t, d, l in zip(q.county_fips, q.n_sites_tested, q.n_sites_detected, q.last_detected_week)}
                                for p, q in ec.groupby("pathogen")}
        D["emerging_window_end"] = str(ec.window_end_week.max())[:10]
    else:
        D["emerging_county"] = None

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
    D["structures"] = recs(r("ProteinStructure"))
    sr_path = Path(export_dir) / "StructuralRegion.csv"
    if sr_path.exists():
        sr_all = pd.read_csv(sr_path)
        # The page shows only regions that could be placed on this structure's
        # own residue numbering, but a count of those alone is unreadable: a
        # reviewer cannot tell whether it is all of UniProt's annotations or
        # some fraction. Carry the denominator and the reason for each
        # omission, and keep the two reasons apart, because they are not the
        # same claim. NOT_IN_STRUCTURE is a fact about the deposited model:
        # UniProt annotates those residues, this entry does not resolve them.
        # NO_ALIGNMENT is a limitation of our own mapping: no alignment was
        # returned, so nothing can be said either way. Reporting the second
        # as the first would dress a failed lookup up as biology.
        if "mapping_status" in sr_all:
            ms = sr_all["mapping_status"].astype(str)
            D["regions_counts"] = {
                p: {"total": int(len(q)),
                    "mapped": int(q["mapping_status"].astype(str).eq("MAPPED").sum()),
                    "not_in_structure": int(q["mapping_status"].astype(str).eq("NOT_IN_STRUCTURE").sum()),
                    "no_alignment": int(q["mapping_status"].astype(str).eq("NO_ALIGNMENT").sum())}
                for p, q in sr_all.groupby("pdb_entry_id")
            }
            sr = sr_all[ms.eq("MAPPED")]
        else:
            D["regions_counts"] = {}
            sr = sr_all
        cols = ["feature_type", "feature_description", "uniprot_accession", "uniprot_start", "uniprot_end",
                "pdb_chain", "pdb_start", "pdb_end", "evidence_count", "annotation_source_url"]
        D["regions"] = {p: recs(q[[c for c in cols if c in q.columns]])
                        for p, q in sr.groupby("pdb_entry_id")} if len(sr) else {}
        # Review status is a property of the whole imported set, so read it
        # from the full table rather than from the mapped subset, which can be
        # empty in a run where no alignment was returned.
        D["regions_review"] = (str(sr_all["expert_review_status"].iloc[0])
                               if len(sr_all) and "expert_review_status" in sr_all else None)
    else:
        D["regions"] = {}
        D["regions_counts"] = {}
        D["regions_review"] = None
    # ------------------------------------------------------------
    # Surveillance-gap analytics (pipeline section 21c / export v5.22+).
    # Every one is optional. A missing table yields None, and the view
    # says plainly that the layer has not populated yet rather than
    # rendering an empty chart that looks like a finding of zero.
    # ------------------------------------------------------------
    def opt(name, cols=None, how="records"):
        p = Path(export_dir) / f"{name}.csv"
        if not p.exists():
            return None
        try:
            df = pd.read_csv(p, low_memory=False)
        except Exception as exc:
            print(f"[WARN] {name}.csv unreadable ({exc}); view will report it as unavailable.")
            return None
        if not len(df):
            return None
        if cols:
            df = df[[c for c in cols if c in df.columns]]
        return recs(df) if how == "records" else json.loads(
            df.replace({np.nan: None}).to_json(orient="records"))[0]

    D["leadtime"] = opt("LeadTime", [
        "pathogen", "state_code", "shedding_lead_weeks", "reporting_lag_weeks",
        "operational_lead_weeks", "usable", "lead_supported", "interpretation",
        "spearman_r", "spearman_p_fdr", "paired_weeks", "last_sample_week", "dataset_updated"])
    D["leadtime_national"] = opt("LeadTimeNational")
    D["attrition_sites"] = opt("AttritionSite", [
        "site_id", "state_code", "county_fips", "county_name", "first_week", "last_week",
        "n_weeks", "population_served", "weeks_since_last", "status", "went_dormant_week",
        "lifespan_weeks", "as_of_week", "dormant_threshold_weeks"])
    D["attrition_yearly"] = opt("AttritionYearly")
    D["attrition_vuln"] = opt("AttritionVulnerability")
    D["forecast_board"] = opt("ForecastScore")
    D["forecast_records"] = opt("ForecastRecord")
    D["representativeness"] = opt("Representativeness", [
        "county_fips", "county_name", "state_code", "n_sites", "sewer_population",
        "county_population", "sewer_share", "sewershed_crosses_county", "svi",
        "state_monitored_svi", "svi_gap", "representativeness", "representativeness_tier"])
    D["rep_national"] = opt("RepresentativenessNational", how="first")
    D["assay_targets"] = opt("AssayTarget")
    # Monitoring status, packed as {fips: [status, sites, sewered_pop,
    # sewer_share, sewered_svi]} so the county lookup can answer instantly
    # without shipping a second copy of the county roster.
    mp = Path(export_dir) / "MonitoringStatus.csv"
    if mp.exists():
        try:
            md = pd.read_csv(mp, dtype={"county_fips": str}, low_memory=False)
            md["county_fips"] = md["county_fips"].str.zfill(5)
            CODE = {"REPORTING": 0, "SEWER_SERVICE_NO_SITE": 1, "LIMITED_SEWER_SERVICE": 2}
            D["monitoring"] = {
                r.county_fips: [CODE.get(str(r.monitoring_status), 2),
                                int(r.n_sites_reporting or 0),
                                int(round(float(r.sewered_population or 0))),
                                R(r.sewer_share), R(r.sewered_svi)]
                for r in md.itertuples()
            }
            D["monitoring_names"] = {r.county_fips: [str(r.county_name or ""), str(r.state_code or "")]
                                     for r in md.itertuples()}
        except Exception as exc:
            print(f"[WARN] MonitoringStatus.csv unreadable ({exc}); the lookup will report it as unavailable.")
            D["monitoring"] = None
            D["monitoring_names"] = None
    else:
        D["monitoring"] = None
        D["monitoring_names"] = None
    D["monitoring_national"] = opt("MonitoringNational", how="first")

    # Per-county urbanicity, packed as {fips: [code, surveilled]} so the map
    # can colour by class and distinguish covered from uncovered inside each
    # class, which is how CDC draws the same figure.
    up = Path(export_dir) / "UrbanicityCounty.csv"
    if up.exists():
        try:
            ud = pd.read_csv(up, dtype={"county_fips": str})
            ud["county_fips"] = ud["county_fips"].str.zfill(5)
            ud = ud.dropna(subset=["rucc_2023"])
            D["rucc_by_fips"] = {
                f: [int(c), 1 if str(s).strip().lower() in ("true", "1", "yes") else 0]
                for f, c, s in zip(ud["county_fips"], ud["rucc_2023"], ud["surveilled"])
            }
        except Exception as exc:
            print(f"[WARN] UrbanicityCounty.csv unreadable ({exc}); the map will report it as unavailable.")
            D["rucc_by_fips"] = None
    else:
        D["rucc_by_fips"] = None
    D["urbanicity"] = opt("UrbanicityCoverage", [
        "rucc_2023", "rucc_label", "is_metro", "n_us_counties", "n_counties_surveilled",
        "pct_of_class_surveilled", "pct_of_surveilled_network", "pct_of_us_counties",
        "population_2020_us", "population_2020_surveilled"])
    D["global_coverage"] = opt("GlobalCoverage", [
        "country", "iso3", "sewer_connected_pct", "income_group", "population",
        "observable_population", "unobservable_population", "has_open_feed",
        "open_machine_readable_feed", "feed_rows_ingested", "feed_status",
        "safely_managed_pct", "sanitation_not_observable_pct",
        "sanitation_not_observable_population", "gap_uninterpretable",
        "denominator_basis", "denominator_caveat"])
    D["global_income"] = opt("GlobalCoverageIncome")
    # Per-county representativeness keyed for the map layer.
    if D["representativeness"]:
        D["rep_by_fips"] = {str(x["county_fips"]).zfill(5): [R(x.get("representativeness")),
                                                             R(x.get("sewer_share")),
                                                             int(x.get("n_sites") or 0)]
                            for x in D["representativeness"]}
        for x in D["representativeness"]:
            f = str(x["county_fips"]).zfill(5)
            if f not in names and isinstance(x.get("county_name"), str):
                names[f] = [x["county_name"], x.get("state_code")]
    else:
        D["rep_by_fips"] = None

    latest = D_summary_latest(r("PathogenSummary"))
    D["latest_sample"] = str(latest.date()) if latest is not None else None
    D["tn_county"] = recs(r("TennesseeCounty"))
    D["tn_align"] = recs(r("TennesseeAlignment"))
    D["tn_equity"] = recs(r("TennesseeEquity"))
    D["tn_seasonal"] = recs(r("TennesseeSeasonal"))
    D["audit"] = recs(r("AuditLog")[["component", "status", "detail", "source"]])
    D["alerts"] = recs(r("Alert")[["alert_type", "severity", "pathogen", "geography", "message", "evidence"]])

    data = json.dumps(D, separators=(",", ":"), allow_nan=False)
    (out / "data.json").write_text(data)
    html = TEMPLATE.read_text().replace("__DATA__", data.replace("</", "<\\/")).replace("__TOPO__", TOPO.read_text())
    html = html.replace("__SUPA__", SUPA.read_text() if SUPA.exists() else "null")
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<link rel="icon" type="image/png" href="img/nwgs-favicon.png">'
            '<link rel="apple-touch-icon" href="img/nwgs-touch-icon.png">'
            '<meta name="theme-color" content="#14213a">'
            '<meta name="author" content="Victoria Love Franklin">'
            '<meta name="copyright" content="© 2026 Victoria Love Franklin. All rights reserved.">'
            '<meta name="description" content="NWGS Grid™: weekly validated wastewater surveillance of respiratory and emerging pathogens across U.S. counties. By Victoria Love Franklin.">'
            '<meta property="og:title" content="NWGS Grid™ — National Wastewater Genomic Surveillance">'
            '<meta property="og:description" content="Weekly wastewater surveillance dashboard by Victoria Love Franklin, Ph.D. Data Science Student · GIS · AI & ML · Developer · Published Researcher.">'
            '<style>[hidden]{display:none!important}body{margin:0}</style></head><body>' + html + "</body></html>")
    (out / "index.html").write_text(page)
    copy_assets(out)
    print(f"Built {out/'index.html'} ({len(page)/1e6:.2f} MB), run {D['run']['run_id']}, data through {D['run']['data_as_of']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
"""
NWGS Grid(TM) - app export step
================================
Author: Victoria Love Franklin — Developer · PhD Student, Data Science · Research Scholar
Copyright © 2026 Victoria Love Franklin. All rights reserved. See LICENSE.

Turns one pipeline run's output tables into the site's data files.

    python3 nwgs_app_export.py <TABLE_DIR> <OUT_DIR> [--allow-mixed-runs]

What it does
  1. Gate:  stops (exit 2) if any Table13 component is FAIL, so last week's
            app data stays live instead of being replaced by broken data.
  2. Check: cross-table consistency (e.g. Table07 county counts must match
            Table13). Mismatches mean tables came from different runs; the
            export stops unless --allow-mixed-runs is passed.
  3. Build: one CSV + one JSON array per data entity, every row stamped with
            run_id and data_as_of. Drops local file paths and internal columns.
  4. Derive: activity categories (same thresholds as the pipeline's
            categorize_activity_z) and data-driven alerts.
  5. Write: manifest.json (row counts, checks, gate result) and
            nwgs_app_payload.json (all entities in one file).

Tables never exported: Table12 PHIL manifest, Table14*, Table19, Table20,
SpatialInput CSVs, Table04 All Lags, raw Table12b/12e/12f rows.
"""
import json
import sys
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

# Same bins as the pipeline's categorize_activity_z()
ACT_BINS = [-np.inf, -1.0, -0.25, 0.25, 1.0, np.inf]
ACT_LABELS = ["Very Low", "Low", "Typical", "Elevated", "High"]
ROUTINE = ["SARS-CoV-2", "RSV", "Influenza A"]
EMERGING = ["Influenza A(H5)", "Measles", "Mpox"]

STATE_NAMES = {}  # filled from Table05


# ------------------------------------------------------------------ helpers
def find(table_dir: Path, key: str, required=True):
    """Find a table by its name prefix, e.g. 'Table04_Best_Lag'."""
    hits = sorted(
        [p for p in table_dir.glob(f"*{key}*.csv") if "PHIL" not in p.name],
        key=lambda p: p.stat().st_mtime,
    )
    if not hits:
        if required:
            raise FileNotFoundError(f"Missing table: {key}")
        return None
    return pd.read_csv(hits[-1], low_memory=False)


def category(z):
    return pd.cut(pd.Series(z), bins=ACT_BINS, labels=ACT_LABELS).astype(str).replace("nan", "No recent data")


def fips5(s):
    return s.astype("Int64").astype(str).str.zfill(5)


def clean(df):
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]
    for c in df.columns:
        if df[c].dtype == float:
            df[c] = df[c].round(6)
    return df


# ------------------------------------------------------------------ main
def main(table_dir, out_dir, allow_mixed=False):
    table_dir, out_dir = Path(table_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checks, ents = [], {}

    t13 = find(table_dir, "Table13_NWGS_Validation_Summary")
    t01 = find(table_dir, "Table01_CDC_Wastewater_Data_Sources")

    # ---- run identity -------------------------------------------------------
    t03 = find(table_dir, "Table03_National_Pathogen_Trends")
    data_as_of = str(pd.to_datetime(t03["week_end"]).max().date())
    pulled = pd.to_datetime(t01["updated_at_metadata"], unit="s", utc=True).max()
    run_id = "run_" + pulled.strftime("%Y%m%dT%H%MZ")

    # ---- 1. gate on Table13 -------------------------------------------------
    fails = t13[t13["status"].str.upper().str.startswith("FAIL")]
    warns = t13[t13["status"].str.upper().str.startswith("WARN")]
    gate = "BLOCKED" if len(fails) else ("PASS_WITH_WARNINGS" if len(warns) else "PASS")

    # ---- 2. cross-table consistency ----------------------------------------
    t07 = find(table_dir, "Table07_Recent_County_Pathogen_Activity")
    for p in ROUTINE:
        row = t13[t13["component"].eq(f"{p} recent activity")]
        if row.empty:
            continue
        expected = int(str(row["detail"].iloc[0]).split()[0])
        got = int(t07.loc[t07["pathogen"].eq(p), "county_fips"].nunique())
        checks.append({"check": f"Table07 vs Table13 recent counties ({p})",
                       "expected": expected, "found": got, "ok": expected == got})

    t08 = find(table_dir, "Table08_LISA_PathogenActivity")
    row = t13[t13["component"].eq("KNN spatial analysis")]
    if not row.empty:
        exp = int(str(row["detail"].iloc[0]).split()[0])
        checks.append({"check": "Table08 LISA rows vs Table13", "expected": exp,
                       "found": len(t08), "ok": exp == len(t08)})

    t04 = find(table_dir, "Table04_Best_Lag_Results")
    row = t13[t13["component"].eq("Wastewater-clinical lag analysis")]
    if not row.empty:
        exp = int(str(row["detail"].iloc[0]).split()[0])
        checks.append({"check": "Table04 best-lag rows vs Table13", "expected": exp,
                       "found": len(t04), "ok": exp == len(t04)})

    t12f = find(table_dir, "Table12f_ML_Prediction_Outliers", required=False)
    row = t13[t13["component"].eq("ML held-out prediction outlier audit")]
    if t12f is not None and not row.empty:
        exp = int(str(row["detail"].iloc[0]).split()[0])
        checks.append({"check": "Table12f outlier rows vs Table13", "expected": exp,
                       "found": len(t12f), "ok": exp == len(t12f)})

    t06b = find(table_dir, "Table06b_Coverage_Equity_GLM")
    row = t13[t13["component"].eq("SVI surveillance readiness inferential model")]
    if not row.empty:
        exp = round(float(str(row["detail"].iloc[0]).split("=")[1].split()[0]), 3)
        got = round(float(t06b["odds_ratio"].iloc[0]), 3)
        checks.append({"check": "Table06b OR vs Table13", "expected": exp, "found": got, "ok": exp == got})

    mixed = [c for c in checks if not c["ok"]]
    if gate == "BLOCKED" or (mixed and not allow_mixed):
        status = "BLOCKED: Table13 FAIL" if gate == "BLOCKED" else "BLOCKED: tables from different runs"
        (out_dir / "manifest.json").write_text(json.dumps(
            {"run_id": run_id, "status": status, "checks": checks,
             "fails": fails.to_dict("records")}, indent=2, default=str))
        print(status)
        for c in mixed:
            print(f"  MISMATCH {c['check']}: expected {c['expected']}, found {c['found']}")
        sys.exit(2)

    stamp = {"run_id": run_id, "data_as_of": data_as_of}

    # ---- 3. entities --------------------------------------------------------
    # PipelineRun
    ents["PipelineRun"] = pd.DataFrame([{
        **stamp, "data_pulled_utc": pulled.isoformat(), "gate_status": gate,
        "n_pass": int((t13["status"] == "PASS").sum()), "n_warning": len(warns), "n_fail": len(fails),
        "consistency_ok": not mixed,
    }])

    # DataSource (Table01)
    d = t01.copy()
    d["updated_utc"] = pd.to_datetime(d["updated_at_metadata"], unit="s", utc=True).astype(str)
    d["source_url"] = "https://data.cdc.gov/d/" + d["dataset_id"]
    ents["DataSource"] = d[["pathogen", "dataset_id", "dataset_name", "rows", "updated_utc", "source_url"]]

    # PathogenSummary (Table02)
    t02 = find(table_dir, "Table02_Pathogen_Summary_Cards")
    ps = t02.drop(columns=["qc_flag_rate"]).copy()
    ps["recent_level"] = np.where(ps["recent_median_site_z"].notna(),
                                  category(ps["recent_median_site_z"]).values, "Detection-based")
    ents["PathogenSummary"] = ps

    # NationalTrend (Table03) + EmergingTrend (Table03b)
    nt = t03.dropna(subset=["median_site_z"]).copy()
    nt["level"] = category(nt["median_site_z"]).values
    ents["NationalTrend"] = nt
    t03b = find(table_dir, "Table03b_Emerging_Pathogen_Detection_Trends")
    ents["EmergingTrend"] = t03b[["pathogen", "week_end", "detection_rate", "n_sites_tested", "n_records"]]

    # County lookup from Table05
    t05 = find(table_dir, "Table05_County_Pathogen_Coverage")
    t05["county_fips"] = fips5(t05["county_fips"])
    lookup = t05.drop_duplicates("county_fips")[["county_fips", "COUNTY", "STATE", "ST_ABBR", "RPL_THEMES"]]
    lookup.columns = ["county_fips", "county_name", "state_name", "state_code", "svi"]

    # CountyActivity (Table07)
    ca = t07.copy()
    ca["county_fips"] = fips5(ca["county_fips"])
    ca["level"] = category(ca["activity_z"]).values
    ca = ca.merge(lookup, on="county_fips", how="left")
    ents["CountyActivity"] = ca[["pathogen", "county_fips", "county_name", "state_code", "activity_z",
                                 "level", "n_sites", "n_records", "activity_end_week"]]

    # StructuralRegion (Table11d, v5.21+; optional so older runs still export)
    t11d = find(table_dir, "Table11d_UniProt_Functional_Regions", required=False)
    if t11d is not None and len(t11d):
        keep = ["pathogen", "pdb_entry_id", "entity_id", "feature_type", "feature_description",
                "uniprot_accession", "uniprot_start", "uniprot_end", "evidence_codes", "evidence_count",
                "pdb_chain", "pdb_start", "pdb_end", "mapping_status",
                "annotation_source", "annotation_source_url", "expert_review_status"]
        ents["StructuralRegion"] = t11d[[c for c in keep if c in t11d.columns]]

    # EmergingCounty (Table07c, v5.21+; optional so older runs still export)
    t07c = find(table_dir, "Table07c_Recent_County_Emerging_Detections", required=False)
    if t07c is not None and len(t07c):
        ec = t07c.copy()
        ec["county_fips"] = fips5(ec["county_fips"])
        ec = ec.merge(lookup[["county_fips", "county_name", "state_code"]], on="county_fips", how="left")
        ents["EmergingCounty"] = ec[["pathogen", "county_fips", "county_name", "state_code", "n_sites_tested",
                                     "n_sites_detected", "last_detected_week", "window_end_week"]]

    # ------------------------------------------------------------
    # Surveillance-gap analytics (pipeline section 21c, v5.22+).
    # All optional: a run produced before 21c existed still exports.
    # ------------------------------------------------------------

    # LeadTime (Table21/21b) - shedding vs reporting vs operational lead
    t21 = find(table_dir, "Table21_LeadTime_Decomposition", required=False)
    if t21 is not None and len(t21):
        keep = ["pathogen", "state_code", "shedding_lead_weeks", "reporting_lag_weeks",
                "operational_lead_weeks", "usable", "lead_supported", "interpretation",
                "spearman_r", "spearman_p_fdr", "paired_weeks", "dataset_id",
                "last_sample_week", "dataset_updated"]
        ents["LeadTime"] = t21[[c for c in keep if c in t21.columns]]
    t21b = find(table_dir, "Table21b_LeadTime_National", required=False)
    if t21b is not None and len(t21b):
        ents["LeadTimeNational"] = t21b

    # Attrition (Table22/22b/22c) - which sites went dark, when, and where
    t22 = find(table_dir, "Table22_Coverage_Attrition_Sites", required=False)
    if t22 is not None and len(t22):
        at = t22.copy()
        if "county_fips" in at.columns:
            at["county_fips"] = at["county_fips"].astype("string").str.zfill(5)
            at = at.merge(lookup[["county_fips", "county_name", "state_code"]].rename(
                columns={"state_code": "lookup_state"}), on="county_fips", how="left")
            at["state_code"] = at["state_code"].fillna(at.pop("lookup_state"))
        keep = ["site_id", "state_code", "county_fips", "county_name", "first_week", "last_week",
                "n_weeks", "n_pathogens", "population_served", "weeks_since_last", "status",
                "went_dormant_week", "lifespan_weeks", "as_of_week", "dormant_threshold_weeks"]
        ents["AttritionSite"] = at[[c for c in keep if c in at.columns]]
    t22b = find(table_dir, "Table22b_Coverage_Attrition_Yearly", required=False)
    if t22b is not None and len(t22b):
        ents["AttritionYearly"] = t22b
    t22c = find(table_dir, "Table22c_Attrition_By_Vulnerability", required=False)
    if t22c is not None and len(t22c):
        ents["AttritionVulnerability"] = t22c

    # Forecast scoreboard (Table23b/23c) - frozen predictions, scored on arrival
    t23c = find(table_dir, "Table23c_Forecast_Scoreboard", required=False)
    if t23c is not None and len(t23c):
        ents["ForecastScore"] = t23c
    t23b = find(table_dir, "Table23b_Forecast_Scored", required=False)
    if t23b is not None and len(t23b):
        keep = ["run_id", "forecast_made_week", "pathogen", "horizon_weeks", "target_week",
                "pred_persistence", "pred_linear", "observed", "err_persistence", "err_linear"]
        ents["ForecastRecord"] = t23b[[c for c in keep if c in t23b.columns]]

    # Representativeness (Table24/24b) - the PHA4GE vacancy, defined
    t24 = find(table_dir, "Table24_County_Representativeness", required=False)
    if t24 is not None and len(t24):
        rp = t24.copy()
        rp["county_fips"] = rp["county_fips"].astype("string").str.zfill(5)
        keep = ["county_fips", "county_name", "state_code", "n_sites", "sewer_population",
                "county_population", "sewer_share", "sewer_share_raw", "sewershed_crosses_county",
                "svi", "state_monitored_svi", "svi_gap", "representativeness",
                "representativeness_tier", "analysis_ready", "definition_version"]
        ents["Representativeness"] = rp[[c for c in keep if c in rp.columns]]
    t24b = find(table_dir, "Table24b_Representativeness_National", required=False)
    if t24b is not None and len(t24b):
        ents["RepresentativenessNational"] = t24b

    # AssayTarget (Table25) - curated, citation-bearing published target regions
    t25 = find(table_dir, "Table25_Assay_Target_Panel", required=False)
    if t25 is not None and len(t25):
        keep = ["pathogen", "assay_name", "target_gene", "reference_accession", "region_start",
                "region_end", "region_length", "citation", "citation_url", "notes",
                "curation_status", "variation_source", "records_considered",
                "overlay_available", "overlay_note"]
        ents["AssayTarget"] = t25[[c for c in keep if c in t25.columns]]

    # GlobalCoverage (Table26/26b) - sewer-connected denominator by country
    t26 = find(table_dir, "Table26_Global_Coverage_Equity", required=False)
    if t26 is not None and len(t26):
        keep = ["country", "iso3", "sewer_connected_pct", "income_group", "population",
                "observable_population", "unobservable_population", "has_open_feed",
                "open_machine_readable_feed", "feed_rows_ingested", "feed_status",
                "safely_managed_pct", "sanitation_not_observable_pct",
                "sanitation_not_observable_population", "gap_uninterpretable",
                "denominator_basis", "denominator_caveat"]
        ents["GlobalCoverage"] = t26[[c for c in keep if c in t26.columns]]
    t26b = find(table_dir, "Table26b_Global_Coverage_By_Income", required=False)
    if t26b is not None and len(t26b):
        ents["GlobalCoverageIncome"] = t26b

    # CountyCluster (Table08 LISA)
    cl = t08.copy()
    cl["county_fips"] = fips5(cl["county_fips"])
    cl = cl.merge(lookup[["county_fips", "county_name", "state_code"]], on="county_fips", how="left")
    ents["CountyCluster"] = cl

    # SpatialSummary (Table08 global + 08c)
    g = find(table_dir, "Table08_Global_MoransI")
    a = find(table_dir, "Table08c_Spatial_Attrition_Audit")
    ents["SpatialSummary"] = g.merge(a[["pathogen", "recent_activity_counties", "total_excluded_from_spatial"]],
                                     on="pathogen", how="left").merge(
        cl.groupby(["pathogen", "lisa_cluster"]).size().unstack(fill_value=0).reset_index(), on="pathogen", how="left")

    # CountyCoverage (Table05)
    cc = t05.rename(columns={"COUNTY": "county_name", "ST_ABBR": "state_code", "RPL_THEMES": "svi"})
    ents["CountyCoverage"] = cc[["county_fips", "county_name", "state_code", "pathogen", "n_weeks", "n_sites",
                                 "first_week", "last_week", "max_population_served", "active_span_completeness",
                                 "analysis_ready", "svi"]]

    # StateLag (Table04 best)
    sl = t04.copy()
    sl["significant_fdr"] = sl["spearman_p_fdr"] < 0.05
    ents["StateLag"] = sl[["pathogen", "state_code", "lag_weeks", "relationship", "spearman_r",
                           "spearman_p_fdr", "significant_fdr", "paired_weeks"]]

    # SeasonalPeak (04d eligible + 04e) and SeasonalPeakState (04c eligible)
    d4 = find(table_dir, "Table04d_Seasonal_National")
    e4 = find(table_dir, "Table04e_Seasonal_Interannual")
    ents["SeasonalPeak"] = d4[d4["eligible"]][["pathogen", "season", "ww_peak_week", "clinical_peak_week",
                                               "ww_peak_magnitude_z", "ww_half_peak_duration_weeks",
                                               "ww_lead_to_clinical_peak_weeks", "implausible_lead_flag"]]
    ents["SeasonalVariability"] = e4
    c4 = find(table_dir, "Table04c_Seasonal_State")
    ents["SeasonalPeakState"] = c4[c4["eligible"] == True][[
        "pathogen", "state_code", "season", "ww_peak_week", "clinical_peak_week",
        "ww_lead_to_clinical_peak_weeks", "implausible_lead_flag"]]

    # Equity (Table06 + 06b)
    t06 = find(table_dir, "Table06_Coverage_Equity")
    eq = t06.copy()
    m = t06b.iloc[0]
    for k in ["n_counties", "odds_ratio", "or_95ci_low", "or_95ci_high", "p_value"]:
        eq[f"glm_{k}"] = m[k]
    ents["EquitySummary"] = eq

    # ModelPerformance (Table12 + 12d + 12h)
    t12 = find(table_dir, "Table12_Exploratory_ML_Benchmark")
    t12d = find(table_dir, "Table12d_Wastewater_Only_Benchmark")
    t12h = find(table_dir, "Table12h_ML_Predictive_Value_Triangulation")
    rows = []
    for p in t12["pathogen"].unique():
        q = t12[t12["pathogen"].eq(p)]
        full = q[q["model"].isin(["RandomForest", "HistGradientBoosting"])].sort_values("R2").iloc[-1]
        dd = t12d[t12d["pathogen"].eq(p)].iloc[0]
        hh = t12h[t12h["pathogen"].eq(p)].iloc[0]
        gain = full["R2"] - dd["clinical_persistence_R2"]
        rows.append({
            "pathogen": p, "best_model": full["model"], "full_model_r2": full["R2"], "full_model_rmse": full["RMSE"],
            "clinical_persistence_r2": dd["clinical_persistence_R2"], "wastewater_only_r2": dd["wastewater_only_R2"],
            "gain_over_persistence": gain, "shap_rank_wastewater_index": hh["shap_rank_of_wastewater_index"],
            "n_train": full["n_train"], "n_test": full["n_test"],
            "plain_language": ("Wastewater adds predictive value beyond recent clinical data."
                               if gain >= 0.02 else
                               "Recent clinical data alone predicts about as well; wastewater adds little extra."),
            "interpretation": hh["triangulated_synthesis"],
        })
    ents["ModelPerformance"] = pd.DataFrame(rows)

    # ShapFeature (Table12g, top 10, no state dummies)
    t12g = find(table_dir, "Table12g_SHAP_Top_Features")
    sf = t12g[~t12g["feature"].str.startswith("state_")]
    ents["ShapFeature"] = sf.groupby("pathogen").head(10)

    # Genomics: AMR (Table09) + NCBI (Table10/10b)
    ents["AmrTarget"] = find(table_dir, "Table09_AMR_ARG_Target_Summary")
    ents["AmrState"] = find(table_dir, "Table09_AMR_ARG_State_Summary")
    t10 = find(table_dir, "Table10_NCBI_Virus_Genomic_Metadata")
    t10b = find(table_dir, "Table10b_NCBI_Genomic_Metadata_Audit")
    # NCBI returns host/location as nested dicts; keep only the readable name
    loc_raw = t10["geographic_location"].astype(str)
    t10["geographic_region"] = loc_raw.str.extract(r"'geographic_region':\s*'([^']+)'")[0]
    t10["usa_state"] = loc_raw.str.extract(r"'usa_state':\s*'([^']+)'")[0]
    for col, key in [("host", "organism_name"), ("geographic_location", "geographic_location")]:
        s = t10[col].astype(str)
        name = s.str.extract(rf"'{key}':\s*'([^']+)'")[0]
        t10[col] = name.where(name.notna(), t10[col])
    t10["release_year"] = pd.to_datetime(t10["release_date"], errors="coerce", utc=True).dt.year
    yr = t10.groupby(["pathogen", "release_year"]).size().rename("records").reset_index()
    ents["GenomicSummary"] = t10b
    ents["GenomicByYear"] = yr
    ents["GenomicRecord"] = t10[["pathogen", "accession", "collection_date", "release_date", "host",
                                 "geographic_location", "geographic_region", "usa_state", "completeness", "complete_genome_flag"]]

    # ProteinStructure (Table11 + 11b + 11c) - URLs kept, local paths dropped
    t11 = find(table_dir, "Table11_RCSB_Representative_Structures")
    t11b = find(table_dir, "Table11b_RCSB_Protein_Entities")
    uni = t11b.groupby("pathogen")["uniprot_ids"].apply(lambda s: ";".join(sorted(set(";".join(s).split(";")))))
    ps11 = t11[["pathogen", "protein", "pdb_entry_id", "rcsb_title", "method", "resolution_A",
                "ncbi_metadata_records", "pdb_entry_url", "pdb_cif_url", "ca_atom_count", "figure_component_qc"]].copy()
    ps11["uniprot_ids"] = ps11["pathogen"].map(uni)
    ps11["image_url"] = "https://cdn.rcsb.org/images/structures/" + ps11["pdb_entry_id"].str.lower() + "_assembly-1.jpeg"
    ents["ProteinStructure"] = ps11

    # Tennessee (Table07b, 15, 16, 17, 17b, 18, 18b)
    t15 = find(table_dir, "Table15_Tennessee_County_Surveillance_Coverage")
    t18b = find(table_dir, "Table18b_Tennessee_County_Seasonal_Coverage")
    tn = t15[["county_fips", "NAME", "surveillance_weeks", "any_analysis_ready", "pathogens_observed", "sites"]].copy()
    tn["county_fips"] = fips5(tn["county_fips"])
    tn = tn.rename(columns={"NAME": "county_name"})
    t18b["county_fips"] = fips5(t18b["county_fips"])
    last = t18b.groupby("county_fips")["season"].max().rename("last_season_with_data")
    tn = tn.merge(last, on="county_fips", how="left")
    tn_now = set(ca.loc[ca["county_fips"].str.startswith("47"), "county_fips"])
    tn["reporting_now"] = tn["county_fips"].isin(tn_now)
    tn["status"] = np.select(
        [tn["reporting_now"], tn["any_analysis_ready"], tn["surveillance_weeks"] > 0],
        ["Reporting now", "Analysis-ready, stopped", "Observed, not analysis-ready"], "No CDC NWSS data")
    ents["TennesseeCounty"] = tn.sort_values("surveillance_weeks", ascending=False)
    ents["TennesseeAlignment"] = find(table_dir, "Table16_Tennessee_WW_Clinical_Alignment")
    ents["TennesseeEquity"] = find(table_dir, "Table17_Tennessee_Equity_By_SVI_Quartile").assign(
        **{f"glm_{k}": find(table_dir, "Table17b_Tennessee_Equity_GLM").iloc[0][k]
           for k in ["odds_ratio_per_0_10_SVI", "or_95ci_low", "or_95ci_high", "p_value"]})
    t18 = find(table_dir, "Table18_Tennessee_Seasonal_Eligibility")
    ents["TennesseeSeasonal"] = t18[["pathogen", "season", "observed_counties", "season_ready_counties",
                                     "eligible_for_tennessee_seasonal_inference", "ww_peak_week",
                                     "clinical_peak_week", "ww_lead_to_clinical_peak_weeks", "implausible_lead_flag"]]

    # AuditLog (Table13 + consistency checks + summary audits)
    al = t13.copy()
    al["source"] = "Table13"
    extra = [{"component": c["check"], "status": "PASS" if c["ok"] else "WARNING_MIXED_RUN",
              "detail": f"expected {c['expected']}, found {c['found']}", "source": "export"} for c in checks]
    t09b = find(table_dir, "Table09b_AMR_Classification_Audit", required=False)
    if t09b is not None:
        extra.append({"component": "AMR classification (Table09b)", "status": t09b["status"].iloc[0],
                      "detail": t09b["detail"].iloc[0], "source": "Table09b"})
    t11c = find(table_dir, "Table11c_RCSB_Structural_Figure_Audit", required=False)
    if t11c is not None:
        last11 = t11c.iloc[-1]
        extra.append({"component": "RCSB structural QC (Table11c)", "status": last11["figure_component_qc"],
                      "detail": f"{last11['metadata_status']} structures, {last11['render_status']}",
                      "source": "Table11c"})
    # External source outcomes become audit rows, so a layer that is empty on
    # the site can always be explained from the published tables alone.
    t26d = find(table_dir, "Table26d_Source_Fetch_Status", required=False)
    if t26d is not None and len(t26d):
        STATUS_MAP = {"OK": "PASS", "EMPTY": "INFO", "FAILED": "WARNING"}
        for _, r in t26d.iterrows():
            extra.append({
                "component": f"Source: {r['source']}",
                "status": STATUS_MAP.get(str(r.get("status")), "INFO"),
                "detail": (str(r.get("detail") or "")
                           + (f" [{r['url']}]" if str(r.get("url") or "") else "")).strip() or "no detail recorded",
                "source": "Table26d",
            })
        ents["SourceStatus"] = t26d

    ents["AuditLog"] = pd.concat([al, pd.DataFrame(extra)], ignore_index=True)

    # ---- 4. derived alerts --------------------------------------------------
    alerts = []
    # a. counties at High activity, grouped by pathogen + state
    hi = ca[ca["level"].eq("High")]
    for (p, st), q in hi.groupby(["pathogen", "state_code"]):
        alerts.append({"alert_type": "High county activity", "severity": "high", "pathogen": p, "geography": st,
                       "message": f"{len(q)} {st} count{'y' if len(q)==1 else 'ies'} at High {p} wastewater activity "
                                  f"(z > 1.0) in the 4 weeks ending {q['activity_end_week'].max()}.",
                       "evidence": "CountyActivity"})
    # b. national trend direction
    for _, r in t02[t02["trend"].eq("Increasing")].iterrows():
        alerts.append({"alert_type": "National trend", "severity": "moderate", "pathogen": r["pathogen"],
                       "geography": "United States",
                       "message": f"National {r['pathogen']} wastewater activity is increasing "
                                  f"(change {r['change_vs_previous_window_z']:+.2f} z vs previous window).",
                       "evidence": "PathogenSummary"})
    # c. emerging detections: latest week above twice the trailing 8-week median
    for p, q in t03b.sort_values("week_end").groupby("pathogen"):
        q = q[q["n_sites_tested"] >= 20]
        if len(q) < 9:
            continue
        latest, base = q.iloc[-1], q.iloc[-9:-1]["detection_rate"].median()
        if latest["detection_rate"] > 2 * base and latest["detection_rate"] > 0:
            alerts.append({"alert_type": "Emerging pathogen detection", "severity": "moderate", "pathogen": p,
                           "geography": "United States",
                           "message": f"{p} detected at {latest['detection_rate']:.1%} of {int(latest['n_sites_tested'])} "
                                      f"sites in week ending {latest['week_end']}, above twice the 8-week median ({base:.1%}).",
                           "evidence": "EmergingTrend"})
    # d. coverage warning (Table13 WARNING rows stay on the Audit Log, not in public alerts)
    tn_ready = int(tn["any_analysis_ready"].sum())
    alerts.append({"alert_type": "Coverage", "severity": "info", "pathogen": "", "geography": "Tennessee",
                   "message": f"Only {len(tn_now)} of 95 Tennessee counties reported in the latest window "
                              f"({tn_ready} have ever been analysis-ready).", "evidence": "TennesseeCounty"})
    ents["Alert"] = pd.DataFrame(alerts)

    # ---- 5. write -----------------------------------------------------------
    manifest = {"run_id": run_id, "data_as_of": data_as_of, "data_pulled_utc": pulled.isoformat(),
                "gate_status": gate, "consistency_checks": checks, "entities": {},
                "author": "Victoria Love Franklin — Developer · PhD Student, Data Science · Research Scholar",
                "copyright": "Copyright © 2026 Victoria Love Franklin. All rights reserved. See LICENSE."}
    payload = {}
    for name, df in ents.items():
        df = clean(df)
        for k, v in reversed(list(stamp.items())):
            if k not in df.columns:
                df.insert(0, k, v)
        df = df.replace({np.nan: None})
        df.to_csv(out_dir / f"{name}.csv", index=False)
        recs = json.loads(df.to_json(orient="records", date_format="iso"))
        payload[name] = recs
        manifest["entities"][name] = len(recs)
    blob = json.dumps(payload, default=str)
    manifest["payload_sha256"] = hashlib.sha256(blob.encode()).hexdigest()
    (out_dir / "nwgs_app_payload.json").write_text(blob)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    print(json.dumps({k: manifest[k] for k in ["run_id", "data_as_of", "gate_status"]}, indent=2))
    for c in checks:
        print(("OK       " if c["ok"] else "MISMATCH ") + f"{c['check']}: expected {c['expected']}, found {c['found']}")
    for n, k in manifest["entities"].items():
        print(f"{n:22s}{k:>7,}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    main(args[0], args[1], allow_mixed="--allow-mixed-runs" in sys.argv)

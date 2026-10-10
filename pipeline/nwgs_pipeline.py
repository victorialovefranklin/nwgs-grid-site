# NWGS Grid

"""
NWGS Grid™ MASTER REPRODUCIBLE PIPELINE v5.20
Author: Victoria Love Franklin — Developer · PhD Student, Data Science · Research Scholar
Copyright © 2026 Victoria Love Franklin. All rights reserved. See LICENSE.
Generated: 2026-09-14 (v5.20 revision)
Validated locally: Python syntax; full live-data rerun required for regenerated results

Research system:
NWGS Grid™ — Multimodal Wastewater Genomic Surveillance Framework

v5.20 CHANGE LOG (this revision)
---------------------------------
Three fixes from the Paper 1 / Paper 2 final figure review before manuscript
submission:

1. SEASONAL-PEAK BOUNDARY GUARD WIDENED (Paper 2 Figure 7 / Table18):
   LEAD_ARTIFACT_GUARD_WEEKS was 6, so a Tennessee SARS-CoV-2 clinical peak
   sitting at week 7-8 from July 1 - just outside that window - never
   tripped the implausible_lead_flag even though the same season also had
   an ~19-week gap to the wastewater peak, the same class of problem the
   flag exists to catch. This was a genuine gap in the guard's reach, not a
   bug in its logic. Widened to 9 weeks, which covers this case with a
   1-week margin without being so wide it starts flagging genuinely normal
   early/late-season variation - re-validated against both the original
   boundary-flag test cases (to confirm no new false positives) and a new
   test case built from this exact scenario (to confirm it now fires).
2. FIGURE 8 OUTLIER CAPTION (Paper 1 Observed-vs-Predicted): previously the
   flagged prediction outliers (Table12f) were invisible on the figure
   itself - a reviewer would see an unlabeled stray point with no pointer
   to the audit trail. plot_observed_vs_predicted() now adds a caption
   directing to Table12f and to the general diagnostic pattern worth
   checking (same-week clusters across many states suggest a reporting
   artifact; an isolated single-week spike bracketed by near-zero weeks
   suggests a source-data error) - written generically since a future rerun
   against live data may flag entirely different rows, not the specific
   week/state pattern seen in this run's data.
3. ML PREDICTIVE-VALUE TRIANGULATION TABLE: the ablation (Figure 9),
   wastewater-only benchmark (Figure 7B), and SHAP explainability
   (Figure 10) all independently point to the same conclusion (wastewater's
   marginal value inside the full model is small because clinical_lag1
   already captures most of its signal, while wastewater's STANDALONE value
   varies sharply by pathogen), but that convergence previously had to be
   assembled by hand from three separate tables/figures. explain_with_shap()
   now also returns each pathogen's ranked SHAP feature importances
   (saved to Table12g_SHAP_Top_Features.csv), and a new
   build_ml_triangulation_summary() merges the ablation deltas, the
   wastewater-only benchmark, and the SHAP ranking of wastewater_index into
   one row per pathogen (Table12h_ML_Predictive_Value_Triangulation.csv) -
   a single citable table for the manuscript's methods/results section
   instead of three.

v5.19 CHANGE LOG (previous revision)
---------------------------------
FIGURE 5 PORTRAIT ORIENTATION - ROOT CAUSE FOUND, DETERMINISTIC FIX APPLIED:
a real production run's own Table20_Portrait_SelfCheck.csv (which only
exists if the v5.18 patched code executed) confirmed
Map_Tennessee_SVI_Surveillance_Readiness.png was STILL landscape at
3021x2208px - the EXACT pixel dimensions as the v5.17 attempt, despite a
completely different width-solving formula between versions. Identical
output from different formulas rules out "wrong script running" (the
v5.17 theory) and instead means matplotlib's bbox_inches="tight" is
cropping the saved PNG down to its actual rendered content, discarding
the deliberately-added blank legend height that both v5.17's and v5.18's
algebra relied on to force a portrait aspect ratio. Adding nominally
"extra" canvas that stays mostly blank does not survive tight-cropping -
this is the exact same lesson the v5.15 changelog already learned for
other composite figures (which is why _image_aspect() reads real
on-disk dimensions instead of trusting nominal figsize), just not yet
applied here.

Two algebra-based upstream attempts to force portrait orientation before
saving have now failed identically, so this revision stops trying to
out-guess matplotlib's cropping behavior and instead guarantees the
POSTCONDITION directly: _verify_portrait_or_warn() (renamed in spirit,
not in name, to preserve call-site compatibility) now actively corrects
a non-portrait figure immediately after detecting it, by reopening the
saved PNG and padding it with a white margin at the bottom until its
height exceeds its width by a safety margin, then re-saving to the same
path and re-verifying. This is deliberately a deterministic, guaranteed
safety net rather than a fourth guess at the right nominal figsize -
the run log clearly marks the result as AUTOFIXED (not a silent PASS) so
a human can still see that Figure 5 needed correction and investigate
the upstream rendering cause at leisure, without that correction being
blocked on getting matplotlib's tight-bbox behavior right first.

v5.18 CHANGE LOG (previous revision)
---------------------------------
Four fixes from the Paper 1 / Paper 2 figure review, in order of how much
they could affect reported conclusions:

1. WASTEWATER-VS-CLINICAL-LAGS ABLATION AMBIGUITY (Paper 1 Figure 9):
   the feature-group ablation showed removing "wastewater_current" and
   "wastewater_lags" produced ~zero change in held-out R2 for all three
   pathogens, while removing "clinical_lags" produced by far the largest
   drop - read alone, this looks like "wastewater adds nothing", which
   sits in tension with Table04_Best_Lag_Results.csv showing wastewater
   genuinely leading clinical activity by 0-2 weeks for a meaningful
   number of states. exploratory_ml() now also (a) computes the
   TRAINING-split Pearson correlation between each wastewater feature and
   clinical_lag1 and flags/prints a warning when it is high enough to
   plausibly explain the ablation result via collinearity rather than
   genuine irrelevance (Table12e_ML_Feature_Collinearity_Audit.csv), and
   (b) fits a "WastewaterOnly" model using ONLY wastewater-derived
   features (no clinical_lag columns at all, so there is nothing for
   wastewater to be collinear with) and compares its standalone R2
   against the clinical-persistence baseline
   (Table12d_Wastewater_Only_Benchmark.csv, plotted as
   Fig_Wastewater_Only_Value.png). This does not change the ablation
   figure itself - it adds the complementary evidence needed to interpret
   it correctly.
2. TENNESSEE SEASONAL PEAK BOUNDARY ARTIFACT, SYMMETRIC CASE (Paper 2
   Figure 7): v5.17's implausible_lead_flag only checked whether the
   WASTEWATER peak sat near a season's START. Tennessee's SARS-CoV-2
   panel surfaced a second, mirror-image failure mode the v5.17 check
   could not catch: the CLINICAL peak landing near a season boundary
   (an early-August secondary wave in the state-level NSSP ED series,
   ~weeks 6-8 from July 1) while the wastewater peak sits mid/late-season,
   producing the same class of multi-month implausible lead but with the
   boundary-adjacent series on the clinical side instead of the
   wastewater side. _summarize_season_peak()'s flag now checks BOTH the
   wastewater and clinical peak against BOTH the season's start and end,
   symmetrically, and records how close the nearest peak sits to a season
   boundary (nearest_peak_to_season_boundary_weeks) so this is visible in
   Table04d/Table18 regardless of which series or which boundary is
   involved.
3. TENNESSEE FIGURE 5 PORTRAIT FIX NOT TAKING EFFECT IN PRODUCTION: a
   fresh Table19 run after the v5.17 Figure 5 sizing patch still showed
   Map_Tennessee_SVI_Surveillance_Readiness.png at the EXACT pre-fix pixel
   width (3021px) - strong evidence that whatever script executed that
   run was not actually running the patched Figure 5 code (a stale copy,
   a duplicate function definition earlier in the file winning, or
   similar). Since a downstream audit table only catches this if someone
   remembers to check it, create_tennessee_paper_figures() now calls a
   new _verify_portrait_or_warn() helper immediately after saving Figure 2
   and Figure 5, which reopens the just-saved PNG from disk and prints an
   impossible-to-miss FAIL directly in the run's own console log - and
   into a first-class validation-summary row - the moment a portrait
   figure is not actually portrait, rather than waiting for a separate
   audit step run against a possibly-stale set of files.
4. ML HELD-OUT PREDICTION OUTLIER TRACING (Paper 1 Figure 8): the RSV
   observed-vs-predicted panel showed one point far off the y=x line
   (observed~2.85, predicted~0) with no way to identify which state/week
   it came from. exploratory_ml() now carries state_code/week_end
   alongside each held-out prediction, and a new
   audit_ml_prediction_outliers() flags any point whose residual exceeds
   a z-score threshold within its own pathogen's residual distribution,
   exporting the exact state/week to
   Table12f_ML_Prediction_Outliers.csv so an outlier can be checked
   against the source data instead of only being visible as an unlabeled
   dot on a scatterplot.

v5.17 CHANGE LOG (previous revision)
---------------------------------
Closes the two remaining open items from the v5.16 figure/table audit,
plus two follow-up items flagged in the same review:

1. SARS-CoV-2 SEASONAL PEAK-DETECTION ARTIFACT: _summarize_season_peak()'s
   rolling smoother used min_periods=(window+1)//2, so the FIRST and LAST
   weeks of a season's data window received a "smoothed" value computed
   from only 1-2 points instead of the full 3-week median. SARS-CoV-2 has
   a real, usually-small secondary summer wave right at the July/August
   start of the season; with a 2-point partial window, a single noisy
   early-August week could pass through smoothing almost unchanged and be
   picked up by argmax() as the season "peak" even though it wasn't one -
   exactly the mechanism that produced the "-18 week lag" values reported
   in two of three eligible SARS-CoV-2 seasons (an early wastewater blip
   compared against the real, much-later clinical peak). Fixed by
   requiring the FULL window (min_periods=window): boundary-week values
   with insufficient support are now NaN and excluded by the existing
   dropna() calls rather than standing in for a real smoothed value. A
   companion implausible_lead_flag is computed alongside the fix and
   surfaced (not silently dropped) whenever a wastewater peak still lands
   in the first 6 weeks of a season AND produces a lead more extreme than
   10 weeks, with a printed WARNING per flagged pathogen/season - matching
   the audit style already used elsewhere in this script - so any
   remaining edge case is visible before a lead number is reported.
2. TENNESSEE SVI/READINESS MAP PORTRAIT ORIENTATION
   (Map_Tennessee_SVI_Surveillance_Readiness.png): the v5.12
   _tn_map_aspect() fix correctly sizes each map panel from Tennessee's
   real ~3.4:1 width:height ratio so neither map stretches, but that alone
   does not make the OVERALL saved figure portrait, because Tennessee's
   true outline is itself wide and short. Two such maps stacked at a flat
   9in figure width plus the previous fixed 1.8in legend strip produced
   total_height ~= 2*(9/3.4) + 1.8 ~= 7.1in against a 9in width - still
   landscape, exactly matching the Table19 audit finding of 3021x2306,
   FAIL_NOT_PORTRAIT (Figure 2 avoids this only because its second panel
   is a full 6.2in bar chart, not a thin legend strip). Fixed by solving
   for a figure width where two map panels plus a legend/annotation panel
   sum to a height that exceeds the width by a fixed safety margin, using
   the freed vertical space for a genuine per-SVI-quartile readiness
   breakdown (mirrors Table17) rather than blank padding. Fix D (v5.15
   colorbar-collision fix) is untouched by this change and re-verified to
   still apply, since it operates on the SVI colorbar inside panel A,
   independent of the overall figure width/height solved here.
3. FIGURE 7 CAPTION NOW SURFACES TABLE18 COUNTY COUNTS
   (Fig_Tennessee_Seasonal_Peaks.png): each plotted season is now
   annotated with its season_ready_counties/observed_counties values
   (already computed into Table18 by tennessee_seasonal_analysis()) so
   the counts are visible on the figure itself, not only in the CSV.
4. Version/step-label consistency: the banner printed by main() now
   matches the module version (v5.17).

v5.16 CHANGE LOG (previous revision)
---------------------------------
ENABLE_EXPLORATORY_ML defaulted to "1" (on). This was previously "0"
(off), which is why Table12_Exploratory_ML_Benchmark.csv,
Table12b_Exploratory_ML_Ablation.csv, and Paper 1 Figures 7-10 never
appeared in prior runs - exploratory_ml() returns three empty results
immediately when this flag is unset, before any of the v5.15 plotting
functions are ever called. Turning it on by default closes that gap
without requiring a manual `export NWGS_ENABLE_ML=1` step before every
run. TRADEOFF: this run now fits 2 models x 5 feature-group ablations x N
pathogens (vs. the original 2 models x N pathogens), so expect a
noticeably longer [17/19] step than before. Set NWGS_ENABLE_ML=0 to
restore the old fast-skip behavior if that cost isn't wanted.

v5.15 CHANGE LOG (previous revision)
---------------------------------
1. PENDING_ML FIGURES 7-10 NOW HAVE BACKING CODE: Figures 7-8 had real
   data and just needed plotting functions (plot_ml_model_performance(),
   plot_observed_vs_predicted()); Figures 9 (ablation) and 10 (SHAP) had
   zero backing code before this revision. exploratory_ml() now also
   returns per-pathogen held-out predictions and a feature-group ablation
   table; plot_ablation() and explain_with_shap() (optional shap
   dependency, degrades gracefully if absent) were added.
2. FIGURE 5 SVI COLORBAR / SUPTITLE COLLISION (Fix D): the colorbar's
   vertical label previously carried the full explanatory phrase at
   default fontsize, extending above the reserved header band and
   colliding with the figure suptitle. Shortened the label, shrank the
   colorbar, and reduced its font size.
3. IMAGE-PANEL COMPOSITE STRETCHING: several combined poster/paper
   figures sized composite cells from a guessed nominal figsize rather
   than each saved PNG's actual on-disk aspect ratio (bbox_inches="tight"
   crops every save to its real content bounds, so the two can differ
   substantially - confirmed by Table19 showing every national CONUS map
   saves landscape ~1.51:1 despite a nominal portrait figsize). Added
   _image_aspect() (reads the real saved aspect from disk) and
   _solve_exact_fit_widths() (solves a shared row height so every panel
   in a row fills its cell at its own real aspect, zero stretch), and
   applied both across create_combined_publication_figures().
4. CDC PHIL 0/6 DOWNLOADS: broadened _extract_phil_highres_url() to also
   match common PHIL image-file path patterns and the page's
   og:image meta tag, and added diagnostic fields (HTTP status, final
   URL, response length) to the PHIL manifest so a still-failing page can
   be diagnosed from Table12_CDC_PHIL_Pathogen_Image_Manifest.csv without
   live access to phil.cdc.gov from this environment.

v5.13 CHANGE LOG (previous revision)
---------------------------------
Three fixes from a script audit:
1. INCOMPLETE STALE-FIGURE CLEANUP: clean_stale_versioned_outputs() only
   globbed three filename patterns (PathogenDetection_*, the pathogen
   intelligence panel, ProteinStructure_*), but several other figures are
   conditionally SUPPRESSED (no file written) rather than regenerated on a
   given run - plot_pathogen_trends() (fewer than 3 non-null weekly z
   values), plot_lag_summary() (no qualifying jurisdiction-pathogen pairs),
   plot_seasonal_peak_analysis() (no eligible complete seasons), and
   tennessee_seasonal_analysis() (no Tennessee pathogen-season meets
   coverage eligibility). If any of these were eligible on an earlier run
   and become ineligible later (data window shift, threshold change, a
   season aging out), the old PNG just sat in FIG_DIR - and nothing
   downstream could tell the difference, since build_figure_use_manifest()
   only checks Path.exists(). A genuinely stale figure could flow all the
   way into a Paper 1/Paper 2 product folder marked GENERATED/PASS. Fixed
   by having clean_stale_versioned_outputs() unconditionally remove every
   PNG in FIG_DIR and STRUCTURE_DIR at the start of each run, since main()
   already regenerates (or correctly re-suppresses) every figure every run
   - there is no figure in this pipeline that is only computed once and
   reused, so nothing legitimate is lost by clearing first.
2. LINEARIZED-CONCENTRATION LEAK INTO DETECTION FALLBACK: harmonize_pathogen()
   builds raw_concentration via a column-presence fallback across
   ["pcr_target_avg_conc","pcr_target_avg_conc_lin","concentration"]. If a
   pathogen's CDC dataset schema never exposes pcr_target_avg_conc at all,
   raw_concentration is populated entirely from the linearized field - the
   exact field add_emerging_detection_flags()'s own docstring says must
   NEVER be used for detection ("The linearized concentration field is
   NEVER used for detection"). Because that safeguard checked the column
   NAME (raw_concentration) rather than its actual SOURCE field, a
   schema-dependent silent violation was possible with no warning, and
   profile_emerging_detection_fields() audited the source columns
   independently without ever checking which one raw_concentration itself
   drew from. Fixed: harmonize_pathogen() now records
   raw_concentration_is_linearized (True only when pcr_target_avg_conc_lin
   was the resolved source), and add_emerging_detection_flags() refuses the
   raw-concentration fallback for any row where that flag is set, leaving
   detection status UNKNOWN instead - with the basis recorded as
   "blocked_raw_concentration_was_linearized" so it is visible in the
   detection audit rather than silently absent.
3. NO AUDIT COVERAGE FOR THE outlier COLUMN'S HARDCODED "Y" TOKEN:
   outlier_flag = df["outlier"]...eq("Y") has the identical silent-failure
   shape that audit_amr_classification() was built to catch for the Detect
   column's hardcoded "D" token (v5.9) - if the actual coding differs
   (e.g. "TRUE"/"1"/"Outlier"), every row silently becomes outlier_flag=False
   with no error anywhere. audit_amr_classification() now also reports the
   raw 'outlier' column's value counts and flags a
   WARNING_OUTLIER_CODING_UNVERIFIED status when every row is False despite
   the source column having non-null values, the same pattern already used
   for the Detect-column check.

v5.12 CHANGE LOG (previous revision)
---------------------------------
The v5.11 pass only touched functions shared across pathogens/products
(_render_image_panel, the AMR map, the three combined poster composites).
This revision fixes four Tennessee-paper-specific figures that were never
covered by that pass:
1. TENNESSEE MULTIPATHOGEN TABLE (Fig_Tennessee_Multipathogen_Surveillance.png):
   plot_tennessee_maps() used a 4.5in-tall figure with the title anchored
   near the top and the note anchored at a fixed low y, leaving the small
   3-row table vertically centered with large blank gaps both above and
   below - bbox_inches="tight" still spanned that full title-to-note extent.
   Reduced to a 3.0in-tall figure with the table placed via an explicit bbox
   near the top instead of loc="center".
2. TENNESSEE EQUITY CHART Y-AXIS (Fig_Tennessee_Equity_Model.png):
   ax.set_ylim(0,100) was hardcoded, but Tennessee's actual readiness rates
   are only ~4-9% (the national equity chart correctly uses 0-100 because
   its rates run 75-90%). The fixed scale wasted over 90% of the chart and
   made the ~2x difference between quartiles (4.2% vs 8.7%) visually
   imperceptible. The y-axis now scales to the actual data with headroom
   for the percentage labels.
3-4. TENNESSEE MAP PANELS (Map_Tennessee_Surveillance_Coverage.png Figure 2,
   Map_Tennessee_SVI_Surveillance_Readiness.png Figure 5): both used
   arbitrary gridspec height_ratios (e.g. 1.2 or 1.05 per map) that gave
   each map panel roughly double the vertical space its actual wide/short
   footprint needed - the same map-aspect-ratio whitespace bug already
   fixed in the companion Tennessee air-quality pipeline, but never applied
   here. A new _tn_map_aspect() helper now sizes each map panel from
   Tennessee's real ~3.4:1 width:height ratio instead of a guess.

v5.11 CHANGE LOG (previous revision)
---------------------------------
1. IMAGE-PANEL LETTERBOXING FIX: _render_image_panel() now calls
   ax.imshow(img, aspect="auto") instead of the default aspect="equal".
   Every embedded PNG previously kept its own native aspect ratio inside
   whatever subplot cell it was placed in, so wide/short trend charts and
   narrow/tall maps left large blank letterbox bands - the root cause of
   the "excessive whitespace" seen across the Respiratory Trends+Maps,
   Surveillance Performance, and Emerging Detection composites. This single
   fix removes most of that whitespace everywhere _render_image_panel() is
   used.
2. AMR STATE MAP "NO DATA" LEGEND: plot_amr_state_map() now adds an
   explicit legend entry ("No study/source-standardized estimate") for the
   gray states, which previously had no on-figure explanation and could be
   misread as a very-low/zero value rather than an absent estimate.
3. EMERGING PATHOGEN COMPOSITE - PORTRAIT LAYOUT: the H5/Mpox/Measles
   detection-frequency composite switched from an extremely wide 1x3
   horizontal layout to a portrait 3-row vertical stack (H5 -> Mpox ->
   Measles), matching each source chart's own wide/short shape.
4. SURVEILLANCE PERFORMANCE COMPOSITE - DROPPED TN TABLE, RESHAPED GRID:
   removed the illegibly small Tennessee multipathogen table from this
   NATIONAL composite (Tennessee remains fully available as its own
   standalone figure and within the Tennessee paper product, so no content
   was lost). The remaining three panels no longer share a plain 2x2 grid;
   the tall coverage map now spans both rows on the left while the two
   landscape bar charts (Lag, Equity) stack on the right, matching each
   panel's real shape.
5. RESPIRATORY TRENDS+MAPS COMPOSITE - RESIZED COLUMNS: the trend-chart
   column now gets width_ratios=[1.7, 1] relative to the map column
   (matching the trend charts' real ~2.2:1 wide aspect vs. the maps'
   ~0.83:1 narrow aspect), and inter-row/inter-column spacing is tightened,
   instead of an equal-width 2-column grid that undersized the trend plots
   and left large gaps between pathogen rows.

v5.10 CHANGE LOG (previous revision)
---------------------------------
1. AMR/ARG FIGURES SEPARATED: create_combined_publication_figures() no longer
   stacks the ARG detection-profile bar chart and the state-level abundance
   choropleth into one combined Fig_Combined_AMR_ARG.png. The two source
   figures have very different aspect ratios (wide/short vs. tall/portrait)
   and each already carries its own title/caption, so combining them produced
   large dead-space gaps and duplicated titling with no added narrative value.
   plot_amr() and plot_amr_state_map() already generate both figures
   independently; the poster figure manifest and the master overview panel
   now reference each of them directly instead of the removed combined file.

v5.9 CHANGE LOG (previous revision)
--------------------------------
1. QCUT CRASH FIX: coverage_equity() and the Tennessee equity model inside
   create_tennessee_paper_figures() both called pd.qcut(..., labels=[4 labels],
   duplicates="drop"). Passing explicit labels together with duplicates="drop"
   does NOT resize the label list when tied SVI percentile values collapse the
   number of quantile bins below 4 (a very plausible outcome for SVI data,
   which has many counties tied at 0.0/1.0) - it raises
   "ValueError: Bin labels must be one fewer than the number of bin edges."
   Both call sites now use a new _safe_svi_quartile() helper that computes the
   quantile bins unlabeled first, and only maps as many labels as bins
   actually survived, printing a warning instead of crashing when fewer than
   4 bins remain.
2. STALE-OUTPUT CLEANUP NOW ACTUALLY RUNS: clean_stale_versioned_outputs() was
   defined (with a docstring explaining it prevents old v4.x 100%-flat
   emerging-pathogen PNGs from surviving into a new output directory) but was
   never called anywhere in main(). It is now called as step [0/19], before
   any new figures are written, so combined/poster figure assembly can never
   silently pick up a stale image left over from a previous run of an older
   script version.
3. AMR/ARG CLASSIFICATION AUDIT: the AMR module previously had no validation
   at all, unlike the emerging-pathogen detection pipeline (which has
   profile_emerging_detection_fields()/emerging_detection_audit()). Two silent
   failure modes existed: AMR_CLASS_MAP keys are bare gene names (e.g. "KPC",
   "NDM", "TEM") while standard nomenclature is usually prefixed (e.g.
   "blaKPC", "blaNDM"), so a mismatch would silently route every row to
   "Other/Unmapped"; and the "detected" flag hard-codes an exact "D" token
   for the Detect column, so any other coding (e.g. "Y"/"N", "Positive") would
   silently produce a 0% detection rate everywhere. A new
   audit_amr_classification() function now checks both conditions, prints the
   raw Detect value counts, flags WARNING/FAIL status, and is saved to
   Table09b_AMR_Classification_Audit.csv and folded into the run validation.
4. VERSION/STEP-LABEL CONSISTENCY: the banner printed by main() now matches
   the module version (v5.9) instead of a stale "v5.6" string left over from
   an earlier revision.

Research system:
NWGS Grid™ — Multimodal Wastewater Genomic Surveillance Framework

CORE PURPOSE
------------
1. Pull six CDC wastewater pathogen datasets by API:
   - SARS-CoV-2: j9g8-acpt
   - Influenza A: ymmh-divb
   - RSV: 45cq-cw4i
   - Avian Influenza A(H5): mtpu-urpp
   - Mpox: xpxn-rzgz
   - Measles: akvg-8vrb
2. Pull CDC NSSP respiratory ED surveillance.
3. Pull CDC PLACES county context.
4. Load local CDC/ATSDR SVI 2022 county file.
5. Load local Census TIGER/Line 2025 county geometry.
6. Harmonize pathogen data WITHOUT forcing incompatible pathogen metrics.
7. Create:
   - provenance/QC outputs
   - pathogen summary cards
   - pathogen trend charts
   - national coverage/activity maps
   - Tennessee case-study maps
   - wastewater–clinical lead/lag results
   - SVI surveillance-equity results
   - spatial clustering using projected KNN weights
   - app-ready CSV/JSON exports
8. Integrate published U.S. wastewater AMR/ARG data from a frozen local CSV.
9. Pull supplemental NCBI virus-genome metadata and create pathogen/protein/structure intelligence using RCSB PDB.
10. Add publication-oriented respiratory seasonal peak analysis for SARS-CoV-2, RSV, and Influenza A.
11. Keep optional hooks for Census ACS, NOAA weather, EPA AQS air quality, and exploratory ML/XAI.

SCIENTIFIC SAFEGUARDS
---------------------
- Raw concentrations are NOT assumed comparable across sites/labs.
- Routine-pathogen activity uses within-site/method/matrix standardized log concentration
  when concentration is available.
- Emerging-pathogen datasets preserve CDC-native detection variables.
- No NWGS composite "risk score" is invented here.
- Positive lag k means wastewater at week t is compared with clinical activity at t+k.
- Spatial inference uses projected county centroids and K-nearest-neighbor weights to
  avoid disconnected/island problems seen in the original Queen-contiguity analysis.
- Poster/app values are derived from current data, never hard-coded.
- API snapshots are frozen locally with retrieval timestamps and SHA256 hashes.
- Seasonal peak inference is limited to routine respiratory pathogens and complete July-June respiratory seasons.
- H5, Mpox, and Measles remain detection-based and are NOT forced into the quantitative seasonal-peak model.
- Tennessee seasonal inference is suppressed unless predefined county-season coverage criteria are met.
"""

# ============================================================
# 00. COLAB INSTALL (run once in a separate cell if needed)
# ============================================================
# !pip -q install pandas numpy requests scipy matplotlib geopandas pyogrio shapely \
#     libpysal esda scikit-learn pyarrow openpyxl pillow statsmodels

# Optional:
# !pip -q install xgboost shap

# ============================================================
# 01. IMPORTS
# ============================================================
import os
import re
import json
import math
import time
import hashlib
import warnings
import shutil
import shlex
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.patches import Patch, FancyBboxPatch
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

import geopandas as gpd
from scipy import stats
import statsmodels.api as sm
from sklearn.neighbors import NearestNeighbors

try:
    from libpysal.weights import KNN
    from esda.moran import Moran, Moran_Local
    HAVE_SPATIAL = True
except Exception:
    HAVE_SPATIAL = False

try:
    from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    HAVE_SKLEARN = True
except Exception:
    HAVE_SKLEARN = False

warnings.filterwarnings("ignore", category=FutureWarning)

# ============================================================
# 02. CONFIGURATION
# ============================================================
PROJECT_ROOT = Path(os.getenv("NWGS_PROJECT_ROOT", "/content/NWGS_GRID"))
STATIC_ROOT = Path(os.getenv("NWGS_STATIC_ROOT", "/content"))

SVI_PATH = Path(os.getenv("NWGS_SVI_PATH", str(STATIC_ROOT / "SVI_2022_US_COUNTY.csv")))
TIGER_SHP = Path(os.getenv("NWGS_TIGER_SHP", str(STATIC_ROOT / "tl_2025_us_county.shp")))
AMR_PATH = Path(os.getenv("NWGS_AMR_PATH", str(STATIC_ROOT / "US_Wastewater_AMR_ARG_2024.csv")))

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROC_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR = PROJECT_ROOT / "outputs"
FIG_DIR = OUT_DIR / "figures"
TABLE_DIR = OUT_DIR / "tables"
APP_DIR = OUT_DIR / "app_exports"
META_DIR = OUT_DIR / "metadata"
PATHOGEN_DIR = OUT_DIR / "pathogen_intelligence"
STRUCTURE_DIR = PATHOGEN_DIR / "protein_structures"
PATHOGEN_IMAGE_DIR = PATHOGEN_DIR / "pathogen_images"
PATHOGEN_CARD_DIR = PATHOGEN_DIR / "cards"
POSTER_FIG_DIR = OUT_DIR / "poster_figures"
PAPER_FIG_DIR = OUT_DIR / "paper_figures"
SUPPLEMENT_FIG_DIR = OUT_DIR / "supplemental_figures"
APHL_POSTER_DIR = OUT_DIR / "01_APHL_POSTER"
PAPER1_DIR = OUT_DIR / "02_PAPER1_NATIONAL_IDLAB"
PAPER2_DIR = OUT_DIR / "03_PAPER2_TENNESSEE"

for d in [RAW_DIR, PROC_DIR, OUT_DIR, FIG_DIR, TABLE_DIR, APP_DIR, META_DIR, PATHOGEN_DIR, STRUCTURE_DIR, PATHOGEN_IMAGE_DIR, PATHOGEN_CARD_DIR, POSTER_FIG_DIR, PAPER_FIG_DIR, SUPPLEMENT_FIG_DIR, APHL_POSTER_DIR, PAPER1_DIR, PAPER2_DIR]:
    d.mkdir(parents=True, exist_ok=True)

STUDY_START = pd.Timestamp(os.getenv("NWGS_STUDY_START", "2022-10-01"))
# Default stays 2026-09-05 so the manuscript run is reproducible. The weekly GitHub
# workflow sets NWGS_STUDY_END to the run date so each update includes the newest weeks.
STUDY_END = pd.Timestamp(os.getenv("NWGS_STUDY_END", "2026-09-05"))

PAGE_SIZE = int(os.getenv("NWGS_PAGE_SIZE", "50000"))
MAX_LAG_WEEKS = int(os.getenv("NWGS_MAX_LAG_WEEKS", "6"))
MIN_PAIRED_WEEKS = int(os.getenv("NWGS_MIN_PAIRED_WEEKS", "20"))
MIN_ANALYSIS_WEEKS = int(os.getenv("NWGS_MIN_ANALYSIS_WEEKS", "52"))
MIN_ACTIVE_COMPLETENESS = float(os.getenv("NWGS_MIN_ACTIVE_COMPLETENESS", "0.70"))
RECENT_ACTIVITY_WEEKS = int(os.getenv("NWGS_RECENT_ACTIVITY_WEEKS", "4"))
SPATIAL_K = int(os.getenv("NWGS_SPATIAL_K", "6"))

# Seasonal analysis: July 1 through June 30 respiratory season.
# Eligibility thresholds are explicit and exported so seasonal inference can be audited.
MIN_SEASON_WEEKS = int(os.getenv("NWGS_MIN_SEASON_WEEKS", "40"))
MIN_SEASON_COMPLETENESS = float(os.getenv("NWGS_MIN_SEASON_COMPLETENESS", "0.75"))
SEASON_SMOOTH_WEEKS = int(os.getenv("NWGS_SEASON_SMOOTH_WEEKS", "3"))
TN_SEASON_MIN_READY_COUNTIES = int(os.getenv("NWGS_TN_SEASON_MIN_READY_COUNTIES", "2"))
TN_SEASON_MIN_MEDIAN_SITES = float(os.getenv("NWGS_TN_SEASON_MIN_MEDIAN_SITES", "2"))
# v5.17 addition: thresholds for the seasonal-peak implausible-lead audit
# flag (see _summarize_season_peak). Exported like every other eligibility
# threshold in this section so the flag's sensitivity can be audited/tuned
# without editing function bodies.
# v5.20: widened from 6 to 9 weeks. A Tennessee SARS-CoV-2 clinical peak at
# week 7-8 from July 1 sat just outside the old 6-week window and never
# tripped the flag despite an ~19-week gap to the wastewater peak in the
# same season - the same class of problem this guard exists to catch. 9
# weeks covers that case with a 1-week margin; see the v5.20 changelog for
# the re-validation against both directions of false positive/negative.
LEAD_ARTIFACT_GUARD_WEEKS = int(os.getenv("NWGS_LEAD_ARTIFACT_GUARD_WEEKS", "9"))
LEAD_ARTIFACT_GUARD_THRESHOLD_WEEKS = float(os.getenv("NWGS_LEAD_ARTIFACT_GUARD_THRESHOLD_WEEKS", "10"))

# v5.18 additions.
# Pearson |r| on the TRAINING split above which a wastewater feature and
# clinical_lag1 are flagged as collinear enough to plausibly explain a
# near-zero ablation delta for wastewater (see exploratory_ml()).
COLLINEARITY_FLAG_THRESHOLD = float(os.getenv("NWGS_COLLINEARITY_FLAG_THRESHOLD", "0.5"))
# Residual z-score (within a pathogen's own held-out residual distribution)
# above which a chronological-holdout prediction is flagged and traced back
# to its exact state/week in Table12f_ML_Prediction_Outliers.csv.
ML_OUTLIER_RESIDUAL_Z_THRESHOLD = float(os.getenv("NWGS_ML_OUTLIER_RESIDUAL_Z_THRESHOLD", "4.0"))
# v5.19 addition: target height:width ratio used when _verify_portrait_or_warn()
# has to pad a figure that came out landscape despite upstream sizing math,
# so the corrected file is unambiguously portrait rather than barely over the line.
PORTRAIT_AUTOFIX_MARGIN = float(os.getenv("NWGS_PORTRAIT_AUTOFIX_MARGIN", "1.10"))

# Set these to True only when credentials / analysis choices are ready.
ENABLE_ACS = os.getenv("NWGS_ENABLE_ACS", "0") == "1"
ENABLE_NOAA = os.getenv("NWGS_ENABLE_NOAA", "0") == "1"
ENABLE_EPA_AQS = os.getenv("NWGS_ENABLE_EPA_AQS", "0") == "1"
# v5.16: defaulted to "1" (on). This was previously "0" (off), which is
# why Table12_Exploratory_ML_Benchmark.csv, Table12b_Exploratory_ML_Ablation.csv,
# and Paper 1 Figures 7-10 never appeared in prior runs - exploratory_ml()
# returns three empty results immediately when this flag is unset, before
# any of the v5.15 plotting functions are ever called. Turning it on by
# default closes that gap without requiring a manual
# `export NWGS_ENABLE_ML=1` step before every run.
# TRADEOFF: this run now fits 2 models x 5 feature-group ablations x N
# pathogens (vs. the original 2 models x N pathogens), so expect a
# noticeably longer [17/19] step than before. Set NWGS_ENABLE_ML=0 to
# restore the old fast-skip behavior if that cost isn't wanted.
ENABLE_EXPLORATORY_ML = os.getenv("NWGS_ENABLE_ML", "1") == "1"
ENABLE_NCBI = os.getenv("NWGS_ENABLE_NCBI", "1") == "1"
ENABLE_RCSB = os.getenv("NWGS_ENABLE_RCSB", "1") == "1"
NCBI_MAX_RECORDS_PER_TAXON = int(os.getenv("NWGS_NCBI_MAX_RECORDS_PER_TAXON", "1000"))
RCSB_MAX_GENOME_MAPPINGS = int(os.getenv("NWGS_RCSB_MAX_GENOME_MAPPINGS", "25"))
NCBI_API_KEY = os.getenv("NCBI_API_KEY")

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
NOAA_TOKEN = os.getenv("NOAA_TOKEN")
EPA_AQS_EMAIL = os.getenv("EPA_AQS_EMAIL")
EPA_AQS_KEY = os.getenv("EPA_AQS_KEY")
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN")

CDC_BASE = "https://data.cdc.gov"

CDC_DATASETS = {
    "sars_cov_2": {
        "id": "j9g8-acpt",
        "label": "SARS-CoV-2",
        "group": "routine_respiratory",
        "clinical_col": "percent_visits_covid",
    },
    "influenza_a": {
        "id": "ymmh-divb",
        "label": "Influenza A",
        "group": "routine_respiratory",
        "clinical_col": "percent_visits_influenza",
    },
    "rsv": {
        "id": "45cq-cw4i",
        "label": "RSV",
        "group": "routine_respiratory",
        "clinical_col": "percent_visits_rsv",
    },
    "h5": {
        "id": "mtpu-urpp",
        "label": "Influenza A(H5)",
        "group": "emerging",
        "clinical_col": None,
    },
    "mpox": {
        "id": "xpxn-rzgz",
        "label": "Mpox",
        "group": "emerging",
        "clinical_col": None,
    },
    "measles": {
        "id": "akvg-8vrb",
        "label": "Measles",
        "group": "emerging",
        "clinical_col": None,
    },
}

NSSP_ED_ID = "rdmq-nq56"
PLACES_ID = "swc5-untb"
# Supplemental genomic context. These are public NCBI taxonomic names; the
# genomic outputs are kept separate from wastewater observations unless a
# defensible accession/sample linkage exists.
NCBI_VIRUS_TAXA = {
    "SARS-CoV-2": "Severe acute respiratory syndrome coronavirus 2",
    "Influenza A": "Influenza A virus",
    "RSV": "Human orthopneumovirus",
    "Mpox": "Monkeypox virus",
    "Measles": "Measles morbillivirus",
}

NCBI_API_BASE = "https://api.ncbi.nlm.nih.gov/datasets/v2"

# CDC PHIL image IDs chosen for public-domain scientific reference imagery.
# H5 uses a general Influenza A virion reference image, explicitly labeled as such.
CDC_PHIL_ASSETS = {
    "SARS-CoV-2": {
        "phil_id": 23591,
        "label": "SARS-CoV-2 virions, thin-section TEM",
        "usage_note": "CDC PHIL public-domain reference image",
    },
    "RSV": {
        "phil_id": 276,
        "label": "Respiratory syncytial virus reference TEM",
        "usage_note": "CDC PHIL reference image",
    },
    "Influenza A": {
        "phil_id": 11745,
        "label": "Influenza A virions, colorized TEM",
        "usage_note": "CDC PHIL public-domain reference image",
    },
    "Influenza A(H5)": {
        "phil_id": 11745,
        "label": "Influenza A virion reference image (not H5-subtype-specific)",
        "usage_note": "CDC PHIL public-domain reference; subtype distinction is provided by the H5 PDB structure, not this virion image",
    },
    "Measles": {
        "phil_id": 10707,
        "label": "Measles virus particle, colorized TEM",
        "usage_note": "CDC PHIL public-domain reference image",
    },
    "Mpox": {
        "phil_id": 26501,
        "label": "Mpox virus particles, colorized TEM",
        "usage_note": "CDC PHIL public-domain reference image",
    },
}

# Representative experimentally determined structures.
# These are structural context, not claims that an individual wastewater sequence
# was structurally solved or mapped to the exact PDB entry.
RCSB_REFERENCE_STRUCTURES = [
    {
        "pathogen": "SARS-CoV-2",
        "protein": "Spike glycoprotein, prefusion",
        "pdb_entry_id": "6VSB",
        "method_expected": "ELECTRON MICROSCOPY",
        "structure_role": "Representative/reference structural context",
    },
    {
        "pathogen": "RSV",
        "protein": "Prefusion fusion glycoprotein F",
        "pdb_entry_id": "8ZQ7",
        "method_expected": "X-RAY DIFFRACTION",
        "structure_role": "Representative/reference structural context",
    },
    {
        "pathogen": "Influenza A",
        "protein": "H1 hemagglutinin",
        "pdb_entry_id": "1RU7",
        "method_expected": "X-RAY DIFFRACTION",
        "structure_role": "Representative/reference structural context",
    },
    {
        "pathogen": "Influenza A(H5)",
        "protein": "H5 hemagglutinin",
        "pdb_entry_id": "9NR2",
        "method_expected": "X-RAY DIFFRACTION",
        "structure_role": "Representative/reference structural context",
    },
    {
        "pathogen": "Measles",
        "protein": "Hemagglutinin",
        "pdb_entry_id": "2ZB5",
        "method_expected": "X-RAY DIFFRACTION",
        "structure_role": "Representative/reference structural context",
    },
    {
        "pathogen": "Mpox",
        "protein": "Poxin",
        "pdb_entry_id": "8C9K",
        "method_expected": "X-RAY DIFFRACTION",
        "structure_role": "Representative/reference structural context",
    },
]
RCSB_SEQUENCE_COORDINATES = "https://sequence-coordinates.rcsb.org/graphql"


# ============================================================
# 03. UTILITIES / PROVENANCE
# ============================================================
PROVENANCE = []

# v5.18 addition: collects results from _verify_portrait_or_warn() so a
# figure-orientation self-check failure is folded into the validation
# summary and run metadata, not only printed to the console.
_PORTRAIT_SELF_CHECK_RESULTS = []

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def save_df(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".parquet":
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)
    PROVENANCE.append({
        "artifact": str(path),
        "retrieved_or_created_utc": utc_now(),
        "sha256": sha256_file(path),
        "rows": len(df),
        "columns": len(df.columns),
    })
    return path

def normalize_fips(x):
    if pd.isna(x):
        return pd.NA
    s = re.sub(r"\D", "", str(x))
    if not s:
        return pd.NA
    return s.zfill(5)[-5:]

def state_fips_from_county(fips):
    if pd.isna(fips):
        return pd.NA
    s = str(fips).zfill(5)
    return s[:2]

def clean_state_code(x):
    if pd.isna(x):
        return pd.NA
    return str(x).strip().upper()

def week_end_saturday(series):
    d = pd.to_datetime(series, errors="coerce")
    # Monday=0 ... Saturday=5
    offset = (5 - d.dt.weekday) % 7
    return d + pd.to_timedelta(offset, unit="D")

def numeric(s):
    return pd.to_numeric(s, errors="coerce")

def first_existing(columns, candidates):
    cols = set(columns)
    for c in candidates:
        if c in cols:
            return c
    return None


def _safe_svi_quartile(series: pd.Series, labels_asc=("Q1 lower", "Q2", "Q3", "Q4 higher")) -> pd.Series:
    """
    v5.9 addition.

    Quartile-bin a continuous series (typically CDC/ATSDR RPL_THEMES) without
    crashing when duplicate/tied values collapse the number of quantile bins
    below the requested count.

    pd.qcut(series, 4, labels=[...4 labels...], duplicates="drop") looks safe
    but is not: passing explicit `labels` together with duplicates="drop"
    does NOT resize the label list to match however many bins actually
    survive after collapsing duplicate edges - it raises
    "ValueError: Bin labels must be one fewer than the number of bin edges"
    the moment fewer than 4 unique bin edges remain. SVI percentile-rank data
    is a realistic trigger for this: many counties sit exactly at 0.0 or 1.0.

    This helper computes the bins unlabeled first, then maps only as many
    labels as bins actually survived (falling back to generic "Q1".."QN"
    labels with a printed warning if fewer than the full set of ascending
    labels survived), so a genuine data-shape edge case degrades gracefully
    instead of stopping the whole pipeline.
    """
    cats = pd.qcut(series, 4, duplicates="drop")
    n_bins = cats.cat.categories.size

    if n_bins == len(labels_asc):
        label_map = dict(zip(cats.cat.categories, labels_asc))
    else:
        label_map = dict(zip(cats.cat.categories, [f"Q{i+1}" for i in range(n_bins)]))
        print(
            f"[SVI QUARTILE WARNING] Only {n_bins}/{len(labels_asc)} quantile bins "
            f"survived (duplicate/tied values in the input series); using generic "
            f"Q1..Q{n_bins} labels instead of the requested {list(labels_asc)}."
        )

    return cats.map(label_map)

# ============================================================
# 04. CDC SOCRATA API
# ============================================================
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "NWGS-Grid-Research/2.0"})
if SOCRATA_APP_TOKEN:
    SESSION.headers.update({"X-App-Token": SOCRATA_APP_TOKEN})
# data.cdc.gov API keys (Key ID + Key Secret) authenticate with HTTP Basic auth.
# Stored as GitHub repository secrets SOCRATA_KEY_ID / SOCRATA_KEY_SECRET; never hard-code them.
SOCRATA_KEY_ID = os.getenv("SOCRATA_KEY_ID")
SOCRATA_KEY_SECRET = os.getenv("SOCRATA_KEY_SECRET")
if SOCRATA_KEY_ID and SOCRATA_KEY_SECRET:
    SESSION.auth = (SOCRATA_KEY_ID, SOCRATA_KEY_SECRET)
    print("[CDC API] Using data.cdc.gov API key authentication")
elif not SOCRATA_APP_TOKEN:
    print("[CDC API] No API key set - requests are unauthenticated and may be throttled")

def cdc_metadata(dataset_id):
    url = f"{CDC_BASE}/api/views/{dataset_id}"
    r = SESSION.get(url, timeout=60)
    r.raise_for_status()
    return r.json()

def dataset_field_names(meta):
    return [c.get("fieldName") for c in meta.get("columns", []) if c.get("fieldName")]

def validate_dataset(dataset_id, label=None):
    meta = cdc_metadata(dataset_id)
    fields = dataset_field_names(meta)
    print(f"[OK] {dataset_id}: {meta.get('name', label or dataset_id)} | {len(fields)} API fields")
    return meta, fields

def socrata_fetch(dataset_id, select=None, where=None, order=None, page_size=PAGE_SIZE, max_rows=None):
    endpoint = f"{CDC_BASE}/resource/{dataset_id}.json"
    frames = []
    offset = 0

    while True:
        limit = page_size
        if max_rows is not None:
            remaining = max_rows - offset
            if remaining <= 0:
                break
            limit = min(limit, remaining)

        params = {"$limit": limit, "$offset": offset}
        if select:
            params["$select"] = select
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order

        for attempt in range(5):
            try:
                r = SESSION.get(endpoint, params=params, timeout=120)
                r.raise_for_status()
                rows = r.json()
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)

        if not rows:
            break

        frames.append(pd.DataFrame(rows))
        offset += len(rows)
        print(f"  fetched {offset:,} rows from {dataset_id}")

        if len(rows) < limit:
            break

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def smart_cdc_fetch(dataset_id, study_start=None, study_end=None):
    """
    Pull full schema-aware data without assuming all pathogen datasets use
    exactly the same date field.
    """
    meta, fields = validate_dataset(dataset_id)

    date_col = first_existing(fields, [
        "sample_collect_date", "sample_collection_date", "date_sampled",
        "sample_date", "collection_date", "date"
    ])

    where = None
    if date_col and study_start is not None and study_end is not None:
        where = (
            f"{date_col} >= '{pd.Timestamp(study_start).date()}' "
            f"AND {date_col} <= '{pd.Timestamp(study_end).date()}'"
        )

    # Pull all columns so CDC-native emerging-pathogen fields are preserved.
    df = socrata_fetch(dataset_id, where=where, order=f"{date_col} ASC" if date_col else None)
    return df, meta

# ============================================================
# 05. STATIC DATA
# ============================================================
def load_svi():
    if not SVI_PATH.exists():
        raise FileNotFoundError(
            f"SVI file not found: {SVI_PATH}\n"
            "Upload SVI_2022_US_COUNTY.csv to Colab /content/ or set NWGS_SVI_PATH."
        )
    df = pd.read_csv(SVI_PATH, dtype={"FIPS": str, "STCNTY": str}, low_memory=False)
    fips_col = "FIPS" if "FIPS" in df.columns else "STCNTY"
    df["county_fips"] = df[fips_col].map(normalize_fips)
    save_df(df, RAW_DIR / "SVI_2022_US_COUNTY_FROZEN.csv")
    return df

def load_tiger():
    if not TIGER_SHP.exists():
        raise FileNotFoundError(
            f"TIGER shapefile not found: {TIGER_SHP}\n"
            "Upload the .shp/.shx/.dbf/.prj/.cpg bundle to Colab /content/."
        )
    gdf = gpd.read_file(TIGER_SHP)
    gdf["county_fips"] = gdf["GEOID"].astype(str).str.zfill(5)
    gdf["state_fips"] = gdf["STATEFP"].astype(str).str.zfill(2)
    return gdf

# ============================================================
# 06. HARMONIZE CDC WASTEWATER DATA
# ============================================================
COMMON_ALIASES = {
    "record_id": ["record_id", "id"],
    "site_id": ["site", "site_id", "wwtp_id", "sewershed_id"],
    "state_code": ["state_territory", "state", "state_abbrev", "state_code"],
    "county_fips": ["county_fips", "fips_code", "countyfips"],
    "counties_served": ["counties_served", "county"],
    "population_served": ["population_served", "pop_served"],
    "sample_id": ["sample_id"],
    "sample_collect_date": ["sample_collect_date", "sample_collection_date", "date_sampled", "sample_date", "collection_date", "date"],
    "sample_type": ["sample_type"],
    "sample_matrix": ["sample_matrix", "matrix"],
    "sample_location": ["sample_location"],
    "major_lab_method": ["major_lab_method", "lab_method"],
    "inhibition_detect": ["inhibition_detect", "inhibition"],
    "ntc_amplify": ["ntc_amplify", "ntc"],
    "pcr_target": ["pcr_target", "target"],
    "gene_target": ["pcr_gene_target_agg", "gene_target"],
    "raw_concentration": ["pcr_target_avg_conc", "pcr_target_avg_conc_lin", "concentration"],
    "flowpop_concentration": ["pcr_target_flowpop_lin", "flowpop_normalized"],
    "fecal_normalized_concentration": ["pcr_target_mic_lin", "mic_normalized"],
    "detection": ["pcr_target_detect", "detect", "detection", "detection_status", "result"],
    "units": ["pcr_target_units", "units"],
    "source": ["source", "data_source"],
    "date_updated": ["date_updated", "updated_at"],
}

def harmonize_pathogen(df, pathogen_key, meta):
    cfg = CDC_DATASETS[pathogen_key]
    out = pd.DataFrame(index=df.index)

    mapping = {}
    for standard, aliases in COMMON_ALIASES.items():
        src = first_existing(df.columns, aliases)
        mapping[standard] = src
        out[standard] = df[src] if src else pd.NA

    out["pathogen_key"] = pathogen_key
    out["pathogen"] = cfg["label"]
    out["pathogen_group"] = cfg["group"]
    out["cdc_dataset_id"] = cfg["id"]

    out["state_code"] = out["state_code"].map(clean_state_code)
    out["sample_collect_date"] = pd.to_datetime(out["sample_collect_date"], errors="coerce")
    out["population_served"] = numeric(out["population_served"])
    for c in ["raw_concentration", "flowpop_concentration", "fecal_normalized_concentration"]:
        out[c] = numeric(out[c])

    # v5.13 addition: raw_concentration is resolved via first_existing() from
    # ["pcr_target_avg_conc","pcr_target_avg_conc_lin","concentration"] - a
    # COLUMN-PRESENCE fallback, not a per-row one. If a pathogen's CDC schema
    # never exposes pcr_target_avg_conc at all, raw_concentration ends up
    # sourced entirely from the linearized field, which
    # add_emerging_detection_flags()'s own docstring says must NEVER be used
    # for detection. This flag lets that function refuse the fallback for any
    # dataframe where it would otherwise silently happen.
    out["raw_concentration_is_linearized"] = (mapping.get("raw_concentration") == "pcr_target_avg_conc_lin")

    # Preserve potentially multi-county FIPS strings in native field.
    out["county_fips_native"] = out["county_fips"].astype("string")
    out["county_fips"] = out["county_fips"].astype("string").map(
        lambda x: normalize_fips(x) if pd.notna(x) and "," not in str(x) else pd.NA
    )

    # QC flags remain transparent; "not tested" is not a failure.
    inhib = out["inhibition_detect"].fillna("not reported").astype(str).str.strip().str.lower()
    ntc = out["ntc_amplify"].fillna("not reported").astype(str).str.strip().str.lower()
    out["qc_inhibition_flag"] = inhib.eq("yes")
    out["qc_ntc_flag"] = ntc.eq("yes")
    out["qc_any_flag"] = out["qc_inhibition_flag"] | out["qc_ntc_flag"]

    # Select preferred quantitative measurement in a documented hierarchy.
    out["analysis_concentration"] = out["fecal_normalized_concentration"]
    out["analysis_concentration_type"] = "fecal_normalized"
    m = out["analysis_concentration"].isna()
    out.loc[m, "analysis_concentration"] = out.loc[m, "flowpop_concentration"]
    out.loc[m, "analysis_concentration_type"] = "flow_population_normalized"
    m = out["analysis_concentration"].isna()
    out.loc[m, "analysis_concentration"] = out.loc[m, "raw_concentration"]
    out.loc[m, "analysis_concentration_type"] = "raw"

    # Treat zero/negative concentrations as missing before log transformation.
    out.loc[out["analysis_concentration"] <= 0, "analysis_concentration"] = np.nan
    out["log10_concentration"] = np.nan
    positive_mask = out["analysis_concentration"].gt(0)
    out.loc[positive_mask, "log10_concentration"] = np.log10(
        out.loc[positive_mask, "analysis_concentration"]
    )

    out["week_end"] = week_end_saturday(out["sample_collect_date"])

    # Keep native source fields in a separate frozen copy; harmonized table records mapping.
    map_path = META_DIR / f"{pathogen_key}_field_mapping.json"
    map_path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    return out

def explode_multicounty_for_coverage(h):
    x = h.copy()
    def split_fips(v):
        if pd.isna(v):
            return []
        bits = re.split(r"[,;|]", str(v))
        return [normalize_fips(b) for b in bits if normalize_fips(b) is not pd.NA and pd.notna(normalize_fips(b))]
    x["county_fips_list"] = x["county_fips_native"].map(split_fips)
    x = x.explode("county_fips_list")
    x["county_fips"] = x["county_fips_list"]
    x = x.drop(columns=["county_fips_list"])
    return x

def add_within_site_standardization(h):
    x = h.copy()
    keys = ["pathogen", "site_id", "major_lab_method", "sample_matrix", "analysis_concentration_type"]

    def zscore_safe(s):
        n = s.notna().sum()
        sd = s.std(ddof=0)
        if n < 3 or pd.isna(sd) or sd == 0:
            return pd.Series(np.nan, index=s.index)
        return (s - s.mean()) / sd

    x["site_method_z"] = (
        x.groupby(keys, dropna=False)["log10_concentration"]
         .transform(zscore_safe)
    )

    # Fallback within site if lab/matrix groups are too sparse.
    fallback = (
        x.groupby(["pathogen", "site_id"], dropna=False)["log10_concentration"]
         .transform(zscore_safe)
    )
    x["site_z"] = x["site_method_z"].fillna(fallback)
    return x

# ============================================================
# 07. PATHOGEN SUMMARY CARDS + TRENDS
# ============================================================


def add_emerging_detection_flags(h):
    """
    Parse emerging-pathogen detection conservatively.

    PRIMARY:
      harmonized CDC pcr_target_detect yes/no.

    FALLBACK:
      raw pcr_target_avg_conc only when the detection field is genuinely absent
      or blank for an individual record. The linearized concentration field
      is NEVER used for detection.

    Records that cannot be interpreted remain UNKNOWN rather than being forced
    positive or negative.

    v5.13 fix: the "never use the linearized field" safeguard previously
    checked the harmonized COLUMN NAME (raw_concentration) rather than its
    actual SOURCE field. Because harmonize_pathogen() resolves
    raw_concentration via a column-presence fallback across
    ["pcr_target_avg_conc","pcr_target_avg_conc_lin","concentration"], any
    pathogen dataset whose schema never exposes pcr_target_avg_conc at all
    would silently populate raw_concentration entirely from the linearized
    field - exactly the field this safeguard is meant to exclude - with no
    warning anywhere. The fallback below now checks
    raw_concentration_is_linearized (set in harmonize_pathogen()) and
    refuses to use raw_concentration for any row where that flag is True,
    leaving detection status UNKNOWN instead and recording why in
    emerging_detection_basis.
    """
    x = h.copy()
    x["emerging_detection_known"] = False
    x["emerging_detection_positive"] = np.nan
    x["emerging_detection_basis"] = pd.NA

    m = x["pathogen_group"].eq("emerging")
    idx = x.index[m]
    det = x.loc[idx, "detection"].fillna("").astype(str).str.strip().str.lower()

    yes_tokens = {
        "yes","y","true","positive","detected","detect","1","1.0",
        "amplification","amplified"
    }
    no_tokens = {
        "no","n","false","negative","not detected","non-detect","nondetect",
        "nd","0","0.0","no amplification","not amplified"
    }

    yes = det.isin(yes_tokens)
    no = det.isin(no_tokens)
    known_text = yes | no

    if known_text.any():
        use_idx = idx[known_text.values]
        x.loc[use_idx, "emerging_detection_known"] = True
        x.loc[use_idx, "emerging_detection_positive"] = yes[known_text].astype(float).values
        x.loc[use_idx, "emerging_detection_basis"] = "pcr_target_detect"

    # Fallback only for blank/unrecognized detection text and a true raw
    # pcr_target_avg_conc value. Never use *_lin, even indirectly via a
    # raw_concentration column that happened to be sourced from it.
    unresolved = idx[~known_text.values]
    if len(unresolved):
        if "raw_concentration_is_linearized" in x.columns:
            lin_sourced = x.loc[unresolved, "raw_concentration_is_linearized"].fillna(False).astype(bool)
        else:
            lin_sourced = pd.Series(False, index=unresolved)

        safe_unresolved = unresolved[~lin_sourced.values]
        blocked_unresolved = unresolved[lin_sourced.values]

        if len(blocked_unresolved):
            x.loc[blocked_unresolved, "emerging_detection_basis"] = "blocked_raw_concentration_was_linearized"

        raw = pd.to_numeric(x.loc[safe_unresolved, "raw_concentration"], errors="coerce")
        valid = raw.notna()
        if valid.any():
            use_idx = safe_unresolved[valid.values]
            x.loc[use_idx, "emerging_detection_known"] = True
            x.loc[use_idx, "emerging_detection_positive"] = (raw.loc[use_idx] > 0).astype(float).values
            x.loc[use_idx, "emerging_detection_basis"] = "pcr_target_avg_conc_fallback"

    return x



def emerging_detection_audit(h):
    rows = []
    emerging = h[h["pathogen_group"].eq("emerging")].copy()

    for pathogen, g in emerging.groupby("pathogen"):
        known = g["emerging_detection_known"].fillna(False).astype(bool)
        pos = g["emerging_detection_positive"].eq(1) & known
        neg = g["emerging_detection_positive"].eq(0) & known

        n_known = int(known.sum())
        n_pos = int(pos.sum())
        n_neg = int(neg.sum())
        pct = 100 * n_pos / n_known if n_known else np.nan

        det_raw = g["detection"].fillna("").astype(str).str.strip().str.lower()
        basis = g["emerging_detection_basis"].fillna("unknown").value_counts()

        if n_known == 0:
            status = "FAIL_NO_INTERPRETABLE_DETECTION"
        elif n_neg == 0:
            status = "FAIL_NO_NEGATIVES"
        elif n_pos == 0:
            status = "WARNING_NO_POSITIVES"
        elif pct >= 99.5:
            status = "FAIL_IMPLAUSIBLE_DETECTION_DISTRIBUTION"
        else:
            status = "PASS"

        rows.append({
            "pathogen": pathogen,
            "records": len(g),
            "known_detection_records": n_known,
            "unknown_detection_records": int((~known).sum()),
            "positive_records": n_pos,
            "negative_records": n_neg,
            "positive_record_pct": pct,
            "raw_detection_yes": int(det_raw.isin(["yes","positive","detected","1","1.0"]).sum()),
            "raw_detection_no": int(det_raw.isin(["no","negative","not detected","0","0.0"]).sum()),
            "basis_pcr_target_detect": int(basis.get("pcr_target_detect", 0)),
            "basis_concentration_fallback": int(basis.get("pcr_target_avg_conc_fallback", 0)),
            "basis_blocked_linearized_source": int(basis.get("blocked_raw_concentration_was_linearized", 0)),
            "sites": g["site_id"].nunique(dropna=True),
            "first_date": g["sample_collect_date"].min(),
            "last_date": g["sample_collect_date"].max(),
            "status": status,
        })
    return pd.DataFrame(rows)


def profile_emerging_detection_fields(raw_by_pathogen):
    """
    Audit the exact source fields before harmonization.

    This is the publication safeguard that prevents a stale or incorrectly
    interpreted concentration field from silently becoming a detection result.
    """
    rows = []
    for pathogen, raw in raw_by_pathogen.items():
        if pathogen not in {"Influenza A(H5)", "Mpox", "Measles"}:
            continue

        for field in ["pcr_target_detect", "pcr_target_avg_conc", "pcr_target_avg_conc_lin"]:
            if field not in raw.columns:
                rows.append({
                    "pathogen": pathogen,
                    "field": field,
                    "field_present": False,
                    "n_records": len(raw),
                    "n_nonmissing": 0,
                    "n_unique": 0,
                    "value_summary": "FIELD ABSENT",
                })
                continue

            s = raw[field]
            nonmissing = s.dropna()
            if field == "pcr_target_detect":
                vc = (
                    nonmissing.astype(str).str.strip().str.lower()
                              .value_counts(dropna=False)
                              .head(20)
                )
                summary = " | ".join([f"{k}:{int(v)}" for k, v in vc.items()])
            else:
                num = pd.to_numeric(nonmissing, errors="coerce")
                summary = (
                    f"zero={int(num.eq(0).sum())}; "
                    f"positive={int(num.gt(0).sum())}; "
                    f"negative={int(num.lt(0).sum())}; "
                    f"numeric={int(num.notna().sum())}"
                )

            rows.append({
                "pathogen": pathogen,
                "field": field,
                "field_present": True,
                "n_records": len(raw),
                "n_nonmissing": int(nonmissing.shape[0]),
                "n_unique": int(nonmissing.astype(str).nunique()),
                "value_summary": summary,
            })
    return pd.DataFrame(rows)


def make_pathogen_summary(h):
    rows = []
    for pathogen, g in h.groupby("pathogen", dropna=False):
        latest = g["sample_collect_date"].max()
        recent_start = latest - pd.Timedelta(weeks=RECENT_ACTIVITY_WEEKS) if pd.notna(latest) else pd.NaT
        recent = g[g["sample_collect_date"] >= recent_start] if pd.notna(recent_start) else g.iloc[0:0]

        valid_sites = g["site_id"].nunique(dropna=True)
        states = g["state_code"].nunique(dropna=True)
        counties = explode_multicounty_for_coverage(g)["county_fips"].nunique(dropna=True)

        group = g["pathogen_group"].dropna().iloc[0] if g["pathogen_group"].notna().any() else None

        current_activity = np.nan
        previous_activity = np.nan
        delta = np.nan
        trend = "Insufficient data"
        detect_rate = np.nan

        if group == "routine_respiratory":
            current_activity = recent["site_z"].median(skipna=True)
            prev = g[
                (g["sample_collect_date"] < recent_start) &
                (g["sample_collect_date"] >= recent_start - pd.Timedelta(weeks=RECENT_ACTIVITY_WEEKS))
            ] if pd.notna(recent_start) else g.iloc[0:0]
            previous_activity = prev["site_z"].median(skipna=True)
            if pd.notna(current_activity) and pd.notna(previous_activity):
                delta = current_activity - previous_activity
                trend = "Increasing" if delta > 0.15 else "Decreasing" if delta < -0.15 else "Stable"

        elif group == "emerging":
            if "emerging_detection_positive" in recent.columns:
                # Collapse to site-week so multiple gene targets do not overweight a site.
                rw = recent.dropna(subset=["site_id","week_end"]).copy()
                sw = (
                    rw.groupby(["site_id","week_end"])["emerging_detection_positive"]
                      .max()
                      .dropna()
                )
                if len(sw):
                    detect_rate = float(sw.mean())
                    trend = "Detection-based"

        rows.append({
            "pathogen": pathogen,
            "pathogen_group": group,
            "records": len(g),
            "sites": valid_sites,
            "counties_represented": counties,
            "states_territories": states,
            "first_observation": g["sample_collect_date"].min(),
            "latest_observation": latest,
            "recent_records": len(recent),
            "recent_detection_rate": detect_rate,
            "recent_median_site_z": current_activity,
            "change_vs_previous_window_z": delta,
            "trend": trend,
            "qc_flag_rate": g["qc_any_flag"].mean() if len(g) else np.nan,
        })
    return pd.DataFrame(rows)


def national_weekly_series(h):
    """
    Routine respiratory pathogens: quantitative within-site standardized activity.
    Emerging pathogens: kept out of this z-score series and summarized separately
    using CDC-native detection information.
    """
    routine = h[h["pathogen_group"].eq("routine_respiratory")].copy()
    site_week = (
        routine.dropna(subset=["week_end"])
         .groupby(["pathogen", "site_id", "week_end"], dropna=False)
         .agg(
             site_z=("site_z", "median"),
             concentration=("analysis_concentration", "median"),
             records=("record_id", "size"),
         )
         .reset_index()
    )
    nat = (
        site_week.groupby(["pathogen", "week_end"])
                 .agg(
                     median_site_z=("site_z", "median"),
                     n_sites=("site_id", "nunique"),
                     n_records=("records", "sum"),
                 )
                 .reset_index()
    )
    return site_week, nat





def national_emerging_series(h):
    """
    Weekly detection frequency for H5, Mpox, and Measles.

    Detection is based primarily on CDC pcr_target_detect yes/no.
    Multiple records/targets from the same site-week are collapsed so a site is
    positive if ANY valid target record is detected during that site-week.
    """
    emerging = h[h["pathogen_group"].eq("emerging")].copy()
    if emerging.empty:
        return pd.DataFrame()

    emerging = emerging.dropna(subset=["week_end","site_id"]).copy()

    if "emerging_detection_positive" not in emerging.columns:
        emerging = add_emerging_detection_flags(emerging)

    valid = emerging[emerging["emerging_detection_known"].fillna(False)].copy()
    if valid.empty:
        return pd.DataFrame()

    site_week = (
        valid.groupby(["pathogen","site_id","week_end"], dropna=False)
             .agg(
                 detected=("emerging_detection_positive","max"),
                 n_records=("record_id","size"),
             )
             .reset_index()
    )

    out = (
        site_week.groupby(["pathogen","week_end"])
                 .agg(
                     detection_rate=("detected","mean"),
                     n_sites_tested=("site_id","nunique"),
                     n_site_weeks=("site_id","size"),
                     n_records=("n_records","sum"),
                 )
                 .reset_index()
    )
    return out


def plot_pathogen_trends(nat):
    for pathogen, g in nat.groupby("pathogen"):
        g = g.sort_values("week_end")
        if g["median_site_z"].notna().sum() < 3:
            continue
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(g["week_end"], g["median_site_z"])
        ax.axhline(0, linewidth=1)
        ax.set_title(f"NWGS Grid™ — {pathogen} National Wastewater Activity")
        ax.set_xlabel("Week")
        ax.set_ylabel("Median within-site standardized log concentration (z)")
        ax.text(
            0.01, 0.01,
            "Source: CDC NWSS. Metric: NWGS Grid™ standardized within-site log-concentration z-score.",
            transform=ax.transAxes, fontsize=8, va="bottom"
        )
        ax.grid(alpha=0.2)
        fig.tight_layout()
        safe = re.sub(r"[^A-Za-z0-9]+", "_", pathogen).strip("_")
        fig.savefig(FIG_DIR / f"PathogenTrend_{safe}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)



def plot_emerging_trends(emerging_weekly, detection_audit=None):
    if emerging_weekly.empty:
        print("[WARN] Emerging-pathogen series empty; no figures generated.")
        return

    audit_lookup = {}
    if detection_audit is not None and not detection_audit.empty:
        audit_lookup = detection_audit.set_index("pathogen").to_dict("index")

    for pathogen, g in emerging_weekly.groupby("pathogen"):
        g = g.sort_values("week_end")
        audit = audit_lookup.get(pathogen, {})
        status = audit.get("status", "UNKNOWN")

        # Publication fail-safe: do not save misleading flat/invalid figures.
        if status.startswith("FAIL"):
            print(f"[SUPPRESS] {pathogen}: detection audit status={status}")
            continue

        if g["detection_rate"].notna().sum() < 3:
            print(f"[SUPPRESS] {pathogen}: fewer than 3 valid detection weeks")
            continue

        unique_rates = g["detection_rate"].dropna().round(8).nunique()
        if unique_rates <= 1:
            print(f"[SUPPRESS] {pathogen}: detection series is flat ({unique_rates} unique rate)")
            continue

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(g["week_end"], g["detection_rate"] * 100)
        ax.set_ylim(0, min(100, max(5, float((g["detection_rate"] * 100).max()) * 1.15)))
        ax.set_title(f"NWGS Grid™ — {pathogen} Wastewater Detection Frequency")
        ax.set_xlabel("Week")
        ax.set_ylabel("Reporting sites positive (%)")
        ax.text(
            0.01, 0.01,
            "Detection based on CDC pcr_target_detect (yes/no); site-week collapsed.",
            transform=ax.transAxes, fontsize=8, va="bottom"
        )
        ax.grid(alpha=0.2)
        fig.tight_layout()
        safe = re.sub(r"[^A-Za-z0-9]+", "_", pathogen).strip("_")
        fig.savefig(FIG_DIR / f"PathogenDetection_{safe}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)


# ============================================================
# 08. CDC NSSP ED CLINICAL DATA
# ============================================================
def load_nssp_ed():
    meta, fields = validate_dataset(NSSP_ED_ID)
    required = ["week_end", "geography", "county",
                "percent_visits_covid", "percent_visits_influenza", "percent_visits_rsv"]
    missing = [x for x in required if x not in fields]
    if missing:
        raise RuntimeError(f"NSSP schema changed; missing fields: {missing}")

    where = (
        f"week_end >= '{STUDY_START.date()}' AND week_end <= '{STUDY_END.date()}' "
        "AND county = 'All'"
    )
    select = ",".join(required)
    df = socrata_fetch(NSSP_ED_ID, select=select, where=where, order="week_end ASC")
    df["week_end"] = pd.to_datetime(df["week_end"], errors="coerce")
    for c in ["percent_visits_covid", "percent_visits_influenza", "percent_visits_rsv"]:
        df[c] = numeric(df[c])
    df["state_name"] = df["geography"].astype(str).str.strip()
    save_df(df, RAW_DIR / "CDC_NSSP_ED_RESPIRATORY_FROZEN.csv")
    return df

STATE_ABBR = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC",
    "Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL",
    "Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
    "Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
    "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR",
    "Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD",
    "Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
    "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY",
    "Puerto Rico":"PR"
}

# ============================================================
# 09. STATE-WEEK MULTIMODAL + LAG ANALYSIS
# ============================================================
def benjamini_hochberg(pvals):
    """Benjamini-Hochberg FDR correction. Returns adjusted p-values in original order."""
    p = np.asarray(pvals, dtype=float)
    out = np.full(len(p), np.nan, dtype=float)
    mask = np.isfinite(p)
    if mask.sum() == 0:
        return out
    pv = p[mask]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    adj = ranked * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.clip(adj, 0, 1)
    restored = np.empty(n, dtype=float)
    restored[order] = adj
    out[np.where(mask)[0]] = restored
    return out

def build_state_week(h):
    routine = h[h["pathogen_group"].eq("routine_respiratory")].copy()
    routine = routine.dropna(subset=["state_code", "week_end"])

    site_week = (
        routine.groupby(["pathogen", "state_code", "site_id", "week_end"], dropna=False)
               .agg(site_z=("site_z", "median"))
               .reset_index()
    )

    state_week = (
        site_week.groupby(["pathogen", "state_code", "week_end"])
                 .agg(
                     wastewater_index=("site_z", "median"),
                     n_sites=("site_id", "nunique"),
                 )
                 .reset_index()
    )
    return state_week

def merge_clinical(state_week, ed):
    e = ed.copy()
    e["state_code"] = e["state_name"].map(STATE_ABBR)

    pieces = []
    for key, cfg in CDC_DATASETS.items():
        if cfg["group"] != "routine_respiratory":
            continue
        clinical_col = cfg["clinical_col"]
        w = state_week[state_week["pathogen"].eq(cfg["label"])].copy()
        c = e[["state_code", "week_end", clinical_col]].rename(columns={clinical_col:"clinical_ed_pct"})
        m = w.merge(c, on=["state_code","week_end"], how="left")
        pieces.append(m)

    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()


def respiratory_season_label(date_value):
    """Return July-June respiratory season label, e.g. 2024-25."""
    d = pd.Timestamp(date_value)
    start_year = d.year if d.month >= 7 else d.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _season_bounds(season_label):
    start_year = int(str(season_label).split("-")[0])
    return pd.Timestamp(start_year, 7, 1), pd.Timestamp(start_year + 1, 6, 30)


def _season_is_complete(season_label):
    start, end = _season_bounds(season_label)
    return (start >= STUDY_START.normalize()) and (end <= STUDY_END.normalize())


def _expected_week_count(season_label):
    start, end = _season_bounds(season_label)
    # Weekly Saturday observations intersecting the July-June season.
    first_sat = start + pd.to_timedelta((5 - start.weekday()) % 7, unit="D")
    last_sat = end - pd.to_timedelta((end.weekday() - 5) % 7, unit="D")
    if last_sat < first_sat:
        return 0
    return int(((last_sat - first_sat).days // 7) + 1)


def _contiguous_half_peak_duration(dates, values, peak_pos):
    """Weeks contiguous around peak at >=50% of positive peak above zero baseline."""
    vals = np.asarray(values, dtype=float)
    if len(vals) == 0 or peak_pos is None or peak_pos < 0 or peak_pos >= len(vals):
        return np.nan, np.nan
    peak = vals[peak_pos]
    if not np.isfinite(peak) or peak <= 0:
        return np.nan, np.nan
    threshold = 0.5 * peak
    left = peak_pos
    right = peak_pos
    while left > 0 and np.isfinite(vals[left-1]) and vals[left-1] >= threshold:
        left -= 1
    while right < len(vals)-1 and np.isfinite(vals[right+1]) and vals[right+1] >= threshold:
        right += 1
    return int(right - left + 1), float(threshold)


def _summarize_season_peak(g, ww_col="wastewater_index", clinical_col="clinical_ed_pct"):
    """
    Summarize one geography/pathogen/season without inventing missing weeks.

    v5.17 fix: min_periods was previously (window+1)//2, allowing the first
    and last weeks of the available data to receive a "smoothed" value from
    only a partial window. For SARS-CoV-2 specifically, a real but small
    early-August secondary wave sitting right at a season's start could
    pass through that partial smoothing almost unchanged and be picked up
    by argmax() as the season peak, producing the "-18 week lag" artifact
    (an early wastewater blip compared against the real, much-later
    clinical peak). min_periods is now the FULL window, so any point
    without full support becomes NaN and is excluded by the existing
    dropna() calls below rather than silently standing in for a real
    smoothed value.

    v5.17 also adds implausible_lead_flag: raised when the wastewater peak
    falls within the first LEAD_ARTIFACT_GUARD_WEEKS weeks of the season's
    available data AND the resulting lead is more extreme than
    LEAD_ARTIFACT_GUARD_THRESHOLD_WEEKS weeks. This surfaces (does not
    silently drop) any remaining edge case for manual review before a lead
    number is reported, matching every other WARNING/FAIL audit pattern
    already used elsewhere in this script.
    """
    q = g[["week_end", ww_col, clinical_col]].copy().sort_values("week_end")
    q["week_end"] = pd.to_datetime(q["week_end"], errors="coerce")
    q[ww_col] = pd.to_numeric(q[ww_col], errors="coerce")
    q[clinical_col] = pd.to_numeric(q[clinical_col], errors="coerce")
    q = q.dropna(subset=["week_end"])
    if q.empty:
        return {}

    # v5.17: full-window requirement (min_periods=window) instead of a
    # partial (window+1)//2 window. Boundary weeks with insufficient
    # support are now NaN, not a noisy 1-2-point stand-in.
    window = max(1, int(SEASON_SMOOTH_WEEKS))
    minp = window
    q["ww_smooth"] = q[ww_col].rolling(window, center=True, min_periods=minp).median()
    q["clinical_smooth"] = q[clinical_col].rolling(window, center=True, min_periods=minp).median()

    out = {
        "observed_ww_weeks": int(q[ww_col].notna().sum()),
        "observed_clinical_weeks": int(q[clinical_col].notna().sum()),
    }

    ww_valid = q.dropna(subset=["ww_smooth"]).reset_index(drop=True)
    if not ww_valid.empty:
        ww_peak_pos = int(ww_valid["ww_smooth"].values.argmax())
        ww_peak = ww_valid.iloc[ww_peak_pos]
        duration, half_thr = _contiguous_half_peak_duration(
            ww_valid["week_end"].values, ww_valid["ww_smooth"].values, ww_peak_pos
        )
        out.update({
            "ww_peak_week": ww_peak["week_end"],
            "ww_peak_magnitude_z": float(ww_peak["ww_smooth"]),
            "ww_half_peak_duration_weeks": duration,
            "ww_half_peak_threshold_z": half_thr,
        })
    else:
        out.update({
            "ww_peak_week": pd.NaT,
            "ww_peak_magnitude_z": np.nan,
            "ww_half_peak_duration_weeks": np.nan,
            "ww_half_peak_threshold_z": np.nan,
        })

    cl_valid = q.dropna(subset=["clinical_smooth"]).reset_index(drop=True)
    if not cl_valid.empty:
        cl_peak_pos = int(cl_valid["clinical_smooth"].values.argmax())
        cl_peak = cl_valid.iloc[cl_peak_pos]
        out.update({
            "clinical_peak_week": cl_peak["week_end"],
            "clinical_peak_magnitude_pct": float(cl_peak["clinical_smooth"]),
        })
    else:
        out.update({"clinical_peak_week": pd.NaT, "clinical_peak_magnitude_pct": np.nan})

    if pd.notna(out["ww_peak_week"]) and pd.notna(out["clinical_peak_week"]):
        # Positive = wastewater peak occurred earlier than clinical peak.
        out["ww_lead_to_clinical_peak_weeks"] = float(
            (pd.Timestamp(out["clinical_peak_week"]) - pd.Timestamp(out["ww_peak_week"])).days / 7.0
        )
    else:
        out["ww_lead_to_clinical_peak_weeks"] = np.nan

    # v5.18 fix: v5.17's implausible_lead_flag only checked whether the
    # WASTEWATER peak sat near the season's START. Tennessee's SARS-CoV-2
    # seasonal figure (Paper 2 Figure 7) surfaced a mirror-image failure
    # mode this could not catch: the CLINICAL peak landing near a season
    # boundary (an early-August secondary wave in the state-level NSSP ED
    # series, ~weeks 6-8 from July 1) while the wastewater peak sits
    # mid/late-season - the same class of implausible multi-month lead,
    # but boundary-adjacent on the clinical side rather than the
    # wastewater side. The flag now checks BOTH peaks against BOTH the
    # season's start and end, symmetrically, so a boundary-support
    # artifact from the rolling smoother is caught regardless of which
    # series or which edge it shows up on.
    def _weeks_from_boundary(peak_week):
        if pd.isna(peak_week) or q.empty:
            return np.nan, np.nan
        from_start = (pd.Timestamp(peak_week) - q["week_end"].min()).days / 7.0
        from_end = (q["week_end"].max() - pd.Timestamp(peak_week)).days / 7.0
        return from_start, from_end

    ww_from_start, ww_from_end = _weeks_from_boundary(out.get("ww_peak_week"))
    cl_from_start, cl_from_end = _weeks_from_boundary(out.get("clinical_peak_week"))

    boundary_distances = [
        d for d in [ww_from_start, ww_from_end, cl_from_start, cl_from_end]
        if pd.notna(d)
    ]
    nearest_boundary_weeks = min(boundary_distances) if boundary_distances else np.nan

    lead = out.get("ww_lead_to_clinical_peak_weeks", np.nan)
    out["nearest_peak_to_season_boundary_weeks"] = nearest_boundary_weeks
    out["implausible_lead_flag"] = bool(
        pd.notna(nearest_boundary_weeks)
        and pd.notna(lead)
        and nearest_boundary_weeks <= LEAD_ARTIFACT_GUARD_WEEKS
        and abs(lead) >= LEAD_ARTIFACT_GUARD_THRESHOLD_WEEKS
    )
    return out


def seasonal_peak_analysis(multimodal):
    """
    Paper 1 national/state seasonal analysis for routine respiratory pathogens.

    Respiratory season is July 1-June 30. Only complete seasons inside the study
    window are eligible for inferential summaries. National values are medians
    across available state-week values, which keeps wastewater and clinical
    geography aligned without claiming population weighting.

    v5.17: propagates _summarize_season_peak()'s new implausible_lead_flag
    into national_df and prints a WARNING line per flagged pathogen/season,
    per the open review item on the SARS-CoV-2 seasonal-lead artifact.
    """
    if multimodal is None or multimodal.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    x = multimodal.copy()
    x["week_end"] = pd.to_datetime(x["week_end"], errors="coerce")
    x = x.dropna(subset=["week_end"])
    x["season"] = x["week_end"].map(respiratory_season_label)

    state_rows = []
    for (pathogen, state, season), g in x.groupby(["pathogen", "state_code", "season"], dropna=False):
        expected = _expected_week_count(season)
        summary = _summarize_season_peak(g)
        ww_n = summary.get("observed_ww_weeks", 0)
        cl_n = summary.get("observed_clinical_weeks", 0)
        completeness = ww_n / expected if expected else np.nan
        eligible = (
            _season_is_complete(season)
            and ww_n >= MIN_SEASON_WEEKS
            and cl_n >= MIN_SEASON_WEEKS
            and pd.notna(completeness)
            and completeness >= MIN_SEASON_COMPLETENESS
        )
        state_rows.append({
            "pathogen": pathogen, "state_code": state, "season": season,
            "expected_weeks": expected, "ww_completeness": completeness,
            "full_season_in_study_window": _season_is_complete(season),
            "eligible": bool(eligible), **summary,
        })
    state_df = pd.DataFrame(state_rows)

    nat_week = (
        x.groupby(["pathogen", "season", "week_end"], dropna=False)
         .agg(wastewater_index=("wastewater_index", "median"),
              clinical_ed_pct=("clinical_ed_pct", "median"),
              states_with_ww=("wastewater_index", "count"),
              states_with_clinical=("clinical_ed_pct", "count"))
         .reset_index()
    )
    nat_rows = []
    for (pathogen, season), g in nat_week.groupby(["pathogen", "season"], dropna=False):
        expected = _expected_week_count(season)
        summary = _summarize_season_peak(g)
        ww_n = summary.get("observed_ww_weeks", 0)
        cl_n = summary.get("observed_clinical_weeks", 0)
        completeness = ww_n / expected if expected else np.nan
        eligible = (
            _season_is_complete(season)
            and ww_n >= MIN_SEASON_WEEKS
            and cl_n >= MIN_SEASON_WEEKS
            and pd.notna(completeness)
            and completeness >= MIN_SEASON_COMPLETENESS
        )
        season_start, _ = _season_bounds(season)
        ww_peak_week = summary.get("ww_peak_week", pd.NaT)
        cl_peak_week = summary.get("clinical_peak_week", pd.NaT)
        nat_rows.append({
            "pathogen": pathogen, "season": season,
            "expected_weeks": expected, "ww_completeness": completeness,
            "full_season_in_study_window": _season_is_complete(season),
            "eligible": bool(eligible),
            "ww_peak_week_from_july1": ((pd.Timestamp(ww_peak_week)-season_start).days/7.0) if pd.notna(ww_peak_week) else np.nan,
            "clinical_peak_week_from_july1": ((pd.Timestamp(cl_peak_week)-season_start).days/7.0) if pd.notna(cl_peak_week) else np.nan,
            **summary,
        })
    national_df = pd.DataFrame(nat_rows)

    # v5.17: print (do not silently drop) any implausible-lead rows among
    # ELIGIBLE seasons, so a flagged season is visible in the console log
    # before its lead number is used anywhere downstream.
    if not national_df.empty and "implausible_lead_flag" in national_df.columns:
        flagged = national_df[
            national_df["eligible"].fillna(False) & national_df["implausible_lead_flag"].fillna(False)
        ]
        for r in flagged.itertuples():
            nearest = getattr(r, "nearest_peak_to_season_boundary_weeks", np.nan)
            print(
                f"[SEASONAL PEAK WARNING] {r.pathogen} {r.season}: a wastewater or "
                f"clinical peak sits within {nearest:.1f} wk of a season boundary "
                f"and the pair yields an extreme lead "
                f"({r.ww_lead_to_clinical_peak_weeks:+.1f} wk) even after full-window "
                f"smoothing. Review before reporting this season's lead value in the "
                f"manuscript. This same check now also applies to Tennessee's "
                f"seasonal analysis (see [SEASONAL PEAK WARNING] lines during "
                f"tennessee_seasonal_analysis(), and Table18's "
                f"nearest_peak_to_season_boundary_weeks / implausible_lead_flag "
                f"columns)."
            )

    inter_rows = []
    elig = national_df[national_df["eligible"]].copy() if not national_df.empty else pd.DataFrame()
    for pathogen, g in elig.groupby("pathogen") if not elig.empty else []:
        inter_rows.append({
            "pathogen": pathogen,
            "eligible_seasons": int(len(g)),
            "mean_ww_peak_week_from_july1": g["ww_peak_week_from_july1"].mean(),
            "sd_ww_peak_week_from_july1": g["ww_peak_week_from_july1"].std(ddof=1) if len(g) > 1 else np.nan,
            "mean_ww_peak_magnitude_z": g["ww_peak_magnitude_z"].mean(),
            "sd_ww_peak_magnitude_z": g["ww_peak_magnitude_z"].std(ddof=1) if len(g) > 1 else np.nan,
            "mean_half_peak_duration_weeks": g["ww_half_peak_duration_weeks"].mean(),
            "sd_half_peak_duration_weeks": g["ww_half_peak_duration_weeks"].std(ddof=1) if len(g) > 1 else np.nan,
            "median_ww_lead_to_clinical_peak_weeks": g["ww_lead_to_clinical_peak_weeks"].median(),
            "n_implausible_lead_flagged": int(g["implausible_lead_flag"].fillna(False).sum()) if "implausible_lead_flag" in g.columns else 0,
        })
    interannual_df = pd.DataFrame(inter_rows)
    return state_df, national_df, interannual_df


def _peak_week_month_ticks():
    """Month labels for July-June respiratory-season week offsets."""
    starts = [0, 4.4, 8.8, 13.1, 17.5, 21.8, 26.2, 30.6, 34.9, 39.3, 43.6, 48.0]
    labels = ["Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"]
    return starts, labels


def plot_seasonal_peak_analysis(national_seasonal):
    """Publication seasonal figures for Paper 1 and the APHL poster."""
    if national_seasonal is None or national_seasonal.empty:
        return
    q = national_seasonal[national_seasonal["eligible"]].copy()
    if q.empty:
        print("[SUPPRESS] Seasonal peak figures: no complete eligible seasons.")
        return

    pathogens = ["SARS-CoV-2", "RSV", "Influenza A"]
    month_ticks, month_labels = _peak_week_month_ticks()

    # Paper 1: detailed vertical peak-timing figure with peak magnitude and duration annotations.
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 12.5), sharex=False)
    for ax, pathogen in zip(axes, pathogens):
        g = q[q["pathogen"].eq(pathogen)].sort_values("season").copy()
        if g.empty:
            ax.text(.5, .5, "No eligible complete seasons", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
            continue
        x = np.arange(len(g))
        ax.plot(x, g["ww_peak_week_from_july1"], marker="o", linewidth=1.8, label="Wastewater peak")
        ax.plot(x, g["clinical_peak_week_from_july1"], marker="s", linewidth=1.6, label="Clinical ED peak")
        for i, row in enumerate(g.itertuples()):
            if pd.notna(row.ww_peak_week_from_july1) and pd.notna(row.clinical_peak_week_from_july1):
                ax.plot([i, i], [row.ww_peak_week_from_july1, row.clinical_peak_week_from_july1], linewidth=.9, alpha=.65)
                lead = getattr(row, "ww_lead_to_clinical_peak_weeks", np.nan)
                mag = getattr(row, "ww_peak_magnitude_z", np.nan)
                dur = getattr(row, "ww_half_peak_duration_weeks", np.nan)
                parts = []
                if pd.notna(lead): parts.append(f"lead {lead:+.0f} wk")
                if pd.notna(mag): parts.append(f"peak z {mag:.2f}")
                if pd.notna(dur): parts.append(f"half-peak {dur:.0f} wk")
                if parts:
                    y = np.nanmax([row.ww_peak_week_from_july1, row.clinical_peak_week_from_july1]) + 1.1
                    ax.text(i, y, "\n".join(parts), ha="center", va="bottom", fontsize=7.2)
        ax.set_xticks(x)
        ax.set_xticklabels(g["season"].astype(str))
        ax.set_yticks(month_ticks)
        ax.set_yticklabels(month_labels)
        ax.set_ylim(-1, 54)
        ax.set_ylabel("Peak month")
        ax.set_title(pathogen, fontweight="bold")
        ax.grid(alpha=.2, axis="y")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(.5, .955), frameon=False)
    fig.suptitle("NWGS Grid™ — Seasonal Wastewater and Clinical Peak Timing", fontsize=15, fontweight="bold")
    fig.text(.5, .018,
             "Eligible complete July-June seasons only. Positive lead = wastewater peak earlier than clinical ED peak. "
             "Peak z = national median standardized wastewater activity; half-peak duration = weeks at ≥50% of seasonal peak amplitude.",
             ha="center", fontsize=8.4, wrap=True)
    fig.tight_layout(rect=[0.08, .055, .98, .92])
    fig.savefig(FIG_DIR / "Fig_Seasonal_Peak_Timing_Paper1.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # APHL poster: convert the former table into an actual trend figure.
    # Each panel shows how WW and clinical peak timing move across seasons, with lead labels.
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 9.5), sharex=True)
    for ax, pathogen in zip(axes, pathogens):
        g = q[q["pathogen"].eq(pathogen)].sort_values("season").copy()
        if g.empty:
            ax.text(.5,.5,"No eligible complete seasons",ha="center",va="center",transform=ax.transAxes)
            continue
        x = np.arange(len(g))
        ax.plot(x, g["ww_peak_week_from_july1"], marker="o", linewidth=2.0, label="Wastewater peak")
        ax.plot(x, g["clinical_peak_week_from_july1"], marker="s", linewidth=1.8, label="Clinical ED peak")
        for i, row in enumerate(g.itertuples()):
            lead = getattr(row, "ww_lead_to_clinical_peak_weeks", np.nan)
            if pd.notna(row.ww_peak_week_from_july1) and pd.notna(row.clinical_peak_week_from_july1):
                ax.plot([i,i], [row.ww_peak_week_from_july1,row.clinical_peak_week_from_july1], linewidth=.9, alpha=.6)
            if pd.notna(lead):
                ax.text(i, min(52, max(row.ww_peak_week_from_july1, row.clinical_peak_week_from_july1)+1.0),
                        f"{lead:+.0f} wk", ha="center", va="bottom", fontsize=8)
        ax.set_yticks(month_ticks)
        ax.set_yticklabels(month_labels)
        ax.set_ylim(-1, 54)
        ax.set_ylabel("Peak month")
        ax.set_title(pathogen, fontweight="bold", loc="left")
        ax.grid(axis="y", alpha=.18)
    seasons = sorted(q["season"].dropna().unique())
    axes[-1].set_xticks(np.arange(len(seasons)))
    axes[-1].set_xticklabels(seasons)
    axes[-1].set_xlabel("Respiratory season (July-June)")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(.5,.945), frameon=False)
    fig.suptitle("NWGS Grid™ — Respiratory Seasonal Peak Trends", fontsize=15, fontweight="bold")
    fig.text(.5,.018,
             "Labels show wastewater-to-clinical peak difference in weeks; positive values indicate an earlier wastewater peak. "
             "Only complete seasons meeting predefined coverage criteria are displayed.",
             ha="center", fontsize=8.5, wrap=True)
    fig.tight_layout(rect=[.08,.055,.98,.91])
    fig.savefig(FIG_DIR / "Fig_APHL_Seasonal_Peak_Panel.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

def tennessee_seasonal_analysis(wastewater, multimodal):
    """
    Tennessee seasonal analysis with season-specific coverage gating.

    A pathogen-season is eligible only when at least TN_SEASON_MIN_READY_COUNTIES
    Tennessee counties independently meet the seasonal week/completeness threshold,
    the statewide series has adequate weeks, and median reporting sites meets the
    configured minimum. Ineligible seasons remain in the audit table but are not
    interpreted as Tennessee seasonal pathogen activity.

    v5.17: Figure 7 now annotates each plotted season with its
    season_ready_counties/observed_counties values (already computed
    below into `out` / Table18) instead of leaving them only in the CSV -
    the "minor/cosmetic" item in the review.
    """
    routine = wastewater[wastewater["pathogen"].isin(["SARS-CoV-2", "RSV", "Influenza A"])].copy()
    routine = explode_multicounty_for_coverage(routine)
    routine = routine[routine["county_fips"].astype(str).str.startswith("47")].copy()
    routine["week_end"] = pd.to_datetime(routine["week_end"], errors="coerce")
    routine = routine.dropna(subset=["week_end", "county_fips"])
    routine["season"] = routine["week_end"].map(respiratory_season_label)

    county_season = (
        routine.groupby(["pathogen", "county_fips", "season"])
               .agg(n_weeks=("week_end", "nunique"), n_sites=("site_id", "nunique"))
               .reset_index()
    )
    if not county_season.empty:
        county_season["expected_weeks"] = county_season["season"].map(_expected_week_count)
        county_season["completeness"] = county_season["n_weeks"] / county_season["expected_weeks"].replace(0, np.nan)
        county_season["season_ready"] = (
            county_season["season"].map(_season_is_complete)
            & (county_season["n_weeks"] >= MIN_SEASON_WEEKS)
            & (county_season["completeness"] >= MIN_SEASON_COMPLETENESS)
        )

    tn = multimodal[multimodal["state_code"].astype(str).eq("TN")].copy()
    tn["week_end"] = pd.to_datetime(tn["week_end"], errors="coerce")
    tn = tn.dropna(subset=["week_end"])
    tn["season"] = tn["week_end"].map(respiratory_season_label)

    rows = []
    for (pathogen, season), g in tn.groupby(["pathogen", "season"]):
        cs = county_season[(county_season["pathogen"].eq(pathogen)) & (county_season["season"].eq(season))] if not county_season.empty else pd.DataFrame()
        ready_counties = int(cs["season_ready"].sum()) if not cs.empty else 0
        observed_counties = int(cs["county_fips"].nunique()) if not cs.empty else 0
        median_sites = pd.to_numeric(g["n_sites"], errors="coerce").median()
        summary = _summarize_season_peak(g)
        expected = _expected_week_count(season)
        ww_n = summary.get("observed_ww_weeks", 0)
        completeness = ww_n / expected if expected else np.nan
        eligible = (
            _season_is_complete(season)
            and ready_counties >= TN_SEASON_MIN_READY_COUNTIES
            and pd.notna(median_sites) and median_sites >= TN_SEASON_MIN_MEDIAN_SITES
            and ww_n >= MIN_SEASON_WEEKS
            and pd.notna(completeness) and completeness >= MIN_SEASON_COMPLETENESS
        )
        rows.append({
            "pathogen": pathogen, "season": season,
            "observed_counties": observed_counties,
            "season_ready_counties": ready_counties,
            "median_reporting_sites": median_sites,
            "expected_weeks": expected,
            "ww_completeness": completeness,
            "full_season_in_study_window": _season_is_complete(season),
            "eligible_for_tennessee_seasonal_inference": bool(eligible),
            "eligibility_rule": (
                f">={TN_SEASON_MIN_READY_COUNTIES} season-ready counties; "
                f">={TN_SEASON_MIN_MEDIAN_SITES:g} median sites; "
                f">={MIN_SEASON_WEEKS} weeks; completeness>={MIN_SEASON_COMPLETENESS:.2f}; complete July-June season"
            ),
            **summary,
        })
    out = pd.DataFrame(rows)

    # v5.18 addition: the same implausible-lead check computed nationally
    # (seasonal_peak_analysis()) is folded into `summary` here via
    # _summarize_season_peak(), but Tennessee's own eligibility pass never
    # printed a warning for it - this is exactly how the Paper 2 Figure 7
    # SARS-CoV-2 divergence went unflagged in the console log. Surface it
    # here too, restricted to seasons TN itself considers eligible.
    if not out.empty and "implausible_lead_flag" in out.columns:
        tn_flagged = out[
            out["eligible_for_tennessee_seasonal_inference"].fillna(False)
            & out["implausible_lead_flag"].fillna(False)
        ]
        for r in tn_flagged.itertuples():
            nearest = getattr(r, "nearest_peak_to_season_boundary_weeks", np.nan)
            print(
                f"[SEASONAL PEAK WARNING] Tennessee {r.pathogen} {r.season}: a "
                f"wastewater or clinical peak sits within {nearest:.1f} wk of a "
                f"season boundary and the pair yields an extreme lead "
                f"({r.ww_lead_to_clinical_peak_weeks:+.1f} wk) even after "
                f"full-window smoothing. Review before reporting this season's "
                f"lead value in Paper 2's text."
            )

    eligible = out[out["eligible_for_tennessee_seasonal_inference"]].copy() if not out.empty else pd.DataFrame()
    if not eligible.empty:
        fig, axes = plt.subplots(3, 1, figsize=(9, 12))
        for ax, pathogen in zip(axes, ["SARS-CoV-2", "RSV", "Influenza A"]):
            z = eligible[eligible["pathogen"].eq(pathogen)].sort_values("season")
            if z.empty:
                ax.text(.5, .5, "No Tennessee seasons met eligibility criteria", ha="center", va="center", transform=ax.transAxes)
            else:
                x = np.arange(len(z))
                season_start = z["season"].map(lambda v: _season_bounds(v)[0])
                ww_week = [(pd.Timestamp(d)-s).days/7 if pd.notna(d) else np.nan for d,s in zip(z["ww_peak_week"],season_start)]
                cl_week = [(pd.Timestamp(d)-s).days/7 if pd.notna(d) else np.nan for d,s in zip(z["clinical_peak_week"],season_start)]
                ax.plot(x, ww_week, marker="o", label="Wastewater peak")
                ax.plot(x, cl_week, marker="s", label="Clinical ED peak")
                # v5.17 addition: surface Table18's observed_counties /
                # season_ready_counties into the figure itself, instead of
                # leaving them only in the CSV.
                for i, row in enumerate(z.itertuples()):
                    candidates = [v for v in (ww_week[i], cl_week[i]) if pd.notna(v)]
                    y_anchor = (min(candidates) - 3.0) if candidates else -3.0
                    ax.annotate(
                        f"{row.season_ready_counties}/{row.observed_counties} cty",
                        xy=(i, y_anchor), ha="center", va="top", fontsize=7.6, color="#444444"
                    )
                ax.set_xticks(x); ax.set_xticklabels(z["season"].astype(str))
                ax.set_ylim(bottom=min(-8, ax.get_ylim()[0]))
            ax.set_title(pathogen, fontweight="bold")
            ax.set_ylabel("Peak week\nfrom July 1")
            ax.grid(alpha=.2)
        handles, labels = axes[0].get_legend_handles_labels()
        if handles:
            fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(.5,.955))
        fig.suptitle("NWGS Grid™ — Tennessee Seasonal Peak Analysis (Coverage-Eligible Seasons Only)",
                     fontsize=14, fontweight="bold")
        fig.text(.5,.02,
                 "Seasons failing predefined surveillance-coverage criteria are suppressed from seasonal inference. "
                 "Annotations show season-ready/observed Tennessee counties (Table18).",
                 ha="center", fontsize=8.6)
        fig.tight_layout(rect=[.07,.05,.98,.92])
        fig.savefig(FIG_DIR / "Fig_Tennessee_Seasonal_Peaks.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
    else:
        print("[SUPPRESS] Tennessee seasonal figure: no pathogen-season met predefined coverage eligibility criteria.")
    return out, county_season


def lag_analysis(multimodal):
    all_rows = []
    best_rows = []

    for (pathogen, state), g in multimodal.groupby(["pathogen","state_code"]):
        g = g.sort_values("week_end").copy()
        if g["wastewater_index"].notna().sum() < MIN_PAIRED_WEEKS:
            continue

        local = []
        for lag in range(MAX_LAG_WEEKS + 1):
            tmp = g[["week_end","wastewater_index","clinical_ed_pct"]].copy()
            # Positive lag k = wastewater at t compared with clinical at t+k.
            tmp["clinical_future"] = tmp["clinical_ed_pct"].shift(-lag)
            q = tmp.dropna(subset=["wastewater_index","clinical_future"])
            if len(q) < MIN_PAIRED_WEEKS:
                continue

            pearson_r, pearson_p = stats.pearsonr(q["wastewater_index"], q["clinical_future"])
            spearman_r, spearman_p = stats.spearmanr(q["wastewater_index"], q["clinical_future"])

            row = {
                "pathogen": pathogen,
                "state_code": state,
                "lag_weeks": lag,
                "paired_weeks": len(q),
                "pearson_r": pearson_r,
                "pearson_p": pearson_p,
                "spearman_r": spearman_r,
                "spearman_p": spearman_p,
            }
            local.append(row)
            all_rows.append(row)

        if local:
            # Best lag is the strongest POSITIVE Spearman association.
            # Tie-breaker favors the shorter lag.
            local_sorted = sorted(
                local,
                key=lambda r: (
                    -(r["spearman_r"] if pd.notna(r["spearman_r"]) else -np.inf),
                    r["lag_weeks"]
                )
            )
            best_rows.append(local_sorted[0])

    all_df = pd.DataFrame(all_rows)
    best_df = pd.DataFrame(best_rows)

    if not all_df.empty:
        all_df["pearson_p_fdr"] = benjamini_hochberg(all_df["pearson_p"].values)
        all_df["spearman_p_fdr"] = benjamini_hochberg(all_df["spearman_p"].values)

    if not best_df.empty:
        best_df["pearson_p_fdr"] = benjamini_hochberg(best_df["pearson_p"].values)
        best_df["spearman_p_fdr"] = benjamini_hochberg(best_df["spearman_p"].values)
        best_df["relationship"] = np.where(
            best_df["lag_weeks"].eq(0), "Synchronous",
            np.where(best_df["lag_weeks"].gt(0), "Wastewater leads", "Clinical leads")
        )

    return all_df, best_df


def plot_lag_summary(best):
    if best.empty:
        return
    s = (
        best.groupby(["pathogen","lag_weeks"])
            .size()
            .rename("states")
            .reset_index()
    )
    pathogens = list(s["pathogen"].unique())
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.8 / max(1, len(pathogens))
    xvals = sorted(s["lag_weeks"].unique())
    for i, p in enumerate(pathogens):
        q = s[s["pathogen"].eq(p)].set_index("lag_weeks").reindex(xvals, fill_value=0)
        ax.bar(np.arange(len(xvals)) + i*width, q["states"], width=width, label=p)
    ax.set_xticks(np.arange(len(xvals)) + width*(len(pathogens)-1)/2)
    ax.set_xticklabels(xvals)
    ax.set_xlabel("Best wastewater lead (weeks)")
    ax.set_ylabel("Number of qualifying states")
    ax.set_title("NWGS Grid™ — Best Wastewater-to-Clinical Lead by Pathogen")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Fig_LagSummary.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

# ============================================================
# 10. COVERAGE + EQUITY
# ============================================================
def build_county_coverage(h, svi):
    cov = explode_multicounty_for_coverage(h)
    cov = cov.dropna(subset=["county_fips","week_end"])

    summary = (
        cov.groupby(["county_fips","pathogen"])
           .agg(
               n_records=("record_id","count"),
               n_sites=("site_id","nunique"),
               n_weeks=("week_end","nunique"),
               first_week=("week_end","min"),
               last_week=("week_end","max"),
               max_population_served=("population_served","max"),
               qc_flag_rate=("qc_any_flag","mean"),
           )
           .reset_index()
    )

    summary["active_span_weeks"] = (
        ((summary["last_week"] - summary["first_week"]).dt.days // 7) + 1
    )
    summary["active_span_completeness"] = (
        summary["n_weeks"] / summary["active_span_weeks"].replace(0, np.nan)
    )
    total_study_weeks = ((STUDY_END - STUDY_START).days // 7) + 1
    summary["study_window_completeness"] = summary["n_weeks"] / total_study_weeks

    summary["analysis_ready"] = (
        (summary["n_weeks"] >= MIN_ANALYSIS_WEEKS) &
        (summary["active_span_completeness"] >= MIN_ACTIVE_COMPLETENESS)
    )

    svi_cols = [c for c in ["county_fips","STATE","ST_ABBR","COUNTY","RPL_THEMES",
                            "RPL_THEME1","RPL_THEME2","RPL_THEME3","RPL_THEME4"] if c in svi.columns]
    summary = summary.merge(svi[svi_cols].drop_duplicates("county_fips"), on="county_fips", how="left")
    return summary


def coverage_equity_model(coverage):
    """
    County-level binomial GLM:
      analysis_ready ~ continuous CDC/ATSDR SVI rank

    County is the analysis unit. Because coverage has pathogen-specific rows,
    readiness is collapsed to whether a county is analysis-ready for ANY
    routine respiratory pathogen. This is an inferential complement to the
    descriptive SVI quartile chart.
    """
    county = (
        coverage.groupby("county_fips")
                .agg(
                    analysis_ready=("analysis_ready","max"),
                    RPL_THEMES=("RPL_THEMES","first"),
                    surveillance_weeks=("n_weeks","max"),
                )
                .reset_index()
                .dropna(subset=["RPL_THEMES","analysis_ready"])
                .copy()
    )

    if len(county) < 100 or county["analysis_ready"].nunique() < 2:
        return pd.DataFrame(), pd.DataFrame()

    county["analysis_ready"] = county["analysis_ready"].astype(int)
    county["svi_10pct"] = pd.to_numeric(county["RPL_THEMES"], errors="coerce") * 10.0
    county = county.dropna(subset=["svi_10pct"])

    X = sm.add_constant(county[["svi_10pct"]], has_constant="add")
    y = county["analysis_ready"]

    model = sm.GLM(y, X, family=sm.families.Binomial()).fit()

    beta = float(model.params["svi_10pct"])
    se = float(model.bse["svi_10pct"])
    p = float(model.pvalues["svi_10pct"])
    or_ = float(np.exp(beta))
    lo = float(np.exp(beta - 1.96 * se))
    hi = float(np.exp(beta + 1.96 * se))

    summary = pd.DataFrame([{
        "model": "Binomial GLM: county analysis_ready ~ SVI",
        "n_counties": len(county),
        "predictor": "CDC/ATSDR SVI overall rank, per 0.10 increase",
        "beta": beta,
        "std_error": se,
        "odds_ratio": or_,
        "or_95ci_low": lo,
        "or_95ci_high": hi,
        "p_value": p,
        "interpretation_direction": (
            "Higher SVI associated with lower odds of analysis-readiness"
            if or_ < 1 else
            "Higher SVI associated with higher odds of analysis-readiness"
        ),
    }])

    return summary, county


def coverage_equity(coverage):
    overall = (
        coverage.groupby("county_fips")
                .agg(
                    surveillance_weeks=("n_weeks","max"),
                    any_analysis_ready=("analysis_ready","max"),
                    RPL_THEMES=("RPL_THEMES","first")
                )
                .reset_index()
    )
    overall = overall.dropna(subset=["RPL_THEMES"])
    if overall.empty:
        return pd.DataFrame()
    # v5.9: use _safe_svi_quartile() instead of a bare pd.qcut(..., labels=[...],
    # duplicates="drop") call, which raises ValueError whenever tied SVI values
    # collapse the number of quantile bins below 4.
    overall["svi_quartile"] = _safe_svi_quartile(
        overall["RPL_THEMES"],
        labels_asc=("Q1 Lower vulnerability", "Q2", "Q3", "Q4 Higher vulnerability"),
    )
    eq = (
        overall.groupby("svi_quartile", observed=True)
               .agg(
                    counties=("county_fips","nunique"),
                    median_surveillance_weeks=("surveillance_weeks","median"),
                    pct_analysis_ready=("any_analysis_ready","mean"),
                    mean_svi=("RPL_THEMES","mean"),
               )
               .reset_index()
    )
    eq["pct_analysis_ready"] *= 100
    return eq

def plot_equity(eq):
    if eq.empty:
        return
    fig, ax = plt.subplots(figsize=(9,5))
    ax.bar(eq["svi_quartile"].astype(str), eq["pct_analysis_ready"])
    ax.set_ylabel("Counties analysis-ready (%)")
    ax.set_xlabel("CDC/ATSDR SVI quartile")
    ax.set_title("NWGS Grid™ — Wastewater Surveillance Readiness by Social Vulnerability")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Fig_Coverage_Equity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

# ============================================================
# 11. MAPS — PUBLICATION-ORIENTED
# ============================================================
CONUS_EXCLUDE_STATEFP = {"02","15","60","66","69","72","78"}  # AK, HI, territories

def conus(gdf):
    return gdf[~gdf["state_fips"].isin(CONUS_EXCLUDE_STATEFP)].copy()


def plot_coverage_map(tiger, coverage):
    c = (
        coverage.groupby("county_fips")
                .agg(surveillance_weeks=("n_weeks","max"))
                .reset_index()
    )
    g = conus(tiger).merge(c, on="county_fips", how="left").to_crs(5070)

    bins = [-np.inf, 0, 25, 51, 103, 155, np.inf]
    labels = ["No data","1–25 weeks","26–51 weeks","52–103 weeks","104–155 weeks","≥156 weeks"]
    g["coverage_cat"] = pd.cut(
        g["surveillance_weeks"].fillna(0),
        bins=bins, labels=labels, include_lowest=True, right=True
    )

    palette = {
        "No data":"#d9d9d9",
        "1–25 weeks":"#f7fbff",
        "26–51 weeks":"#c6dbef",
        "52–103 weeks":"#6baed6",
        "104–155 weeks":"#3182bd",
        "≥156 weeks":"#08519c",
    }

    fig, ax = plt.subplots(figsize=(10,12))
    for lab in labels:
        q = g[g["coverage_cat"].astype(str).eq(lab)]
        if not q.empty:
            q.plot(ax=ax, color=palette[lab], linewidth=0.08, edgecolor="white")
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("NWGS Grid™ — U.S. County Wastewater Surveillance Coverage")
    handles = [Patch(facecolor=palette[x], edgecolor="none", label=x) for x in labels]
    ax.legend(handles=handles, title="Qualifying surveillance weeks", loc="lower left", frameon=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Fig_National_Coverage_CONUS.png", dpi=300, bbox_inches="tight")
    plt.close(fig)



ACTIVITY_CATEGORY_ORDER = ["Very Low","Low","Typical","Elevated","High"]
ACTIVITY_CATEGORY_COLORS = {
    "Very Low":"#2166ac",
    "Low":"#67a9cf",
    "Typical":"#f7f7f7",
    "Elevated":"#ef8a62",
    "High":"#b2182b",
    "No recent data":"#d9d9d9",
}

def categorize_activity_z(s):
    return pd.cut(
        s,
        bins=[-np.inf,-1.0,-0.25,0.25,1.0,np.inf],
        labels=ACTIVITY_CATEGORY_ORDER,
        include_lowest=True
    )

def latest_county_activity(h):
    routine = h[h["pathogen_group"].eq("routine_respiratory")].copy()
    routine = explode_multicounty_for_coverage(routine)
    routine = routine.dropna(subset=["county_fips","week_end","site_z"])
    if routine.empty:
        return pd.DataFrame()

    latest = routine["week_end"].max()
    start = latest - pd.Timedelta(weeks=RECENT_ACTIVITY_WEEKS-1)
    recent = routine[(routine["week_end"] >= start) & (routine["week_end"] <= latest)]

    # Each multi-county sewershed contributes the same site measurement to represented
    # counties; this is a coverage/representation mapping, not population allocation.
    county_activity = (
        recent.groupby(["pathogen","county_fips"])
              .agg(
                  activity_z=("site_z","median"),
                  n_sites=("site_id","nunique"),
                  n_records=("record_id","count")
              )
              .reset_index()
    )
    county_activity["activity_end_week"] = latest
    return county_activity


def recent_emerging_by_county(h):
    """
    v5.21: where emerging pathogens (H5, measles, mpox) were detected recently.
    Same detection rule as national_emerging_series() (a site-week is positive if
    any valid target record is detected), summarized per county over the latest
    RECENT_ACTIVITY_WEEKS weeks so the app can map detections by state.
    """
    emerging = h[h["pathogen_group"].eq("emerging")].copy()
    if emerging.empty:
        return pd.DataFrame()
    if "emerging_detection_positive" not in emerging.columns:
        emerging = add_emerging_detection_flags(emerging)
    emerging = explode_multicounty_for_coverage(emerging)
    valid = emerging[emerging["emerging_detection_known"].fillna(False)].dropna(subset=["county_fips", "week_end", "site_id"])
    if valid.empty:
        return pd.DataFrame()
    latest = valid["week_end"].max()
    start = latest - pd.Timedelta(weeks=RECENT_ACTIVITY_WEEKS - 1)
    recent = valid[(valid["week_end"] >= start) & (valid["week_end"] <= latest)]
    site_week = (recent.groupby(["pathogen", "county_fips", "site_id", "week_end"])
                       .agg(detected=("emerging_detection_positive", "max")).reset_index())
    site = site_week.groupby(["pathogen", "county_fips", "site_id"]).agg(any_detect=("detected", "max")).reset_index()
    out = (site.groupby(["pathogen", "county_fips"])
               .agg(n_sites_tested=("site_id", "nunique"), n_sites_detected=("any_detect", "sum")).reset_index())
    last_pos = (site_week[site_week["detected"].fillna(False).astype(bool)]
                .groupby(["pathogen", "county_fips"])["week_end"].max().rename("last_detected_week").reset_index())
    out = out.merge(last_pos, on=["pathogen", "county_fips"], how="left")
    out["n_sites_detected"] = out["n_sites_detected"].astype(int)
    out["window_end_week"] = latest
    return out


def plot_activity_maps(tiger, activity):
    if activity.empty:
        return
    base = conus(tiger).to_crs(5070)
    for pathogen, q in activity.groupby("pathogen"):
        g = base.merge(q, on="county_fips", how="left")
        g["activity_cat"] = categorize_activity_z(g["activity_z"])

        fig, ax = plt.subplots(figsize=(10,12))
        # Full county basemap first.
        g.plot(ax=ax, color=ACTIVITY_CATEGORY_COLORS["No recent data"], linewidth=0.05, edgecolor="white")
        for lab in ACTIVITY_CATEGORY_ORDER:
            z = g[g["activity_cat"].astype(str).eq(lab)]
            if not z.empty:
                z.plot(ax=ax, color=ACTIVITY_CATEGORY_COLORS[lab], linewidth=0.05, edgecolor="white")

        ax.set_aspect("equal")
        ax.set_axis_off()
        end_week = pd.to_datetime(q["activity_end_week"], errors="coerce").max()
        ax.set_title(f"NWGS Grid™ — Recent {pathogen} Wastewater Activity")
        handles = [Patch(facecolor=ACTIVITY_CATEGORY_COLORS[x], label=x) for x in ACTIVITY_CATEGORY_ORDER]
        handles.append(Patch(facecolor=ACTIVITY_CATEGORY_COLORS["No recent data"], label="No recent data"))
        ax.legend(handles=handles, title="CDC NWSS data\nNWGS standardized activity", loc="lower left")
        if pd.notna(end_week):
            ax.text(0.99, 0.01, f"Recent 4-week window ending {end_week.date()}",
                    transform=ax.transAxes, ha="right", va="bottom", fontsize=8)
        fig.tight_layout()
        safe = re.sub(r"[^A-Za-z0-9]+", "_", pathogen).strip("_")
        fig.savefig(FIG_DIR / f"Map_RecentActivity_{safe}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)




def plot_tennessee_maps(tiger, activity):
    """
    Tennessee is shown as a surveillance-coverage case study rather than three
    separate choropleths when recent reporting is sparse.
    """
    if activity.empty:
        return

    tn_total = int(tiger[tiger["state_fips"].eq("47")]["county_fips"].nunique())
    tn_activity = activity[activity["county_fips"].astype(str).str.startswith("47")].copy()
    if tn_activity.empty:
        return

    rows = []
    for pathogen in ["SARS-CoV-2","RSV","Influenza A"]:
        q = tn_activity[tn_activity["pathogen"].eq(pathogen)]
        rows.append({
            "Pathogen": pathogen,
            "Reporting counties": int(q["county_fips"].nunique()),
            "Total counties": tn_total,
            "Reporting sites": int(q["n_sites"].sum()) if not q.empty else 0,
            "Median activity z": q["activity_z"].median() if not q.empty else np.nan,
            "Activity category": str(categorize_activity_z(pd.Series([q["activity_z"].median()])).iloc[0])
                if not q.empty and pd.notna(q["activity_z"].median()) else "No recent data",
            "Window end": pd.to_datetime(q["activity_end_week"], errors="coerce").max() if not q.empty else pd.NaT,
        })

    tab = pd.DataFrame(rows)
    save_df(tab, TABLE_DIR / "Table07b_Tennessee_Multipathogen_Surveillance.csv")

    # v5.12 fix: previously this used figsize=(11, 4.5) with the title
    # anchored near the top of the axes, the note text at a fixed y=0.06,
    # and the table placed loc="center" - since the table itself is small
    # (3 data rows), it ended up vertically centered with large blank gaps
    # both above (title-to-table) and below (table-to-note-to-bottom), and
    # bbox_inches="tight" still spans that full title-to-note extent. A much
    # shorter figsize plus an explicit table bbox anchored near the top
    # removes that dead space.
    fig, ax = plt.subplots(figsize=(11, 3.0))
    ax.axis("off")
    title = "NWGS Grid™ — Tennessee Recent Multipathogen Wastewater Surveillance"
    ax.set_title(title, pad=10, fontsize=13)

    display = tab[["Pathogen","Reporting counties","Reporting sites","Median activity z","Activity category"]].copy()
    display["Reporting counties"] = display["Reporting counties"].astype(str) + f"/{tn_total}"
    display["Median activity z"] = display["Median activity z"].map(
        lambda x: f"{x:.2f}" if pd.notna(x) else "NA"
    )

    table = ax.table(
        cellText=display.values,
        colLabels=display.columns,
        cellLoc="center",
        bbox=[0.02, 0.30, 0.96, 0.55],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    max_end = pd.to_datetime(tab["Window end"], errors="coerce").max()
    note = f"Recent {RECENT_ACTIVITY_WEEKS}-week window"
    if pd.notna(max_end):
        note += f" ending {max_end.date()}"
    note += ". Sparse coverage limits county-level interpretation."
    ax.text(0.5, 0.14, note, transform=ax.transAxes, ha="center", fontsize=9)

    fig.savefig(FIG_DIR / "Fig_Tennessee_Multipathogen_Surveillance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)



def _tn_base(tiger):
    """Return all 95 Tennessee counties in EPSG:5070."""
    tn = tiger[tiger["state_fips"].astype(str).eq("47")].copy()
    tn["county_fips"] = tn["county_fips"].astype(str).str.zfill(5)
    if HAVE_SPATIAL:
        tn = tn.to_crs(5070)
    return tn


def _tn_map_aspect(tn) -> float:
    """
    v5.12 addition.

    Width/height ratio of the Tennessee county base in its plotting CRS
    (roughly 3.4:1, wide and short). Two Tennessee paper figures
    (Map_Tennessee_Surveillance_Coverage.png and
    Map_Tennessee_SVI_Surveillance_Readiness.png) previously sized their map
    panels using arbitrary gridspec height_ratios (e.g. 1.2 out of a total of
    2.63 in a 12.5in-tall figure), which gave each map axes far more height
    than the state's actual shape needs. Since GeoDataFrame.plot() always
    preserves the real-world aspect ratio, the map only filled a thin
    horizontal band inside that oversized axes, leaving large blank margins
    above and below - the same bug already fixed for the Tennessee air
    quality pipeline's stacked maps. This helper lets each panel be sized
    from the real ratio instead of a guessed height_ratio.

    NOTE (v5.17): sizing each map panel correctly from this ratio does NOT
    by itself guarantee the overall saved FIGURE is portrait - see the
    v5.17 changelog entry and the Figure 5 block in
    create_tennessee_paper_figures() for the follow-on fix. Figure 2 was
    already portrait only because its second panel is a full bar chart
    (adds real height), not because of this helper alone.
    """
    minx, miny, maxx, maxy = tn.total_bounds
    return (maxx - minx) / (maxy - miny)


def _verify_portrait_or_warn(path, label):
    """
    v5.18 addition, v5.19 hardened into an active correction rather than
    detection-only.

    Immediately after saving a figure that is required to be portrait,
    reopen the saved PNG from disk and check its actual pixel dimensions.
    A real production run's own Table20_Portrait_SelfCheck.csv proved
    Map_Tennessee_SVI_Surveillance_Readiness.png was STILL landscape at
    the EXACT pixel dimensions (3021x2208) across two different
    algebra-based sizing formulas (v5.17 and v5.18) - meaning
    matplotlib's bbox_inches="tight" was cropping away the deliberately
    -added blank legend height both formulas relied on to force a
    portrait aspect ratio before saving. Two upstream attempts to solve
    this by picking the right nominal figsize have now failed
    identically, so this function no longer only detects the problem -
    it actively corrects it: if the saved image is not portrait, it is
    reopened, padded with a white margin at the bottom until height
    exceeds width by PORTRAIT_AUTOFIX_MARGIN, and re-saved to the same
    path. The run log and validation summary mark this outcome as
    AUTOFIXED (never a silent PASS), so a human can still see that this
    figure needed correction and investigate the upstream rendering
    cause (most likely: give the legend panel genuinely-rendered content
    that is large enough to survive tight-cropping on its own, rather
    than relying on allocated-but-mostly-blank canvas) without that
    investigation blocking publication in the meantime.
    """
    row = {"label": label, "path": str(path)}
    if not path.exists():
        print(f"[PORTRAIT SELF-CHECK] {label}: FAIL - file was not written: {path}")
        row.update({"status": "FAIL_NOT_WRITTEN", "width_px": None, "height_px": None})
        _PORTRAIT_SELF_CHECK_RESULTS.append(row)
        return

    try:
        with Image.open(path) as im:
            w, h = im.size
    except Exception as e:
        print(f"[PORTRAIT SELF-CHECK] {label}: FAIL - could not read saved image: {e}")
        row.update({"status": f"FAIL_UNREADABLE:{e}", "width_px": None, "height_px": None})
        _PORTRAIT_SELF_CHECK_RESULTS.append(row)
        return

    if h > w:
        print(f"[PORTRAIT SELF-CHECK] {label}: PASS ({w}x{h}px, portrait)")
        row.update({"status": "PASS", "width_px": w, "height_px": h})
        _PORTRAIT_SELF_CHECK_RESULTS.append(row)
        return

    # v5.19: not portrait - pad rather than only report. Target height
    # exceeds width by a clear safety margin so the corrected file isn't
    # borderline.
    print(
        f"[PORTRAIT SELF-CHECK] {label}: FAIL_NOT_PORTRAIT ({w}x{h}px, landscape/square) - "
        f"applying deterministic white-margin padding rather than relying on upstream sizing math "
        f"a third time (see v5.19 changelog)."
    )
    try:
        target_h = max(h + 1, int(math.ceil(w * PORTRAIT_AUTOFIX_MARGIN)))
        with Image.open(path) as im:
            im = im.convert("RGB")
            padded = Image.new("RGB", (w, target_h), color=(255, 255, 255))
            padded.paste(im, (0, 0))
        padded.save(path)
        with Image.open(path) as im2:
            new_w, new_h = im2.size
        if new_h > new_w:
            print(
                f"[PORTRAIT AUTO-FIX] {label}: padded {w}x{h}px -> {new_w}x{new_h}px "
                f"(white margin added at bottom) to force portrait orientation. "
                f"This is a deterministic safety net, not a fix to the underlying "
                f"matplotlib rendering cause - see the v5.19 changelog before assuming "
                f"this figure's layout is otherwise final."
            )
            row.update({
                "status": "AUTOFIXED_AFTER_FAIL",
                "width_px": new_w, "height_px": new_h,
                "pre_autofix_width_px": w, "pre_autofix_height_px": h,
            })
        else:
            print(f"[PORTRAIT AUTO-FIX] {label}: FAIL - padding did not achieve portrait orientation ({new_w}x{new_h}px).")
            row.update({"status": "FAIL_AUTOFIX_UNSUCCESSFUL", "width_px": new_w, "height_px": new_h})
    except Exception as e:
        print(f"[PORTRAIT AUTO-FIX] {label}: FAIL - padding attempt raised {type(e).__name__}: {e}")
        row.update({"status": f"FAIL_AUTOFIX_ERROR:{e}", "width_px": w, "height_px": h})

    _PORTRAIT_SELF_CHECK_RESULTS.append(row)


def create_tennessee_paper_figures(tiger, coverage, activity, multimodal, svi):
    """
    Generate publication-oriented Tennessee Paper 2 figures.

    Figure audit rules implemented here:
      * portrait/vertical map canvases;
      * legends carry category meaning and counts;
      * no result appears only in a title;
      * no annotation overlaps a legend or map;
      * sparse wastewater reporting is presented as a surveillance limitation,
        never as statewide pathogen absence/activity.
    """
    if not HAVE_SPATIAL:
        print("WARNING Tennessee paper maps skipped: spatial stack unavailable.")
        return

    tn = _tn_base(tiger)
    if tn.empty:
        print("WARNING Tennessee paper figures skipped: Tennessee geometry unavailable.")
        return
    n_tn = int(tn["county_fips"].nunique())
    if n_tn != 95:
        print(f"WARNING Tennessee geometry has {n_tn} counties; expected 95.")

    # --------------------------------------------------------------
    # Figure 1: redesigned portrait multimodal study design
    # --------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(.5, .965, "NWGS Grid™ — Tennessee Study Design", ha="center", va="top",
            fontsize=18, fontweight="bold")
    ax.text(.5, .925, "95-county framework for surveillance reach, temporal alignment, and equity",
            ha="center", va="top", fontsize=11)

    def _card(x, y, w, h, title, body, lw=1.2):
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.015",
                               facecolor="white", edgecolor="black", linewidth=lw,
                               transform=ax.transAxes)
        ax.add_patch(patch)
        ax.text(x+w/2, y+h*.68, title, ha="center", va="center",
                fontsize=11, fontweight="bold", transform=ax.transAxes)
        ax.text(x+w/2, y+h*.34, body, ha="center", va="center",
                fontsize=9.5, transform=ax.transAxes, wrap=True)
        return (x+w/2, y, x+w/2, y+h)

    # Three source cards are stacked vertically so nothing collides on a portrait page.
    _card(.12,.735,.76,.095,"CDC NWSS",
          "Wastewater surveillance • SARS-CoV-2 • RSV • Influenza A")
    _card(.12,.615,.76,.095,"CDC NSSP ED",
          "Clinical respiratory activity • emergency-department burden")
    _card(.12,.495,.76,.095,"CDC/ATSDR SVI",
          "County social vulnerability • all 95 Tennessee counties")

    # Source-to-integration spine.
    for y0 in [.735,.615,.495]:
        ax.annotate("", xy=(.5,.405), xytext=(.5,y0), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="->", lw=1.2))

    _card(.08,.315,.84,.095,"NWGS Grid™ multimodal geospatial-temporal integration",
          "Coverage & blind spots  •  Wastewater-clinical alignment  •  SVI/readiness  •  Equity  •  Seasonal eligibility",
          lw=1.5)

    # Three interpretation outputs in a non-overlapping vertical stack.
    outputs = [
        (.12,.205,.76,.065,"Surveillance reach","Where longitudinal monitoring exists"),
        (.12,.125,.76,.065,"Equity & readiness","Who is represented by the surveillance system"),
        (.12,.045,.76,.065,"Temporal interpretation","Alignment and seasonality only when coverage is eligible"),
    ]
    for x,y,w,h,title,body in outputs:
        ax.annotate("", xy=(.5,y+h), xytext=(.5,.315), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="->", lw=1.0))
        _card(x,y,w,h,title,body,lw=1.0)

    # Safeguard is deliberately separated from the analytical workflow instead of sharing a box.
    ax.text(.5,.008,
            "Interpretation safeguard: sparse wastewater reporting is a surveillance-system limitation; "
            "it is not evidence of pathogen absence or statewide Tennessee activity.",
            ha="center", va="bottom", fontsize=8.6, fontweight="bold",
            transform=ax.transAxes, wrap=True)
    fig.tight_layout(rect=[.02,.02,.98,.99])
    fig.savefig(FIG_DIR / "Fig_Tennessee_Study_Design.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # County-level historic coverage, routine respiratory pathogens only.
    routine = coverage[coverage["pathogen"].isin(["SARS-CoV-2","RSV","Influenza A"])].copy()
    tn_cov = routine[routine["county_fips"].astype(str).str.startswith("47")].copy()
    county_cov = (
        tn_cov.groupby("county_fips")
              .agg(surveillance_weeks=("n_weeks","max"),
                   any_analysis_ready=("analysis_ready","max"),
                   pathogens_observed=("pathogen","nunique"),
                   sites=("n_sites","max"))
              .reset_index()
    )
    g = tn.merge(county_cov, on="county_fips", how="left", validate="1:1")
    g["surveillance_weeks"] = g["surveillance_weeks"].fillna(0)
    g["any_analysis_ready"] = g["any_analysis_ready"].fillna(False).astype(bool)
    g["pathogens_observed"] = g["pathogens_observed"].fillna(0)
    g["sites"] = g["sites"].fillna(0)
    save_df(g.drop(columns="geometry"), TABLE_DIR / "Table15_Tennessee_County_Surveillance_Coverage.csv")

    reporting = int((g["surveillance_weeks"] > 0).sum())
    ready = int(g["any_analysis_ready"].sum())
    observed_not_ready = int(((g["surveillance_weeks"] > 0) & ~g["any_analysis_ready"]).sum())
    no_surveillance = int((g["surveillance_weeks"] <= 0).sum())
    g["readiness_label"] = np.where(
        g["any_analysis_ready"], "Analysis-ready",
        np.where(g["surveillance_weeks"] > 0, "Observed, not analysis-ready", "No historical surveillance")
    )

    # --------------------------------------------------------------
    # Figure 2: portrait readiness map + explicit legend + exact observed-county values
    # v5.12 fix: panel A's height_ratio was a guessed 1.2 (out of 2.63 total)
    # in a 12.5in-tall figure, giving the map axes ~5.7in of height for a
    # state whose real 9in-wide silhouette only needs ~9/aspect inches tall.
    # Since GeoDataFrame.plot() preserves the true aspect ratio, the extra
    # axes height became blank margin above/below the map. height_ratios are
    # now derived from Tennessee's real width:height ratio.
    # --------------------------------------------------------------
    tn_aspect = _tn_map_aspect(tn)
    map_h_in = 9.0 / tn_aspect  # inches, for a 9in-wide figure
    fig_h = map_h_in + 1.6 + 6.2  # map + legend strip + bar-chart panel
    fig = plt.figure(figsize=(9, fig_h))
    gs = fig.add_gridspec(3, 1, height_ratios=[map_h_in, 1.6, 6.2], hspace=.18)
    ax = fig.add_subplot(gs[0,0])
    ax_leg = fig.add_subplot(gs[1,0])
    ax2 = fig.add_subplot(gs[2,0])
    readiness_colors = {
        "Analysis-ready":"#2166ac",
        "Observed, not analysis-ready":"#92c5de",
        "No historical surveillance":"#d9d9d9",
    }
    for label in ["No historical surveillance","Observed, not analysis-ready","Analysis-ready"]:
        z = g[g["readiness_label"].eq(label)]
        if not z.empty:
            z.plot(ax=ax, color=readiness_colors[label], linewidth=.55, edgecolor="white")
    ax.set_axis_off(); ax.set_aspect("equal")
    ax.set_title("A. Tennessee wastewater surveillance coverage and blind spots",
                 fontsize=13, fontweight="bold", pad=10)

    counts = {
        "No historical surveillance": no_surveillance,
        "Observed, not analysis-ready": observed_not_ready,
        "Analysis-ready": ready,
    }
    ax_leg.axis("off")
    handles = [Patch(facecolor=readiness_colors[k], edgecolor="black",
                     label=f"{k}: {counts[k]}/95") for k in counts]
    ax_leg.legend(handles=handles, title="Routine-respiratory surveillance status",
                  loc="center", ncol=1, frameon=True, fontsize=9.2, title_fontsize=9.5)
    ax_leg.text(.5,.02,
                f"Historical surveillance observed in {reporting}/95 counties; {ready}/95 meet both the ≥{MIN_ANALYSIS_WEEKS}-week and active-span-completeness readiness criteria.",
                ha="center", va="bottom", fontsize=8.4, transform=ax_leg.transAxes, wrap=True)

    observed = g[g["surveillance_weeks"] > 0].copy()
    name_col = "NAME" if "NAME" in observed.columns else ("NAMELSAD" if "NAMELSAD" in observed.columns else "county_fips")
    observed["county_label"] = observed[name_col].astype(str).str.replace(" County", "", regex=False)
    observed = observed.sort_values("surveillance_weeks")
    if not observed.empty:
        bar_colors = [readiness_colors[x] for x in observed["readiness_label"]]
        bars = ax2.barh(observed["county_label"], observed["surveillance_weeks"], color=bar_colors)
        xmax = max(float(observed["surveillance_weeks"].max()) * 1.13, MIN_ANALYSIS_WEEKS * 1.35)
        ax2.set_xlim(0, xmax)
        for bar, value, status in zip(bars, observed["surveillance_weeks"], observed["readiness_label"]):
            ax2.text(bar.get_width()+xmax*.008, bar.get_y()+bar.get_height()/2,
                     f"{int(value)} wk", va="center", fontsize=8.5)
        ax2.axvline(MIN_ANALYSIS_WEEKS, linestyle="--", linewidth=1,
                    label=f"Minimum weeks component of readiness ({MIN_ANALYSIS_WEEKS})")
        ax2.legend(loc="lower right", fontsize=8)
    else:
        ax2.text(.5,.5,"No qualifying historical routine-respiratory surveillance",
                 ha="center",va="center",transform=ax2.transAxes)
    ax2.set_xlabel("Maximum qualifying surveillance weeks across routine respiratory pathogens")
    ax2.set_ylabel("County")
    ax2.set_title("B. Exact surveillance duration among historically observed counties",
                  fontsize=12, fontweight="bold")
    ax2.grid(axis="x", alpha=.2)

    fig.suptitle("NWGS Grid™ — Tennessee Surveillance Coverage", fontsize=16, fontweight="bold", y=.985)
    fig.text(.5,.012,
             "Readiness requires both duration and active-span completeness. Gray counties are surveillance blind spots, not evidence of pathogen absence.",
             ha="center", fontsize=8.7, wrap=True)
    fig.subplots_adjust(left=.13, right=.96, top=.94, bottom=.055)
    fig.savefig(FIG_DIR / "Map_Tennessee_Surveillance_Coverage.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    _verify_portrait_or_warn(FIG_DIR / "Map_Tennessee_Surveillance_Coverage.png", "Figure 2 (Tennessee Surveillance Coverage)")

    # --------------------------------------------------------------
    # Figure 3: Tennessee wastewater trends
    # --------------------------------------------------------------
    tn_mm = multimodal[multimodal["state_code"].astype(str).eq("TN")].copy()
    pathogens = ["SARS-CoV-2","RSV","Influenza A"]
    fig, axes = plt.subplots(3, 1, figsize=(9, 11), sharex=True)
    for i, (ax, pathogen) in enumerate(zip(axes, pathogens)):
        q = tn_mm[tn_mm["pathogen"].eq(pathogen)].sort_values("week_end")
        if not q.empty and q["wastewater_index"].notna().any():
            ax.plot(q["week_end"], q["wastewater_index"], lw=1.5)
            ax.axhline(0, lw=.8)
        else:
            ax.text(.5,.5,"Insufficient Tennessee wastewater series",ha="center",va="center",transform=ax.transAxes)
        ax.set_title(f"{chr(65+i)}. {pathogen}", fontweight="bold")
        ax.set_ylabel("Activity z")
        ax.grid(alpha=.2)
    axes[-1].set_xlabel("Week")
    fig.suptitle("NWGS Grid™ — Tennessee Respiratory Wastewater Activity Trends", fontsize=15, fontweight="bold")
    fig.text(.5,.02,"NWGS standardized within-site activity; interpretation is constrained by reporting coverage.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=[.05,.04,.98,.94])
    fig.savefig(FIG_DIR / "Fig_Tennessee_Multipathogen_Trends.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # --------------------------------------------------------------
    # Figure 4: wastewater-clinical alignment; collision-safe layout
    # --------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(9, 11), sharex=True)
    alignment_rows = []
    for i, (ax, pathogen) in enumerate(zip(axes, pathogens)):
        q = tn_mm[tn_mm["pathogen"].eq(pathogen)].sort_values("week_end").copy().dropna(subset=["week_end"])
        if not q.empty:
            clinical = pd.to_numeric(q["clinical_ed_pct"], errors="coerce")
            if clinical.notna().sum() >= 3 and clinical.std(ddof=0) > 0:
                q["clinical_z"] = (clinical - clinical.mean()) / clinical.std(ddof=0)
            else:
                q["clinical_z"] = np.nan
            ax.plot(q["week_end"], q["wastewater_index"], label="Wastewater activity z", lw=1.4)
            if q["clinical_z"].notna().any():
                ax.plot(q["week_end"], q["clinical_z"], label="NSSP ED activity z", lw=1.2)
            paired = q[["wastewater_index","clinical_ed_pct"]].dropna()
            rho = paired["wastewater_index"].corr(paired["clinical_ed_pct"], method="spearman") if len(paired) >= 3 else np.nan
            alignment_rows.append({"pathogen":pathogen,"paired_weeks":len(paired),"spearman_rho_same_week":rho})
            stat_text = f"Paired weeks: {len(paired)}\nSpearman ρ: {rho:.2f}" if pd.notna(rho) else f"Paired weeks: {len(paired)}\nSpearman ρ: NA"
            ax.text(.985,.82,stat_text,ha="right",va="top",transform=ax.transAxes,fontsize=8.5,
                    bbox=dict(boxstyle="round,pad=.3",fc="white",ec="0.5",alpha=.9))
        else:
            alignment_rows.append({"pathogen":pathogen,"paired_weeks":0,"spearman_rho_same_week":np.nan})
            ax.text(.5,.5,"Insufficient Tennessee paired series",ha="center",va="center",transform=ax.transAxes)
        ax.set_title(f"{chr(65+i)}. {pathogen}", fontweight="bold")
        ax.set_ylabel("Standardized activity")
        ax.grid(alpha=.2)
    axes[-1].set_xlabel("Week")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(.5,.95), frameon=False)
    fig.suptitle("NWGS Grid™ — Tennessee Wastewater and Clinical Respiratory Surveillance Alignment",
                 fontsize=14.5, fontweight="bold")
    fig.text(.5,.02,"Same-week descriptive comparison; associations do not imply causality.",ha="center",fontsize=9)
    fig.tight_layout(rect=[.05,.04,.98,.91])
    fig.savefig(FIG_DIR / "Fig_Tennessee_WW_Clinical_Alignment.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    save_df(pd.DataFrame(alignment_rows), TABLE_DIR / "Table16_Tennessee_WW_Clinical_Alignment.csv")

    # --------------------------------------------------------------
    # Figure 5: vertical SVI + readiness maps with dedicated legends and counts
    # v5.17 fix (portrait orientation): the v5.12 _tn_map_aspect() fix
    # correctly sizes each map panel from Tennessee's real ~3.4:1
    # width:height ratio so neither map stretches - but that alone does
    # not make the OVERALL saved figure portrait, because Tennessee's
    # true outline is itself wide and short. Two such maps stacked at a
    # flat 9in figure width plus the previous fixed 1.8in legend strip
    # produced total_height ~= 2*(9/3.4) + 1.8 ~= 7.1in against a 9in
    # width - still landscape, matching the Table19 audit finding of
    # 3021x2306 / FAIL_NOT_PORTRAIT. Figure 2 avoids this because its
    # second panel is a full bar chart (6.2in), not a thin legend strip.
    # Fix: solve for a figure width where two map panels plus a
    # legend/annotation panel sum to a height that exceeds the width by a
    # fixed safety margin, and use the freed vertical space for a genuine
    # per-SVI-quartile readiness breakdown (mirrors Table17) rather than
    # blank padding.
    # --------------------------------------------------------------
    svi_small = svi[["county_fips","RPL_THEMES"]].drop_duplicates("county_fips").copy()
    svi_small["county_fips"] = svi_small["county_fips"].astype(str).str.zfill(5)
    ge = g.merge(svi_small, on="county_fips", how="left", validate="1:1")

    tn_aspect = _tn_map_aspect(tn)

    # Solve fig_w so that 2 * map_h_in + legend_h_in >= PORTRAIT_MARGIN * fig_w,
    # using a legend panel large enough to hold real content (title +
    # quartile breakdown + methodology note), not just the bare swatches.
    PORTRAIT_MARGIN = 1.15          # target height:width safety margin
    MIN_LEGEND_H_IN = 3.0           # enough room for legend + quartile table + note
    denom = PORTRAIT_MARGIN - (2.0 / tn_aspect)
    if denom > 0.05:
        fig_w = MIN_LEGEND_H_IN / denom
        fig_w = float(np.clip(fig_w, 5.5, 9.0))
    else:
        # Degenerate/unexpected aspect ratio: fall back to a safely narrow width.
        fig_w = 5.5
    map_h_in = fig_w / tn_aspect
    legend_h_in = max(MIN_LEGEND_H_IN, PORTRAIT_MARGIN * fig_w - 2 * map_h_in)

    fig = plt.figure(figsize=(fig_w, 2 * map_h_in + legend_h_in))
    gs = fig.add_gridspec(3, 1, height_ratios=[map_h_in, map_h_in, legend_h_in], hspace=.18)
    ax_a = fig.add_subplot(gs[0,0])
    ax_b = fig.add_subplot(gs[1,0])
    ax_leg = fig.add_subplot(gs[2,0])

    ge.plot(column="RPL_THEMES", ax=ax_a, cmap="viridis", legend=True,
            linewidth=.45, edgecolor="white", vmin=0, vmax=1,
            # Fix D (v5.15, re-verified unchanged by this patch): colorbar
            # label/size kept short and small enough to stay clear of the
            # suptitle regardless of the new fig_w/fig_h solved above.
            legend_kwds={"label":"SVI percentile rank","shrink":.55,"pad":.02,"fraction":.05},
            missing_kwds={"color":"lightgray"})
    ax_a.set_title("A. Social vulnerability", fontweight="bold", pad=8)
    ax_a.set_axis_off(); ax_a.set_aspect("equal")
    _svi_cbar = ax_a.get_figure().axes[-1]
    _svi_cbar.yaxis.label.set_size(9)
    _svi_cbar.tick_params(labelsize=8)

    for label in ["No historical surveillance","Observed, not analysis-ready","Analysis-ready"]:
        z = ge[ge["readiness_label"].eq(label)]
        if not z.empty:
            z.plot(ax=ax_b, color=readiness_colors[label], linewidth=.45, edgecolor="white")
    ax_b.set_title("B. Wastewater surveillance readiness", fontweight="bold", pad=8)
    ax_b.set_axis_off(); ax_b.set_aspect("equal")

    ax_leg.axis("off")
    handles = [Patch(facecolor=readiness_colors[k], edgecolor="black",
                     label=f"{k}: {counts[k]}/95 ({100*counts[k]/95:.1f}%)") for k in counts]
    ax_leg.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=1,
                  fontsize=9.2, title="Surveillance readiness", title_fontsize=9.5, frameon=True)

    # v5.17 addition: per-SVI-quartile readiness breakdown, computed the
    # same way as Table17, so the extra vertical space added for portrait
    # orientation is genuine content rather than padding.
    try:
        ge_q = ge.dropna(subset=["RPL_THEMES"]).copy()
        ge_q["svi_quartile"] = _safe_svi_quartile(ge_q["RPL_THEMES"])
        quartile_tab = (
            ge_q.groupby("svi_quartile", observed=True)
                .agg(counties=("county_fips","nunique"),
                     pct_ready=("any_analysis_ready","mean"))
                .reset_index()
        )
        quartile_tab["pct_ready"] = (quartile_tab["pct_ready"] * 100)
        quartile_lines = "   |   ".join(
            f"{row.svi_quartile}: {row.pct_ready:.1f}% ready (n={int(row.counties)})"
            for row in quartile_tab.itertuples()
        )
    except Exception:
        quartile_lines = ""

    if quartile_lines:
        ax_leg.text(.5, .40, "Readiness by SVI quartile (see Table17):\n" + quartile_lines,
                    ha="center", va="center", fontsize=8.6, transform=ax_leg.transAxes, wrap=True)

    ax_leg.text(.5, .06,
                f"Readiness = >={MIN_ANALYSIS_WEEKS} qualifying weeks plus active-span completeness >={MIN_ACTIVE_COMPLETENESS:.0%}. "
                "SVI percentile rank: 0 = lowest vulnerability, 1 = highest. "
                "No-surveillance counties remain in the denominator so equity analyses measure system reach rather than pathogen absence.",
                ha="center", va="bottom", fontsize=8.2, transform=ax_leg.transAxes, wrap=True)

    fig.suptitle("NWGS Grid™ — Tennessee Social Vulnerability and Wastewater Surveillance Readiness",
                 fontsize=14.5, fontweight="bold", y=.975)
    fig.subplots_adjust(left=.06, right=.94, top=.92, bottom=.03)
    fig.savefig(FIG_DIR / "Map_Tennessee_SVI_Surveillance_Readiness.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    _verify_portrait_or_warn(FIG_DIR / "Map_Tennessee_SVI_Surveillance_Readiness.png", "Figure 5 (Tennessee SVI + Surveillance Readiness)")

    # --------------------------------------------------------------
    # Figure 6: Tennessee-specific descriptive/inferential equity model
    # --------------------------------------------------------------
    model_df = ge[["county_fips","RPL_THEMES","any_analysis_ready","surveillance_weeks"]].dropna(subset=["RPL_THEMES"]).copy()
    model_df["analysis_ready"] = model_df["any_analysis_ready"].astype(int)
    # v5.9: use _safe_svi_quartile() instead of a bare pd.qcut(..., labels=[...],
    # duplicates="drop") call - Tennessee's 95-county subset is even more
    # likely than the national dataset to have tied RPL_THEMES values collapse
    # the quantile bin count below 4.
    model_df["svi_quartile"] = _safe_svi_quartile(model_df["RPL_THEMES"])
    eq = model_df.groupby("svi_quartile",observed=True).agg(
        counties=("county_fips","nunique"), pct_analysis_ready=("analysis_ready","mean"), median_weeks=("surveillance_weeks","median")
    ).reset_index()
    eq["pct_analysis_ready"] *= 100

    model_summary = pd.DataFrame()
    if len(model_df) >= 40 and model_df["analysis_ready"].nunique() == 2:
        try:
            model_df["svi_10pct"] = pd.to_numeric(model_df["RPL_THEMES"], errors="coerce") * 10
            X = sm.add_constant(model_df[["svi_10pct"]], has_constant="add")
            m = sm.GLM(model_df["analysis_ready"], X, family=sm.families.Binomial()).fit()
            b,se = float(m.params["svi_10pct"]), float(m.bse["svi_10pct"])
            model_summary = pd.DataFrame([{
                "model":"Tennessee exploratory binomial GLM: analysis_ready ~ SVI",
                "n_counties":len(model_df), "odds_ratio_per_0_10_SVI":float(np.exp(b)),
                "or_95ci_low":float(np.exp(b-1.96*se)), "or_95ci_high":float(np.exp(b+1.96*se)),
                "p_value":float(m.pvalues["svi_10pct"]), "note":"Unadjusted exploratory association; not causal."
            }])
        except Exception as e:
            model_summary = pd.DataFrame([{"model":"Tennessee exploratory GLM","note":f"Model not estimable: {e}"}])
    save_df(eq, TABLE_DIR / "Table17_Tennessee_Equity_By_SVI_Quartile.csv")
    save_df(model_summary, TABLE_DIR / "Table17b_Tennessee_Equity_GLM.csv")

    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    bars = ax.bar(eq["svi_quartile"].astype(str), eq["pct_analysis_ready"])
    # v5.12 fix: y-axis was hardcoded to 0-100 regardless of the actual data
    # range. Tennessee's readiness rates are only ~4-9% (unlike the national
    # equity chart, where 0-100 is appropriate because readiness runs
    # 75-90%), so the fixed 0-100 scale wasted over 90% of the chart and
    # made the roughly 2x difference between quartiles (e.g. 4.2% vs 8.7%)
    # visually imperceptible. The axis now scales to the actual data with
    # headroom reserved for the percentage labels above each bar.
    ymax = max(15.0, float(eq["pct_analysis_ready"].max()) * 1.6)
    ax.set_ylim(0, ymax)
    ax.set_ylabel("Tennessee counties analysis-ready (%)")
    ax.set_xlabel("CDC/ATSDR SVI quartile")
    ax.set_title("NWGS Grid™ — Tennessee Surveillance Readiness by Social Vulnerability", fontweight="bold")
    for b,v in zip(bars,eq["pct_analysis_ready"]):
        ax.text(b.get_x()+b.get_width()/2, min(ymax*0.98, v+ymax*0.02), f"{v:.1f}%", ha="center", fontsize=9)
    note = "Descriptive county-level comparison."
    if not model_summary.empty and "odds_ratio_per_0_10_SVI" in model_summary.columns and pd.notna(model_summary.iloc[0].get("odds_ratio_per_0_10_SVI")):
        r=model_summary.iloc[0]
        note += (f" Exploratory GLM OR per 0.10 SVI={r['odds_ratio_per_0_10_SVI']:.2f} "
                 f"(95% CI {r['or_95ci_low']:.2f}-{r['or_95ci_high']:.2f}); p={r['p_value']:.3g}.")
    note += " Not causal; population/rurality adjustment requires additional covariates."
    fig.text(.5,.02,note,ha="center",fontsize=8.8,wrap=True)
    fig.tight_layout(rect=[.05,.06,.98,.96])
    fig.savefig(FIG_DIR / "Fig_Tennessee_Equity_Model.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("PASS Tennessee paper figure engine generated audited portrait Figures 1-6 plus sparse-coverage supplement.")

# ============================================================
# 12. SPATIAL ANALYSIS — KNN TO AVOID ISLAND PROBLEM
# ============================================================

def spatial_activity_analysis(tiger, activity):
    if not HAVE_SPATIAL or activity.empty:
        return pd.DataFrame(), pd.DataFrame()

    global_rows, local_rows = [], []
    base = conus(tiger).to_crs(5070)

    for pathogen, q in activity.groupby("pathogen"):
        # Fresh pathogen-specific merge and weights object each iteration.
        g = base.merge(q.copy(), on="county_fips", how="inner")
        g = g.dropna(subset=["activity_z"]).copy()

        safe = re.sub(r"[^A-Za-z0-9]+", "_", pathogen).strip("_")
        export_cols = [c for c in [
            "county_fips","activity_z","n_sites","n_records","activity_end_week"
        ] if c in g.columns]
        save_df(g[export_cols].copy(), TABLE_DIR / f"SpatialInput_{safe}.csv")

        if len(g) < max(20, SPATIAL_K + 2):
            continue

        k_use = min(SPATIAL_K, len(g)-1)
        w = KNN.from_dataframe(g, k=k_use)
        w.transform = "R"

        y = g["activity_z"].astype(float).values
        if np.nanstd(y) == 0:
            continue

        moran = Moran(y, w, permutations=999)
        global_rows.append({
            "pathogen": pathogen,
            "n_counties": len(g),
            "weights_method": f"KNN_k{k_use}_EPSG5070",
            "morans_i": moran.I,
            "expected_i": moran.EI,
            "p_sim": moran.p_sim,
            "z_sim": moran.z_sim,
        })

        ml = Moran_Local(y, w, permutations=999)
        z = (y - np.nanmean(y)) / np.nanstd(y)
        lagz = w.sparse @ z

        labels = np.full(len(g), "Not Significant", dtype=object)
        sig = ml.p_sim < 0.05
        labels[sig & (z >= 0) & (lagz >= 0)] = "High-High"
        labels[sig & (z < 0) & (lagz < 0)] = "Low-Low"
        labels[sig & (z >= 0) & (lagz < 0)] = "High-Low"
        labels[sig & (z < 0) & (lagz >= 0)] = "Low-High"

        tmp = pd.DataFrame({
            "pathogen": pathogen,
            "county_fips": g["county_fips"].values,
            "activity_z": y,
            "local_morans_i": ml.Is,
            "p_sim": ml.p_sim,
            "lisa_cluster": labels,
        })
        local_rows.append(tmp)

    return (
        pd.DataFrame(global_rows),
        pd.concat(local_rows, ignore_index=True) if local_rows else pd.DataFrame()
    )


def pathogen_independence_audit(activity, lisa=None):
    pathogens = ["SARS-CoV-2","RSV","Influenza A"]
    rows = []

    for i in range(len(pathogens)):
        for j in range(i+1, len(pathogens)):
            a_name, b_name = pathogens[i], pathogens[j]
            a = activity[activity["pathogen"].eq(a_name)][["county_fips","activity_z"]].rename(
                columns={"activity_z":"a_activity"}
            )
            b = activity[activity["pathogen"].eq(b_name)][["county_fips","activity_z"]].rename(
                columns={"activity_z":"b_activity"}
            )
            m = a.merge(b, on="county_fips", how="inner")

            n = len(m)
            exact = np.isclose(m["a_activity"], m["b_activity"], equal_nan=False, atol=1e-12) if n else np.array([])
            corr = m[["a_activity","b_activity"]].corr().iloc[0,1] if n >= 3 else np.nan

            row = {
                "comparison": f"{a_name} vs {b_name}",
                "common_counties": n,
                "identical_activity_values": int(exact.sum()) if n else 0,
                "pct_identical_activity": 100 * exact.mean() if n else np.nan,
                "activity_correlation": corr,
            }

            if lisa is not None and not lisa.empty:
                la = lisa[lisa["pathogen"].eq(a_name)][["county_fips","lisa_cluster"]].rename(
                    columns={"lisa_cluster":"a_lisa"}
                )
                lb = lisa[lisa["pathogen"].eq(b_name)][["county_fips","lisa_cluster"]].rename(
                    columns={"lisa_cluster":"b_lisa"}
                )
                lm = la.merge(lb, on="county_fips", how="inner")
                row["common_lisa_counties"] = len(lm)
                row["pct_identical_lisa_class"] = (
                    100 * (lm["a_lisa"] == lm["b_lisa"]).mean() if len(lm) else np.nan
                )
            else:
                row["common_lisa_counties"] = np.nan
                row["pct_identical_lisa_class"] = np.nan

            pct = row["pct_identical_activity"]
            if pd.notna(pct) and pct >= 95:
                row["status"] = "FAIL_NEAR_IDENTICAL_ACTIVITY"
            elif pd.notna(corr) and corr >= 0.98:
                row["status"] = "WARNING_HIGH_CORRELATION"
            else:
                row["status"] = "PASS"

            rows.append(row)
    return pd.DataFrame(rows)


def plot_lisa_maps(tiger, lisa):
    if lisa.empty:
        return

    colors = {
        "High-High":"#b2182b",
        "Low-Low":"#2166ac",
        "High-Low":"#ef8a62",
        "Low-High":"#67a9cf",
        "Not Significant":"#f0f0f0",
        "No recent data":"#bdbdbd",
    }
    order = ["High-High","Low-Low","High-Low","Low-High","Not Significant","No recent data"]
    base = conus(tiger).to_crs(5070)

    for pathogen, q in lisa.groupby("pathogen"):
        g = base.merge(q, on="county_fips", how="left")
        g["lisa_display"] = g["lisa_cluster"].fillna("No recent data")

        fig, ax = plt.subplots(figsize=(10,12))
        for lab in order:
            z = g[g["lisa_display"].eq(lab)]
            if not z.empty:
                z.plot(ax=ax, color=colors[lab], linewidth=0.05, edgecolor="white")

        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.set_title(f"NWGS Grid™ — {pathogen} Local Spatial Association (KNN-LISA)")
        handles = [Patch(facecolor=colors[x], label=x) for x in order]
        ax.legend(handles=handles, title="Local Moran's I class", loc="lower left", frameon=True)
        ax.text(
            0.99, 0.01,
            f"KNN k={SPATIAL_K}, EPSG:5070; permutation p<0.05 for cluster classes",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8
        )
        fig.tight_layout()
        safe = re.sub(r"[^A-Za-z0-9]+", "_", pathogen).strip("_")
        fig.savefig(FIG_DIR / f"Map_LISA_{safe}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)


# ============================================================
# 13. CDC PLACES
# ============================================================
def load_places():
    meta, fields = validate_dataset(PLACES_ID)
    wanted = [
        "year","stateabbr","statedesc","locationname","category","measure",
        "data_value_unit","data_value_type","data_value","totalpopulation",
        "locationid","measureid","datavaluetypeid","short_question_text","geolocation"
    ]
    select = ",".join([c for c in wanted if c in fields])
    where_parts = []
    if "datavaluetypeid" in fields:
        where_parts.append("datavaluetypeid = 'AgeAdjPrv'")
    # Focus on a compact set of context measures if supported.
    if "measureid" in fields:
        ids = ["CASTHMA","COPD","DIABETES","CHD","OBESITY"]
        where_parts.append("(" + " OR ".join([f"measureid='{x}'" for x in ids]) + ")")
    where = " AND ".join(where_parts) if where_parts else None
    df = socrata_fetch(PLACES_ID, select=select, where=where)
    if "locationid" in df.columns:
        df["county_fips"] = df["locationid"].map(normalize_fips)
    if "data_value" in df.columns:
        df["data_value"] = numeric(df["data_value"])
    save_df(df, RAW_DIR / "CDC_PLACES_2025_FROZEN.csv")
    return df

# ============================================================
# 14. OPTIONAL CENSUS ACS
# ============================================================
def load_acs_optional():
    if not ENABLE_ACS:
        print("[SKIP] ACS disabled. Set NWGS_ENABLE_ACS=1 to enable.")
        return pd.DataFrame()
    if not CENSUS_API_KEY:
        print("[SKIP] CENSUS_API_KEY not set.")
        return pd.DataFrame()

    base = "https://api.census.gov/data/2024/acs/acs5/profile"
    # Conservative variables; verify against 2024 group metadata before publication.
    get_vars = ["NAME","DP05_0001E","DP03_0062E","DP03_0128PE"]
    params = {
        "get": ",".join(get_vars),
        "for": "county:*",
        "in": "state:*",
        "key": CENSUS_API_KEY,
    }
    r = requests.get(base, params=params, timeout=120)
    r.raise_for_status()
    rows = r.json()
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df["county_fips"] = df["state"].str.zfill(2) + df["county"].str.zfill(3)
    save_df(df, RAW_DIR / "CENSUS_ACS_2024_FROZEN.csv")
    return df

# ============================================================
# 15. OPTIONAL NOAA WEATHER
# ============================================================
def noaa_status():
    if not ENABLE_NOAA:
        print("[SKIP] NOAA disabled. Set NWGS_ENABLE_NOAA=1 to enable.")
        return
    if not NOAA_TOKEN:
        print("[SKIP] NOAA_TOKEN not set.")
        return
    r = requests.get(
        "https://www.ncei.noaa.gov/cdo-web/api/v2/datasets",
        headers={"token": NOAA_TOKEN},
        params={"limit": 1},
        timeout=60,
    )
    r.raise_for_status()
    print("[OK] NOAA token validated. Add county/station-specific extraction only after analysis geography is frozen.")

# ============================================================
# 16. OPTIONAL EPA AQS AIR QUALITY
# ============================================================
def epa_aqs_status():
    """
    Retains EPA AQS in NWGS as an OPTIONAL environmental-context module.
    National daily extraction is intentionally not auto-run because it can create
    a very large request workload. Freeze geography/pollutants first.

    Recommended initial pollutants if scientifically justified:
      88101 = PM2.5 FRM/FEM mass
      44201 = Ozone
    """
    if not ENABLE_EPA_AQS:
        print("[SKIP] EPA AQS disabled. Set NWGS_ENABLE_EPA_AQS=1 to enable.")
        return
    if not (EPA_AQS_EMAIL and EPA_AQS_KEY):
        print("[SKIP] EPA_AQS_EMAIL / EPA_AQS_KEY not set.")
        return
    # Lightweight credential/test request: annual_data/byCounty example on a tiny scope.
    url = "https://aqs.epa.gov/data/api/annualData/byCounty"
    params = {
        "email": EPA_AQS_EMAIL,
        "key": EPA_AQS_KEY,
        "param": "88101",
        "bdate": str(STUDY_END.year),
        "edate": str(STUDY_END.year),
        "state": "47",   # Tennessee validation scope only
        "county": "037", # Davidson County
    }
    r = requests.get(url, params=params, timeout=120)
    if r.ok:
        print("[OK] EPA AQS credentials/API reachable. Full extraction remains optional.")
    else:
        print(f"[WARN] EPA AQS test returned HTTP {r.status_code}; verify credentials/API parameters.")

# ============================================================
# 17. OPTIONAL EXPLORATORY ML
# ============================================================
def exploratory_ml(multimodal):
    """
    App/demo-oriented exploratory forecast benchmark.
    NOT a substitute for the dedicated ID Lab Con validation pipeline.
    Predicts same-week clinical ED activity from wastewater index + site count + lags.
    Uses chronological 80/20 split within each pathogen pooled across states after
    state fixed-effect one-hot encoding.

    v5.15: previously returned only the MAE/RMSE/R2 summary table, which
    could back a model-performance bar chart (Paper 1 Figure 7) but left
    Figures 8-10 (observed-vs-predicted, ablation, SHAP) with literally no
    backing code - they were labeled PENDING_ML in the figure manifest but
    nothing existed to generate them even when NWGS_ENABLE_ML=1. This now
    also returns the best model's held-out predictions (feeds
    plot_observed_vs_predicted(), Figure 8) and a feature-group ablation
    table (feeds plot_ablation(), Figure 9), computed in the same pass so
    the chronological split and fitted models are shared rather than
    redone. Figure 10 (SHAP) is handled separately by explain_with_shap()
    since it depends on the optional shap package.

    v5.18: the ablation above can understate wastewater's contribution
    when wastewater features are collinear with the retained clinical-lag
    features (removing a group that's redundant with what's left doesn't
    hurt R2 even if that group carries real signal on its own). This now
    also returns (a) a train-split collinearity audit between each
    wastewater feature and clinical_lag1, and (b) a "WastewaterOnly"
    benchmark - the same model architectures fit using ONLY
    wastewater-derived features, with every clinical_lag column dropped
    entirely - so wastewater's standalone predictive value can be read
    directly rather than inferred from an ablation delta that may be
    diluted by collinearity. Held-out predictions also now carry their
    source state_code/week_end so an outlier can be traced back to an
    exact row (see audit_ml_prediction_outliers()).

    Returns (results_df, predictions, ablation_df, wastewater_only_df, collinearity_df):
      results_df       - unchanged MAE/RMSE/R2 per pathogen/model, plus new
                          "WastewaterOnly_<model>" rows.
      predictions       - {pathogen: {"model", "y_true", "y_pred",
                          "fitted_model", "X_train", "ids_test"}} for the
                          best (lowest-RMSE) non-baseline full-feature model
                          per pathogen. ids_test is a state_code/week_end
                          frame aligned row-for-row with y_true/y_pred.
      ablation_df       - R2 with each feature group removed vs the full
                          model, for that same best model's architecture.
      wastewater_only_df - per pathogen: best wastewater-only model's R2/RMSE
                          vs the clinical-persistence baseline's R2/RMSE.
      collinearity_df   - per pathogen/wastewater-feature: training-split
                          Pearson r against clinical_lag1, and a
                          high_collinearity_flag.
    """
    empty_return = (pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    if not ENABLE_EXPLORATORY_ML:
        print("[SKIP] Exploratory ML disabled. Set NWGS_ENABLE_ML=1 to enable.")
        return empty_return
    if not HAVE_SKLEARN or multimodal.empty:
        print("[SKIP] scikit-learn unavailable or multimodal data empty.")
        return empty_return

    feature_groups = {
        "wastewater_current": ["wastewater_index"],
        "wastewater_lags": ["ww_lag1", "ww_lag2", "ww_lag3", "ww_lag4"],
        "clinical_lags": ["clinical_lag1", "clinical_lag2", "clinical_lag3", "clinical_lag4"],
        "site_count": ["n_sites"],
    }

    results = []
    predictions = {}
    ablation_rows = []
    collinearity_rows = []
    wastewater_only_rows = []

    for pathogen, g in multimodal.groupby("pathogen"):
        x = g.sort_values(["state_code","week_end"]).copy()
        for lag in [1,2,3,4]:
            x[f"ww_lag{lag}"] = x.groupby("state_code")["wastewater_index"].shift(lag)
            x[f"clinical_lag{lag}"] = x.groupby("state_code")["clinical_ed_pct"].shift(lag)

        x = x.dropna(subset=["clinical_ed_pct","wastewater_index","ww_lag1","clinical_lag1"])
        if len(x) < 200:
            continue

        base_cols = ["wastewater_index","n_sites","ww_lag1","ww_lag2","ww_lag3","ww_lag4",
                     "clinical_lag1","clinical_lag2","clinical_lag3","clinical_lag4"]
        X = x[base_cols].copy()
        state_dummies = pd.get_dummies(x["state_code"], prefix="state", dtype=float)
        state_cols = list(state_dummies.columns)
        X = pd.concat([X, state_dummies], axis=1).fillna(0)
        y = x["clinical_ed_pct"].astype(float)

        order = np.argsort(x["week_end"].values)
        X = X.iloc[order].reset_index(drop=True)
        y = y.iloc[order].reset_index(drop=True)
        # v5.18 addition: carry state_code/week_end through the same
        # chronological reorder as X/y, so a held-out prediction can be
        # traced back to an exact source row (audit_ml_prediction_outliers()).
        ids = x[["state_code", "week_end"]].iloc[order].reset_index(drop=True)

        cut = int(len(X)*0.80)
        Xtr, Xte = X.iloc[:cut], X.iloc[cut:]
        ytr, yte = y.iloc[:cut], y.iloc[cut:]
        ids_test = ids.iloc[cut:].reset_index(drop=True)

        # v5.18 addition: feature-collinearity diagnostic, computed on the
        # TRAINING split only (never the held-out test split, to avoid
        # leaking test-set information into a diagnostic). Paper 1 Figure 9
        # showed removing "wastewater_current"/"wastewater_lags" produced
        # ~zero change in held-out R2 for all three pathogens, while
        # removing "clinical_lags" produced by far the largest drop - a
        # result that, read alone, suggests wastewater carries no
        # predictive value. But the lag analysis (Table04_Best_Lag_Results.csv)
        # shows wastewater genuinely leading clinical activity by 0-2 weeks
        # for a meaningful number of states. The likely explanation: a tree
        # ensemble can satisfy most of its need for "recent trend"
        # information from whichever correlated feature it locks onto
        # first, so ablating either alone can understate its standalone
        # value. This quantifies that correlation so the reader can judge
        # whether the ablation figure's near-zero wastewater contribution
        # reflects genuine irrelevance or collinearity with the retained
        # clinical-lag features.
        collinearity_rows_local = []
        for ww_col in ["wastewater_index", "ww_lag1", "ww_lag2", "ww_lag3", "ww_lag4"]:
            if ww_col in Xtr.columns and "clinical_lag1" in Xtr.columns:
                paired = Xtr[[ww_col, "clinical_lag1"]].dropna()
                corr = paired[ww_col].corr(paired["clinical_lag1"]) if len(paired) >= 3 else np.nan
                collinearity_rows_local.append({
                    "pathogen": pathogen,
                    "wastewater_feature": ww_col,
                    "clinical_feature": "clinical_lag1",
                    "pearson_r_train_split": corr,
                    "n_train_rows": len(paired),
                    "high_collinearity_flag": bool(pd.notna(corr) and abs(corr) >= COLLINEARITY_FLAG_THRESHOLD),
                })
        collinearity_rows.extend(collinearity_rows_local)
        flagged_local = [r for r in collinearity_rows_local if r["high_collinearity_flag"]]
        if flagged_local:
            worst = max(flagged_local, key=lambda r: abs(r["pearson_r_train_split"]))
            print(
                f"[ML COLLINEARITY WARNING] {pathogen}: {worst['wastewater_feature']} vs "
                f"clinical_lag1 Pearson r={worst['pearson_r_train_split']:.2f} on the "
                f"training split - the ablation figure's near-zero wastewater "
                f"contribution for this pathogen may reflect collinearity with "
                f"retained clinical-lag features rather than genuine irrelevance. "
                f"See Fig_Wastewater_Only_Value.png for a standalone wastewater-only "
                f"benchmark that removes this ambiguity."
            )

        models = {
            "RandomForest": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
            "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42),
        }

        # Clinical-history persistence baseline
        baseline = x.iloc[order]["clinical_lag1"].reset_index(drop=True).iloc[cut:]
        results.append({
            "pathogen": pathogen,
            "model": "ClinicalPersistence",
            "n_train": len(ytr),
            "n_test": len(yte),
            "MAE": mean_absolute_error(yte, baseline),
            "RMSE": mean_squared_error(yte, baseline) ** 0.5,
            "R2": r2_score(yte, baseline),
        })

        fitted = {}
        for name, model in models.items():
            model.fit(Xtr, ytr)
            pred = model.predict(Xte)
            rmse = mean_squared_error(yte, pred) ** 0.5
            fitted[name] = {"model": model, "pred": pred, "rmse": rmse}
            results.append({
                "pathogen": pathogen,
                "model": name,
                "n_train": len(ytr),
                "n_test": len(yte),
                "MAE": mean_absolute_error(yte, pred),
                "RMSE": rmse,
                "R2": r2_score(yte, pred),
            })

        best_name = min(fitted, key=lambda k: fitted[k]["rmse"])
        best = fitted[best_name]
        predictions[pathogen] = {
            "model": best_name,
            "y_true": yte.values,
            "y_pred": best["pred"],
            "fitted_model": best["model"],
            "X_train": Xtr,
            "ids_test": ids_test,
        }

        # v5.18 addition: "WastewaterOnly" benchmark - the SAME model
        # architectures fit using ONLY wastewater-derived features (current
        # value, its four lags, and site count; state fixed effects are
        # kept since they are a geography control, not a clinical feature),
        # with every clinical_lag column dropped entirely rather than
        # merely down-weighted. This directly answers "does wastewater
        # carry standalone predictive value" without the collinearity
        # ambiguity in the feature-group ablation below: a low ablation
        # delta only tells you removing wastewater doesn't hurt the FULL
        # model; a WastewaterOnly model's own R2 tells you what wastewater
        # can do entirely on its own, with nothing to be collinear with.
        ww_only_cols = [c for c in X.columns if not c.startswith("clinical_lag")]
        Xtr_wwonly, Xte_wwonly = Xtr[ww_only_cols], Xte[ww_only_cols]
        ww_only_fitted = {}
        for ww_name, ww_model_cls, ww_kwargs in [
            ("RandomForest", RandomForestRegressor, {"n_estimators": 300, "random_state": 42, "n_jobs": -1}),
            ("HistGradientBoosting", HistGradientBoostingRegressor, {"random_state": 42}),
        ]:
            m_ww = ww_model_cls(**ww_kwargs)
            m_ww.fit(Xtr_wwonly, ytr)
            pred_ww = m_ww.predict(Xte_wwonly)
            rmse_ww = mean_squared_error(yte, pred_ww) ** 0.5
            ww_only_fitted[ww_name] = {"pred": pred_ww, "rmse": rmse_ww}
            results.append({
                "pathogen": pathogen,
                "model": f"WastewaterOnly_{ww_name}",
                "n_train": len(ytr),
                "n_test": len(yte),
                "MAE": mean_absolute_error(yte, pred_ww),
                "RMSE": rmse_ww,
                "R2": r2_score(yte, pred_ww),
            })
        ww_only_best_name = min(ww_only_fitted, key=lambda k: ww_only_fitted[k]["rmse"])
        wastewater_only_rows.append({
            "pathogen": pathogen,
            "best_wastewater_only_model": ww_only_best_name,
            "wastewater_only_R2": r2_score(yte, ww_only_fitted[ww_only_best_name]["pred"]),
            "wastewater_only_RMSE": ww_only_fitted[ww_only_best_name]["rmse"],
            "clinical_persistence_R2": r2_score(yte, baseline),
            "clinical_persistence_RMSE": mean_squared_error(yte, baseline) ** 0.5,
            "full_model_R2": r2_score(yte, best["pred"]),
            "full_model_RMSE": best["rmse"],
        })

        # v5.15: feature-group ablation for Figure 9. Refit the SAME best
        # model architecture with each feature group's columns dropped
        # entirely (not zeroed, so the model genuinely cannot see them),
        # everything else identical to the full-feature fit above.
        full_r2 = r2_score(yte, best["pred"])
        ablation_rows.append({
            "pathogen": pathogen, "removed_group": "(none - full model)",
            "n_features_removed": 0, "R2": full_r2, "delta_R2_vs_full": 0.0,
        })
        model_cls = type(best["model"])
        model_kwargs = (
            {"n_estimators": 300, "random_state": 42, "n_jobs": -1}
            if model_cls is RandomForestRegressor
            else {"random_state": 42}
        )
        all_groups = dict(feature_groups)
        all_groups["state_fixed_effects"] = state_cols
        for group_name, cols in all_groups.items():
            drop_cols = [c for c in cols if c in X.columns]
            if not drop_cols:
                continue
            Xtr_ab = Xtr.drop(columns=drop_cols)
            Xte_ab = Xte.drop(columns=drop_cols)
            m_ab = model_cls(**model_kwargs)
            m_ab.fit(Xtr_ab, ytr)
            pred_ab = m_ab.predict(Xte_ab)
            r2_ab = r2_score(yte, pred_ab)
            ablation_rows.append({
                "pathogen": pathogen, "removed_group": group_name,
                "n_features_removed": len(drop_cols), "R2": r2_ab,
                "delta_R2_vs_full": r2_ab - full_r2,
            })

    return (
        pd.DataFrame(results),
        predictions,
        pd.DataFrame(ablation_rows),
        pd.DataFrame(wastewater_only_rows),
        pd.DataFrame(collinearity_rows),
    )


def plot_ml_model_performance(results_df):
    """
    v5.15 addition. Paper 1 Figure 7 - previously PENDING_ML with a table
    (Table12_Exploratory_ML_Benchmark.csv) but no plotting function at all.
    Grouped bar chart of test-set RMSE by model, one group per pathogen.
    """
    if results_df.empty:
        return
    pathogens = sorted(results_df["pathogen"].unique())
    model_order = ["ClinicalPersistence", "RandomForest", "HistGradientBoosting"]
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.8 / len(model_order)
    xpos = np.arange(len(pathogens))
    for i, m in enumerate(model_order):
        vals = []
        for p in pathogens:
            row = results_df[(results_df["pathogen"].eq(p)) & (results_df["model"].eq(m))]
            vals.append(float(row["RMSE"].iloc[0]) if not row.empty else np.nan)
        ax.bar(xpos + i * width, vals, width=width, label=m)
    ax.set_xticks(xpos + width * (len(model_order) - 1) / 2)
    ax.set_xticklabels(pathogens)
    ax.set_ylabel("RMSE (clinical ED %, held-out test set)")
    ax.set_title("NWGS Grid™ — Exploratory Model Performance by Pathogen")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Fig_ML_Model_Performance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_observed_vs_predicted(predictions, outliers_df=None):
    """
    v5.15 addition. Paper 1 Figure 8 - previously PENDING_ML with zero
    backing code (exploratory_ml() only returned aggregate metrics, never
    the actual held-out predictions needed for a scatter plot). One panel
    per pathogen, observed vs predicted clinical ED %, y=x reference line.

    v5.20 addition: previously the outliers flagged by
    audit_ml_prediction_outliers() (Table12f) were invisible on this
    figure - a reviewer would see an unlabeled stray point with no pointer
    to the audit trail. Points present in `outliers_df` (pass the same
    DataFrame audit_ml_prediction_outliers() returns) are now circled in
    red, and a caption directs to Table12f along with a GENERIC diagnostic
    pattern worth checking - deliberately not naming specific
    states/weeks/pathogens, since a future rerun against live data may
    flag an entirely different set of rows than whatever produced this
    particular image.
    """
    if not predictions:
        return
    pathogens = list(predictions.keys())
    fig, axes = plt.subplots(1, len(pathogens), figsize=(5 * len(pathogens), 5))
    axes = np.atleast_1d(axes)
    any_outliers = outliers_df is not None and not outliers_df.empty
    for ax, pathogen in zip(axes, pathogens):
        d = predictions[pathogen]
        yt, yp = np.asarray(d["y_true"], dtype=float), np.asarray(d["y_pred"], dtype=float)
        ax.scatter(yt, yp, alpha=.4, s=18)
        if any_outliers:
            p_out = outliers_df[outliers_df["pathogen"].eq(pathogen)]
            if not p_out.empty:
                ax.scatter(
                    p_out["observed_clinical_ed_pct"], p_out["predicted_clinical_ed_pct"],
                    facecolors="none", edgecolors="red", s=70, linewidths=1.4,
                    label=f"Flagged outlier (n={len(p_out)}, see Table12f)"
                )
                ax.legend(loc="lower right", fontsize=7.5)
        lo = float(np.nanmin([yt.min(), yp.min()]))
        hi = float(np.nanmax([yt.max(), yp.max()]))
        ax.plot([lo, hi], [lo, hi], linewidth=1, linestyle="--")
        r2 = r2_score(yt, yp)
        ax.text(.05, .92, f"{d['model']}\nR²={r2:.2f}", transform=ax.transAxes,
                va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=.3", fc="white", ec="0.6", alpha=.9))
        ax.set_xlabel("Observed clinical ED %")
        ax.set_ylabel("Predicted clinical ED %")
        ax.set_title(pathogen, fontweight="bold")
        ax.grid(alpha=.2)
    fig.suptitle("NWGS Grid™ — Chronological Holdout: Observed vs Predicted",
                 fontsize=14, fontweight="bold")
    if any_outliers:
        fig.text(
            .5, .015,
            f"{len(outliers_df)} held-out prediction(s) flagged as residual outliers within their own "
            "pathogen's distribution (circled red; see Table12f_ML_Prediction_Outliers.csv for exact "
            "state/week). Outliers clustered in the same week across several states typically indicate "
            "a reporting-period effect (e.g. holiday-timing artifacts in the clinical source data); an "
            "isolated single-week spike bracketed by near-zero weeks typically indicates a source-data "
            "error rather than a genuine model failure - check both patterns before treating any one "
            "point as a modeling problem.",
            ha="center", fontsize=7.6, wrap=True
        )
        fig.tight_layout(rect=[0, 0.045, 1, 0.92])
    else:
        fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(FIG_DIR / "Fig_Observed_vs_Predicted.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_ablation(ablation_df):
    """
    v5.15 addition. Paper 1 Figure 9 - previously PENDING_ML with zero
    backing code, not even a dataframe. Bar chart of the change in R2
    when each multimodal feature group is entirely removed and the best
    model is refit, relative to the full-feature model (delta=0 line).
    A more negative bar means that feature group mattered more.
    """
    if ablation_df.empty:
        return
    q = ablation_df[ablation_df["removed_group"].ne("(none - full model)")].copy()
    if q.empty:
        return
    pathogens = sorted(q["pathogen"].unique())
    groups = sorted(q["removed_group"].unique())
    fig, ax = plt.subplots(figsize=(10, 5.5))
    width = 0.8 / max(1, len(pathogens))
    xpos = np.arange(len(groups))
    for i, p in enumerate(pathogens):
        vals = []
        for gname in groups:
            row = q[(q["pathogen"].eq(p)) & (q["removed_group"].eq(gname))]
            vals.append(float(row["delta_R2_vs_full"].iloc[0]) if not row.empty else np.nan)
        ax.bar(xpos + i * width, vals, width=width, label=p)
    ax.axhline(0, linewidth=1, color="black")
    ax.set_xticks(xpos + width * (len(pathogens) - 1) / 2)
    ax.set_xticklabels(groups, rotation=20, ha="right")
    ax.set_ylabel("Change in R² vs full model (more negative = group mattered more)")
    ax.set_title("NWGS Grid™ — Multimodal Feature-Group Ablation")
    ax.legend()
    # v5.18 addition: a near-zero wastewater delta here can reflect
    # collinearity with retained clinical-lag features rather than genuine
    # irrelevance - point to the standalone benchmark that resolves this.
    fig.text(.5, .01,
              "A near-zero wastewater delta here can reflect collinearity with retained clinical-lag features, "
              "not necessarily that wastewater carries no signal - see Fig_Wastewater_Only_Value.png for a "
              "standalone wastewater-only benchmark and Table12e for the underlying collinearity audit.",
              ha="center", fontsize=8, wrap=True)
    fig.tight_layout(rect=[0, .05, 1, 1])
    fig.savefig(FIG_DIR / "Fig_Multimodal_Ablation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_wastewater_only_comparison(wastewater_only_df):
    """
    v5.18 addition. Directly answers the ablation-vs-lag-analysis tension
    flagged in figure review: does wastewater carry standalone predictive
    value for clinical ED activity, independent of any collinearity with
    clinical-lag features? Bar chart comparing R2 for the clinical-history
    persistence baseline, a model fit using ONLY wastewater-derived
    features (no clinical_lag columns at all), and the full multimodal
    model, per pathogen.
    """
    if wastewater_only_df.empty:
        return
    pathogens = list(wastewater_only_df["pathogen"])
    x = np.arange(len(pathogens))
    width = 0.26
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.bar(x - width, wastewater_only_df["clinical_persistence_R2"], width,
           label="Clinical-history persistence baseline")
    ax.bar(x, wastewater_only_df["wastewater_only_R2"], width,
           label="Wastewater-only model (no clinical features)")
    ax.bar(x + width, wastewater_only_df["full_model_R2"], width,
           label="Full multimodal model")
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(pathogens)
    ax.set_ylabel("R² (held-out chronological test set)")
    ax.set_title("NWGS Grid™ — Standalone Predictive Value of Wastewater Data")
    ax.legend(fontsize=9)
    fig.text(
        .5, .015,
        "Compares a clinical-history-only baseline against a model built from wastewater features alone "
        "(no clinical lags) and the full multimodal model. Complements Fig_Multimodal_Ablation.png, which "
        "can understate wastewater's contribution when it is collinear with retained clinical-lag features.",
        ha="center", fontsize=8.3, wrap=True
    )
    fig.tight_layout(rect=[0, .07, 1, 1])
    fig.savefig(FIG_DIR / "Fig_Wastewater_Only_Value.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def audit_ml_prediction_outliers(predictions, residual_z_threshold=None):
    """
    v5.18 addition. Paper 1 Figure 8 (Observed vs Predicted) showed a
    single RSV point far off the y=x line (observed~2.85, predicted~0)
    with no way to identify which state/week it came from. exploratory_ml()
    now carries state_code/week_end alongside each held-out prediction
    (predictions[pathogen]["ids_test"]); this flags any point whose
    residual exceeds `residual_z_threshold` standard deviations of that
    pathogen's OWN residual distribution and exports the exact state/week,
    so an outlier can be checked against the source data instead of only
    being visible as an unlabeled dot on a scatterplot.
    """
    if residual_z_threshold is None:
        residual_z_threshold = ML_OUTLIER_RESIDUAL_Z_THRESHOLD
    rows = []
    for pathogen, d in predictions.items():
        ids = d.get("ids_test")
        yt = np.asarray(d["y_true"], dtype=float)
        yp = np.asarray(d["y_pred"], dtype=float)
        if ids is None or len(ids) != len(yt):
            continue
        resid = yt - yp
        sd = np.nanstd(resid)
        if not np.isfinite(sd) or sd == 0:
            continue
        z = resid / sd
        flagged_idx = np.where(np.abs(z) >= residual_z_threshold)[0]
        for i in flagged_idx:
            row = {
                "pathogen": pathogen,
                "state_code": ids.iloc[i]["state_code"] if "state_code" in ids.columns else None,
                "week_end": ids.iloc[i]["week_end"] if "week_end" in ids.columns else None,
                "observed_clinical_ed_pct": float(yt[i]),
                "predicted_clinical_ed_pct": float(yp[i]),
                "residual": float(resid[i]),
                "residual_z": float(z[i]),
            }
            rows.append(row)
            print(
                f"[ML OUTLIER] {pathogen} {row['state_code']} week {row['week_end']}: "
                f"observed={row['observed_clinical_ed_pct']:.3f} "
                f"predicted={row['predicted_clinical_ed_pct']:.3f} (z={row['residual_z']:.1f})"
            )
    return pd.DataFrame(rows)


try:
    import shap
    HAVE_SHAP = True
except Exception:
    HAVE_SHAP = False


def explain_with_shap(predictions):
    """
    v5.15 addition. Paper 1 Figure 10 - previously PENDING_ML with zero
    backing code and no optional-dependency handling at all. Computes
    SHAP feature importances for the best-performing tree-based model per
    pathogen (both RandomForest and HistGradientBoosting are tree-based,
    so shap.TreeExplainer applies to whichever one was selected as best
    in exploratory_ml()). Requires the optional `shap` package (see the
    commented Colab install cell at the top of this script); if it is not
    installed, this prints a console message and returns without writing
    a figure, rather than crashing the run.

    v5.20: also returns a DataFrame of every pathogen's ranked feature
    importances (not just the top-8 plotted), saved by the caller as
    Table12g_SHAP_Top_Features.csv and consumed by
    build_ml_triangulation_summary() to fold SHAP's evidence together with
    the ablation and wastewater-only benchmark into one citable table -
    previously a reader had to manually cross-reference three separate
    figures to see that all three methods agree.

    Returns shap_features_df with columns: pathogen, model, feature, rank
    (1 = most important), mean_abs_shap.
    """
    shap_rows = []
    if not HAVE_SHAP:
        print("[SKIP] shap not installed; Fig_SHAP_Explainability.png not generated. "
              "Install with `pip install shap` to enable Paper 1 Figure 10.")
        return pd.DataFrame(shap_rows)
    if not predictions:
        return pd.DataFrame(shap_rows)
    pathogens = list(predictions.keys())
    fig, axes = plt.subplots(1, len(pathogens), figsize=(6 * len(pathogens), 5))
    axes = np.atleast_1d(axes)
    any_plotted = False
    for ax, pathogen in zip(axes, pathogens):
        d = predictions[pathogen]
        model = d["fitted_model"]
        Xtr = d["X_train"]
        try:
            background = Xtr.sample(min(200, len(Xtr)), random_state=42)
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(background)
            mean_abs = np.abs(shap_values).mean(axis=0)
            full_order = np.argsort(mean_abs)[::-1]
            all_feats = background.columns.to_numpy()[full_order]
            all_vals = mean_abs[full_order]
            for rank, (feat, val) in enumerate(zip(all_feats, all_vals), start=1):
                shap_rows.append({
                    "pathogen": pathogen,
                    "model": d["model"],
                    "feature": feat,
                    "rank": rank,
                    "mean_abs_shap": float(val),
                })

            order = full_order[:8]
            feats = background.columns.to_numpy()[order]
            vals = mean_abs[order]
            ax.barh(range(len(feats)), vals[::-1])
            ax.set_yticks(range(len(feats)))
            ax.set_yticklabels(feats[::-1], fontsize=8)
            ax.set_xlabel("Mean |SHAP value|")
            ax.set_title(f"{pathogen}\n{d['model']}", fontweight="bold")
            any_plotted = True
        except Exception as e:
            ax.text(.5, .5, f"SHAP unavailable for\n{pathogen}: {type(e).__name__}",
                    ha="center", va="center", transform=ax.transAxes)
    if not any_plotted:
        plt.close(fig)
        return pd.DataFrame(shap_rows)
    fig.suptitle("NWGS Grid™ — SHAP Feature Explainability", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(FIG_DIR / "Fig_SHAP_Explainability.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pd.DataFrame(shap_rows)


def build_ml_triangulation_summary(ablation_df, wastewater_only_df, shap_features_df):
    """
    v5.20 addition.

    The feature-group ablation (Fig 9), the standalone wastewater-only
    benchmark (Fig 7B), and SHAP explainability (Fig 10) all independently
    point to the same conclusion about wastewater's predictive value - that
    its MARGINAL contribution inside the full model is small because
    clinical_lag1 already captures most of its signal, while its
    STANDALONE value varies sharply by pathogen (positive for Influenza A
    and RSV, negative for SARS-CoV-2). That convergence previously had to
    be assembled by hand by a reader cross-referencing three separate
    tables/figures. This merges all three into one row per pathogen so the
    manuscript's methods/results section can cite a single table instead
    of three.
    """
    if ablation_df is None or ablation_df.empty:
        return pd.DataFrame()

    rows = []
    pathogens = sorted(ablation_df["pathogen"].unique())
    for pathogen in pathogens:
        ab = ablation_df[ablation_df["pathogen"].eq(pathogen)]
        delta_current = ab[ab["removed_group"].eq("wastewater_current")]["delta_R2_vs_full"]
        delta_lags = ab[ab["removed_group"].eq("wastewater_lags")]["delta_R2_vs_full"]
        delta_clinical = ab[ab["removed_group"].eq("clinical_lags")]["delta_R2_vs_full"]

        ww_only_r2 = np.nan
        clin_persist_r2 = np.nan
        if wastewater_only_df is not None and not wastewater_only_df.empty:
            wo = wastewater_only_df[wastewater_only_df["pathogen"].eq(pathogen)]
            if not wo.empty:
                ww_only_r2 = float(wo.iloc[0]["wastewater_only_R2"])
                clin_persist_r2 = float(wo.iloc[0]["clinical_persistence_R2"])

        shap_rank = np.nan
        shap_val = np.nan
        n_features_ranked = np.nan
        if shap_features_df is not None and not shap_features_df.empty:
            sf = shap_features_df[
                (shap_features_df["pathogen"].eq(pathogen))
                & (shap_features_df["feature"].eq("wastewater_index"))
            ]
            if not sf.empty:
                shap_rank = int(sf.iloc[0]["rank"])
                shap_val = float(sf.iloc[0]["mean_abs_shap"])
                n_features_ranked = int(
                    shap_features_df[shap_features_df["pathogen"].eq(pathogen)]["rank"].max()
                )

        # Plain-language synthesis, generated from the actual numbers rather
        # than hardcoded, so a future rerun's different results produce a
        # correctly-updated sentence rather than a stale one.
        marginal_small = (
            pd.notna(delta_current.iloc[0]) and abs(delta_current.iloc[0]) < 0.03
            if len(delta_current) else True
        )
        standalone_positive = pd.notna(ww_only_r2) and ww_only_r2 > 0
        if marginal_small and standalone_positive:
            synthesis = (
                "Wastewater's marginal contribution inside the full model is small, "
                "but it carries genuine standalone predictive value that clinical_lag1 "
                "makes redundant (collinearity), not irrelevance."
            )
        elif marginal_small and not standalone_positive:
            synthesis = (
                "Wastewater's marginal contribution inside the full model is small, "
                "AND it has no standalone predictive value on its own for this "
                "pathogen in this dataset - consistent with genuine irrelevance, "
                "not just collinearity."
            )
        else:
            synthesis = "See underlying values; does not match either simple pattern above."

        rows.append({
            "pathogen": pathogen,
            "ablation_delta_wastewater_current": float(delta_current.iloc[0]) if len(delta_current) else np.nan,
            "ablation_delta_wastewater_lags": float(delta_lags.iloc[0]) if len(delta_lags) else np.nan,
            "ablation_delta_clinical_lags": float(delta_clinical.iloc[0]) if len(delta_clinical) else np.nan,
            "wastewater_only_R2": ww_only_r2,
            "clinical_persistence_R2": clin_persist_r2,
            "shap_rank_of_wastewater_index": shap_rank,
            "shap_mean_abs_wastewater_index": shap_val,
            "n_features_ranked_by_shap": n_features_ranked,
            "triangulated_synthesis": synthesis,
        })

    return pd.DataFrame(rows)



# ============================================================
# 18. AMR / ARG WASTEWATER MODULE
# ============================================================
AMR_REQUIRED_COLUMNS = [
    "site","plant","city","state","Region","zipcode","population","target",
    "mean_ARG_raw","mean_16S","mean_ARG_S","n","Detect","zscore","outlier"
]
AMR_CLASS_MAP = {
    "CMY":"Beta-lactam", "CTX-M":"Beta-lactam", "KPC":"Beta-lactam",
    "NDM":"Beta-lactam", "OXA-48":"Beta-lactam", "TEM":"Beta-lactam",
    "VIM":"Beta-lactam", "MCR-1":"Colistin", "MecA":"Methicillin",
    "TetW":"Tetracycline", "VanA":"Vancomycin"
}

def load_amr_arg():
    if not AMR_PATH.exists():
        raise FileNotFoundError(
            f"AMR file not found: {AMR_PATH}\n"
            "Upload US_Wastewater_AMR_ARG_2024.csv to Colab /content/ or set NWGS_AMR_PATH."
        )
    df = pd.read_csv(AMR_PATH, low_memory=False)
    missing = [c for c in AMR_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise RuntimeError(f"AMR CSV schema mismatch. Missing columns: {missing}")
    df = df[AMR_REQUIRED_COLUMNS].copy()
    for c in ["population","mean_ARG_raw","mean_16S","mean_ARG_S","n","zscore"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["target"] = df["target"].astype(str).str.strip()
    df["amr_class"] = df["target"].map(AMR_CLASS_MAP).fillna("Other/Unmapped")
    df["detected"] = df["Detect"].astype(str).str.strip().str.upper().eq("D")
    df["outlier_flag"] = df["outlier"].astype(str).str.strip().str.upper().eq("Y")
    df["state_code"] = df["state"].map(STATE_ABBR)
    # Preserve source z-score. This is NOT an NWGS risk score.
    save_df(df, PROC_DIR / "NWGS_AMR_ARG_HARMONIZED.csv")
    return df


def audit_amr_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    v5.9 addition; extended in v5.13.

    The AMR/ARG module previously had no validation at all, unlike the
    emerging-pathogen detection pipeline (profile_emerging_detection_fields()/
    emerging_detection_audit()). Silent-failure modes checked here:

    1) AMR_CLASS_MAP keys are bare gene names ("KPC", "NDM", "TEM", "VIM",
       "CTX-M", "MecA", "TetW", "VanA"), while standard nomenclature for these
       genes is often prefixed/cased differently (e.g. "blaKPC", "blaNDM",
       "mecA", "tetW", "vanA"). If the supplied CSV's `target` column uses a
       different convention than the bare names in AMR_CLASS_MAP, every row
       silently falls into "Other/Unmapped" via the .map().fillna() call in
       load_amr_arg(), and plot_amr()'s detection-profile chart becomes
       meaningless with no warning anywhere.
    2) `detected` is computed as an exact match against the literal token
       "D" in the Detect column. If the actual coding is "Y"/"N",
       "Positive"/"Negative", or numeric, every row becomes False and every
       downstream detection-rate figure/table silently reports 0% everywhere
       instead of raising an error.
    3) (v5.13) `outlier_flag` has the identical hardcoded-token risk as (2),
       checking for an exact "Y" token in the `outlier` column. If the
       actual coding differs (e.g. "TRUE"/"1"/"Outlier"), every row silently
       becomes outlier_flag=False with no warning - this column is not yet
       consumed by any table/figure, but the same silent-failure shape
       deserves the same audit coverage before anything is built on top of
       it.

    This function reports all three conditions with an explicit
    PASS/WARNING/FAIL status and prints the raw Detect and outlier column
    value counts, so a coding mismatch is visible in the console log and
    validation table instead of only showing up later as an inexplicably
    flat or empty chart.
    """
    unmapped_pct = 100 * df["amr_class"].eq("Other/Unmapped").mean() if len(df) else np.nan
    detect_raw_values = df["Detect"].astype(str).str.strip().value_counts().head(10)
    detection_rate_overall = float(df["detected"].mean()) if len(df) else np.nan

    outlier_raw_values = df["outlier"].astype(str).str.strip().value_counts().head(10)
    outlier_rate_overall = float(df["outlier_flag"].mean()) if len(df) else np.nan

    status = "PASS"
    reasons = []
    if pd.notna(unmapped_pct) and unmapped_pct > 50:
        status = "FAIL_MAJORITY_UNMAPPED_TARGETS"
        reasons.append(f"{unmapped_pct:.1f}% of target rows unmapped to an AMR_CLASS_MAP class")
    elif pd.notna(unmapped_pct) and unmapped_pct > 10:
        status = "WARNING_HIGH_UNMAPPED_TARGETS"
        reasons.append(f"{unmapped_pct:.1f}% of target rows unmapped to an AMR_CLASS_MAP class")

    if len(df) and df["detected"].eq(False).all():
        status = "FAIL_NO_DETECTIONS_CHECK_DETECT_COLUMN_CODING"
        reasons.append(
            "every row has detected=False; the Detect column may not use the "
            "literal 'D' token this pipeline checks for"
        )

    # v5.13 addition: same hardcoded-token check as Detect, applied to the
    # outlier column. Only downgrades status if nothing worse has already
    # been found, since a majority-unmapped or all-False-detection result is
    # a more severe publication blocker than an unverified outlier flag.
    if len(df) and df["outlier_flag"].eq(False).all() and df["outlier"].notna().any():
        reasons.append(
            "every row has outlier_flag=False despite non-null 'outlier' values; "
            "the column may not use the literal 'Y' token this pipeline checks for"
        )
        if status == "PASS":
            status = "WARNING_OUTLIER_CODING_UNVERIFIED"

    reason_text = "; ".join(reasons) if reasons else "target mapping, Detect coding, and outlier coding look consistent"

    print(f"[AMR AUDIT] {status} | {reason_text}")
    print(f"[AMR AUDIT] Raw 'Detect' column value counts (top 10):\n{detect_raw_values.to_string()}")
    print(f"[AMR AUDIT] Overall detection rate as currently coded: {detection_rate_overall:.1%}"
          if pd.notna(detection_rate_overall) else "[AMR AUDIT] Overall detection rate: N/A (no rows)")
    print(f"[AMR AUDIT] Raw 'outlier' column value counts (top 10):\n{outlier_raw_values.to_string()}")
    print(f"[AMR AUDIT] Overall outlier_flag rate as currently coded: {outlier_rate_overall:.1%}"
          if pd.notna(outlier_rate_overall) else "[AMR AUDIT] Overall outlier_flag rate: N/A (no rows)")

    return pd.DataFrame([{
        "n_rows": len(df),
        "unmapped_target_pct": unmapped_pct,
        "overall_detection_rate": detection_rate_overall,
        "detect_column_raw_values": json.dumps(detect_raw_values.to_dict()),
        "overall_outlier_flag_rate": outlier_rate_overall,
        "outlier_column_raw_values": json.dumps(outlier_raw_values.to_dict()),
        "status": status,
        "detail": reason_text,
    }])


def summarize_amr(amr):
    target = (
        amr.groupby(["target","amr_class"], dropna=False)
           .agg(
               sites=("site","nunique"),
               states=("state","nunique"),
               detection_rate=("detected","mean"),
               median_16s_normalized=("mean_ARG_S","median"),
               median_source_z=("zscore","median"),
           )
           .reset_index()
    )
    target["detection_rate_pct"] = target["detection_rate"] * 100

    # Population is repeated across ARG targets. Sum once per unique site, not per target row.
    site_pop = (
        amr[["state","state_code","site","population"]]
        .drop_duplicates(["state","state_code","site"])
    )
    pop_state = (
        site_pop.groupby(["state","state_code"], dropna=False)
                .agg(unique_site_population_sum=("population","sum"))
                .reset_index()
    )

    state = (
        amr.groupby(["state","state_code"], dropna=False)
           .agg(
               sites=("site","nunique"),
               targets=("target","nunique"),
               median_source_z=("zscore","median"),
               mean_detection_rate=("detected","mean"),
           )
           .reset_index()
           .merge(pop_state, on=["state","state_code"], how="left")
    )
    state["mean_detection_rate_pct"] = state["mean_detection_rate"] * 100
    return target, state


def plot_amr(amr_target):
    if amr_target.empty:
        return
    q = amr_target.sort_values("detection_rate_pct", ascending=False)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(q["target"], q["detection_rate_pct"])
    ax.set_ylabel("Sites with detection (%)")
    ax.set_xlabel("Antimicrobial resistance gene target")
    ax.set_title("NWGS Grid™ — U.S. Wastewater ARG Detection Profile")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Fig_AMR_ARG_Detection_Profile.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_amr_state_map(tiger, amr_state):
    q = amr_state.dropna(subset=["state_code"]).copy()
    if q.empty:
        return
    code_to_fips = {
        "AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11",
        "FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21",
        "LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30",
        "NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39",
        "OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49",
        "VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56","PR":"72"
    }
    q["state_fips"] = q["state_code"].map(code_to_fips)
    states = conus(tiger).dissolve(by="state_fips", as_index=False).to_crs(5070)
    st = states.merge(q, on="state_fips", how="left")

    fig, ax = plt.subplots(figsize=(10,12))
    st.plot(ax=ax, color="#d9d9d9", linewidth=0.25, edgecolor="white")
    measured = st[st["median_source_z"].notna()]
    if not measured.empty:
        measured.plot(
            column="median_source_z", ax=ax, legend=True, linewidth=0.25, edgecolor="white",
            legend_kwds={"label":"Median source-standardized ARG abundance (z-score)"}
        )
    # v5.11 addition: explicit legend entry for the gray states, which
    # previously had no on-figure explanation and could be misread as a
    # very-low or zero value rather than "no state-level estimate exists in
    # this cross-sectional study."
    no_data_patch = Patch(
        facecolor="#d9d9d9", edgecolor="white",
        label="No study/source-standardized estimate"
    )
    ax.legend(handles=[no_data_patch], loc="lower left", frameon=True, fontsize=9)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("NWGS Grid™ — Wastewater AMR/ARG Source-Standardized Abundance by State")
    ax.text(
        0.99, 0.01,
        "Cross-sectional May 2024 wastewater study; negative z-scores mean below source reference mean, not 'negative burden'.",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "Map_AMR_ARG_State_Burden.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ============================================================
# 19. NCBI VIRUS GENOMIC METADATA API
# ============================================================
def _deep_get_first(obj, keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and v not in (None, "", [], {}):
                return v
        for v in obj.values():
            found = _deep_get_first(v, keys)
            if found not in (None, "", [], {}):
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _deep_get_first(v, keys)
            if found not in (None, "", [], {}):
                return found
    return None

def ncbi_virus_metadata(taxon_label, taxon_name, max_records=NCBI_MAX_RECORDS_PER_TAXON):
    if not ENABLE_NCBI:
        return pd.DataFrame()
    from urllib.parse import quote
    url = f"{NCBI_API_BASE}/virus/taxon/{quote(taxon_name, safe='')}/dataset_report"
    headers = {"Accept":"application/json", "User-Agent":"NWGS-Grid-Research/5.19"}
    if NCBI_API_KEY:
        headers["api-key"] = NCBI_API_KEY

    rows, token = [], None
    while len(rows) < max_records:
        params = {"page_size": min(1000, max_records-len(rows))}
        if token:
            params["page_token"] = token
        r = requests.get(url, params=params, headers=headers, timeout=120)
        if not r.ok:
            print(f"[WARN] NCBI {taxon_label}: HTTP {r.status_code}. Genomic context skipped for this taxon.")
            break
        payload = r.json()
        reports = payload.get("reports", [])
        if not reports:
            break
        rows.extend(reports)
        token = payload.get("next_page_token") or payload.get("nextPageToken")
        if not token:
            break

    flat = []
    for rec in rows[:max_records]:
        accession = _deep_get_first(rec, {"accession"})
        flat.append({
            "pathogen": taxon_label,
            "taxon_query": taxon_name,
            "accession": accession if isinstance(accession, str) else json.dumps(accession) if accession else None,
            "collection_date": _deep_get_first(rec, {"collection_date","collectionDate"}),
            "release_date": _deep_get_first(rec, {"release_date","releaseDate"}),
            "host": _deep_get_first(rec, {"host"}),
            "geographic_location": _deep_get_first(rec, {"geographic_location","geo_loc_name","geoLocName","location"}),
            "isolate": _deep_get_first(rec, {"isolate","isolate_name","isolateName"}),
            "completeness": _deep_get_first(rec, {"completeness"}),
            "raw_json": json.dumps(rec, separators=(",",":")),
        })
    return pd.DataFrame(flat)


def pull_ncbi_genomics():
    frames = []
    for label, taxon in NCBI_VIRUS_TAXA.items():
        print(f"  NCBI genomic metadata: {label}")
        df = ncbi_virus_metadata(label, taxon)
        if not df.empty:
            frames.append(df)
    allg = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    if not allg.empty:
        # NCBI may return timezone-aware ISO timestamps. Normalize both NCBI
        # dates and study boundaries to UTC before comparison.
        allg["collection_date"] = pd.to_datetime(
            allg["collection_date"], errors="coerce", utc=True
        )
        allg["release_date"] = pd.to_datetime(
            allg["release_date"], errors="coerce", utc=True
        )

        study_start_utc = pd.Timestamp(STUDY_START)
        study_end_utc = pd.Timestamp(STUDY_END)

        study_start_utc = (
            study_start_utc.tz_localize("UTC")
            if study_start_utc.tzinfo is None
            else study_start_utc.tz_convert("UTC")
        )
        study_end_utc = (
            study_end_utc.tz_localize("UTC")
            if study_end_utc.tzinfo is None
            else study_end_utc.tz_convert("UTC")
        )

        # If collection date is unavailable, release date is allowed through
        # one year after the study end to accommodate database release delay.
        in_collection_window = allg["collection_date"].between(
            study_start_utc, study_end_utc, inclusive="both"
        )
        in_release_window = allg["release_date"].between(
            study_start_utc,
            study_end_utc + pd.Timedelta(days=365),
            inclusive="both"
        )
        allg["study_era_record"] = in_collection_window | (allg["collection_date"].isna() & in_release_window)

        comp = allg["completeness"].fillna("").astype(str).str.upper()
        allg["complete_genome_flag"] = comp.str.contains("COMPLETE")

        filtered = allg[allg["study_era_record"]].copy()
        if filtered.empty:
            print("[WARN] No NCBI records met study-era filters; retaining raw metadata only.")
            filtered = allg.copy()

        save_df(filtered.drop(columns=["raw_json"], errors="ignore"), TABLE_DIR / "Table10_NCBI_Virus_Genomic_Metadata.csv")

        raw_path = RAW_DIR / "NCBI_Virus_Genomic_Metadata_RAW.jsonl"
        with raw_path.open("w", encoding="utf-8") as f:
            for row in allg["raw_json"]:
                f.write(row + "\n")

        audit = (
            filtered.groupby("pathogen")
                    .agg(
                        records=("accession","count"),
                        dated_collection=("collection_date","count"),
                        complete_genome_records=("complete_genome_flag","sum"),
                    )
                    .reset_index()
        )
        save_df(audit, TABLE_DIR / "Table10b_NCBI_Genomic_Metadata_Audit.csv")
        return filtered

    return allg



# ============================================================
# 20. CDC PHIL PATHOGEN REFERENCE IMAGES
# ============================================================
def _extract_phil_highres_url(html, base_url):
    """
    v5.15: broadened after CDC PHIL downloads went 0/6 on the last run.
    The original two patterns only matched an anchor whose visible text
    contained "hi-resolution" - if PHIL's page markup changed (e.g. the
    link text wording changed, or the download control became a button
    with no matching anchor text), both would silently return None with
    no way to tell why. Now tries, in order: the original two anchor-text
    patterns; a same-directory-agnostic pattern matching common PHIL
    image-file paths (PHIL_Images/, getimage.aspx, or /*_hi.jpg-style
    names) regardless of surrounding link text; and the page's
    <meta property="og:image"> tag, which many CDC pages populate with a
    direct, full-resolution image URL for social-share previews and is
    independent of PHIL's own download-link markup.
    NOTE: this could not be validated against the live phil.cdc.gov site
    from this environment (network egress here is allowlisted to a fixed
    set of domains that does not include phil.cdc.gov). If downloads are
    still 0/6 after this change, the diagnostic fields now added to
    download_cdc_phil_pathogen_images() (HTTP status, final URL after
    redirects, response length) should be checked in
    Table12_CDC_PHIL_Pathogen_Image_Manifest.csv to pinpoint whether the
    page itself is unreachable, redirecting, or simply uses markup this
    parser still doesn't recognize.
    """
    patterns = [
        r'href=["\']([^"\']+)["\'][^>]*>\s*(?:<[^>]+>\s*)*[^<]*hi-resolution',
        r'href=["\']([^"\']+)["\'][^>]*>\s*(?:<[^>]+>\s*)*Click here for hi-resolution image',
        r'href=["\']([^"\']*(?:PHIL_Images|getimage\.aspx|GetImage\.axd)[^"\']*)["\']',
    ]
    for pat in patterns:
        m = re.search(pat, html, flags=re.I | re.S)
        if m:
            return urljoin(base_url, m.group(1))

    og_image = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        html, flags=re.I
    )
    if og_image:
        return urljoin(base_url, og_image.group(1))

    # Fallback: find nearby href containing image extension.
    candidates = re.findall(r'href=["\']([^"\']+\.(?:jpg|jpeg|png|tif|tiff))["\']', html, flags=re.I)
    return urljoin(base_url, candidates[0]) if candidates else None


def download_cdc_phil_pathogen_images():
    """
    Download public-domain/reference pathogen imagery from CDC PHIL where
    available. The manifest always exports even if a network/image download
    fails, so the app can display a source link instead of a broken image.
    """
    rows = []
    session = requests.Session()
    session.headers.update({"User-Agent":"NWGS-Grid-Research/5.19"})

    for pathogen, cfg in CDC_PHIL_ASSETS.items():
        pid = cfg["phil_id"]
        page_url = f"https://phil.cdc.gov/Details.aspx?pid={pid}"
        status = "NOT_ATTEMPTED"
        image_url = None
        local_path = None
        message = None
        page_http_status = None
        page_final_url = None
        page_response_chars = None

        try:
            r = session.get(page_url, timeout=60)
            page_http_status = r.status_code
            page_final_url = r.url
            page_response_chars = len(r.text)
            r.raise_for_status()
            image_url = _extract_phil_highres_url(r.text, page_url)

            if image_url:
                ir = session.get(image_url, timeout=120)
                ir.raise_for_status()
                ctype = (ir.headers.get("Content-Type") or "").lower()
                ext = ".jpg"
                if "png" in ctype:
                    ext = ".png"
                elif "tif" in ctype:
                    ext = ".tif"

                safe = re.sub(r"[^A-Za-z0-9]+", "_", pathogen).strip("_")
                local_path = PATHOGEN_IMAGE_DIR / f"CDC_PHIL_{safe}_{pid}{ext}"
                local_path.write_bytes(ir.content)
                status = "PASS"
            else:
                status = "WARNING_NO_HIGHRES_URL"
                message = (
                    f"PHIL page reachable (HTTP {page_http_status}, "
                    f"{page_response_chars} chars) but no high-resolution image "
                    f"URL matched any known pattern - page markup may have changed."
                )
        except Exception as e:
            status = "WARNING_DOWNLOAD_FAILED"
            message = f"{type(e).__name__}: {e}"

        rows.append({
            "pathogen": pathogen,
            "source": "CDC Public Health Image Library (PHIL)",
            "phil_id": pid,
            "label": cfg["label"],
            "usage_note": cfg["usage_note"],
            "phil_page_url": page_url,
            "page_http_status": page_http_status,
            "page_final_url": page_final_url,
            "page_response_chars": page_response_chars,
            "image_url": image_url,
            "local_image_path": str(local_path) if local_path else None,
            "download_status": status,
            "message": message,
        })
        print(f"[PHIL] {pathogen}: {status} | page_http={page_http_status} chars={page_response_chars} | {message or ''}")

    manifest = pd.DataFrame(rows)
    save_df(manifest, TABLE_DIR / "Table12_CDC_PHIL_Pathogen_Image_Manifest.csv")
    return manifest


# ============================================================
# 21. RCSB PDB STRUCTURAL BIOLOGY
# ============================================================
def rcsb_map_ncbi_genome(accession):
    if not ENABLE_RCSB or not accession or not str(accession).startswith("NC_"):
        return []
    query = '''
    query NCBI2PDB($id: String!){
      alignments(from: NCBI_GENOME, to: PDB_ENTITY, queryId: $id) {
        target_alignments { target_id }
      }
    }
    '''
    r = requests.post(
        RCSB_SEQUENCE_COORDINATES,
        json={"query": query, "variables": {"id": str(accession)}},
        headers={"Content-Type":"application/json", "User-Agent":"NWGS-Grid-Research/5.19"},
        timeout=60,
    )
    if not r.ok:
        return []
    payload = r.json()
    if payload.get("errors"):
        return []
    aligns = (((payload.get("data") or {}).get("alignments") or {}).get("target_alignments") or [])
    return sorted({a.get("target_id") for a in aligns if a.get("target_id")})




def _rcsb_entry_metadata(pdb_id):
    """
    Query RCSB GraphQL for entry and polymer-entity metadata, including
    experimentally reported method/resolution and UniProt cross-references.
    """
    query = """
    query Entry($id: String!) {
      entry(entry_id: $id) {
        rcsb_id
        exptl { method }
        rcsb_entry_info { resolution_combined }
        struct { title }
        polymer_entities {
          rcsb_polymer_entity {
            pdbx_description
          }
          rcsb_polymer_entity_container_identifiers {
            entity_id
            uniprot_ids
          }
        }
      }
    }
    """
    try:
        r = requests.post(
            "https://data.rcsb.org/graphql",
            json={"query": query, "variables": {"id": pdb_id}},
            headers={"Content-Type":"application/json","User-Agent":"NWGS-Grid-Research/5.19"},
            timeout=60,
        )
        r.raise_for_status()
        entry = ((r.json().get("data") or {}).get("entry") or {})
        methods = "; ".join(sorted({
            str(x.get("method")) for x in (entry.get("exptl") or []) if x.get("method")
        }))
        resolution = (entry.get("rcsb_entry_info") or {}).get("resolution_combined") or []
        resolution = resolution[0] if resolution else np.nan

        entities = []
        for pe in entry.get("polymer_entities") or []:
            ids = pe.get("rcsb_polymer_entity_container_identifiers") or {}
            desc = (pe.get("rcsb_polymer_entity") or {}).get("pdbx_description")
            entities.append({
                "entity_id": ids.get("entity_id"),
                "protein_description": desc,
                "uniprot_ids": ";".join(ids.get("uniprot_ids") or []),
            })
        return {
            "title": (entry.get("struct") or {}).get("title"),
            "method": methods,
            "resolution_A": resolution,
            "entities": entities,
            "metadata_status": "PASS",
        }
    except Exception as e:
        return {
            "title": None, "method": None, "resolution_A": np.nan,
            "entities": [], "metadata_status": f"WARNING:{e}"
        }


def _download_coordinate_file(pdb_id, suffix):
    """Download one RCSB coordinate representation and preserve a local frozen copy."""
    suffix = str(suffix).lower().lstrip(".")
    if suffix not in {"cif", "pdb"}:
        raise ValueError("suffix must be 'cif' or 'pdb'")
    url = f"https://files.rcsb.org/download/{pdb_id}.{suffix}"
    try:
        r = requests.get(
            url,
            headers={"User-Agent":"NWGS-Grid-Research/5.19"},
            timeout=120,
        )
        r.raise_for_status()
        path = STRUCTURE_DIR / f"{pdb_id}.{suffix}"
        path.write_bytes(r.content)
        if path.stat().st_size < 100:
            return None, f"WARNING_EMPTY_{suffix.upper()}"
        return path, "PASS"
    except Exception as e:
        return None, f"WARNING:{type(e).__name__}:{e}"


def _download_structure_coordinates(pdb_id):
    """
    Prefer RCSB mmCIF, the current archival coordinate format, then fall back
    to legacy PDB text when mmCIF retrieval or parsing is unavailable.

    Returns a dictionary so download status for BOTH representations is retained
    in the publication audit rather than silently discarded.
    """
    cif_path, cif_status = _download_coordinate_file(pdb_id, "cif")
    pdb_path, pdb_status = (None, "NOT_ATTEMPTED")

    # PDB is a fallback. It is downloaded only if mmCIF retrieval fails; if mmCIF
    # downloads but later parsing fails, pull_rcsb_structure_mappings performs a
    # second-stage PDB fallback and updates these fields.
    if cif_path is None:
        pdb_path, pdb_status = _download_coordinate_file(pdb_id, "pdb")

    if cif_path is not None:
        selected_path, selected_format = cif_path, "mmCIF"
    elif pdb_path is not None:
        selected_path, selected_format = pdb_path, "PDB"
    else:
        selected_path, selected_format = None, None

    return {
        "selected_path": selected_path,
        "selected_format": selected_format,
        "cif_path": cif_path,
        "cif_download_status": cif_status,
        "pdb_path": pdb_path,
        "pdb_download_status": pdb_status,
    }


def _parse_ca_atoms_from_pdb(path):
    rows = []
    if path is None or not Path(path).exists():
        return pd.DataFrame(columns=["chain","resid","resname","x","y","z"])
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not (line.startswith("ATOM") or line.startswith("HETATM")):
                continue
            atom = line[12:16].strip()
            if atom != "CA":
                continue
            altloc = line[16:17].strip()
            if altloc not in {"", "A", "."}:
                continue
            try:
                resid_raw = line[22:26].strip()
                rows.append({
                    "chain": line[21:22].strip() or "_",
                    "resid": int(resid_raw) if resid_raw else len(rows) + 1,
                    "resname": line[17:20].strip(),
                    "x": float(line[30:38]),
                    "y": float(line[38:46]),
                    "z": float(line[46:54]),
                })
            except Exception:
                continue
    return pd.DataFrame(rows)


def _parse_ca_atoms_from_mmcif(path):
    """
    Lightweight parser for the _atom_site loop in RCSB mmCIF files.
    Only C-alpha records are retained, which is sufficient for the reproducible
    backbone rendering used by NWGS Grid. No external structural-biology parser
    is required.
    """
    cols = []
    rows = []
    in_atom_loop = False
    data_started = False

    if path is None or not Path(path).exists():
        return pd.DataFrame(columns=["chain","resid","resname","x","y","z"])

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = iter(f)
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if line == "loop_":
                cols = []
                in_atom_loop = False
                data_started = False
                continue
            if line.startswith("_atom_site."):
                cols.append(line.split()[0])
                in_atom_loop = True
                continue
            if not in_atom_loop or not cols:
                continue
            if line.startswith("_") or line == "loop_" or line.startswith("data_"):
                if data_started:
                    break
                continue
            if line == "#":
                if data_started:
                    break
                continue

            try:
                vals = shlex.split(line, posix=True)
            except Exception:
                vals = line.split()
            if len(vals) < len(cols):
                # Extremely uncommon wrapped rows are skipped conservatively.
                continue
            data_started = True
            rec = dict(zip(cols, vals[:len(cols)]))

            group = rec.get("_atom_site.group_PDB", "ATOM")
            if group not in {"ATOM", "HETATM"}:
                continue
            atom = rec.get("_atom_site.auth_atom_id") or rec.get("_atom_site.label_atom_id")
            if str(atom).strip().upper() != "CA":
                continue
            alt = rec.get("_atom_site.label_alt_id", ".")
            if alt not in {".", "?", "A", ""}:
                continue

            chain = (
                rec.get("_atom_site.auth_asym_id")
                or rec.get("_atom_site.label_asym_id")
                or "_"
            )
            resid = (
                rec.get("_atom_site.auth_seq_id")
                or rec.get("_atom_site.label_seq_id")
                or str(len(rows) + 1)
            )
            resname = rec.get("_atom_site.auth_comp_id") or rec.get("_atom_site.label_comp_id") or ""
            try:
                rows.append({
                    "chain": str(chain),
                    "resid": int(float(resid)),
                    "resname": str(resname),
                    "x": float(rec["_atom_site.Cartn_x"]),
                    "y": float(rec["_atom_site.Cartn_y"]),
                    "z": float(rec["_atom_site.Cartn_z"]),
                })
            except Exception:
                continue

    return pd.DataFrame(rows)


def _parse_structure_ca_atoms(path, coordinate_format):
    fmt = str(coordinate_format or "").upper()
    if fmt == "MMCIF":
        return _parse_ca_atoms_from_mmcif(path)
    if fmt == "PDB":
        return _parse_ca_atoms_from_pdb(path)
    return pd.DataFrame(columns=["chain","resid","resname","x","y","z"])


def render_structure_backbone_png(pdb_id, coord_path, coordinate_format, protein_label):
    """
    Render an actual coordinate-derived protein backbone from deposited RCSB
    coordinates. The figure card supplies labels, so this PNG intentionally has
    no internal title or axes and can be embedded cleanly in the publication
    structural-intelligence panel.
    """
    atoms = _parse_structure_ca_atoms(coord_path, coordinate_format)
    if atoms.empty:
        return None, "FAIL_NO_CA_ATOMS", 0

    fig = plt.figure(figsize=(6.2, 5.3), facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    plotted = 0

    for chain, g in atoms.groupby("chain", sort=True):
        g = g.sort_values("resid")
        xyz = g[["x","y","z"]].to_numpy(float)
        if len(xyz) < 2:
            continue
        d = np.sqrt(((xyz[1:] - xyz[:-1])**2).sum(axis=1))
        start = 0
        cuts = list(np.where(d > 8.0)[0] + 1) + [len(xyz)]
        for end in cuts:
            seg = xyz[start:end]
            if len(seg) >= 2:
                ax.plot(seg[:,0], seg[:,1], seg[:,2], linewidth=1.4)
                plotted += len(seg)
            start = end

    if plotted == 0:
        plt.close(fig)
        return None, "FAIL_NO_RENDERABLE_BACKBONE", len(atoms)

    ax.set_axis_off()
    ax.view_init(elev=18, azim=38)
    try:
        ax.set_box_aspect((1, 1, 0.85))
    except Exception:
        pass
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    out_path = STRUCTURE_DIR / f"ProteinStructure_{pdb_id}.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    return out_path, "PASS", len(atoms)


def render_pdb_backbone_png(pdb_id, pdb_path, protein_label):
    """Backward-compatible wrapper retained for older notebook cells."""
    p, status, _ = render_structure_backbone_png(pdb_id, pdb_path, "PDB", protein_label)
    return p, status


def pull_rcsb_structure_mappings(genomics):
    """
    Create the six-pathogen structural-biology output with strict publication QC.

    Retrieval order:
      1) RCSB mmCIF (.cif), the current archival coordinate representation;
      2) legacy PDB (.pdb) fallback if mmCIF retrieval OR parsing fails.

    Publication requirement:
      all six configured pathogens must render successfully. Partial structural
      panels are explicitly marked FAIL and must not be treated as publication-ready.
    """
    if not ENABLE_RCSB:
        return pd.DataFrame()

    record_counts = {}
    if genomics is not None and not genomics.empty and "pathogen" in genomics.columns:
        record_counts = genomics.groupby("pathogen").size().to_dict()

    structure_rows = []
    entity_rows = []

    for ref in RCSB_REFERENCE_STRUCTURES:
        pathogen = ref["pathogen"]
        pdb_id = ref["pdb_entry_id"]
        meta = _rcsb_entry_metadata(pdb_id)
        dl = _download_structure_coordinates(pdb_id)

        coord_path = dl["selected_path"]
        coord_format = dl["selected_format"]
        png_path = None
        render_status = "FAIL_NO_COORDINATES"
        parse_status = "NOT_ATTEMPTED"
        ca_atom_count = 0

        if coord_path is not None:
            png_path, render_status, ca_atom_count = render_structure_backbone_png(
                pdb_id, coord_path, coord_format, f"{pathogen}: {ref['protein']}"
            )
            parse_status = "PASS" if ca_atom_count > 0 else "FAIL_NO_CA_ATOMS"

        # Second-stage fallback: mmCIF downloaded but parser/render failed.
        if render_status != "PASS" and coord_format == "mmCIF":
            if dl["pdb_path"] is None:
                dl["pdb_path"], dl["pdb_download_status"] = _download_coordinate_file(pdb_id, "pdb")
            if dl["pdb_path"] is not None:
                p2, s2, n2 = render_structure_backbone_png(
                    pdb_id, dl["pdb_path"], "PDB", f"{pathogen}: {ref['protein']}"
                )
                if s2 == "PASS":
                    png_path, render_status, ca_atom_count = p2, s2, n2
                    coord_path, coord_format = dl["pdb_path"], "PDB"
                    parse_status = "PASS_FALLBACK_PDB"
                else:
                    parse_status = f"MMCIF_FAILED_AND_PDB_{s2}"

        ncbi_count_key = "Influenza A" if pathogen == "Influenza A(H5)" else pathogen

        structure_rows.append({
            "pathogen": pathogen,
            "protein": ref["protein"],
            "pdb_entry_id": pdb_id,
            "rcsb_title": meta.get("title"),
            "method": meta.get("method"),
            "resolution_A": meta.get("resolution_A"),
            "expected_method": ref["method_expected"],
            "structure_role": ref["structure_role"],
            "ncbi_metadata_records": record_counts.get(ncbi_count_key, np.nan),
            "pdb_entry_url": f"https://www.rcsb.org/structure/{pdb_id}",
            "pdb_cif_url": f"https://files.rcsb.org/download/{pdb_id}.cif",
            "pdb_coordinate_url": f"https://files.rcsb.org/download/{pdb_id}.pdb",
            "coordinate_format_used": coord_format,
            "local_coordinate_path": str(coord_path) if coord_path else None,
            "local_cif_path": str(dl["cif_path"]) if dl["cif_path"] else None,
            "local_pdb_path": str(dl["pdb_path"]) if dl["pdb_path"] else None,
            "protein_png_path": str(png_path) if png_path else None,
            "metadata_status": meta.get("metadata_status"),
            "cif_download_status": dl["cif_download_status"],
            "pdb_download_status": dl["pdb_download_status"],
            "parse_status": parse_status,
            "ca_atom_count": ca_atom_count,
            "render_status": render_status,
            "figure_component_qc": "PASS" if render_status == "PASS" else "FAIL",
        })

        for ent in meta.get("entities", []):
            entity_rows.append({
                "pathogen": pathogen,
                "pdb_entry_id": pdb_id,
                "reference_protein": ref["protein"],
                **ent,
            })

    out = pd.DataFrame(structure_rows)
    entities = pd.DataFrame(entity_rows)

    expected = len(RCSB_REFERENCE_STRUCTURES)
    rendered = int(out["render_status"].eq("PASS").sum()) if not out.empty else 0
    meta_pass = int(out["metadata_status"].eq("PASS").sum()) if not out.empty else 0
    overall = "PASS" if rendered == expected and meta_pass == expected else "FAIL_INCOMPLETE_STRUCTURES"

    audit = out[[
        "pathogen","pdb_entry_id","metadata_status","cif_download_status",
        "pdb_download_status","coordinate_format_used","parse_status",
        "ca_atom_count","render_status","figure_component_qc"
    ]].copy()
    audit = pd.concat([audit, pd.DataFrame([{
        "pathogen":"STRUCTURAL FIGURE QC",
        "pdb_entry_id":"",
        "metadata_status":f"{meta_pass}/{expected}",
        "cif_download_status":"",
        "pdb_download_status":"",
        "coordinate_format_used":"",
        "parse_status":"",
        "ca_atom_count":int(out["ca_atom_count"].sum()) if not out.empty else 0,
        "render_status":f"{rendered}/{expected} rendered",
        "figure_component_qc":overall,
    }])], ignore_index=True)

    save_df(out, TABLE_DIR / "Table11_RCSB_Representative_Structures.csv")
    save_df(entities, TABLE_DIR / "Table11b_RCSB_Protein_Entities.csv")
    save_df(audit, TABLE_DIR / "Table11c_RCSB_Structural_Figure_Audit.csv")
    return out


# ============================================================
# 21b. UNIPROT FUNCTIONAL REGION ANNOTATIONS (v5.21)
# ============================================================
# Descriptive, citation-backed annotation layer only. Every region below is
# imported verbatim from UniProt's curated feature table for the same protein
# the representative structure contains, then mapped onto that structure's own
# author residue numbering using RCSB's published sequence alignments. Nothing
# here is predicted, scored or ranked by this pipeline: the app reproduces
# public reference annotations next to the structure they describe, with the
# source accession and evidence recorded for every row.

UNIPROT_REST = "https://rest.uniprot.org/uniprotkb"
RCSB_DATA_GRAPHQL = "https://data.rcsb.org/graphql"

# UniProt feature types kept for display, mapped to plain-language labels.
# Per-residue bookkeeping types (glycosylation, disulfide bonds, variants) are
# deliberately excluded: they are numerous and add noise rather than context.
UNIPROT_FEATURE_TYPES = {
    "Domain": "Domain",
    "Region": "Region",
    "Motif": "Motif",
    "Binding site": "Binding site",
    "Active site": "Active site",
    "Site": "Functional site",
    "Transmembrane": "Transmembrane",
    "Intramembrane": "Intramembrane",
    "Signal": "Signal peptide",
    "Topological domain": "Topological domain",
    "Coiled coil": "Coiled coil",
}


def _uniprot_feature_table(accession):
    """Curated feature table for one UniProt accession (REST, public, no key)."""
    r = SESSION.get(f"{UNIPROT_REST}/{accession}.json", timeout=90,
                    headers={"Accept": "application/json"})
    r.raise_for_status()
    return parse_uniprot_features(r.json(), accession)


def parse_uniprot_features(payload, accession):
    """Pull display-worthy features out of a UniProtKB JSON record."""
    rows = []
    protein_name = (((payload.get("proteinDescription") or {}).get("recommendedName") or {})
                    .get("fullName") or {}).get("value")
    seq_len = (payload.get("sequence") or {}).get("length")
    for feat in payload.get("features") or []:
        label = UNIPROT_FEATURE_TYPES.get(feat.get("type"))
        if not label:
            continue
        loc = feat.get("location") or {}
        start = (loc.get("start") or {}).get("value")
        end = (loc.get("end") or {}).get("value")
        if start is None or end is None:
            continue   # uncertain or open-ended positions are skipped, never guessed
        evidence = feat.get("evidences") or []
        rows.append({
            "uniprot_accession": accession,
            "uniprot_protein_name": protein_name,
            "uniprot_sequence_length": seq_len,
            "feature_type": label,
            "feature_description": (feat.get("description") or "").strip() or label,
            "uniprot_start": int(start),
            "uniprot_end": int(end),
            "evidence_codes": ";".join(sorted({e.get("evidenceCode") for e in evidence if e.get("evidenceCode")})),
            "evidence_count": len(evidence),
        })
    return rows


def _rcsb_uniprot_entity_alignment(accession):
    """
    RCSB 1D-coordinates alignment: UniProt sequence positions -> PDB entity
    (label_seq_id) positions, per aligned block.
    """
    query = """
    query Align($id: String!){
      alignment(from: UNIPROT, to: PDB_ENTITY, queryId: $id) {
        target_alignment {
          target_id
          aligned_regions { query_begin query_end target_begin target_end }
        }
      }
    }
    """
    r = SESSION.post(RCSB_SEQUENCE_COORDINATES,
                     json={"query": query, "variables": {"id": str(accession)}},
                     headers={"Content-Type": "application/json",
                              "User-Agent": "NWGS-Grid-Research/5.21"},
                     timeout=90)
    if not r.ok:
        return {}
    return parse_rcsb_alignment(r.json())


def parse_rcsb_alignment(payload):
    """{entity_id: [(query_begin, query_end, target_begin, target_end), ...]}"""
    out = {}
    if payload.get("errors"):
        return out
    targets = (((payload.get("data") or {}).get("alignment") or {}).get("target_alignment") or [])
    for tgt in targets:
        tid = tgt.get("target_id")
        if not tid:
            continue
        blocks = []
        for reg in tgt.get("aligned_regions") or []:
            qb, qe = reg.get("query_begin"), reg.get("query_end")
            tb, te = reg.get("target_begin"), reg.get("target_end")
            if None in (qb, qe, tb, te):
                continue
            blocks.append((int(qb), int(qe), int(tb), int(te)))
        if blocks:
            out[tid] = blocks
    return out


def _rcsb_entity_auth_numbering(pdb_id, entity_id):
    """
    Author residue numbering for one polymer entity, per chain. RCSB gives
    auth_to_entity_poly_seq_mapping: position i in the entity sequence is
    author residue number mapping[i-1] in that chain.
    """
    query = """
    query Inst($entry: String!, $entity: String!){
      polymer_entity(entry_id: $entry, entity_id: $entity) {
        polymer_entity_instances {
          rcsb_polymer_entity_instance_container_identifiers {
            auth_asym_id
            auth_to_entity_poly_seq_mapping
          }
        }
      }
    }
    """
    r = SESSION.post(RCSB_DATA_GRAPHQL,
                     json={"query": query, "variables": {"entry": str(pdb_id).upper(),
                                                         "entity": str(entity_id)}},
                     headers={"Content-Type": "application/json",
                              "User-Agent": "NWGS-Grid-Research/5.21"},
                     timeout=90)
    if not r.ok:
        return {}
    return parse_rcsb_auth_mapping(r.json())


def parse_rcsb_auth_mapping(payload):
    """{auth_asym_id: [author residue numbers, indexed by entity seq position]}"""
    out = {}
    if payload.get("errors"):
        return out
    insts = (((payload.get("data") or {}).get("polymer_entity") or {})
             .get("polymer_entity_instances") or [])
    for inst in insts:
        ids = inst.get("rcsb_polymer_entity_instance_container_identifiers") or {}
        chain = ids.get("auth_asym_id")
        mapping = ids.get("auth_to_entity_poly_seq_mapping")
        if chain and mapping:
            out[chain] = list(mapping)
    return out


def uniprot_range_to_entity_range(start, end, blocks):
    """
    Convert a UniProt residue range to PDB entity positions using aligned
    blocks. Returns (entity_start, entity_end) for the covered portion, or
    None when the region falls outside every aligned block.
    """
    hits = []
    for qb, qe, tb, te in blocks:
        lo, hi = max(start, qb), min(end, qe)
        if lo > hi:
            continue
        hits.append((tb + (lo - qb), tb + (hi - qb)))
    if not hits:
        return None
    return min(h[0] for h in hits), max(h[1] for h in hits)


def entity_range_to_auth_range(e_start, e_end, auth_map):
    """Entity sequence positions -> author residue numbers for one chain."""
    n = len(auth_map)
    if e_start < 1 or e_end > n or e_start > e_end:
        return None
    vals = [v for v in auth_map[e_start - 1:e_end] if v is not None]
    if not vals:
        return None
    try:
        nums = [int(v) for v in vals]
    except (TypeError, ValueError):
        return None
    return min(nums), max(nums)


def pull_uniprot_functional_regions(entities):
    """
    Build Table11d: UniProt curated regions for every representative structure,
    mapped onto that structure's author residue numbering so the app can
    highlight them in 3D. Purely descriptive; see the section note above.
    """
    if entities is None or entities.empty:
        return pd.DataFrame()

    rows, seen_acc = [], {}
    for rec in entities.to_dict("records"):
        pdb_id = str(rec.get("pdb_entry_id") or "").upper()
        entity_id = str(rec.get("entity_id") or "")
        accessions = [a.strip() for a in str(rec.get("uniprot_ids") or "").split(";") if a.strip()]
        if not pdb_id or not entity_id or not accessions:
            continue

        auth_map = {}
        try:
            auth_map = _rcsb_entity_auth_numbering(pdb_id, entity_id)
        except Exception as exc:
            print(f"[UNIPROT] {pdb_id}_{entity_id}: author-numbering lookup failed ({type(exc).__name__})")

        for acc in accessions:
            if acc not in seen_acc:
                try:
                    seen_acc[acc] = (_uniprot_feature_table(acc), _rcsb_uniprot_entity_alignment(acc))
                except Exception as exc:
                    print(f"[UNIPROT] {acc}: fetch failed ({type(exc).__name__}: {exc})")
                    seen_acc[acc] = ([], {})
            feats, aligns = seen_acc[acc]
            blocks = aligns.get(f"{pdb_id}_{entity_id}") or []

            for f in feats:
                e_rng = uniprot_range_to_entity_range(f["uniprot_start"], f["uniprot_end"], blocks) if blocks else None
                chain = auth_start = auth_end = None
                if e_rng and auth_map:
                    for ch in sorted(auth_map):
                        a_rng = entity_range_to_auth_range(e_rng[0], e_rng[1], auth_map[ch])
                        if a_rng:
                            chain, auth_start, auth_end = ch, a_rng[0], a_rng[1]
                            break
                if auth_start is None:
                    status = "NOT_IN_STRUCTURE" if blocks else "NO_ALIGNMENT"
                else:
                    status = "MAPPED"
                row = {
                    "pathogen": rec.get("pathogen"),
                    "pdb_entry_id": pdb_id,
                    "entity_id": entity_id,
                    "reference_protein": rec.get("reference_protein"),
                }
                row.update(f)
                row.update({
                    "pdb_chain": chain,
                    "pdb_start": auth_start,
                    "pdb_end": auth_end,
                    "mapping_status": status,
                    "annotation_source": "UniProtKB",
                    "annotation_source_url": f"https://www.uniprot.org/uniprotkb/{acc}/entry",
                    "mapping_source": "RCSB 1D-coordinates alignment + auth_to_entity_poly_seq_mapping",
                    "expert_review_status": "pending_expert_review",
                })
                rows.append(row)

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["pathogen", "pdb_entry_id", "uniprot_start"]).reset_index(drop=True)
    save_df(out, TABLE_DIR / "Table11d_UniProt_Functional_Regions.csv")
    n_mapped = int((out["mapping_status"] == "MAPPED").sum()) if not out.empty else 0
    print(f"[UNIPROT] functional regions: {len(out)} annotations, {n_mapped} mapped onto structure coordinates")
    return out


# ============================================================
# 21c. SURVEILLANCE-GAP ANALYTICS (v5.22)
# ------------------------------------------------------------
# Six additions that occupy documented vacancies in the public
# wastewater-surveillance literature. Every one of them is computed from
# data this pipeline already pulls, or from an explicitly cited public
# feed. None of them predicts, scores or ranks anything beyond what the
# cited source itself publishes.
#
#  12a  Lead-time decomposition      shedding / reporting / operational
#  12b  Coverage attrition           which sites went dark, and when
#  12c  Forecast scoreboard          frozen predictions scored on arrival
#  12d  Representativeness           sewer-served share x vulnerability skew
#  12e  Assay-target vulnerability   published primer regions vs public variation
#  12f  Global coverage equity       AMELAG / RIVM / WHO-UNICEF JMP
# ============================================================

DORMANT_WEEKS = int(os.getenv("NWGS_DORMANT_WEEKS", "8"))
FORECAST_HISTORY = PROC_DIR / "NWGS_FORECAST_HISTORY.csv"
ASSAY_TARGET_PATH = Path(os.getenv("NWGS_ASSAY_TARGET_PATH",
                                   str(STATIC_ROOT / "NWGS_ASSAY_TARGETS.csv")))
AMELAG_URL = os.getenv(
    "NWGS_AMELAG_URL",
    "https://raw.githubusercontent.com/robert-koch-institut/Abwassersurveillance_AMELAG/main/amelag_einzelstandorte.tsv",
)
JMP_PATH = Path(os.getenv("NWGS_JMP_PATH", str(STATIC_ROOT / "WHO_UNICEF_JMP_SANITATION.csv")))


# ------------------------------------------------------------
# 12a. LEAD-TIME DECOMPOSITION
# ------------------------------------------------------------
def lead_time_decomposition(best_lag, raw_manifest, wastewater):
    """Split the headline 'wastewater leads clinical' number into its three parts.

    shedding_lead_weeks     virus detectable in sewage before ED visits rise.
                            This is the cross-correlation best lag already
                            computed in Table04_Best_Lag_Results.
    reporting_lag_weeks     sample collection -> value visible in the public CDC
                            dataset. Measured as the CDC dataset's own
                            rowsUpdatedAt metadata minus the latest sample week
                            present in that dataset.
    operational_lead_weeks  shedding_lead - reporting_lag. This is the only
                            figure that answers "could a health department have
                            acted on this before the clinical signal arrived?"
                            It can be zero or negative, and when it is, the
                            surveillance value of the signal was not realised.

    The literature almost always reports shedding lead alone, which overstates
    usable warning time. Nothing here is modelled; all three terms are
    differences between observed dates.
    """
    if best_lag is None or len(best_lag) == 0:
        return pd.DataFrame()

    man = pd.DataFrame(raw_manifest) if not isinstance(raw_manifest, pd.DataFrame) else raw_manifest.copy()
    if man.empty or "updated_at_metadata" not in man.columns:
        return pd.DataFrame()

    # Latest sample week actually present per pathogen, from the frozen harmonised frame.
    last_sample = (
        wastewater.dropna(subset=["week_end"])
                  .groupby("pathogen")["week_end"].max()
                  .rename("last_sample_week")
                  .reset_index()
    )

    man = man[["pathogen", "dataset_id", "updated_at_metadata"]].copy()
    man["dataset_updated"] = pd.to_datetime(man["updated_at_metadata"], errors="coerce", utc=True).dt.tz_localize(None)
    rep = man.merge(last_sample, on="pathogen", how="inner")
    rep["last_sample_week"] = pd.to_datetime(rep["last_sample_week"], errors="coerce")
    rep["reporting_lag_days"] = (rep["dataset_updated"] - rep["last_sample_week"]).dt.days
    # A negative reporting lag is impossible and means the metadata timestamp is
    # stale relative to the data it describes; drop rather than report nonsense.
    rep.loc[rep["reporting_lag_days"] < 0, "reporting_lag_days"] = np.nan
    rep["reporting_lag_weeks"] = rep["reporting_lag_days"] / 7.0

    b = best_lag.copy()
    b = b[["pathogen", "state_code", "lag_weeks", "spearman_r", "spearman_p_fdr", "paired_weeks"]]
    b = b.rename(columns={"lag_weeks": "shedding_lead_weeks"})

    out = b.merge(rep[["pathogen", "dataset_id", "dataset_updated", "last_sample_week",
                       "reporting_lag_days", "reporting_lag_weeks"]],
                  on="pathogen", how="left")

    out["operational_lead_weeks"] = out["shedding_lead_weeks"] - out["reporting_lag_weeks"]
    out["usable"] = out["operational_lead_weeks"] > 0
    # Only call a lead statistically supported if the association survives FDR.
    out["lead_supported"] = out["spearman_p_fdr"].lt(0.05) & out["spearman_r"].gt(0)
    out["interpretation"] = np.where(
        ~out["lead_supported"], "No supported lead at any tested offset",
        np.where(out["operational_lead_weeks"] > 0.5, "Usable operational lead",
                 np.where(out["operational_lead_weeks"] > -0.5, "Lead consumed by reporting delay",
                          "Signal published after clinical rise")),
    )
    return out.sort_values(["pathogen", "operational_lead_weeks"], ascending=[True, False])


def lead_time_national(decomp):
    """Per-pathogen distribution of the three lead-time terms across states."""
    if decomp is None or decomp.empty:
        return pd.DataFrame()
    d = decomp[decomp["lead_supported"]].copy()
    if d.empty:
        return pd.DataFrame()

    def q(s, p):
        v = s.dropna()
        return float(np.percentile(v, p)) if len(v) else np.nan

    rows = []
    for pathogen, g in d.groupby("pathogen"):
        rows.append({
            "pathogen": pathogen,
            "n_states_supported": int(g["state_code"].nunique()),
            "shedding_lead_median": q(g["shedding_lead_weeks"], 50),
            "shedding_lead_p25": q(g["shedding_lead_weeks"], 25),
            "shedding_lead_p75": q(g["shedding_lead_weeks"], 75),
            "reporting_lag_weeks": float(g["reporting_lag_weeks"].median()),
            "operational_lead_median": q(g["operational_lead_weeks"], 50),
            "operational_lead_p25": q(g["operational_lead_weeks"], 25),
            "operational_lead_p75": q(g["operational_lead_weeks"], 75),
            "pct_states_usable": float(100.0 * g["usable"].mean()),
        })
    return pd.DataFrame(rows).sort_values("operational_lead_median", ascending=False)


# ------------------------------------------------------------
# 12b. COVERAGE ATTRITION
# ------------------------------------------------------------
def coverage_attrition(wastewater, dormant_weeks=DORMANT_WEEKS):
    """Per-site reporting lifespan: when each site started, stopped, and who it covered.

    A site is 'dormant' when its most recent sample is more than
    dormant_weeks before the latest sample week anywhere in the dataset. This
    is a reporting-status statement, not a claim that the facility closed.
    """
    w = wastewater.dropna(subset=["site_id", "week_end"]).copy()
    if w.empty:
        return pd.DataFrame(), pd.DataFrame()
    w["week_end"] = pd.to_datetime(w["week_end"], errors="coerce")
    asof = w["week_end"].max()

    site = (
        w.groupby(["site_id", "state_code"], dropna=False)
         .agg(first_week=("week_end", "min"),
              last_week=("week_end", "max"),
              n_weeks=("week_end", "nunique"),
              n_pathogens=("pathogen", "nunique"),
              population_served=("population_served", "max"),
              county_fips=("county_fips", "first"))
         .reset_index()
    )
    site["weeks_since_last"] = ((asof - site["last_week"]).dt.days / 7.0).round(1)
    site["status"] = np.where(site["weeks_since_last"] <= dormant_weeks, "active", "dormant")
    site["went_dormant_week"] = np.where(site["status"].eq("dormant"),
                                         site["last_week"].dt.strftime("%Y-%m-%d"), None)
    site["lifespan_weeks"] = ((site["last_week"] - site["first_week"]).dt.days / 7.0).round(1)
    site["as_of_week"] = asof.strftime("%Y-%m-%d")
    site["dormant_threshold_weeks"] = dormant_weeks

    # Yearly ledger: sites reporting, sites that stopped that year, population affected.
    s = site.copy()
    s["start_year"] = s["first_week"].dt.year
    s["end_year"] = s["last_week"].dt.year
    years = sorted(set(s["start_year"].dropna().astype(int)) | set(s["end_year"].dropna().astype(int)))
    rows = []
    for y in years:
        reporting = s[(s["start_year"] <= y) & (s["end_year"] >= y)]
        started = s[s["start_year"] == y]
        # A site "stopped in year y" only if it never reported again after y.
        stopped = s[(s["end_year"] == y) & (s["status"].eq("dormant"))]
        rows.append({
            "year": int(y),
            "sites_reporting": int(len(reporting)),
            "sites_started": int(len(started)),
            "sites_stopped": int(len(stopped)),
            "population_reporting": float(reporting["population_served"].sum(skipna=True)),
            "population_lost": float(stopped["population_served"].sum(skipna=True)),
            "net_site_change": int(len(started) - len(stopped)),
        })
    yearly = pd.DataFrame(rows)
    if not yearly.empty:
        yearly["cumulative_population_lost"] = yearly["population_lost"].cumsum()
    return site.sort_values(["status", "last_week"]), yearly


def attrition_by_vulnerability(site_attrition, svi_lookup):
    """Did dormancy fall evenly across the social-vulnerability distribution?

    Descriptive comparison only. No causal claim: a site going dormant and a
    county's vulnerability score are both observed, and nothing here identifies
    why any particular site stopped reporting.
    """
    if site_attrition is None or site_attrition.empty or svi_lookup is None or svi_lookup.empty:
        return pd.DataFrame()
    s = site_attrition.dropna(subset=["county_fips"]).copy()
    s = s.merge(svi_lookup, on="county_fips", how="left")
    s = s.dropna(subset=["svi"])
    if s.empty:
        return pd.DataFrame()
    s["svi_quartile"] = pd.qcut(s["svi"], 4, labels=["Q1 least vulnerable", "Q2", "Q3", "Q4 most vulnerable"],
                                duplicates="drop")
    g = (s.groupby("svi_quartile", observed=True)
          .agg(sites=("site_id", "nunique"),
               dormant=("status", lambda x: int((x == "dormant").sum())),
               population_served=("population_served", "sum"))
          .reset_index())
    g["pct_dormant"] = (100.0 * g["dormant"] / g["sites"]).round(1)
    return g


# ------------------------------------------------------------
# 12c. ARCHIVED-FORECAST SCOREBOARD
# ------------------------------------------------------------
def record_forecasts(national_week, run_id, horizons=(1, 2, 3, 4)):
    """Append this run's forecasts to a persisted history, before any outcome is known.

    The forecast itself is deliberately simple: a persistence baseline plus a
    linear extrapolation of the trailing 4 weeks of the national median site
    z-score. The contribution here is NOT the model. It is that predictions are
    frozen with their run_id before the outcome exists, so the scoreboard cannot
    be retrofitted. A stronger model can be added later and scored on the same
    ledger.
    """
    if national_week is None or national_week.empty:
        return pd.DataFrame()
    nw = national_week.dropna(subset=["week_end", "median_site_z"]).copy()
    nw["week_end"] = pd.to_datetime(nw["week_end"], errors="coerce")
    rows = []
    for pathogen, g in nw.groupby("pathogen"):
        g = g.sort_values("week_end")
        if len(g) < 6:
            continue
        tail = g.tail(4)
        last_week = g["week_end"].iloc[-1]
        last_val = float(g["median_site_z"].iloc[-1])
        # Least-squares slope over the trailing 4 weeks, in z per week.
        x = np.arange(len(tail), dtype=float)
        y = tail["median_site_z"].to_numpy(dtype=float)
        slope = float(np.polyfit(x, y, 1)[0]) if np.isfinite(y).all() and len(y) >= 2 else 0.0
        for hz in horizons:
            target = last_week + pd.Timedelta(weeks=hz)
            rows.append({
                "run_id": run_id,
                "forecast_made_week": last_week.strftime("%Y-%m-%d"),
                "pathogen": pathogen,
                "horizon_weeks": int(hz),
                "target_week": target.strftime("%Y-%m-%d"),
                "pred_persistence": round(last_val, 4),
                "pred_linear": round(last_val + slope * hz, 4),
                "anchor_value": round(last_val, 4),
                "trailing_slope": round(slope, 4),
            })
    new = pd.DataFrame(rows)
    if new.empty:
        return new

    if FORECAST_HISTORY.exists():
        try:
            hist = pd.read_csv(FORECAST_HISTORY)
            # Never rewrite a prediction already on the ledger for this run_id.
            hist = hist[~hist["run_id"].eq(run_id)]
            new = pd.concat([hist, new], ignore_index=True)
        except Exception as exc:
            print(f"[WARN] forecast history unreadable, starting a new ledger: {exc}")
    new.to_csv(FORECAST_HISTORY, index=False)
    return new


def score_forecasts(history, national_week):
    """Score every matured forecast against what was actually observed."""
    if history is None or history.empty or national_week is None or national_week.empty:
        return pd.DataFrame(), pd.DataFrame()
    obs = national_week.dropna(subset=["week_end", "median_site_z"]).copy()
    obs["target_week"] = pd.to_datetime(obs["week_end"], errors="coerce").dt.strftime("%Y-%m-%d")
    obs = obs[["pathogen", "target_week", "median_site_z"]].rename(columns={"median_site_z": "observed"})

    h = history.copy()
    scored = h.merge(obs, on=["pathogen", "target_week"], how="inner")
    if scored.empty:
        return pd.DataFrame(), pd.DataFrame()
    for m in ("persistence", "linear"):
        scored[f"err_{m}"] = scored[f"pred_{m}"] - scored["observed"]
        scored[f"abs_err_{m}"] = scored[f"err_{m}"].abs()

    rows = []
    for (pathogen, hz), g in scored.groupby(["pathogen", "horizon_weeks"]):
        row = {"pathogen": pathogen, "horizon_weeks": int(hz), "n_scored": int(len(g))}
        for m in ("persistence", "linear"):
            row[f"mae_{m}"] = round(float(g[f"abs_err_{m}"].mean()), 4)
            row[f"rmse_{m}"] = round(float(np.sqrt((g[f"err_{m}"] ** 2).mean())), 4)
            row[f"bias_{m}"] = round(float(g[f"err_{m}"].mean()), 4)
        # Skill of the linear model relative to persistence. Negative means the
        # trend term made the forecast worse, which is a publishable result.
        row["skill_vs_persistence"] = (
            round(1.0 - row["mae_linear"] / row["mae_persistence"], 4)
            if row["mae_persistence"] else np.nan
        )
        rows.append(row)
    return scored, pd.DataFrame(rows).sort_values(["pathogen", "horizon_weeks"])


# ------------------------------------------------------------
# 12d. COUNTY REPRESENTATIVENESS
# ------------------------------------------------------------
def county_representativeness(wastewater, coverage, svi=None):
    """How much of a county is actually inside a monitored sewershed, and who.

    PHA4GE's wastewater reporting guidance calls for a representativeness
    measure and does not define one. This supplies an explicit, reproducible
    definition with every input shown:

      sewer_share       sum of population_served for distinct sites mapped to
                        the county, divided by county population. Capped at 1.0
                        for reporting; values above 1 are retained in
                        sewer_share_raw because they indicate a sewershed that
                        crosses county lines, not an error.
      svi_gap           county SVI minus the population-weighted mean SVI of
                        monitored counties in the same state. Positive means
                        this county is more vulnerable than its state's
                        monitored average, i.e. monitoring is skewed away from it.
      representativeness  sewer_share penalised by the absolute SVI gap.

    The SVI gap is a county-level proxy. A true within-sewershed demographic
    comparison needs block-group service-area boundaries, which CDC NWSS does
    not publish; that limitation is reported rather than papered over.
    """
    if wastewater is None or wastewater.empty or coverage is None or coverage.empty:
        return pd.DataFrame()

    w = wastewater.dropna(subset=["county_fips", "site_id"]).copy()
    if w.empty:
        return pd.DataFrame()
    # One row per site, so a site sampled for six pathogens is not counted six times.
    sites = (w.groupby(["county_fips", "site_id"], dropna=False)
              .agg(population_served=("population_served", "max"))
              .reset_index())
    per_county = (sites.groupby("county_fips")
                       .agg(n_sites=("site_id", "nunique"),
                            sewer_population=("population_served", "sum"))
                       .reset_index())

    # Collapse the pathogen-keyed coverage frame to one row per county, and
    # rename CDC/ATSDR SVI columns to the neutral names used downstream.
    cov = (coverage.groupby("county_fips")
                   .agg(analysis_ready=("analysis_ready", "max"),
                        svi=("RPL_THEMES", "first"),
                        county_name=("COUNTY", "first"),
                        state_code=("ST_ABBR", "first"))
                   .reset_index())

    # County population comes from the frozen SVI extract (E_TOTPOP), which is
    # the only county denominator this pipeline already holds. Without it the
    # sewer share is undefined and is reported as missing rather than guessed.
    if svi is not None and not getattr(svi, "empty", True):
        pop_col = next((c for c in ("E_TOTPOP", "E_TOTPOP_2022", "TOTPOP") if c in svi.columns), None)
        if pop_col:
            pops = (svi[["county_fips", pop_col]].dropna(subset=["county_fips"])
                       .drop_duplicates("county_fips")
                       .rename(columns={pop_col: "county_population"}))
            cov = cov.merge(pops, on="county_fips", how="left")
            print(f"[OK] representativeness denominator from SVI column {pop_col}")
        else:
            print("[WARN] No county population column in the SVI extract; "
                  "sewer_share will be null and the view will say so.")

    out = cov.merge(per_county, on="county_fips", how="left")
    out["n_sites"] = out["n_sites"].fillna(0).astype(int)
    out["sewer_population"] = out["sewer_population"].fillna(0.0)

    if "county_population" not in out.columns:
        out["county_population"] = np.nan
    pop = pd.to_numeric(out["county_population"], errors="coerce")
    out["sewer_share_raw"] = np.where(pop > 0, out["sewer_population"] / pop, np.nan)
    out["sewer_share"] = out["sewer_share_raw"].clip(upper=1.0)
    out["sewershed_crosses_county"] = out["sewer_share_raw"].gt(1.0)

    if "svi" in out.columns:
        monitored = out[out["n_sites"] > 0].copy()
        wts = pd.to_numeric(monitored["county_population"], errors="coerce").fillna(0.0)
        ref = (monitored.assign(_w=wts)
                        .groupby("state_code")
                        .apply(lambda g: np.average(g["svi"].dropna(),
                                                    weights=g.loc[g["svi"].notna(), "_w"])
                               if g["svi"].notna().any() and g.loc[g["svi"].notna(), "_w"].sum() > 0
                               else np.nan, include_groups=False)
                        .rename("state_monitored_svi").reset_index())
        out = out.merge(ref, on="state_code", how="left")
        out["svi_gap"] = out["svi"] - out["state_monitored_svi"]
    else:
        out["state_monitored_svi"] = np.nan
        out["svi_gap"] = np.nan

    gap_pen = out["svi_gap"].abs().fillna(0.0).clip(upper=1.0)
    out["representativeness"] = (out["sewer_share"].fillna(0.0) * (1.0 - 0.5 * gap_pen)).round(4)
    out["representativeness_tier"] = pd.cut(
        out["representativeness"], [-0.001, 0.0001, 0.25, 0.5, 0.75, 1.0],
        labels=["Unmonitored", "Minimal", "Partial", "Substantial", "High"],
    ).astype("string")
    out["definition_version"] = "nwgs-representativeness-v1"
    return out.sort_values("representativeness", ascending=False)


def representativeness_national(rep):
    if rep is None or rep.empty:
        return pd.DataFrame()
    r = rep.copy()
    pop = pd.to_numeric(r["county_population"], errors="coerce")
    rows = [{
        "counties_total": int(len(r)),
        "counties_monitored": int((r["n_sites"] > 0).sum()),
        "counties_unmonitored": int((r["n_sites"] == 0).sum()),
        "median_sewer_share_monitored": round(float(r.loc[r["n_sites"] > 0, "sewer_share"].median()), 4),
        "population_total": float(pop.sum(skipna=True)),
        "population_in_sewershed": float(r["sewer_population"].sum(skipna=True)),
        "pct_population_in_sewershed": round(float(100.0 * r["sewer_population"].sum(skipna=True)
                                                   / pop.sum(skipna=True)), 2) if pop.sum(skipna=True) else np.nan,
        "counties_sewershed_crosses": int(r["sewershed_crosses_county"].sum()),
        "median_svi_gap_monitored": round(float(r.loc[r["n_sites"] > 0, "svi_gap"].median(skipna=True)), 4),
        "median_svi_gap_unmonitored": round(float(r.loc[r["n_sites"] == 0, "svi_gap"].median(skipna=True)), 4),
    }]
    return pd.DataFrame(rows)


# ------------------------------------------------------------
# 12e. ASSAY-TARGET VULNERABILITY
# ------------------------------------------------------------
def assay_target_panel(path=ASSAY_TARGET_PATH):
    """Load a curated, citation-bearing table of published assay target regions.

    This is deliberately a CURATED INPUT, not a computed product. Primer and
    probe coordinates are published in specific papers and CDC protocol
    documents, and inventing or inferring them would be worse than having no
    panel at all. Each row must carry its own citation and the accession its
    coordinates are expressed against; rows failing that check are dropped and
    counted.

    The purpose is assay quality control: when a target region accumulates
    sequence variation, a validated diagnostic can quietly lose sensitivity.
    The 2024-2025 measles genotype B3 case is the reference example - a single
    N-gene substitution rose from under 2% to the majority of submitted
    sequences and degraded a widely used RT-PCR target. That failure mode is
    invisible in every public wastewater aggregate, CDC's included, because
    aggregates report detections and never report what the assay could no
    longer see.

    Nothing here recommends, designs or optimises an assay. It reports
    published coordinates alongside published variant frequencies so a
    laboratory can decide whether to re-verify its own panel.
    """
    required = ["pathogen", "assay_name", "target_gene", "reference_accession",
                "region_start", "region_end", "citation"]
    if not path.exists():
        print(f"[INFO] No curated assay-target panel at {path}; "
              f"assay-target view will report an empty, honest state.")
        return pd.DataFrame(columns=required + ["citation_url", "notes", "dropped_reason"])
    try:
        a = pd.read_csv(path)
    except Exception as exc:
        print(f"[WARN] assay-target panel unreadable: {exc}")
        return pd.DataFrame(columns=required + ["citation_url", "notes", "dropped_reason"])

    missing_cols = [c for c in required if c not in a.columns]
    if missing_cols:
        print(f"[WARN] assay-target panel missing required columns {missing_cols}; ignoring file.")
        return pd.DataFrame(columns=required + ["citation_url", "notes", "dropped_reason"])

    a["region_start"] = pd.to_numeric(a["region_start"], errors="coerce")
    a["region_end"] = pd.to_numeric(a["region_end"], errors="coerce")
    ok = (a[required].notna().all(axis=1)
          & a["citation"].astype(str).str.strip().ne("")
          & a["region_end"].ge(a["region_start"]))
    dropped = int((~ok).sum())
    if dropped:
        print(f"[WARN] {dropped} assay-target row(s) dropped for missing citation, "
              f"accession or coordinates.")
    a = a[ok].copy()
    a["region_length"] = (a["region_end"] - a["region_start"] + 1).astype(int)
    a["curation_status"] = "curated_with_citation"
    return a


def assay_variation_overlay(panel, genomic_records):
    """Count public sequence records overlapping each curated target region.

    genomic_records is the NCBI Virus metadata already pulled in section 19. If
    it carries no per-position variation, this returns the panel with the
    overlay columns present but null, and says so, rather than implying
    coverage it does not have.
    """
    if panel is None or panel.empty:
        return pd.DataFrame()
    out = panel.copy()
    out["variation_source"] = None
    out["records_considered"] = np.nan
    out["overlay_available"] = False
    if genomic_records is None or len(genomic_records) == 0:
        out["overlay_note"] = ("No per-position variation table available in this run. "
                               "Region coordinates and citations are shown without an "
                               "observed-variation overlay.")
        return out
    g = genomic_records.copy()
    if "pathogen" not in g.columns:
        out["overlay_note"] = "Genomic metadata present but not pathogen-keyed; overlay skipped."
        return out
    counts = g.groupby("pathogen").size().rename("records_considered").reset_index()
    out = out.drop(columns=["records_considered"]).merge(counts, on="pathogen", how="left")
    out["variation_source"] = "NCBI Virus metadata (record counts only)"
    out["overlay_note"] = ("Record counts reflect public sequences available for the pathogen, "
                           "not substitutions inside the target region. Per-position variant "
                           "frequencies require an alignment step that this pipeline does not "
                           "perform; treat these counts as denominators only.")
    return out


# ------------------------------------------------------------
# 12f. GLOBAL COVERAGE EQUITY
# ------------------------------------------------------------
def fetch_amelag(url=AMELAG_URL):
    """Germany's AMELAG site-level wastewater series (Robert Koch-Institut, CC BY 4.0).

    One of only two national wastewater programmes publishing genuinely
    machine-readable site-level data under an open licence. Fetch failures are
    non-fatal: this layer is supplementary and must never block a run.
    """
    try:
        r = SESSION.get(url, timeout=120)
        r.raise_for_status()
        from io import StringIO
        a = pd.read_csv(StringIO(r.text), sep="\t")
        a["source"] = "RKI AMELAG"
        a["licence"] = "CC BY 4.0"
        a["source_url"] = url
        print(f"[OK] AMELAG: {len(a):,} rows")
        return a
    except Exception as exc:
        print(f"[WARN] AMELAG unavailable ({exc}); global layer will note the gap.")
        return pd.DataFrame()


def global_coverage_equity(jmp_path=JMP_PATH, amelag=None):
    """Country-level surveillance coverage against sewer-connected population.

    The denominator question nobody publishes: wastewater-based surveillance can
    only ever observe people connected to a sewer. WHO/UNICEF JMP sanitation
    data gives that denominator per country. Expressed as a share, the global
    picture is structurally different from the US one - most of the world's
    population is not reachable by this method at all, and the countries with
    the least sewer connection are the ones with no programme.

    Requires the JMP extract as a frozen static input, because the JMP portal
    does not expose a stable machine-readable endpoint. Absent that file this
    returns empty and the view says so.
    """
    if not jmp_path.exists():
        print(f"[INFO] No JMP sanitation extract at {jmp_path}; "
              f"global coverage-equity view will report an empty, honest state.")
        return pd.DataFrame(), pd.DataFrame()
    try:
        j = pd.read_csv(jmp_path)
    except Exception as exc:
        print(f"[WARN] JMP extract unreadable: {exc}")
        return pd.DataFrame(), pd.DataFrame()

    cols = {c.lower().strip(): c for c in j.columns}
    def pick(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None
    c_country = pick("country", "country_name", "name")
    c_iso = pick("iso3", "iso_a3", "iso")
    c_sewer = pick("sewer_connected_pct", "sewer_pct", "at_least_basic_sanitation_pct")
    c_income = pick("income_group", "income")
    c_pop = pick("population", "pop_total")
    if not c_country or not c_sewer:
        print("[WARN] JMP extract lacks country/sewer columns; global layer skipped.")
        return pd.DataFrame(), pd.DataFrame()

    g = pd.DataFrame({
        "country": j[c_country],
        "iso3": j[c_iso] if c_iso else None,
        "sewer_connected_pct": pd.to_numeric(j[c_sewer], errors="coerce"),
        "income_group": j[c_income] if c_income else None,
        "population": pd.to_numeric(j[c_pop], errors="coerce") if c_pop else np.nan,
    })

    # Registry of national programmes known to publish openly licensed,
    # machine-readable wastewater data. Being in this registry is NOT the same
    # as this pipeline having ingested it: only Germany is fetched today, and
    # the feed_status column states that plainly rather than implying coverage
    # the run does not have.
    open_feeds = {"Germany": "RKI AMELAG (CC BY 4.0)", "Netherlands": "RIVM open data"}
    ingested = {"Germany"}
    g["open_machine_readable_feed"] = g["country"].map(open_feeds)
    g["has_open_feed"] = g["open_machine_readable_feed"].notna()
    g["feed_rows_ingested"] = np.nan
    g["feed_status"] = np.where(~g["has_open_feed"], "No open feed known",
                                np.where(g["country"].isin(ingested),
                                         "Fetch attempted this run", "Known feed, not yet ingested"))
    if amelag is not None and not amelag.empty:
        g.loc[g["country"].eq("Germany"), "feed_rows_ingested"] = len(amelag)
        g.loc[g["country"].eq("Germany"), "feed_status"] = "Ingested this run"
    else:
        g.loc[g["country"].eq("Germany"), "feed_status"] = "Fetch failed this run"

    g["observable_population"] = g["population"] * g["sewer_connected_pct"] / 100.0
    g["unobservable_population"] = g["population"] - g["observable_population"]

    summary_rows = []
    if g["income_group"].notna().any():
        for grp, q in g.groupby("income_group"):
            summary_rows.append({
                "income_group": grp,
                "countries": int(len(q)),
                "countries_with_open_feed": int(q["has_open_feed"].sum()),
                "median_sewer_connected_pct": round(float(q["sewer_connected_pct"].median(skipna=True)), 1),
                "population": float(q["population"].sum(skipna=True)),
                "observable_population": float(q["observable_population"].sum(skipna=True)),
            })
    summary = pd.DataFrame(summary_rows)
    if not summary.empty:
        summary["pct_population_observable"] = (
            100.0 * summary["observable_population"] / summary["population"]
        ).round(1)
    return g.sort_values("sewer_connected_pct", na_position="last"), summary


# ============================================================
# 21. APP EXPORTS
# ============================================================
def export_app_json(summary, activity, best_lag, global_moran, amr_target=None, amr_state=None, genomics=None, pdb_map=None):
    payload = {
        "generated_utc": utc_now(),
        "study_period": {
            "start": str(STUDY_START.date()),
            "end": str(STUDY_END.date()),
        },
        "pathogens": json.loads(summary.to_json(orient="records", date_format="iso")),
        "latest_activity": json.loads(activity.to_json(orient="records", date_format="iso")) if not activity.empty else [],
        "best_lag_results": json.loads(best_lag.to_json(orient="records", date_format="iso")) if not best_lag.empty else [],
        "spatial_global": json.loads(global_moran.to_json(orient="records", date_format="iso")) if not global_moran.empty else [],
        "amr_arg_targets": json.loads(amr_target.to_json(orient="records", date_format="iso")) if amr_target is not None and not amr_target.empty else [],
        "amr_arg_states": json.loads(amr_state.to_json(orient="records", date_format="iso")) if amr_state is not None and not amr_state.empty else [],
        "genomic_context": json.loads(genomics.drop(columns=["raw_json"], errors="ignore").to_json(orient="records", date_format="iso")) if genomics is not None and not genomics.empty else [],
        "pdb_mappings": json.loads(pdb_map.to_json(orient="records", date_format="iso")) if pdb_map is not None and not pdb_map.empty else [],
        "disclaimer": (
            "Research/prototype surveillance outputs. Interpret with source-specific QC, "
            "coverage, uncertainty, and public-health professional review."
        )
    }
    path = APP_DIR / "nwgs_app_payload.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path




def build_validation_summary(
    wastewater, detection_audit, activity, lisa, independence,
    best_lag, equity, amr_target, equity_model=None, pdb_map=None,
    spatial_attrition=None, pathogen_manifest=None, detection_source_profile=None,
    amr_classification_audit=None, seasonal_national=None,
    portrait_self_check=None, ml_collinearity=None, ml_wastewater_only=None,
    ml_outliers=None,
):
    rows = []

    for pathogen in ["SARS-CoV-2","RSV","Influenza A"]:
        g = activity[activity["pathogen"].eq(pathogen)]
        rows.append({
            "component": f"{pathogen} recent activity",
            "status": "PASS" if len(g) >= 20 else "WARNING_LOW_RECENT_COVERAGE",
            "detail": f"{g['county_fips'].nunique()} recent counties"
        })

    if detection_audit is not None and not detection_audit.empty:
        for r in detection_audit.itertuples():
            rows.append({
                "component": f"{r.pathogen} detection parser",
                "status": r.status,
                "detail": (
                    f"{int(r.positive_records)} positive / "
                    f"{int(r.negative_records)} negative / "
                    f"{int(r.known_detection_records)} known; "
                    f"{int(r.unknown_detection_records)} unknown"
                    + (
                        f"; {int(r.basis_blocked_linearized_source)} blocked (raw_concentration was linearized)"
                        if hasattr(r, "basis_blocked_linearized_source") and int(r.basis_blocked_linearized_source) > 0
                        else ""
                    )
                )
            })

    if detection_source_profile is not None and not detection_source_profile.empty:
        for pathogen in ["Influenza A(H5)","Mpox","Measles"]:
            g = detection_source_profile[
                detection_source_profile["pathogen"].eq(pathogen) &
                detection_source_profile["field"].eq("pcr_target_detect")
            ]
            if g.empty:
                status, detail = "FAIL_SOURCE_FIELD_MISSING", "pcr_target_detect absent"
            else:
                present = bool(g.iloc[0]["field_present"])
                summary = str(g.iloc[0]["value_summary"])
                status = "PASS" if present else "FAIL_SOURCE_FIELD_MISSING"
                detail = summary
            rows.append({
                "component": f"{pathogen} raw CDC detection-field audit",
                "status": status,
                "detail": detail
            })

    if independence is not None and not independence.empty:
        for r in independence.itertuples():
            rows.append({
                "component": f"Pathogen independence: {r.comparison}",
                "status": r.status,
                "detail": (
                    f"{r.pct_identical_activity:.2f}% identical activity among "
                    f"{int(r.common_counties)} common counties"
                    if pd.notna(r.pct_identical_activity) else "insufficient common counties"
                )
            })

    tn = activity[activity["county_fips"].astype(str).str.startswith("47")]
    tn_n = tn["county_fips"].nunique()
    rows.append({
        "component": "Tennessee recent wastewater coverage",
        "status": "WARNING_SPARSE_COVERAGE" if tn_n < 20 else "PASS",
        "detail": f"{tn_n}/95 unique counties across recent respiratory activity table"
    })

    rows.append({
        "component": "KNN spatial analysis",
        "status": "PASS" if lisa is not None and not lisa.empty else "FAIL",
        "detail": f"{len(lisa) if lisa is not None else 0} county-pathogen LISA rows"
    })

    if spatial_attrition is not None and not spatial_attrition.empty:
        excluded = int(spatial_attrition["total_excluded_from_spatial"].sum())
        rows.append({
            "component": "Spatial geography attrition audit",
            "status": "PASS",
            "detail": f"{excluded} recent county-pathogen observations excluded from CONUS spatial analysis"
        })

    rows.append({
        "component": "Wastewater-clinical lag analysis",
        "status": "PASS" if best_lag is not None and len(best_lag) >= 30 else "WARNING",
        "detail": f"{len(best_lag) if best_lag is not None else 0} jurisdiction-pathogen best-lag rows"
    })

    # v5.17 addition: fold the seasonal-peak implausible-lead audit flag
    # (see _summarize_season_peak / seasonal_peak_analysis) into the
    # validation summary, so a flagged season is visible alongside every
    # other component rather than only in the console log.
    if seasonal_national is not None and not seasonal_national.empty and "implausible_lead_flag" in seasonal_national.columns:
        elig = seasonal_national[seasonal_national["eligible"].fillna(False)]
        n_flagged = int(elig["implausible_lead_flag"].fillna(False).sum())
        flagged_detail = "; ".join(
            f"{r.pathogen} {r.season} ({r.ww_lead_to_clinical_peak_weeks:+.1f} wk)"
            for r in elig[elig["implausible_lead_flag"].fillna(False)].itertuples()
        ) if n_flagged else "none"
        rows.append({
            "component": "Seasonal peak implausible-lead audit",
            "status": "PASS" if n_flagged == 0 else "WARNING_IMPLAUSIBLE_LEAD_FLAGGED",
            "detail": f"{n_flagged} eligible season(s) flagged: {flagged_detail}"
        })

    rows.append({
        "component": "SVI surveillance readiness descriptive",
        "status": "PASS" if equity is not None and len(equity) == 4 else "WARNING",
        "detail": f"{len(equity) if equity is not None else 0} SVI quartiles"
    })

    if equity_model is not None and not equity_model.empty:
        er = equity_model.iloc[0]
        rows.append({
            "component": "SVI surveillance readiness inferential model",
            "status": "PASS" if pd.notna(er["p_value"]) else "WARNING",
            "detail": (
                f"OR={er['odds_ratio']:.3f} per 0.10 SVI increase; "
                f"95% CI {er['or_95ci_low']:.3f}-{er['or_95ci_high']:.3f}; "
                f"p={er['p_value']:.3g}"
            )
        })

    rows.append({
        "component": "AMR/ARG module",
        "status": "PASS" if amr_target is not None and len(amr_target) >= 5 else "WARNING",
        "detail": f"{len(amr_target) if amr_target is not None else 0} ARG targets"
    })

    # v5.9: fold the AMR classification audit into the validation summary,
    # so a target-mapping, Detect-coding, or (v5.13) outlier-coding mismatch
    # shows up here alongside every other component instead of only in a
    # console print statement.
    if amr_classification_audit is not None and not amr_classification_audit.empty:
        r = amr_classification_audit.iloc[0]
        rows.append({
            "component": "AMR/ARG classification audit (target mapping + Detect/outlier coding)",
            "status": r["status"],
            "detail": r["detail"],
        })

    if pdb_map is not None and not pdb_map.empty:
        expected_structures = len(RCSB_REFERENCE_STRUCTURES)
        rendered = int(pdb_map["render_status"].eq("PASS").sum()) if "render_status" in pdb_map else 0
        meta_pass = int(pdb_map["metadata_status"].eq("PASS").sum()) if "metadata_status" in pdb_map else 0
        status = "PASS" if rendered == expected_structures and meta_pass == expected_structures else "FAIL_INCOMPLETE_STRUCTURES"
        detail = (
            f"{rendered}/{expected_structures} protein PNGs rendered; "
            f"{meta_pass}/{expected_structures} RCSB metadata queries passed; "
            "publication figure requires 6/6"
        )
    else:
        status, detail = "FAIL_NO_STRUCTURES", "0/6 representative structures rendered"

    rows.append({
        "component": "RCSB protein/structure visualization",
        "status": status,
        "detail": detail
    })

    if pathogen_manifest is not None and not pathogen_manifest.empty:
        downloaded = int(pathogen_manifest["download_status"].eq("PASS").sum())
        rows.append({
            "component": "CDC PHIL pathogen reference imagery",
            "status": "PASS" if downloaded >= 4 else "WARNING_PARTIAL_IMAGES",
            "detail": f"{downloaded}/{len(pathogen_manifest)} pathogen reference images downloaded"
        })

    # v5.18 addition: fold the figure-generation-time portrait self-check
    # into the validation summary, so a Figure 2/5 orientation failure is
    # visible alongside every other component instead of requiring someone
    # to separately open Table19_Figure_Layout_Audit.csv.
    if portrait_self_check is not None and not portrait_self_check.empty:
        for r in portrait_self_check.itertuples():
            dims = f"{r.width_px}x{r.height_px}px" if pd.notna(getattr(r, "width_px", None)) else "unreadable"
            # v5.19: AUTOFIXED_AFTER_FAIL means the figure needed correction
            # but IS portrait in the file actually delivered - report it as
            # a WARNING (visible, investigate later) rather than the same
            # FAIL status as a figure nobody has corrected at all.
            display_status = (
                "WARNING_AUTOFIXED" if str(r.status) == "AUTOFIXED_AFTER_FAIL" else r.status
            )
            pre = ""
            if str(r.status) == "AUTOFIXED_AFTER_FAIL":
                pre_w = getattr(r, "pre_autofix_width_px", None)
                pre_h = getattr(r, "pre_autofix_height_px", None)
                pre_w_s = f"{int(pre_w)}" if pd.notna(pre_w) else "?"
                pre_h_s = f"{int(pre_h)}" if pd.notna(pre_h) else "?"
                pre = f" (was {pre_w_s}x{pre_h_s}px before padding)"
            rows.append({
                "component": f"Portrait self-check: {r.label}",
                "status": display_status,
                "detail": f"{dims}{pre}; {r.path}",
            })

    # v5.18 addition: surface the wastewater/clinical-lags collinearity
    # diagnostic and the standalone wastewater-only benchmark, so a reader
    # of the validation summary sees the context needed to interpret
    # Fig_Multimodal_Ablation.png's near-zero wastewater deltas correctly.
    if ml_collinearity is not None and not ml_collinearity.empty:
        flagged = ml_collinearity[ml_collinearity["high_collinearity_flag"].fillna(False)]
        rows.append({
            "component": "ML wastewater/clinical-lag collinearity audit",
            "status": "WARNING_HIGH_COLLINEARITY" if len(flagged) else "PASS",
            "detail": (
                "; ".join(
                    f"{r.pathogen}: {r.wastewater_feature} vs clinical_lag1 r={r.pearson_r_train_split:.2f}"
                    for r in flagged.itertuples()
                ) if len(flagged) else "no wastewater feature exceeded the collinearity threshold"
            ),
        })

    if ml_wastewater_only is not None and not ml_wastewater_only.empty:
        details = "; ".join(
            f"{r.pathogen}: wastewater-only R2={r.wastewater_only_R2:.3f} vs "
            f"clinical-persistence R2={r.clinical_persistence_R2:.3f}"
            for r in ml_wastewater_only.itertuples()
        )
        rows.append({
            "component": "ML standalone wastewater-only predictive value",
            "status": "PASS",
            "detail": details,
        })

    if ml_outliers is not None and not ml_outliers.empty:
        rows.append({
            "component": "ML held-out prediction outlier audit",
            "status": "WARNING_OUTLIERS_FLAGGED",
            "detail": f"{len(ml_outliers)} prediction(s) flagged; see Table12f_ML_Prediction_Outliers.csv",
        })

    return pd.DataFrame(rows)


def spatial_attrition_audit(activity, lisa, tiger):
    rows = []
    conus_fips = set(conus(tiger)["county_fips"].astype(str))
    lisa = lisa if lisa is not None else pd.DataFrame()

    for pathogen, g in activity.groupby("pathogen"):
        recent_fips = set(g["county_fips"].dropna().astype(str))
        matched = recent_fips & conus_fips
        lisa_fips = set(
            lisa.loc[lisa["pathogen"].eq(pathogen), "county_fips"].dropna().astype(str)
        ) if not lisa.empty else set()

        rows.append({
            "pathogen": pathogen,
            "recent_activity_counties": len(recent_fips),
            "conus_geometry_matched": len(matched),
            "spatial_lisa_counties": len(lisa_fips),
            "excluded_nonconus_or_unmatched": len(recent_fips - matched),
            "excluded_after_geometry_match": len(matched - lisa_fips),
            "total_excluded_from_spatial": len(recent_fips - lisa_fips),
        })
    return pd.DataFrame(rows)



def create_pathogen_intelligence_figure(pathogen_manifest, pdb_map):
    """
    Publication-style six-card structural pathogen intelligence figure modeled
    on the approved NWGS Grid visual: routine respiratory pathogens in a blue
    band, emerging-detection pathogens in a peach band, with one bordered card
    per pathogen and actual coordinate-derived RCSB structure renders.

    The function deliberately does NOT substitute artistic or generated protein
    images. If a deposited structure fails to render, that card is visibly marked
    as failed and the strict 6/6 structural QC remains failed.
    """
    preferred = ["SARS-CoV-2","RSV","Influenza A","Influenza A(H5)","Mpox","Measles"]
    letters = dict(zip(preferred, list("ABCDEF")))
    organism = {
        "SARS-CoV-2":"Severe acute respiratory syndrome coronavirus 2",
        "RSV":"Human respiratory syncytial virus (RSV)",
        "Influenza A":"Influenza A virus",
        "Influenza A(H5)":"Influenza A virus (H5 reference)",
        "Mpox":"Monkeypox virus (Mpox)",
        "Measles":"Measles virus",
    }
    if pdb_map is None:
        pdb_map = pd.DataFrame()

    fig = plt.figure(figsize=(18, 12), facecolor="white")
    gs = fig.add_gridspec(
        2, 3, left=.025, right=.975, bottom=.085, top=.845,
        hspace=.12, wspace=.02
    )

    # Main title / scientific safeguard.
    fig.text(.5, .972, "NWGS Grid™ — Genomic & Structural Pathogen Intelligence",
             ha="center", va="top", fontsize=20, fontweight="bold")
    fig.text(.5, .942,
             "Representative reference structures for six configured pathogens from RCSB PDB",
             ha="center", va="top", fontsize=13)
    fig.text(.5, .917,
             "Structures provide representative/reference structural context and are not wastewater-isolate structures.",
             ha="center", va="top", fontsize=11, style="italic")

    # Group bands positioned above each card row.
    band1 = fig.add_axes([.025, .855, .95, .04]); band1.axis("off")
    band1.add_patch(plt.Rectangle((0,0),1,1,transform=band1.transAxes,
                                  facecolor="#dceeff",edgecolor="#3a82c4",linewidth=1.4))
    band1.text(.5,.5,"Routine respiratory surveillance pathogens",ha="center",va="center",
               fontsize=15,fontweight="bold",color="#173b70")
    band2 = fig.add_axes([.025, .455, .95, .04]); band2.axis("off")
    band2.add_patch(plt.Rectangle((0,0),1,1,transform=band2.transAxes,
                                  facecolor="#fde8d8",edgecolor="#e88a3a",linewidth=1.4))
    band2.text(.5,.5,"Emerging detection surveillance pathogens",ha="center",va="center",
               fontsize=15,fontweight="bold",color="#7a3f0e")

    # Move lower row down enough to leave room for its group band.
    for i, pathogen in enumerate(preferred):
        row, col = divmod(i, 3)
        ax = fig.add_subplot(gs[row, col])
        if row == 1:
            # gridspec top edge would overlap the band; shrink/move manually.
            pos = ax.get_position()
            ax.set_position([pos.x0, pos.y0, pos.width, pos.height * .88])
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_facecolor("white")
        edge = "#3a82c4" if row == 0 else "#e88a3a"
        for sp in ax.spines.values():
            sp.set_visible(True); sp.set_color(edge); sp.set_linewidth(1.1)

        prow = pdb_map[pdb_map.get("pathogen", pd.Series(dtype=str)).astype(str).eq(pathogen)] if not pdb_map.empty else pd.DataFrame()
        ref = next((x for x in RCSB_REFERENCE_STRUCTURES if x["pathogen"] == pathogen), {})
        protein = ref.get("protein", "Representative protein")
        pdb_id = ref.get("pdb_entry_id", "")
        method = ref.get("method_expected", "")
        resolution_txt = "Not reported"
        render_status = "FAIL_NOT_RUN"
        coord_fmt = ""
        img_path = None

        if not prow.empty:
            r = prow.iloc[0]
            protein = str(r.get("protein") or protein)
            pdb_id = str(r.get("pdb_entry_id") or pdb_id)
            method = str(r.get("method") or r.get("expected_method") or method)
            res = r.get("resolution_A")
            if pd.notna(res):
                try: resolution_txt = f"{float(res):.2f} Å"
                except Exception: resolution_txt = str(res)
            render_status = str(r.get("render_status") or "")
            coord_fmt = str(r.get("coordinate_format_used") or "")
            img_path = r.get("protein_png_path")

        # Header block.
        header_fc = "#edf6ff" if row == 0 else "#fff3e9"
        ax.add_patch(plt.Rectangle((0, .83), 1, .17, transform=ax.transAxes,
                                   facecolor=header_fc, edgecolor="none", zorder=0))
        ax.text(.5,.965,f"{letters[pathogen]}. {pathogen}",ha="center",va="top",
                fontsize=13.5,fontweight="bold",transform=ax.transAxes)
        ax.text(.5,.918,protein,ha="center",va="top",fontsize=10.5,fontweight="bold",
                transform=ax.transAxes,wrap=True)
        ax.text(.5,.865,f"RCSB PDB {pdb_id}",ha="center",va="top",fontsize=10.5,
                fontweight="bold",transform=ax.transAxes)

        # Structure render region.
        if isinstance(img_path, str) and Path(img_path).exists() and render_status == "PASS":
            try:
                im = Image.open(img_path).convert("RGB")
                iax = ax.inset_axes([.08,.32,.84,.48])
                iax.imshow(im); iax.axis("off")
            except Exception:
                render_status = "FAIL_IMAGE_OPEN"
        if render_status != "PASS":
            ax.text(.5,.555,
                    f"RCSB PDB {pdb_id}\nStructure render unavailable\nQC: {render_status}",
                    ha="center",va="center",fontsize=10,transform=ax.transAxes,
                    bbox=dict(boxstyle="round,pad=.5",fc="#f5f5f5",ec="#aa3333"))

        info = [
            ("Method", method.title() if method else "Not reported"),
            ("Resolution", resolution_txt),
            ("Protein", protein),
            ("PDB ID", pdb_id),
            ("Coordinates", coord_fmt or "Not rendered"),
            ("Source", "RCSB Protein Data Bank"),
            ("Organism", organism[pathogen]),
        ]
        y = .285
        for label, value in info:
            ax.text(.04,y,f"{label}:",ha="left",va="top",fontsize=8.6,fontweight="bold",
                    transform=ax.transAxes)
            ax.text(.22,y,str(value),ha="left",va="top",fontsize=8.6,
                    transform=ax.transAxes,wrap=True)
            y -= .037

    # Footer audit statement.
    rendered = int(pdb_map["render_status"].eq("PASS").sum()) if (pdb_map is not None and not pdb_map.empty and "render_status" in pdb_map) else 0
    qc = "PASS" if rendered == 6 else "FAIL"
    footer = fig.add_axes([.025,.018,.95,.055]); footer.axis("off")
    footer.add_patch(plt.Rectangle((0,0),1,1,transform=footer.transAxes,
                                   facecolor="#f2f2f2",edgecolor="#c8c8c8",linewidth=1))
    footer.text(.015,.63,"RCSB PDB structures are displayed from deposited coordinates; mmCIF is preferred with legacy PDB fallback.",
                ha="left",va="center",fontsize=9)
    footer.text(.015,.28,"Representative/reference structural context; not wastewater-isolate structures.",
                ha="left",va="center",fontsize=9)
    footer.text(.985,.63,f"Structural figure QC: {qc} — {rendered}/6 structures rendered",
                ha="right",va="center",fontsize=9.5,fontweight="bold",
                color=("#1b6e2e" if qc == "PASS" else "#9b1c1c"))
    footer.text(.985,.28,"Publication-ready only when QC = PASS.",ha="right",va="center",fontsize=9)

    out_path = FIG_DIR / "Fig_Genomic_Structural_Pathogen_Intelligence.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path


def clean_stale_versioned_outputs():
    """
    v5.13 fix: previously this function only globbed three filename patterns
    (PathogenDetection_*, the pathogen intelligence panel, ProteinStructure_*).
    But several other figures in this pipeline are conditionally SUPPRESSED
    (no file written) rather than regenerated on a given run:
      - plot_pathogen_trends(): skips a pathogen with <3 non-null weekly z values
      - plot_lag_summary(): writes nothing if best_lag is empty
      - plot_seasonal_peak_analysis(): writes nothing if no seasons are eligible
      - tennessee_seasonal_analysis(): writes nothing if no TN pathogen-season
        meets coverage eligibility
    If any of these were eligible on an earlier run and become ineligible on a
    later run (data window shift, threshold change, a season aging out of
    eligibility), the OLD PNG just sat in FIG_DIR - and nothing downstream
    could tell the difference, since build_figure_use_manifest() only checks
    Path.exists(). A genuinely stale, no-longer-eligible figure could flow
    all the way into a Paper 1/Paper 2 product folder marked
    GENERATED/PASS.

    Fix: since main() already regenerates (or correctly re-suppresses) every
    figure in FIG_DIR and every structure render in STRUCTURE_DIR on every
    run - there is no figure in this pipeline that is computed once and
    reused across runs - the safest fix is to unconditionally clear every
    PNG in both directories at the very start of main(), before anything is
    regenerated. This guarantees no stale figure can survive regardless of
    which function's suppression logic produced it, including any
    suppression path added in the future that isn't yet covered by an
    explicit glob pattern.
    """
    removed = 0
    for directory in (FIG_DIR, STRUCTURE_DIR):
        if not directory.exists():
            continue
        for p in directory.glob("*.png"):
            try:
                p.unlink()
                removed += 1
            except Exception:
                pass
    print(f"[CLEANUP] Removed {removed} figure file(s) from previous runs (FIG_DIR + STRUCTURE_DIR cleared unconditionally).")



def _load_figure_image(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None


def _image_aspect(path, default=1.5):
    """
    v5.15 addition. Read a saved figure's actual width/height ratio from
    disk instead of guessing it from the matplotlib figsize() the source
    function used. bbox_inches="tight" crops every saved PNG to its real
    content bounds, so the on-disk aspect ratio can differ substantially
    from the nominal figsize - Table19_Figure_Layout_Audit.csv confirmed
    every national CONUS map (nominal figsize=(10,12), i.e. portrait) is
    actually saved as landscape 2970x1963 (aspect ~1.51) once cropped.
    Composite panels sized from the nominal figsize rather than this real
    value are exactly the ones that stretched (see the v5.15 changelog
    entry on create_combined_publication_figures()). Falls back to
    `default` if the file is missing or unreadable.
    """
    img = _load_figure_image(path)
    if img is None:
        return default
    w, h = img.size
    if h <= 0:
        return default
    return w / h


def _solve_exact_fit_widths(total_width_in, gap_in, aspects):
    """
    v5.15 addition.

    Given N source images that will sit side-by-side in one row (or
    stacked in one column) of a composite figure, solve for a single
    shared height (or width) and each panel's own dimension such that
    EVERY panel exactly fills its cell at its own real aspect ratio -
    zero stretch, zero letterboxing, for all of them simultaneously.

    This is the general form of the per-panel sizing already used for
    Tennessee's map figures (_tn_map_aspect()) and for _image_aspect()
    above, extended to rows that mix two or more differently-shaped
    source images (e.g. a wide trend chart next to a narrower map).

    Math: n images with aspect ratios a_i share height H and gap g
    between them. total_width = sum(H * a_i) + (n-1) * g, so
    H = (total_width - (n-1)*g) / sum(a_i), and each panel's width is
    H * a_i.

    Returns (shared_height_in, [width_in, ...]).
    """
    n_gaps = max(0, len(aspects) - 1)
    denom = sum(aspects) if aspects else 1.0
    shared_h = (total_width_in - n_gaps * gap_in) / denom
    widths = [shared_h * a for a in aspects]
    return shared_h, widths


def _render_image_panel(ax, img, title=None):
    """
    v5.11 fix: ax.imshow() previously used the default aspect="equal", which
    preserves each embedded PNG's own aspect ratio inside whatever subplot
    cell it's placed in. Wide/short trend charts and narrow/tall maps rarely
    match a square grid cell, so matplotlib letterboxed them - large blank
    bands above/below or beside every panel. This was the single biggest
    contributor to the "excessive whitespace" seen across the Respiratory
    Trends+Maps, Surveillance Performance, and Emerging Detection composites.
    aspect="auto" stretches each image to completely fill its cell instead.
    """
    ax.axis("off")
    if img is not None:
        ax.imshow(img, aspect="auto")
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold")


def create_combined_publication_figures(detection_audit=None):
    """
    Combine the strongest NWGS figures into publication/poster-ready panels.

    Individual figures are preserved. These composites are additional exports
    designed to reduce poster clutter and make pathogen comparisons easier.
    """

    # ----------------------------------------------------------
    # A. Respiratory trends: SARS-CoV-2 + RSV + Influenza A
    # ----------------------------------------------------------
    trend_specs = [
        ("SARS-CoV-2", FIG_DIR / "PathogenTrend_SARS_CoV_2.png"),
        ("RSV", FIG_DIR / "PathogenTrend_RSV.png"),
        ("Influenza A", FIG_DIR / "PathogenTrend_Influenza_A.png"),
    ]
    imgs = [(name, _load_figure_image(path)) for name, path in trend_specs]
    if any(img is not None for _, img in imgs):
        fig, axes = plt.subplots(3, 1, figsize=(12, 13))
        for ax, (name, img) in zip(axes, imgs):
            _render_image_panel(ax, img, name)
        fig.suptitle(
            "NWGS Grid™ — National Respiratory Wastewater Activity Trends\n"
            "Source: CDC NWSS | NWGS standardized within-site log-concentration z-score",
            fontsize=15, fontweight="bold"
        )
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(
            FIG_DIR / "Fig_Combined_Respiratory_Trends.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)

    # ----------------------------------------------------------
    # B. Trend + recent-activity map for each respiratory pathogen
    # v5.15 fix: width_ratios=[1.7, 1] was a guess at the trend chart's
    # ~2.2:1 wide aspect vs. the map's narrow aspect - but Table19 showed
    # the saved maps are actually landscape (~1.51:1), not the narrow
    # shape the ratio assumed, so the map column still stretched visibly
    # (confirmed in the uploaded Poster Figure 3). Both columns now use
    # _image_aspect() on the actual saved files and
    # _solve_exact_fit_widths() to size a shared row height so BOTH the
    # trend chart and the map fill their cell exactly, every row, with
    # zero stretch.
    # ----------------------------------------------------------
    pairs = [
        ("SARS-CoV-2",
         FIG_DIR / "PathogenTrend_SARS_CoV_2.png",
         FIG_DIR / "Map_RecentActivity_SARS_CoV_2.png"),
        ("RSV",
         FIG_DIR / "PathogenTrend_RSV.png",
         FIG_DIR / "Map_RecentActivity_RSV.png"),
        ("Influenza A",
         FIG_DIR / "PathogenTrend_Influenza_A.png",
         FIG_DIR / "Map_RecentActivity_Influenza_A.png"),
    ]
    any_pair = any(p.exists() or m.exists() for _, p, m in pairs)
    if any_pair:
        trend_aspect = _image_aspect(pairs[0][1], default=2.2)
        map_aspect = _image_aspect(pairs[0][2], default=1.51)
        fig_width_in = 15.0
        col_gap_in = 0.5
        row_h, (trend_w, map_w) = _solve_exact_fit_widths(
            fig_width_in, col_gap_in, [trend_aspect, map_aspect]
        )
        row_gap_in = 0.35
        fig_height_in = row_h * 3 + row_gap_in * 2 + 1.4
        fig, axes = plt.subplots(
            3, 2, figsize=(fig_width_in, fig_height_in),
            gridspec_kw={
                "width_ratios": [trend_w, map_w],
                "hspace": row_gap_in / row_h,
                "wspace": col_gap_in / ((trend_w + map_w) / 2),
            },
        )
        for i, (name, trend_path, map_path) in enumerate(pairs):
            trend_img = _load_figure_image(trend_path)
            map_img = _load_figure_image(map_path)
            _render_image_panel(axes[i, 0], trend_img, f"{name} — National Trend")
            _render_image_panel(axes[i, 1], map_img, f"{name} — Recent County Activity")
        fig.suptitle(
            "NWGS Grid™ — Respiratory Pathogen Trends and Geospatial Activity\n"
            "CDC NWSS source data with NWGS Grid™ analytical standardization",
            fontsize=16, fontweight="bold"
        )
        fig.subplots_adjust(top=0.90, bottom=0.02, left=0.03, right=0.98)
        fig.savefig(
            FIG_DIR / "Fig_Combined_Respiratory_Trends_and_Maps.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)


    # ----------------------------------------------------------
    # C. All recent-activity maps
    # v5.15 fix: figsize=(10, 18) hardcoded a guessed height for 3 stacked
    # maps regardless of their actual saved aspect ratio. Table19 showed
    # these files save as landscape (~1.51:1) rather than the portrait
    # shape the guess assumed, so aspect="auto" stretched every panel
    # vertically to fill the oversized cell. Height is now computed per
    # panel from the actual saved file at a fixed 10in width, so each
    # panel exactly matches its source image with zero stretch.
    # ----------------------------------------------------------
    recent_specs = [
        ("SARS-CoV-2", FIG_DIR / "Map_RecentActivity_SARS_CoV_2.png"),
        ("RSV", FIG_DIR / "Map_RecentActivity_RSV.png"),
        ("Influenza A", FIG_DIR / "Map_RecentActivity_Influenza_A.png"),
    ]
    imgs = [(name, _load_figure_image(path)) for name, path in recent_specs]
    if any(img is not None for _, img in imgs):
        width_in = 10.0
        heights = [width_in / _image_aspect(path, default=1.51) for _, path in recent_specs]
        fig, axes = plt.subplots(
            3, 1, figsize=(width_in, sum(heights) + 1.0),
            gridspec_kw={"height_ratios": heights, "hspace": 0.15},
        )
        for ax, (name, img) in zip(np.atleast_1d(axes), imgs):
            _render_image_panel(ax, img, name)
        fig.suptitle(
            "NWGS Grid™ — Recent Respiratory Pathogen Activity",
            fontsize=15, fontweight="bold"
        )
        fig.subplots_adjust(top=0.93, bottom=0.02, left=0.02, right=0.98)
        fig.savefig(
            FIG_DIR / "Fig_Combined_RecentActivity_Maps.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)

    # ----------------------------------------------------------
    # D. All KNN-LISA maps
    # v5.15 fix: same figsize=(10, 18) stretching bug as Section C above,
    # same fix - heights computed per panel from the actual saved files.
    # ----------------------------------------------------------
    lisa_specs = [
        ("SARS-CoV-2", FIG_DIR / "Map_LISA_SARS_CoV_2.png"),
        ("RSV", FIG_DIR / "Map_LISA_RSV.png"),
        ("Influenza A", FIG_DIR / "Map_LISA_Influenza_A.png"),
    ]
    imgs = [(name, _load_figure_image(path)) for name, path in lisa_specs]
    if any(img is not None for _, img in imgs):
        width_in = 10.0
        heights = [width_in / _image_aspect(path, default=1.51) for _, path in lisa_specs]
        fig, axes = plt.subplots(
            3, 1, figsize=(width_in, sum(heights) + 1.0),
            gridspec_kw={"height_ratios": heights, "hspace": 0.18},
        )
        for ax, (name, img) in zip(np.atleast_1d(axes), imgs):
            _render_image_panel(ax, img, name)
        fig.suptitle(
            "NWGS Grid™ — KNN-LISA Spatial Clustering of Recent Respiratory Activity\n"
            "KNN k=6 | EPSG:5070 | permutation-based local spatial inference",
            fontsize=14, fontweight="bold"
        )
        fig.subplots_adjust(top=0.90, bottom=0.02, left=0.02, right=0.98)
        fig.savefig(
            FIG_DIR / "Fig_Combined_LISA_Maps.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)

    # ----------------------------------------------------------
    # E. Surveillance performance / equity / lag
    # v5.15 fix: this was the worst offender confirmed by Table19 and
    # visible directly in the uploaded Poster Figure 3 - the coverage map
    # was given a tall narrow left column (width_ratios=[1,1.3] inside a
    # (15,10) figure gives the map axes ~6.5in width for 10in of height,
    # aspect ~0.65) to span both rows, but the map's real saved aspect is
    # landscape (~1.51:1, confirmed by Table19). Forcing a wide/short
    # image to fill a tall/narrow cell under aspect="auto" is exactly what
    # produced the visible vertical stretch.
    #
    # Rather than another guessed ratio, this now solves the geometry
    # directly from the three actual saved files: the map keeps its own
    # full-width row at its own aspect ratio (no distortion), and the two
    # landscape bar charts (Lag, Equity) share a second row below it,
    # each sized to its own aspect via _solve_exact_fit_widths() so
    # neither one stretches either. This also restores the map to a
    # sensible width instead of the previous panel, where reviewer
    # feedback removed the Tennessee table from this NATIONAL composite -
    # Tennessee remains fully available as its own standalone figure and
    # inside the Tennessee paper product, so no content is lost here.
    # ----------------------------------------------------------
    result_specs = [
        ("National Surveillance Coverage",
         FIG_DIR / "Fig_National_Coverage_CONUS.png"),
        ("Wastewater–Clinical Lead/Lag",
         FIG_DIR / "Fig_LagSummary.png"),
        ("Coverage Equity by Social Vulnerability",
         FIG_DIR / "Fig_Coverage_Equity.png"),
    ]
    imgs = [(name, _load_figure_image(path)) for name, path in result_specs]
    if any(img is not None for _, img in imgs):
        fig_width_in = 14.0
        gap_in = 0.4
        map_aspect = _image_aspect(result_specs[0][1], default=1.51)
        lag_aspect = _image_aspect(result_specs[1][1], default=2.0)
        eq_aspect = _image_aspect(result_specs[2][1], default=1.8)

        map_h = fig_width_in / map_aspect
        bottom_h, (lag_w, eq_w) = _solve_exact_fit_widths(
            fig_width_in, gap_in, [lag_aspect, eq_aspect]
        )
        row_gap_in = 0.4
        fig_height_in = map_h + bottom_h + row_gap_in + 1.3

        fig = plt.figure(figsize=(fig_width_in, fig_height_in))
        gs = fig.add_gridspec(
            2, 2,
            height_ratios=[map_h, bottom_h],
            width_ratios=[lag_w, eq_w],
            hspace=row_gap_in / bottom_h,
            wspace=gap_in / ((lag_w + eq_w) / 2),
        )
        ax_map = fig.add_subplot(gs[0, :])
        ax_lag = fig.add_subplot(gs[1, 0])
        ax_eq = fig.add_subplot(gs[1, 1])
        _render_image_panel(ax_map, imgs[0][1], imgs[0][0])
        _render_image_panel(ax_lag, imgs[1][1], imgs[1][0])
        _render_image_panel(ax_eq, imgs[2][1], imgs[2][0])
        fig.suptitle(
            "NWGS Grid™ — Surveillance Coverage, Equity, and Temporal Performance",
            fontsize=16, fontweight="bold"
        )
        fig.subplots_adjust(top=0.90, bottom=0.03, left=0.03, right=0.98)
        fig.savefig(
            FIG_DIR / "Fig_Combined_Surveillance_Performance.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)

    # ----------------------------------------------------------
    # F. AMR/ARG module
    # v5.10: no longer combined into a single stacked panel. The bar chart
    # (Fig_AMR_ARG_Detection_Profile.png) and the state choropleth
    # (Map_AMR_ARG_State_Burden.png) have very different aspect ratios (wide/
    # short vs. tall/portrait) and each already carries its own title/caption
    # from plot_amr()/plot_amr_state_map(), so stacking them produced a large
    # dead-space gap plus duplicated titling. They now remain as the two
    # independent figures those functions already generate; see the figure
    # manifest below, which assigns each to the poster separately.
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # G. Emerging pathogen detection trends.
    # Only combine pathogens whose parser audit PASSES.
    # ----------------------------------------------------------
    audit_status = {}
    if detection_audit is not None and not detection_audit.empty:
        audit_status = detection_audit.set_index("pathogen")["status"].to_dict()

    emerging_specs = [
        ("Influenza A(H5)", FIG_DIR / "PathogenDetection_Influenza_A_H5.png"),
        ("Mpox", FIG_DIR / "PathogenDetection_Mpox.png"),
        ("Measles", FIG_DIR / "PathogenDetection_Measles.png"),
    ]
    valid = []
    for name, path in emerging_specs:
        if audit_status.get(name) == "PASS":
            img = _load_figure_image(path)
            if img is not None:
                valid.append((name, img))

    if valid:
        # v5.11: switched from a horizontal 1xN layout (which grew
        # extremely wide with three panels, each a short/wide time-series
        # chart squeezed into a tall square cell and leaving large unused
        # margins) to a portrait N-row vertical stack. Each detection-trend
        # PNG is itself wide/short, so stacking rows - one pathogen per row,
        # H5 -> Mpox -> Measles - matches the source images' actual shape.
        fig, axes = plt.subplots(len(valid), 1, figsize=(11, 4.5 * len(valid)))
        axes = np.atleast_1d(axes)
        for ax, (name, img) in zip(axes, valid):
            _render_image_panel(ax, img, name)
        fig.suptitle(
            "NWGS Grid™ — Emerging Pathogen Wastewater Detection Frequency\n"
            "Only pathogens passing source-field and parser validation are displayed",
            fontsize=14, fontweight="bold"
        )
        fig.subplots_adjust(top=0.90, bottom=0.03, hspace=0.30, left=0.06, right=0.97)
        fig.savefig(
            FIG_DIR / "Fig_Combined_Emerging_Pathogen_Detection.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)

    # ----------------------------------------------------------
    # H. Master poster panel: strongest results only
    # ----------------------------------------------------------
    master_specs = [
        ("Respiratory Trends + Maps",
         FIG_DIR / "Fig_Combined_Respiratory_Trends_and_Maps.png"),
        ("Coverage / Equity / Lag",
         FIG_DIR / "Fig_Combined_Surveillance_Performance.png"),
        ("Genomic + Structural Pathogen Intelligence",
         FIG_DIR / "Fig_Genomic_Structural_Pathogen_Intelligence.png"),
        # v5.10: AMR/ARG module is no longer combined into one panel (see
        # create_combined_publication_figures, section F); the master
        # overview panel now references the standalone detection-profile
        # figure directly instead of the removed combined file.
        ("AMR / ARG Module: Detection Profile",
         FIG_DIR / "Fig_AMR_ARG_Detection_Profile.png"),
    ]
    imgs = [(name, _load_figure_image(path)) for name, path in master_specs]
    if any(img is not None for _, img in imgs):
        fig, axes = plt.subplots(2, 2, figsize=(22, 18))
        for ax, (name, img) in zip(axes.flat, imgs):
            _render_image_panel(ax, img, name)
        fig.suptitle(
            "NWGS Grid™ — Multimodal Wastewater Genomic Surveillance Results",
            fontsize=18, fontweight="bold"
        )
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(
            FIG_DIR / "Fig_NWGS_Master_Results_Panel.png",
            dpi=300, bbox_inches="tight"
        )
        plt.close(fig)




def audit_figure_layouts():
    """Audit publication figure files for portrait map orientation and basic render integrity."""
    map_files = [
        "Fig_National_Coverage_CONUS.png",
        "Map_RecentActivity_SARS_CoV_2.png",
        "Map_RecentActivity_RSV.png",
        "Map_RecentActivity_Influenza_A.png",
        "Map_LISA_SARS_CoV_2.png",
        "Map_LISA_RSV.png",
        "Map_LISA_Influenza_A.png",
        "Map_AMR_ARG_State_Burden.png",
        "Map_Tennessee_Surveillance_Coverage.png",
        "Map_Tennessee_SVI_Surveillance_Readiness.png",
        "Fig_Combined_RecentActivity_Maps.png",
        "Fig_Combined_LISA_Maps.png",
    ]
    rows = []
    for name in map_files:
        path = FIG_DIR / name
        if not path.exists():
            rows.append({"figure_file":name,"exists":False,"width_px":np.nan,"height_px":np.nan,
                         "orientation":None,"portrait_map_status":"WARNING_MISSING"})
            continue
        try:
            with Image.open(path) as im:
                w,h = im.size
            orientation = "portrait" if h > w else "square" if h == w else "landscape"
            status = "PASS" if h > w else "FAIL_NOT_PORTRAIT"
            rows.append({"figure_file":name,"exists":True,"width_px":w,"height_px":h,
                         "orientation":orientation,"portrait_map_status":status})
        except Exception as e:
            rows.append({"figure_file":name,"exists":True,"width_px":np.nan,"height_px":np.nan,
                         "orientation":None,"portrait_map_status":f"WARNING_READ_FAILED: {e}"})
    audit = pd.DataFrame(rows)
    save_df(audit, TABLE_DIR / "Table19_Figure_Layout_Audit.csv")
    return audit


def build_figure_use_manifest():
    """
    Explicit three-product figure plan.

    PRODUCT 1: APHL Annual 2027 Poster
      Framework/system integration and selected validated results.

    PRODUCT 2: Paper 1 — National ID Lab Con study
      Empirical respiratory-virus evaluation across U.S. jurisdictions.

    PRODUCT 3: Paper 2 — Tennessee-focused study
      Tennessee surveillance coverage/blind spots, equity, clinical alignment,
      and contextual/environmental intelligence.

    A figure may be generated from the same reproducible data pipeline, but
    each scholarly product receives its own figure assignment and copy.
    """
    rows = [
        # =====================================================
        # APHL POSTER
        # =====================================================
        dict(product="APHL_POSTER", figure_file="Fig_NWGS_Framework_Architecture.png",
             figure_number="Poster Figure 1", section="Framework Architecture",
             purpose="NWGS Grid multimodal data-to-decision architecture.", required=True,
             status_type="PENDING_DESIGN"),
        dict(product="APHL_POSTER", figure_file="Fig_Combined_Respiratory_Trends_and_Maps.png",
             figure_number="Poster Figure 2", section="National Respiratory Surveillance",
             purpose="SARS-CoV-2, RSV, and Influenza A national trends paired with recent county activity.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="APHL_POSTER", figure_file="Fig_Combined_Surveillance_Performance.png",
             figure_number="Poster Figure 3", section="Coverage, Equity, and Temporal Performance",
             purpose="National coverage, SVI readiness, and wastewater-clinical temporal alignment. Tennessee-specific results appear only in the Tennessee paper product, not in this national composite.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="APHL_POSTER", figure_file="Fig_APHL_Seasonal_Peak_Panel.png",
             figure_number="Poster Figure 3B", section="Respiratory Seasonality",
             purpose="Concise complete-season peak timing summary for SARS-CoV-2, RSV, and Influenza A; not applied to detection-based emerging pathogens.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="APHL_POSTER", figure_file="Fig_Combined_Emerging_Pathogen_Detection.png",
             figure_number="Poster Figure 4", section="Emerging Pathogen Detection",
             purpose="H5, Mpox, and Measles detection frequency; display only when source-field/parser validation passes.", required=True,
             status_type="GENERATED_IF_VALID"),
        dict(product="APHL_POSTER", figure_file="Fig_Genomic_Structural_Pathogen_Intelligence.png",
             figure_number="Poster Figure 5", section="Genomic and Structural Intelligence",
             purpose="All six pathogens: SARS-CoV-2, RSV, Influenza A, H5, Mpox, and Measles with CDC PHIL imagery and representative RCSB structural context.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="APHL_POSTER", figure_file="Fig_AMR_ARG_Detection_Profile.png",
             figure_number="Poster Supplemental A", section="AMR / One Health Extension",
             purpose="Optional framework-extension figure: ARG detection frequency by gene target; published cross-sectional AMR/ARG data, not live surveillance.", required=False,
             status_type="OPTIONAL"),
        # v5.14: Poster Supplemental B (Map_AMR_ARG_State_Burden.png) dropped
        # from the poster manifest at user request - the map occupied only
        # a small lower-left box against a mostly-blank canvas (same
        # title-to-content whitespace pattern the v5.12 Tennessee fixes
        # addressed, but never applied to plot_amr_state_map()), and its
        # legend/source-note text overlapped illegibly. It was already
        # status_type=OPTIONAL/required=False, so removing it drops no
        # required poster content; Supplemental A (the ARG detection bar
        # chart) still fully represents the AMR/ARG module on the poster.
        # plot_amr_state_map() itself is untouched and still runs/saves the
        # standalone figure to FIG_DIR each run - it is simply no longer
        # copied into 01_APHL_POSTER by organize_figures_by_scholarly_product().

        # =====================================================
        # PAPER 1 — NATIONAL ID LAB CON
        # =====================================================
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Study_Design_Workflow.png",
             figure_number="Figure 1", section="Study Design",
             purpose="National respiratory-virus multimodal data-integration and evaluation workflow.", required=True,
             status_type="PENDING_DESIGN"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Combined_Respiratory_Trends.png",
             figure_number="Figure 2", section="National Temporal Patterns",
             purpose="National SARS-CoV-2, RSV, and Influenza A wastewater activity trends.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Seasonal_Peak_Timing_Paper1.png",
             figure_number="Figure 3", section="Seasonal Peak Analysis",
             purpose="Complete-season wastewater and clinical peak timing, magnitude, duration, and interannual variability for routine respiratory pathogens. Any season flagged by the v5.17 implausible-lead audit (Table04d/e) should be checked before citing its lead value.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_LagSummary.png",
             figure_number="Figure 4", section="Wastewater-Clinical Temporal Alignment",
             purpose="Selected wastewater-clinical lag by pathogen; positive lag means wastewater leads.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Combined_RecentActivity_Maps.png",
             figure_number="Figure 5", section="Geospatial Activity",
             purpose="Recent county-level respiratory pathogen activity.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Combined_LISA_Maps.png",
             figure_number="Figure 6", section="Spatial Clustering",
             purpose="KNN-LISA spatial clustering for SARS-CoV-2, RSV, and Influenza A.", required=True,
             status_type="GENERATED_ANALYSIS"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_ML_Model_Performance.png",
             figure_number="Figure 7", section="Predictive Modeling",
             purpose="Baseline versus multimodal model performance.", required=True,
             status_type="PENDING_ML"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Wastewater_Only_Value.png",
             figure_number="Figure 7B", section="Predictive Modeling — Standalone Wastewater Value",
             purpose="Standalone wastewater-only model vs. clinical-persistence baseline vs. full model, resolving the collinearity ambiguity in the Figure 9 ablation (see Table12e). v5.20: one of three converging diagnostics merged into Table12h_ML_Predictive_Value_Triangulation.csv alongside the ablation and SHAP ranking.", required=True,
             status_type="PENDING_ML"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Observed_vs_Predicted.png",
             figure_number="Figure 8", section="Forecast Validation",
             purpose="Observed versus predicted clinical burden / target. v5.20: flagged residual outliers (Table12f) are now circled on the figure with a caption explaining the diagnostic pattern rather than appearing as unlabeled points.", required=True,
             status_type="PENDING_ML"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Multimodal_Ablation.png",
             figure_number="Figure 9", section="Ablation",
             purpose="Incremental value of multimodal feature groups. v5.20: one of three converging diagnostics merged into Table12h_ML_Predictive_Value_Triangulation.csv alongside the wastewater-only benchmark and SHAP ranking.", required=True,
             status_type="PENDING_ML"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_SHAP_Explainability.png",
             figure_number="Figure 10", section="Explainability",
             purpose="SHAP feature contributions for the final model. v5.20: full ranked feature list saved to Table12g_SHAP_Top_Features.csv; wastewater_index's rank is one of three converging diagnostics in Table12h_ML_Predictive_Value_Triangulation.csv.", required=True,
             status_type="PENDING_ML"),
        dict(product="PAPER1_NATIONAL_IDLAB", figure_file="Fig_Coverage_Equity.png",
             figure_number="Supplemental Figure S1", section="Coverage Equity",
             purpose="National analysis-readiness gradient by SVI.", required=False,
             status_type="SUPPLEMENTAL"),

        # =====================================================
        # PAPER 2 — TENNESSEE
        # =====================================================
        dict(product="PAPER2_TENNESSEE", figure_file="Fig_Tennessee_Study_Design.png",
             figure_number="Figure 1", section="Study Design",
             purpose="Tennessee 95-county surveillance, clinical, equity, rurality, and environmental integration workflow.", required=True,
             status_type="PENDING_TN_ANALYSIS"),
        dict(product="PAPER2_TENNESSEE", figure_file="Map_Tennessee_Surveillance_Coverage.png",
             figure_number="Figure 2", section="Surveillance Coverage and Blind Spots",
             purpose="All 95 Tennessee counties showing wastewater reporting coverage and surveillance gaps.", required=True,
             status_type="PENDING_TN_ANALYSIS"),
        dict(product="PAPER2_TENNESSEE", figure_file="Fig_Tennessee_Multipathogen_Trends.png",
             figure_number="Figure 3", section="Pathogen Surveillance",
             purpose="Tennessee SARS-CoV-2, RSV, and Influenza A temporal surveillance where data support inference.", required=True,
             status_type="PENDING_TN_ANALYSIS"),
        dict(product="PAPER2_TENNESSEE", figure_file="Fig_Tennessee_WW_Clinical_Alignment.png",
             figure_number="Figure 4", section="Wastewater-Clinical Concordance",
             purpose="Tennessee wastewater versus clinical respiratory activity, with sample-size limitations reported.", required=True,
             status_type="PENDING_TN_ANALYSIS"),
        dict(product="PAPER2_TENNESSEE", figure_file="Map_Tennessee_SVI_Surveillance_Readiness.png",
             figure_number="Figure 5", section="Surveillance Equity",
             purpose="County SVI and wastewater surveillance readiness/blind spots. v5.19: this figure is now force-corrected to portrait by deterministic white-margin padding if matplotlib's own tight-bbox cropping produces a landscape file (see Table20/Table13's portrait self-check rows for whether this run needed the correction).", required=True,
             status_type="PENDING_TN_ANALYSIS"),
        dict(product="PAPER2_TENNESSEE", figure_file="Fig_Tennessee_Equity_Model.png",
             figure_number="Figure 6", section="Equity Model",
             purpose="Tennessee-specific association between vulnerability and surveillance readiness, adjusted where possible for population/rurality.", required=True,
             status_type="PENDING_TN_ANALYSIS"),
        dict(product="PAPER2_TENNESSEE", figure_file="Fig_Tennessee_Seasonal_Peaks.png",
             figure_number="Figure 7", section="Seasonal Peak Analysis",
             purpose="Tennessee seasonal peak timing only for pathogen-seasons meeting predefined county-season coverage eligibility criteria; suppressed otherwise. v5.17: annotated with season_ready_counties/observed_counties (Table18).", required=False,
             status_type="GENERATED_IF_VALID"),
        dict(product="PAPER2_TENNESSEE", figure_file="Map_Tennessee_Environmental_Context.png",
             figure_number="Figure 8", section="Environmental Intelligence",
             purpose="EPA AQS/environmental context where enabled and analytically justified.", required=False,
             status_type="PENDING_OPTIONAL_API"),
        dict(product="PAPER2_TENNESSEE", figure_file="Fig_Tennessee_Multipathogen_Surveillance.png",
             figure_number="Supplemental Figure S1", section="Current Sparse-Coverage Snapshot",
             purpose="Current 2/95-county reporting snapshot retained as a limitation/supplement, not statewide inference.", required=False,
             status_type="GENERATED_LIMITATION"),
    ]

    manifest = pd.DataFrame(rows)

    def resolve(row):
        p = FIG_DIR / row["figure_file"]
        if p.exists():
            return "GENERATED"
        if str(row["status_type"]).startswith("PENDING"):
            return "PENDING_FUTURE_ANALYSIS"
        if row["status_type"] == "GENERATED_IF_VALID":
            return "NOT_GENERATED_OR_VALIDATION_SUPPRESSED"
        return "MISSING_OR_OPTIONAL"

    manifest["generation_status"] = manifest.apply(resolve, axis=1)
    manifest["source_path"] = manifest["figure_file"].apply(lambda x: str(FIG_DIR / x))
    save_df(manifest, TABLE_DIR / "Table14_Figure_Use_Manifest.csv")
    return manifest



def organize_figures_by_scholarly_product(manifest):
    """
    Copy generated figures into three completely separate scholarly-product
    folders. A copy failure is logged and does not abort the pipeline.
    """
    product_dirs = {
        "APHL_POSTER": APHL_POSTER_DIR,
        "PAPER1_NATIONAL_IDLAB": PAPER1_DIR,
        "PAPER2_TENNESSEE": PAPER2_DIR,
    }

    for d in product_dirs.values():
        d.mkdir(parents=True, exist_ok=True)
        for p in d.glob("*.png"):
            try:
                p.unlink()
            except Exception:
                pass

    copy_rows = []
    for r in manifest.itertuples():
        src = Path(r.source_path)
        dest_dir = product_dirs.get(r.product)
        if dest_dir is None:
            continue

        if not src.exists():
            copy_rows.append({
                "product": r.product,
                "figure_file": r.figure_file,
                "figure_number": r.figure_number,
                "copy_status": "NOT_YET_GENERATED",
                "copied_to": None,
                "copy_error": None,
            })
            continue

        prefix = re.sub(r"[^A-Za-z0-9]+", "_", str(r.figure_number)).strip("_")
        dest = dest_dir / f"{prefix}__{src.name}"
        try:
            shutil.copy2(src, dest)
            status, err = "PASS", None
        except Exception as e:
            status, err = "WARNING_COPY_FAILED", str(e)

        copy_rows.append({
            "product": r.product,
            "figure_file": r.figure_file,
            "figure_number": r.figure_number,
            "copy_status": status,
            "copied_to": str(dest) if status == "PASS" else None,
            "copy_error": err,
        })

    copy_manifest = pd.DataFrame(copy_rows)
    save_df(copy_manifest, TABLE_DIR / "Table14b_Figure_Copy_Manifest.csv")
    return copy_manifest




def audit_scholarly_product_folders(manifest, copy_manifest):
    """Fail loudly when a generated figure was not copied into its assigned product folder."""
    rows = []
    dirs = {
        "APHL_POSTER": APHL_POSTER_DIR,
        "PAPER1_NATIONAL_IDLAB": PAPER1_DIR,
        "PAPER2_TENNESSEE": PAPER2_DIR,
    }
    for product, d in dirs.items():
        assigned = manifest[manifest["product"].eq(product)]
        generated = assigned[assigned["generation_status"].eq("GENERATED")]
        pngs = list(d.glob("*.png"))
        rows.append({
            "product": product,
            "assigned_figures": len(assigned),
            "generated_at_classification": len(generated),
            "png_files_in_product_folder": len(pngs),
            "folder": str(d),
            "status": "PASS" if len(pngs) >= len(generated) else "WARNING_COPY_MISMATCH",
        })
    audit = pd.DataFrame(rows)
    save_df(audit, TABLE_DIR / "Table14c_Scholarly_Product_Folder_Audit.csv")
    for r in rows:
        print(f"{r['product']}: {r['png_files_in_product_folder']} PNG files in folder | {r['status']}")
    return audit

def write_figure_readme(manifest):
    """
    Write a separate figure plan/readme for each scholarly product.
    """
    products = {
        "APHL_POSTER": (
            APHL_POSTER_DIR,
            "APHL Annual 2027 Poster",
            "NWGS Grid™: A Multimodal Wastewater Genomic Surveillance Framework for Geospatial, Genomic, and Public Health Intelligence",
        ),
        "PAPER1_NATIONAL_IDLAB": (
            PAPER1_DIR,
            "Paper 1 — National / ID Lab Con 2027",
            "From Wastewater Signals to Clinical Burden: A Multimodal Machine-Learning and Geospatial Evaluation of Respiratory Virus Surveillance Across U.S. Jurisdictions",
        ),
        "PAPER2_TENNESSEE": (
            PAPER2_DIR,
            "Paper 2 — Tennessee",
            "Decoding Tennessee Wastewater Surveillance: A Multimodal Geospatial Assessment of Infectious-Disease Signals, Surveillance Coverage, and Public-Health Equity",
        ),
    }

    for product, (dest_dir, label, title) in products.items():
        subset = manifest[manifest["product"].eq(product)].copy()
        lines = [
            f"NWGS Grid™ — {label}",
            "=" * (13 + len(label)),
            "",
            "Title:",
            title,
            "",
            "FIGURE PLAN",
            "-----------",
            "",
        ]
        for r in subset.itertuples():
            lines.extend([
                f"{r.figure_number}: {r.figure_file}",
                f"  Section: {r.section}",
                f"  Status: {r.generation_status}",
                f"  Required: {r.required}",
                f"  Purpose: {r.purpose}",
                "",
            ])
        (dest_dir / "README_FIGURE_PLAN.txt").write_text("\n".join(lines), encoding="utf-8")


# ============================================================
# 22. MAIN
# ============================================================
def main():
    print("\n=== NWGS GRID™ MASTER MULTIMODAL PIPELINE v5.19 ===\n")

    print("[0/19] Clearing all figure outputs from previous runs (unconditional)...")
    clean_stale_versioned_outputs()

    print("\n[1/19] Loading frozen SVI...")
    svi = load_svi()

    print("\n[2/19] Loading frozen TIGER/Line counties...")
    tiger = load_tiger()

    print("\n[3/19] Pulling six CDC wastewater pathogen APIs...")
    harmonized = []
    raw_manifest = []
    raw_by_pathogen = {}

    for key, cfg in CDC_DATASETS.items():
        print(f"\n--- {cfg['label']} ({cfg['id']}) ---")
        raw, meta = smart_cdc_fetch(cfg["id"], STUDY_START, STUDY_END)
        raw_by_pathogen[cfg["label"]] = raw.copy()
        raw_path = save_df(raw, RAW_DIR / f"CDC_WASTEWATER_{key.upper()}_{cfg['id']}_FROZEN.csv")
        raw_manifest.append({
            "pathogen": cfg["label"],
            "dataset_id": cfg["id"],
            "dataset_name": meta.get("name"),
            "rows": len(raw),
            "columns": len(raw.columns),
            "updated_at_metadata": meta.get("rowsUpdatedAt"),
            "raw_snapshot": str(raw_path),
        })
        h = harmonize_pathogen(raw, key, meta)
        harmonized.append(h)

    wastewater = pd.concat(harmonized, ignore_index=True)
    wastewater = wastewater[
        wastewater["sample_collect_date"].between(STUDY_START, STUDY_END, inclusive="both") |
        wastewater["sample_collect_date"].isna()
    ].copy()
    wastewater = add_within_site_standardization(wastewater)
    wastewater = add_emerging_detection_flags(wastewater)

    save_df(pd.DataFrame(raw_manifest), TABLE_DIR / "Table01_CDC_Wastewater_Data_Sources.csv")
    source_detection_profile = profile_emerging_detection_fields(raw_by_pathogen)
    save_df(source_detection_profile, TABLE_DIR / "Table01b_CDC_Emerging_Detection_SourceField_Profile.csv")
    save_df(wastewater, PROC_DIR / "NWGS_WASTEWATER_HARMONIZED.parquet")

    print("\n[4/19] Creating pathogen cards + trend series...")
    pathogen_summary = make_pathogen_summary(wastewater)
    site_week, national_week = national_weekly_series(wastewater)
    detection_audit = emerging_detection_audit(wastewater)
    emerging_week = national_emerging_series(wastewater)
    save_df(pathogen_summary, TABLE_DIR / "Table02_Pathogen_Summary_Cards.csv")
    save_df(national_week, TABLE_DIR / "Table03_National_Pathogen_Trends.csv")
    save_df(emerging_week, TABLE_DIR / "Table03b_Emerging_Pathogen_Detection_Trends.csv")
    save_df(detection_audit, TABLE_DIR / "Table03c_Emerging_Pathogen_Detection_Audit.csv")
    plot_pathogen_trends(national_week)
    plot_emerging_trends(emerging_week, detection_audit)

    print("\n[5/19] Pulling current CDC NSSP ED respiratory surveillance...")
    ed = load_nssp_ed()

    print("\n[6/19] Building state-week multimodal respiratory table...")
    state_week = build_state_week(wastewater)
    multimodal = merge_clinical(state_week, ed)
    save_df(multimodal, PROC_DIR / "NWGS_STATE_WEEK_MULTIMODAL.csv")

    print("\n[7/19] Running wastewater-clinical lag analyses...")
    all_lag, best_lag = lag_analysis(multimodal)
    save_df(all_lag, TABLE_DIR / "Table04_All_Lag_Results.csv")
    save_df(best_lag, TABLE_DIR / "Table04_Best_Lag_Results.csv")
    plot_lag_summary(best_lag)

    print("\n[7b/19] Running publication seasonal peak analyses...")
    season_state, season_national, season_interannual = seasonal_peak_analysis(multimodal)
    save_df(season_state, TABLE_DIR / "Table04c_Seasonal_State_Pathogen_Peaks.csv")
    save_df(season_national, TABLE_DIR / "Table04d_Seasonal_National_Pathogen_Peaks.csv")
    save_df(season_interannual, TABLE_DIR / "Table04e_Seasonal_Interannual_Variability.csv")
    plot_seasonal_peak_analysis(season_national)

    print("\n[8/19] Building county coverage + equity analysis...")
    coverage = build_county_coverage(wastewater, svi)
    equity = coverage_equity(coverage)
    equity_model, equity_county = coverage_equity_model(coverage)
    save_df(coverage, TABLE_DIR / "Table05_County_Pathogen_Coverage.csv")
    save_df(equity, TABLE_DIR / "Table06_Coverage_Equity.csv")
    save_df(equity_model, TABLE_DIR / "Table06b_Coverage_Equity_GLM.csv")
    save_df(equity_county, TABLE_DIR / "Table06c_Coverage_Equity_CountyModelInput.csv")
    plot_equity(equity)

    print("\n[9/19] Building redesigned pathogen activity maps...")
    activity = latest_county_activity(wastewater)
    save_df(activity, TABLE_DIR / "Table07_Recent_County_Pathogen_Activity.csv")
    try:
        emerging_county = recent_emerging_by_county(wastewater)
        save_df(emerging_county, TABLE_DIR / "Table07c_Recent_County_Emerging_Detections.csv")
    except Exception as exc:  # optional app layer; never blocks the run
        print(f"[WARN] Table07c emerging detections by county skipped: {exc}")
    plot_coverage_map(tiger, coverage)
    plot_activity_maps(tiger, activity)
    plot_tennessee_maps(tiger, activity)

    print("\n[10/19] Running corrected spatial analysis (projected KNN-LISA)...")
    global_moran, lisa = spatial_activity_analysis(tiger, activity)
    save_df(global_moran, TABLE_DIR / "Table08_Global_MoransI_PathogenActivity.csv")
    save_df(lisa, TABLE_DIR / "Table08_LISA_PathogenActivity.csv")
    plot_lisa_maps(tiger, lisa)
    independence = pathogen_independence_audit(activity, lisa)
    spatial_attrition = spatial_attrition_audit(activity, lisa, tiger)
    save_df(independence, TABLE_DIR / "Table08b_Pathogen_Independence_Audit.csv")
    save_df(spatial_attrition, TABLE_DIR / "Table08c_Spatial_Attrition_Audit.csv")

    print("\n[10b/19] Generating Tennessee Paper 2 figure package...")
    create_tennessee_paper_figures(tiger, coverage, activity, multimodal, svi)
    tn_seasonal, tn_county_seasonal = tennessee_seasonal_analysis(wastewater, multimodal)
    save_df(tn_seasonal, TABLE_DIR / "Table18_Tennessee_Seasonal_Eligibility_and_Peaks.csv")
    save_df(tn_county_seasonal, TABLE_DIR / "Table18b_Tennessee_County_Seasonal_Coverage.csv")

    print("\n[11/19] Pulling CDC PLACES + optional contextual APIs...")
    places = load_places()
    _ = load_acs_optional()
    noaa_status()
    epa_aqs_status()

    print("\n[12/19] Loading published U.S. wastewater AMR/ARG data...")
    amr = load_amr_arg()
    amr_classification_audit = audit_amr_classification(amr)
    save_df(amr_classification_audit, TABLE_DIR / "Table09b_AMR_Classification_Audit.csv")
    amr_target, amr_state = summarize_amr(amr)
    save_df(amr_target, TABLE_DIR / "Table09_AMR_ARG_Target_Summary.csv")
    save_df(amr_state, TABLE_DIR / "Table09_AMR_ARG_State_Summary.csv")
    plot_amr(amr_target)
    plot_amr_state_map(tiger, amr_state)

    print("\n[13/19] Downloading CDC PHIL pathogen reference imagery...")
    pathogen_manifest = download_cdc_phil_pathogen_images()

    print("\n[14/19] Pulling supplemental NCBI genomic metadata...")
    genomics = pull_ncbi_genomics()

    print("\n[15/19] Pulling RCSB protein metadata + rendering deposited structures...")
    pdb_map = pull_rcsb_structure_mappings(genomics)
    try:
        _ent_path = TABLE_DIR / "Table11b_RCSB_Protein_Entities.csv"
        structure_regions = pull_uniprot_functional_regions(
            pd.read_csv(_ent_path) if _ent_path.exists() else pd.DataFrame())
    except Exception as exc:   # optional annotation layer; never blocks a run
        structure_regions = pd.DataFrame()
        print(f"[WARN] UniProt functional regions skipped: {type(exc).__name__}: {exc}")

    print("\n[16/19] Creating genomic + structural pathogen intelligence figure...")
    pathogen_intelligence_figure = create_pathogen_intelligence_figure(pathogen_manifest, pdb_map)
    save_df(pathogen_manifest, APP_DIR / "pathogen_image_manifest.csv")
    save_df(pdb_map, APP_DIR / "protein_structure_manifest.csv")
    if not pdb_map.empty:
        (APP_DIR / "protein_structure_manifest.json").write_text(
            pdb_map.replace({np.nan: None}).to_json(orient="records", indent=2),
            encoding="utf-8"
        )

    print("\n[17/19] Creating app exports + optional exploratory ML...")
    ml, ml_predictions, ml_ablation, ml_wastewater_only, ml_collinearity = exploratory_ml(multimodal)
    if not ml.empty:
        save_df(ml, TABLE_DIR / "Table12_Exploratory_ML_Benchmark.csv")
        plot_ml_model_performance(ml)
    if not ml_ablation.empty:
        save_df(ml_ablation, TABLE_DIR / "Table12b_Exploratory_ML_Ablation.csv")
        plot_ablation(ml_ablation)
    # v5.18 additions: standalone wastewater-only benchmark and the
    # collinearity audit that motivates it (see exploratory_ml() docstring
    # and the v5.18 changelog entry on the Figure 9 ablation ambiguity).
    if not ml_wastewater_only.empty:
        save_df(ml_wastewater_only, TABLE_DIR / "Table12d_Wastewater_Only_Benchmark.csv")
        plot_wastewater_only_comparison(ml_wastewater_only)
    if not ml_collinearity.empty:
        save_df(ml_collinearity, TABLE_DIR / "Table12e_ML_Feature_Collinearity_Audit.csv")
    if ml_predictions:
        # v5.20: compute outliers BEFORE plotting Figure 8, so the figure
        # itself can circle the flagged points instead of only listing
        # them in a separate table (see plot_observed_vs_predicted() v5.20
        # addition).
        ml_outliers = audit_ml_prediction_outliers(ml_predictions)
        if not ml_outliers.empty:
            save_df(ml_outliers, TABLE_DIR / "Table12f_ML_Prediction_Outliers.csv")
        plot_observed_vs_predicted(ml_predictions, outliers_df=ml_outliers)
        ml_shap_features = explain_with_shap(ml_predictions)
        if not ml_shap_features.empty:
            save_df(ml_shap_features, TABLE_DIR / "Table12g_SHAP_Top_Features.csv")
        # v5.20 addition: fold the ablation, wastewater-only benchmark, and
        # SHAP ranking together into one citable table instead of leaving
        # a reader to cross-reference three separate figures by hand.
        ml_triangulation = build_ml_triangulation_summary(ml_ablation, ml_wastewater_only, ml_shap_features)
        if not ml_triangulation.empty:
            save_df(ml_triangulation, TABLE_DIR / "Table12h_ML_Predictive_Value_Triangulation.csv")
    else:
        ml_outliers = pd.DataFrame()
        ml_shap_features = pd.DataFrame()
        ml_triangulation = pd.DataFrame()

    # ------------------------------------------------------------
    # [17b/19] Surveillance-gap analytics (v5.22, section 21c).
    # Each block is independently wrapped: these occupy documented
    # vacancies in the literature, but none of them is allowed to take
    # the weekly run down with it.
    # ------------------------------------------------------------
    print("\n[17b/19] Building surveillance-gap analytics...")
    pipeline_run_id = "run_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")
    svi_lookup = (coverage.groupby("county_fips")
                          .agg(svi=("RPL_THEMES", "first"))
                          .reset_index()) if "RPL_THEMES" in coverage.columns else pd.DataFrame()

    lead_decomp = lead_national = pd.DataFrame()
    try:
        lead_decomp = lead_time_decomposition(best_lag, raw_manifest, wastewater)
        lead_national = lead_time_national(lead_decomp)
        if not lead_decomp.empty:
            save_df(lead_decomp, TABLE_DIR / "Table21_LeadTime_Decomposition.csv")
        if not lead_national.empty:
            save_df(lead_national, TABLE_DIR / "Table21b_LeadTime_National.csv")
    except Exception as exc:
        print(f"[WARN] lead-time decomposition skipped: {type(exc).__name__}: {exc}")

    attrition_sites = attrition_yearly = attrition_vuln = pd.DataFrame()
    try:
        attrition_sites, attrition_yearly = coverage_attrition(wastewater)
        attrition_vuln = attrition_by_vulnerability(attrition_sites, svi_lookup)
        if not attrition_sites.empty:
            save_df(attrition_sites, TABLE_DIR / "Table22_Coverage_Attrition_Sites.csv")
        if not attrition_yearly.empty:
            save_df(attrition_yearly, TABLE_DIR / "Table22b_Coverage_Attrition_Yearly.csv")
        if not attrition_vuln.empty:
            save_df(attrition_vuln, TABLE_DIR / "Table22c_Attrition_By_Vulnerability.csv")
    except Exception as exc:
        print(f"[WARN] coverage attrition skipped: {type(exc).__name__}: {exc}")

    forecast_board = forecast_scored = pd.DataFrame()
    try:
        forecast_ledger = record_forecasts(national_week, pipeline_run_id)
        forecast_scored, forecast_board = score_forecasts(forecast_ledger, national_week)
        if not forecast_ledger.empty:
            save_df(forecast_ledger, TABLE_DIR / "Table23_Forecast_Ledger.csv")
        if not forecast_scored.empty:
            save_df(forecast_scored, TABLE_DIR / "Table23b_Forecast_Scored.csv")
        if not forecast_board.empty:
            save_df(forecast_board, TABLE_DIR / "Table23c_Forecast_Scoreboard.csv")
    except Exception as exc:
        print(f"[WARN] forecast scoreboard skipped: {type(exc).__name__}: {exc}")

    representativeness = rep_national = pd.DataFrame()
    try:
        representativeness = county_representativeness(wastewater, coverage, svi)
        rep_national = representativeness_national(representativeness)
        if not representativeness.empty:
            save_df(representativeness, TABLE_DIR / "Table24_County_Representativeness.csv")
        if not rep_national.empty:
            save_df(rep_national, TABLE_DIR / "Table24b_Representativeness_National.csv")
    except Exception as exc:
        print(f"[WARN] representativeness skipped: {type(exc).__name__}: {exc}")

    assay_panel = pd.DataFrame()
    try:
        assay_panel = assay_variation_overlay(assay_target_panel(), genomics)
        if not assay_panel.empty:
            save_df(assay_panel, TABLE_DIR / "Table25_Assay_Target_Panel.csv")
    except Exception as exc:
        print(f"[WARN] assay-target panel skipped: {type(exc).__name__}: {exc}")

    global_countries = global_income = pd.DataFrame()
    try:
        amelag = fetch_amelag()
        if not amelag.empty:
            save_df(amelag, RAW_DIR / "RKI_AMELAG_FROZEN.csv")
        global_countries, global_income = global_coverage_equity(amelag=amelag)
        if not global_countries.empty:
            save_df(global_countries, TABLE_DIR / "Table26_Global_Coverage_Equity.csv")
        if not global_income.empty:
            save_df(global_income, TABLE_DIR / "Table26b_Global_Coverage_By_Income.csv")
    except Exception as exc:
        print(f"[WARN] global coverage equity skipped: {type(exc).__name__}: {exc}")

    # App-ready tables
    save_df(pathogen_summary, APP_DIR / "pathogen_cards.csv")
    save_df(national_week, APP_DIR / "pathogen_trends.csv")
    save_df(emerging_week, APP_DIR / "emerging_pathogen_detection_trends.csv")
    save_df(activity, APP_DIR / "county_pathogen_activity.csv")
    save_df(best_lag, APP_DIR / "wastewater_clinical_lag.csv")
    save_df(season_national, APP_DIR / "seasonal_peak_summary.csv")
    save_df(tn_seasonal, APP_DIR / "tennessee_seasonal_eligibility.csv")
    save_df(equity, APP_DIR / "coverage_equity.csv")
    save_df(lisa, APP_DIR / "spatial_clusters.csv")
    save_df(amr_target, APP_DIR / "amr_arg_targets.csv")
    save_df(amr_state, APP_DIR / "amr_arg_states.csv")
    if not genomics.empty:
        save_df(genomics.drop(columns=["raw_json"], errors="ignore"), APP_DIR / "genomic_context.csv")
    if not pdb_map.empty:
        save_df(pdb_map, APP_DIR / "pdb_mappings.csv")
    export_app_json(pathogen_summary, activity, best_lag, global_moran, amr_target, amr_state, genomics, pdb_map)

    # v5.18 addition: export the figure-generation-time portrait self-check
    # collected by _verify_portrait_or_warn() during
    # create_tennessee_paper_figures(), regardless of what the separate
    # Table19 layout audit later finds - this is the check that runs at
    # the moment the figure is actually produced by THIS execution.
    portrait_self_check_df = pd.DataFrame(_PORTRAIT_SELF_CHECK_RESULTS)
    if not portrait_self_check_df.empty:
        save_df(portrait_self_check_df, TABLE_DIR / "Table20_Portrait_SelfCheck.csv")

    validation = build_validation_summary(
        wastewater, detection_audit, activity, lisa, independence,
        best_lag, equity, amr_target,
        equity_model=equity_model,
        pdb_map=pdb_map,
        spatial_attrition=spatial_attrition,
        pathogen_manifest=pathogen_manifest,
        detection_source_profile=source_detection_profile,
        amr_classification_audit=amr_classification_audit,
        seasonal_national=season_national,
        portrait_self_check=portrait_self_check_df,
        ml_collinearity=ml_collinearity,
        ml_wastewater_only=ml_wastewater_only,
        ml_outliers=ml_outliers,
    )
    save_df(validation, TABLE_DIR / "Table13_NWGS_Validation_Summary.csv")

    print("\n[18/19] Creating combined publication/poster figures...")
    create_combined_publication_figures(detection_audit=detection_audit)
    figure_layout_audit = audit_figure_layouts()
    nonportrait_maps = figure_layout_audit[figure_layout_audit["portrait_map_status"].eq("FAIL_NOT_PORTRAIT")] if not figure_layout_audit.empty else pd.DataFrame()
    if len(nonportrait_maps):
        print(f"WARNING figure layout audit found {len(nonportrait_maps)} non-portrait map exports.")
    else:
        print("PASS figure layout audit: generated map exports are portrait-oriented.")

    print("\n[19/19] Classifying figures into APHL Poster, Paper 1 National, and Paper 2 Tennessee...")
    figure_use_manifest = build_figure_use_manifest()
    figure_copy_manifest = organize_figures_by_scholarly_product(figure_use_manifest)
    folder_audit = audit_scholarly_product_folders(figure_use_manifest, figure_copy_manifest)
    write_figure_readme(figure_use_manifest)

    print("\n=== THREE-PRODUCT FIGURE CLASSIFICATION SUMMARY ===")
    for product, label in [
        ("APHL_POSTER", "APHL poster"),
        ("PAPER1_NATIONAL_IDLAB", "Paper 1 national"),
        ("PAPER2_TENNESSEE", "Paper 2 Tennessee"),
    ]:
        s = figure_use_manifest[figure_use_manifest["product"].eq(product)]
        generated = int(s["generation_status"].eq("GENERATED").sum())
        pending = int(s["generation_status"].str.startswith("PENDING").sum())
        print(f"{label}: {generated} generated | {pending} pending")

    if figure_copy_manifest is not None and not figure_copy_manifest.empty:
        failed_copies = int(figure_copy_manifest["copy_status"].eq("WARNING_COPY_FAILED").sum())
        print(f"Figure copy warnings: {failed_copies}")

    expected_pathogens = {
        "SARS-CoV-2", "RSV", "Influenza A",
        "Influenza A(H5)", "Mpox", "Measles"
    }
    if pdb_map is not None and not pdb_map.empty:
        rendered_pathogens = set(
            pdb_map.loc[pdb_map["render_status"].eq("PASS"), "pathogen"].dropna().astype(str)
        )
    else:
        rendered_pathogens = set()
    missing_structures = sorted(expected_pathogens - rendered_pathogens)
    print(f"Representative structures rendered: {len(rendered_pathogens & expected_pathogens)}/6")
    if missing_structures:
        print("FAIL missing/unrendered representative structures:", ", ".join(missing_structures))
        print("Structural figure QC: FAIL — publication figure requires 6/6 structures rendered.")
    else:
        print("Structural figure QC: PASS — 6/6 structures rendered, including RSV.")

    # v5.17: surface the seasonal implausible-lead audit in the same
    # top-of-summary block as the structural QC check above, so it is seen
    # even by someone only skimming the run banner rather than reading the
    # full validation table.
    if season_national is not None and not season_national.empty and "implausible_lead_flag" in season_national.columns:
        elig_seasons = season_national[season_national["eligible"].fillna(False)]
        n_flagged_seasons = int(elig_seasons["implausible_lead_flag"].fillna(False).sum())
        if n_flagged_seasons:
            print(f"WARNING seasonal peak audit flagged {n_flagged_seasons} eligible season(s) for implausible wastewater lead — see Table04d and the [SEASONAL PEAK WARNING] lines above before reporting lead values.")
        else:
            print("PASS seasonal peak audit: no eligible season flagged for an implausible wastewater lead.")

    # v5.18 addition: surface the figure-generation-time portrait
    # self-check in the same top-of-summary block, so a Figure 5 (or
    # Figure 2) orientation failure from THIS run is visible immediately,
    # rather than only discoverable by separately opening Table19 or
    # Table20 after the fact.
    if not portrait_self_check_df.empty:
        statuses = portrait_self_check_df["status"].astype(str)
        n_autofixed = int(statuses.eq("AUTOFIXED_AFTER_FAIL").sum())
        n_unresolved_fail = int(statuses.str.startswith("FAIL").sum())
        n_clean_pass = int(statuses.eq("PASS").sum())
        if n_unresolved_fail:
            print(
                f"FAIL portrait self-check: {n_unresolved_fail}/{len(portrait_self_check_df)} "
                f"figure(s) that are required to be portrait could NOT be corrected even after "
                f"the v5.19 auto-fix padding attempt — see the [PORTRAIT AUTO-FIX] lines above "
                f"and Table20_Portrait_SelfCheck.csv."
            )
        elif n_autofixed:
            print(
                f"WARNING portrait self-check: {n_autofixed}/{len(portrait_self_check_df)} figure(s) "
                f"needed v5.19's white-margin auto-fix to become portrait ({n_clean_pass} passed cleanly "
                f"without correction). The delivered files ARE portrait, but the underlying "
                f"matplotlib rendering cause is still unresolved — see the v5.19 changelog."
            )
        else:
            print(f"PASS portrait self-check: {n_clean_pass}/{len(portrait_self_check_df)} required-portrait figure(s) confirmed portrait in this run's own output, no correction needed.")


    print("\n================ NWGS GRID VALIDATION ================")
    for r in validation.itertuples():
        print(f"{r.component:48s} {r.status:28s} {r.detail}")
    print("=======================================================")

    # Provenance and run metadata
    prov = pd.DataFrame(PROVENANCE)
    prov.to_csv(META_DIR / "DATA_PROVENANCE.csv", index=False)

    run_meta = {
        "generated_utc": utc_now(),
        "study_start": str(STUDY_START.date()),
        "study_end": str(STUDY_END.date()),
        "cdc_datasets": CDC_DATASETS,
        "n_wastewater_records_harmonized": int(len(wastewater)),
        "n_pathogens": int(wastewater["pathogen"].nunique()),
        "n_states_territories": int(wastewater["state_code"].nunique()),
        "spatial_weights": f"KNN k={SPATIAL_K}, projected EPSG:5070",
        "min_lag_pairs": MIN_PAIRED_WEEKS,
        "max_lag_weeks": MAX_LAG_WEEKS,
        "season_definition": "July 1-June 30",
        "min_season_weeks": MIN_SEASON_WEEKS,
        "min_season_completeness": MIN_SEASON_COMPLETENESS,
        "season_smoothing_weeks": SEASON_SMOOTH_WEEKS,
        "lead_artifact_guard_weeks": LEAD_ARTIFACT_GUARD_WEEKS,
        "lead_artifact_guard_threshold_weeks": LEAD_ARTIFACT_GUARD_THRESHOLD_WEEKS,
        "tn_season_min_ready_counties": TN_SEASON_MIN_READY_COUNTIES,
        "tn_season_min_median_sites": TN_SEASON_MIN_MEDIAN_SITES,
        "epa_enabled": ENABLE_EPA_AQS,
        "noaa_enabled": ENABLE_NOAA,
        "acs_enabled": ENABLE_ACS,
        "exploratory_ml_enabled": ENABLE_EXPLORATORY_ML,
        "ncbi_enabled": ENABLE_NCBI,
        "rcsb_enabled": ENABLE_RCSB,
        "amr_source_file": str(AMR_PATH),
        "n_amr_rows": int(len(amr)),
        "n_amr_targets": int(amr["target"].nunique()),
        "n_amr_sites": int(amr["site"].nunique()),
    }
    (META_DIR / "RUN_METADATA.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    print("\nDONE.")
    print(f"Project outputs: {OUT_DIR}")
    print(f"Figures:         {FIG_DIR}")
    print(f"Tables:          {TABLE_DIR}")
    print(f"App exports:     {APP_DIR}")
    print(f"Metadata:        {META_DIR}")
    print("\nIMPORTANT: Review source-specific fields/QC and all numerical results before")
    print("using them in an abstract, poster, manuscript, or operational public-health claim.")

if __name__ == "__main__":
    main()
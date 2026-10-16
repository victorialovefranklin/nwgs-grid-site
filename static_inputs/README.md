# Static inputs

Files the pipeline reads but does not download. Everything here is public and
in the public domain, kept in the repository so that any past release can be
reproduced exactly even if a publisher moves or revises its file.

The large files are gzipped. Every byte of the original is preserved —
`gunzip` returns the publisher's file unchanged — and `pandas.read_csv()` reads
`.csv.gz` directly, so nothing in the pipeline needs to decompress first.

| File | Source | Downloaded | Original | Stored |
|---|---|---|---|---|
| `SVI_2022_US_COUNTY.csv` | [CDC/ATSDR SVI 2022](https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html), United States, counties | 2026 | 3,144 rows × 158 cols | 2.3 MB |
| `SVI_2022_US_TRACT.csv.gz` | [CDC/ATSDR SVI 2022](https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html), United States, census tracts | 2026-10-16 | 84,120 rows × 160 cols, 85.1 MB | 20.9 MB |
| `RUCC_2023_US_COUNTY.csv` | [USDA ERS Rural-Urban Continuum Codes](https://www.ers.usda.gov/data-products/rural-urban-continuum-codes), 2023 edition | 2026-10-16 | 9,703 rows, 3,235 counties | 0.6 MB |
| `EPA_Sewershed_Crosswalk_tracts.csv.gz` | [EPA National Sewershed Dataset v1.2](https://github.com/USEPA/Sewersheds) | 2026-10-16 | 96,932 rows, 5.4 MB | 1.9 MB |
| `EPA_Sewershed_Crosswalk_block_groups.csv.gz` | [EPA National Sewershed Dataset v1.2](https://github.com/USEPA/Sewersheds) | 2026-10-16 | 228,024 rows, 11.5 MB | 3.5 MB |
| `EPA_Sewershed_Attributes.csv.gz` | [EPA National Sewershed Dataset v1.2](https://github.com/USEPA/Sewersheds), Sewersheds layer | 2026-10-16 | 17,079 rows | 0.7 MB |
| `US_Wastewater_AMR_ARG_2024.csv` | [Kim et al. 2025](https://doi.org/10.1101/2025.04.02.25325128), `Averaged` sheet of the published manuscript data | 2026-10-16 | 1,792 rows, 163 plants, 39 states | 0.3 MB |
| `Kim_2025_ManuscriptData.xlsx` | The same study's full workbook, archived whole: `README`, `dPCR_Conc`, `Averaged`, `Aggregated`, `Determinants` | 2026-10-16 | 4,811 dPCR rows | 0.9 MB |
| `NWGS_ASSAY_TARGETS.template.csv` | Template for the optional curated assay-target panel | — | — | <0.1 MB |
| `NWGS_FORECAST_LEDGER.csv` | Written back by the workflow after each run | — | grows weekly | — |

## Notes that matter when reading these

**The SVI files use `-999` for unavailable values**, not for low vulnerability.
They must be converted to missing before any calculation. CDC's documentation
excludes them from its own derived values for the same reason. 778 tracts in
the 2022 United States file carry `-999` for the overall ranking, mostly tracts
with no population, and they are reported as unscored rather than dropped.

**The RUCC file is Windows-1252, not UTF-8.** Seventeen county names carry
accented characters, and reading it as UTF-8 fails part way through. It is also
in long form, three rows per county keyed on an `Attribute` column, so it is
pivoted before use.

**The RUCC file uses Connecticut's nine planning regions** (FIPS 09110–09190),
which replaced its eight counties. Surveillance records still carrying the
retired county codes will not join, and the unmatched identifiers are reported
in `Table06e` rather than discarded.

**EPA's sewershed boundaries are 81% modelled.** 13,826 of 17,079 were produced
by machine learning and 3,253 come from reported sources. `Method`, `Source`,
`Min_Prob` and `Mean_Prob` in the attributes file carry that distinction per
sewershed, and anything derived from them states which basis it used.

**The sewershed crosswalk is weighted by buildings, not area.** EPA intersects
Microsoft building footprint centroids of at least 40 m² with census blocks and
with the sewershed's share of each block. Area weighting would overstate rural
sewer coverage substantially.

**The AMR panel's CSV is re-exported from the archived workbook, not edited.**
An earlier copy had written `mean_16S` in scientific notation at three
significant figures, which put 276 of 1,792 rows up to 0.5% away from the
published value. The ratio the panels actually use, `mean_ARG_S`, was
unaffected, but the stored file no longer matched its source. It is now written
at full precision from `Kim_2025_ManuscriptData.xlsx`, which is archived here so
the export can be repeated.

## Why these are not downloaded at run time

Each has a URL that changes without the data changing. USDA's download carries a
cache-busting token that is replaced whenever ERS republishes. EPA distributes
its current release through Git LFS, which an anonymous fetch cannot read. A
run-time download would therefore fail silently one week with no indication in
the run log, and the pipeline would publish a set of figures missing a layer.

These sources are revised on a scale of years, so pinning them costs nothing and
freezes provenance for every release.

## Replacing one

Download the new file, keep the same name, gzip it if the original exceeds about
5 MB, and update the row count and download date in the table above. Then run the
pipeline once and check the Audit log: every one of these files produces a source
row there, and a layer that failed to load says so rather than disappearing.

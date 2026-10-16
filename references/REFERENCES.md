# NWGS Grid - references and citations

Every source the project uses, in one place: the literature it argues against or
builds on, the datasets it reads, and the software it runs on.

**Access column:** *Free* means the publisher serves the full text at no charge,
so the link below reaches a PDF in one or two clicks. *Public domain* means the
work carries no copyright and may be reproduced with citation.

PDFs are not committed to this repository. Publisher terms vary, and a stored
copy goes stale against the version of record. Use the links; put any PDFs you
download in `references/pdfs/`, which `.gitignore` keeps out of version control.

---

## 1. Literature

### Wastewater surveillance systems and coverage

**Mark-Carew M, Bias M, Reckling S, Madhobi K, Cornforth D, Volkov I, Rainey AL,
Lorentz B, Taibl KR, Oakley LP, West R, Welsh R, Mercante JW, Womack N,
Fehrenbach N, Yoder J.** Progress and Expansion of the National Wastewater
Surveillance System, United States, 2020–2024. *Emerging Infectious Diseases*.
2026;32(Suppl).
→ https://wwwnc.cdc.gov/eid/article/32/13/26-1118_article
**Access: Public domain** (CDC journal; reproducible with citation)

CDC's own account of NWSS. Used three ways: its reporting-timeliness figures
support the reporting-lag term in the lead-time decomposition; its metropolitan
coverage split is the published figure the urbanicity page checks itself
against; and its statement that sewershed boundaries were collected but not
released is cited where that limitation is reported.

**Alkhouri NB, Fisher V, Abuelezam NN.** Equity in Wastewater Surveillance:
Assessment of the National Wastewater Surveillance System for COVID-19.
*AJPM Focus*. 2025;5(1):100434.
→ https://doi.org/10.1016/j.focus.2025.100434
**Access: Free** (open access)

The closest published analysis to the coverage-equity model. Cited on that page
so the model is presented against existing work rather than as a novel finding.

**Schenk H, Rauch W, Zulli A, Boehm AB.** SARS-CoV-2 surveillance in US
wastewater: leading indicators and data variability analysis in 2023–2024.
*PLOS ONE*. 2024;19(11):e0313927.
→ https://doi.org/10.1371/journal.pone.0313927
**Access: Free** (open access)

Lead-time and variability context for the shedding-lead term.

### Assay sensitivity

**Beck AS, Lopareva EN, Hwang H, Hart D, de Almeida M, Anderson R, Rota PA,
Bankamp B.** Evaluation of the sensitivity of a measles diagnostic real-time
RT-PCR assay incorporating recently observed priming mismatch variants, 2024.
*Eurosurveillance*. 2024;29(28):2400410.
→ https://doi.org/10.2807/1560-7917.ES.2024.29.28.2400410
**Access: Free** (open access)

The documented case of circulating variants degrading a widely used RT-PCR
target. Cited in the assay-target panel as the reason that layer exists.

### Antimicrobial resistance in wastewater

**Kim S, Zulli A, Chan EMG, Duong D, Linfield RY, McCormack C, White BJ,
Wolfe MK, Boehm AB, Pickering AJ.** Wastewater surveillance reveals patterns of
antibiotic resistance across the United States. *Nature Communications*.
2026;17:4680.
→ https://doi.org/10.1038/s41467-026-71195-4
**Access: Free** (open access, CC BY 4.0)

Source of every figure on the resistance-gene panels. 163 treatment plants in
39 states, eleven resistance genes measured by digital droplet PCR and
normalised to 16S rRNA. The project stores the study's `Averaged` sheet
unchanged; the detection calls, z-scores and outlier flags are the authors',
not derived here.

The CC BY 4.0 licence permits this reuse provided the work is credited, the
licence is linked, and any changes are stated. The stored copy is unmodified
apart from being re-exported at full numeric precision, which is recorded in
`static_inputs/README.md`.

Underlying data: https://doi.org/10.5281/ZENODO.18749049 (Zenodo), also at
https://purl.stanford.edu/vb318cm9509

### Structural and sequence resources

**Berman HM, Westbrook J, Feng Z, Gilliland G, Bhat TN, Weissig H,
Shindyalov IN, Bourne PE.** The Protein Data Bank. *Nucleic Acids Research*.
2000;28(1):235–242.
→ https://doi.org/10.1093/nar/28.1.235
**Access: Free** (open access)

**The UniProt Consortium.** UniProt: the Universal Protein Knowledgebase.
*Nucleic Acids Research*. 2025.
→ https://www.uniprot.org
**Access: Free** (open access)

Source of the curated functional regions shown on the structures page. Each row
on that page carries its own accession, so individual annotations cite back to
the specific entry rather than to this reference alone.

---

## 2. Datasets

| Dataset | Publisher | Used for | Link | Terms |
|---|---|---|---|---|
| NWSS wastewater data, six pathogens | CDC | Every activity figure on the site | https://data.cdc.gov | Public domain |
| NSSP emergency department visits | CDC | The clinical series the lead-time analysis compares against | https://data.cdc.gov | Public domain |
| PLACES county health measures | CDC | County health context | https://data.cdc.gov | Public domain |
| Social Vulnerability Index 2022, county and census tract | CDC/ATSDR | Coverage equity; vulnerability inside monitored sewersheds | https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html | Public domain |
| Rural-Urban Continuum Codes, 2023 | USDA Economic Research Service | The urbanicity axis of coverage | https://www.ers.usda.gov/data-products/rural-urban-continuum-codes | Public domain |
| National Sewershed Dataset, v1.2 | EPA | Measured sewered population per county | https://github.com/USEPA/Sewersheds | Public domain |
| Clean Watersheds Needs Survey 2022 | EPA | Treatment facility inventory behind the sewershed data | https://www.epa.gov/cwns | Public domain |
| TIGER/Line county boundaries, 2025 | U.S. Census Bureau | County geography | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html | Public domain |
| NCBI Virus and NCBI Datasets API v2 | National Library of Medicine | Sequence records and genomic summaries | https://www.ncbi.nlm.nih.gov/datasets | Public domain |
| Protein Data Bank entries | RCSB PDB | Reference structures | https://www.rcsb.org | Open, cite per entry |
| WHO/UNICEF JMP sanitation data | WHO/UNICEF | Global sewer-connection shares | https://washdata.org | Open, cite source |
| World Bank income classification | World Bank | Country income groups | https://api.worldbank.org | CC BY 4.0 |

Exact file names, download dates and original row counts for everything stored
in this repository are recorded in `static_inputs/README.md`.

---

## 3. Software

| Software | Citation or source | Licence |
|---|---|---|
| D³ | Bostock M, Ogievetsky V, Heer J. D³: Data-Driven Documents. *IEEE Transactions on Visualization and Computer Graphics*. 2011;17(12):2301–2309. https://doi.org/10.1109/TVCG.2011.185 | BSD |
| 3Dmol.js | Rego N, Koes D. 3Dmol.js: molecular visualization with WebGL. *Bioinformatics*. 2015;31(8):1322–1324. https://doi.org/10.1093/bioinformatics/btu829 | BSD |
| us-atlas | Bostock M. us-atlas: U.S. state and county boundaries in TopoJSON, derived from U.S. Census Bureau files. https://github.com/topojson/us-atlas | ISC |
| topojson-client | https://github.com/topojson/topojson-client | ISC |
| pandas, NumPy, SciPy, statsmodels, scikit-learn, SHAP, matplotlib | See `docs/DASHBOARD_AUDIT.md` for the versions used in each run | BSD / MIT |
| GeoPandas, Shapely, PyProj, pyogrio, libpysal, esda | Spatial analysis and Moran's I | BSD / MIT |
| Supabase | Accounts, saved alerts and forms | Apache 2.0 |

---

## 4. How to cite NWGS Grid

Use **Cite this repository** on GitHub, which reads `CITATION.cff`, and name the
weekly release your numbers came from. Every figure belongs to one dated run, so
a citation without the run identifier cannot be checked later.

```
Franklin, V. L. (2026). NWGS Grid™: National Wastewater Genomic Surveillance
Grid [Software and web dashboard]. Release <run_id>.
https://nwgsgrid.com
```

---

## 5. Keeping this current

Add a source here in the same change that introduces it, not afterwards. A
figure that reaches the site before its citation reaches this file is a figure
no reader can check, which is the failure this project exists to avoid.

`references.bib` carries the same literature in BibTeX for manuscript use.

# Changelog

All notable changes to the baseline template. Versions follow [Semantic Versioning](https://semver.org/).

## [3.0.0] — 2026-09-26

Threat modeling moves **inside the workbook**, and the project becomes **Excel only**. Many environments where
the baseline is used don't allow running Python, PowerShell or macros, so nothing in the process may depend on
executing code: everything is calculated by formulas in the same workbook, and the master template is maintained
directly in Excel.

### Breaking
- **Excel for Microsoft 365 required** (dynamic array functions: `FILTER`, `SORT`, `XLOOKUP`, `TEXTJOIN`,
  `VSTACK`, …). No macros — the file stays a plain `.xlsx`.
- **Removed**: `scripts/` (migrate, export, check, upgrade), `tests/`, `requirements.txt`, the CI workflow and
  the machine-readable `contract/` folder (replaced by the human-readable
  [`docs/workbook-structure.md`](docs/workbook-structure.md)). `CONTRACT_VERSION` removed from `_meta`.
- **The separate `app-threat-modeling` repository is abandoned** — it will not be created. All references to it
  are gone; the threat model is now the `Threat Model` sheet, always up to date, with nothing to run.

### Added
- **Views** (formulas only): `Threat Model`, `Controls to Verify`, `Backlog` (controls to fix + log sources to
  enable), `Detection Plan`, `Catalog Health` (consistency checks that replace the removed CI).
- **Central catalog** (Excel Tables, protected without password): `Threat Library`, `Threat-Control Map`,
  `Detections`, `Threat-Detection Map`, `Log Sources`, `TM Config` (risk scale and matrices).
- **Master Template / Custom Controls**: columns R–V — `Linked threats`, `Threat priority`, `Verify first?`,
  `Backlog priority`, `Linked threat IDs`.
- **Extended Characterization**: `ARCHETYPE_PRIMARY_ID`, `ARCHETYPE_SECONDARY_ID`, `IS_COTS`; the Security review
  triggers are now one hand-editable row each (the result cells `EXT_MISSING_COUNT`, `NEEDS_SECURITY_REVIEW`,
  `REVIEW_REASONS` stay where they were).
- **Starter catalog (all Draft, review before use)**: 17 threats covering every STRIDE category and the COTS
  cases, each linked to real ASVS requirements; 10 detections with Sigma rules in
  [`detections/sigma/`](detections/sigma/); 6 log sources; starter controls `TMX-VENDOR-001` (replaces
  `TMX-EXAMPLE-001`), `TMX-VENDOR-002`, `TMX-WAF-001`, `TMX-EGRESS-001`.
- **Example workbook**: [`examples/Example_COTS_Hosted_App.xlsx`](examples/Example_COTS_Hosted_App.xlsx)
  (fictional).
- **Docs**: [`docs/threat-modeling-method.md`](docs/threat-modeling-method.md) (method + maintainer guide +
  Excel 365 acceptance checklist), [`docs/workbook-structure.md`](docs/workbook-structure.md).

### Unchanged
- All v1/v2 named ranges, answer cells, computed cells and matrices; `Master Template` columns A–G remain a
  verbatim copy of OWASP ASVS 5.0.0. Applicable, Criticality and the Security review result compute exactly as in
  v2.

### Upgrading a v2 application copy
By hand, in Excel — see
[`docs/threat-modeling-method.md`](docs/threat-modeling-method.md#upgrading-an-application-copy).

## [2.0.0] — 2026-09-26

Threat modeling integration (first version: an external threat modeling engine reading the workbook through a
machine-readable contract — superseded by 3.0.0, where the engine, the contract, the scripts and the separate
repository were removed).

### Added
- **`Extended Characterization` sheet** — 53 additional questions (identification, business, sourcing model,
  architecture archetype, users, authentication, authorization, data flows, hosting, COTS/vendor, logging),
  with per-row `Applicable` / `Status` logic and a result block (`EXT_MISSING_COUNT`,
  `NEEDS_SECURITY_REVIEW`, `REVIEW_REASONS`) implementing the 7 Security review triggers.
- **`Archetypes` sheet** — reference list of 10 architecture archetypes.
- **Hidden `_lists` and `_meta` sheets** — dropdown sources and `CONTRACT_VERSION` / `TEMPLATE_VERSION` /
  `ASVS_VERSION`.
- **`Remediation Owner` column (Q)** on `Master Template` and `Custom Controls`
  (`Internal dev`, `Configuration`, `Vendor`, `Compensating`, `Risk acceptance`).
- **`Custom Controls`** extended from 20 to 200 rows; `CUSTOM-NN` / `TMX-<AREA>-NNN` ID convention;
  `TMX-EXAMPLE-001` worked example (vendor remote access through PAM).
- **`APP_NAME` named range** on `Characterization Form!D5` (it was the only v1 answer cell without one).
- **Machine-readable contract** in `contract/` (`characterization.yml`, `archetypes.yml`,
  `workbook-contract.yml`, generated `controls.json`).
- **Scripts**: `migrate_v2.py` (idempotent migration — the only way the template is changed),
  `export_contract.py`, `check_contract.py`, `upgrade_app_workbook.py` (moves a filled-in v1 app copy to v2);
  regression tests in `tests/`; CI workflow `contract.yml`.
- **Docs**: README "Related project" section and diagram; governance sections *Remediation Owner*,
  *Relationship with threat modeling* and *Security review triggers*; Confluence template sections *Threat
  Model* and *Detection Plan*, new Page Properties, Extended Characterization answers, and Remediation Owner /
  linked threats on each gap task.

### Changed
- Coverage matrix, *Architecture and design*: now covered by questionnaire-driven threat modeling plus
  Security review for flagged cases.
- `Instructions` sheet rewritten for the v2 process order (characterization → threat model → hardening
  assessment starting with the controls to verify first → threat model again).

### Unchanged
- All v1 named ranges, answer cells, computed cells and the criticality matrix.
- `Master Template` columns A–P (A–G remain a verbatim copy of OWASP ASVS 5.0.0), and every v1 formula;
  Applicable and Criticality compute exactly as in v1.


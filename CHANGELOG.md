# Changelog

All notable changes to the baseline template and its contract. Versions follow
[Semantic Versioning](https://semver.org/); the contract version and the template version move together
unless stated otherwise.

## [2.0.0] — 2026-09-26

Threat modeling integration. The baseline workbook becomes the **single intake and single control catalog**
for both the hardening record and the threat modeling engine,
[app-threat-modeling](https://github.com/Zzanoni/app-threat-modeling), so application teams fill in one
workbook per application instead of a second questionnaire, risk tier and control list.

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
- **Machine-readable contract** in [`contract/`](contract/) (`characterization.yml`, `archetypes.yml`,
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

### Unchanged (guaranteed by `migrate_v2.py` and the tests)
- All v1 named ranges, answer cells, computed cells and the criticality matrix.
- `Master Template` columns A–P (A–G remain a verbatim copy of OWASP ASVS 5.0.0), and every v1 formula;
  Applicable and Criticality compute exactly as in v1.

### Upgrading
Application copies filled in on v1: `python scripts/upgrade_app_workbook.py app_v1.xlsx app_v2.xlsx`, then
fill in the new `Extended Characterization` sheet.

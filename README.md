# Application Hardening Baseline

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](LICENSE)
[![OWASP ASVS 5.0.0](https://img.shields.io/badge/OWASP%20ASVS-5.0.0-blue.svg)](https://github.com/OWASP/ASVS)

A stack-agnostic application-hardening baseline, built on the full **OWASP ASVS 5.0.0** requirement
set (345 requirements, 17 chapters), designed to scale across 100+ applications without rewriting a
document for each one.

## Why this exists

Most "application hardening" checklists either duplicate what SAST/DAST/SCA already catch, or stay so
generic they never get enforced. This repo separates the two things that actually matter:

- **A governance baseline** — what "hardened" means at this company, and how each requirement maps to a
  real technical control (pipeline gate, scheduled scan, or periodic pentest) — see
  [`docs/hardening-baseline-governance.md`](docs/hardening-baseline-governance.md).
- **A master template** — the full ASVS 5.0.0 requirement set, pre-wired with formulas that filter it
  down to what's actually applicable to a given application, based on a short characterization form —
  see [`templates/ASVS_Master_Hardening_Template.xlsx`](templates/ASVS_Master_Hardening_Template.xlsx).

The result: onboarding a new application's hardening record is answering ~9 closed questions, not writing
a document from scratch.

## Repository structure

```
app-hardening-baseline/
├── README.md
├── docs/
│   ├── hardening-baseline-governance.md   # Why ASVS, baseline categories, coverage matrix, governance model
│   └── confluence-page-template.md        # Spec for the per-application Confluence page
└── templates/
    ├── ASVS_Master_Hardening_Template.xlsx  # The 345-requirement master checklist with applicability formulas
    └── confluence-page-template.xml         # Ready-to-import Confluence storage-format page template
```

## How the master template works

The workbook has three sheets:

| Sheet | Purpose |
| --- | --- |
| **Instructions** | Step-by-step usage guide and scope notes |
| **Characterization Form** | ~9 closed-vocabulary questions about the application (target ASVS level, exposes an API, uses OAuth/OIDC, session model, etc.) |
| **Master Template** | All 345 ASVS 5.0.0 requirements, each tagged with chapter, section, level, control type, and a live `Applicable?` formula |

Applicability is computed on **two axes at once**:

1. **Chapter gating** — each of the 17 ASVS chapters is either always applicable (e.g., Authentication,
   Access Control, Cryptography) or conditional on one characterization answer (e.g., Chapter V10 – OAuth
   and OIDC only applies if the app answers "uses OAuth/OIDC = Yes").
2. **Level gating** — a requirement is only in scope if its ASVS level (L1/L2/L3) is at or below the
   application's target level.

Both conditions are plain Excel formulas over named ranges, so changing an answer in the Characterization
Form re-filters the entire 345-row template instantly — no macros, no external tooling required to use it.

## Choosing the target ASVS level

ASVS levels are a risk-based scale, not a size-based one:

- **L1** — baseline, fully automatable, applies to every application.
- **L2** — standard for applications that handle sensitive data or meaningful transactions (recommended
  corporate default).
- **L3** — high-assurance applications (regulated financial data, health data, critical infrastructure).

Where a formal data-classification or business-impact tier already exists for an application, derive the
target level from that. Otherwise, use the characterization answers as a proxy: no sensitive data / no
API / no transactions → L1; sensitive data or API/SSO/multi-tenant exposure → L2; regulated financial data
or high-impact irreversible actions → L3.

## Applying this to a specific application

1. Copy `templates/ASVS_Master_Hardening_Template.xlsx`, renamed for the application.
2. Fill in the **Characterization Form** sheet.
3. Filter the **Master Template** sheet's `Applicable?` column to `Applicable`.
4. For each applicable requirement, record the real coverage status, the tool/evidence used, and any
   notes.
5. Publish the filtered result as the application's formal hardening record: a Confluence page per
   application, built from [`docs/confluence-page-template.md`](docs/confluence-page-template.md) (spec)
   and [`templates/confluence-page-template.xml`](templates/confluence-page-template.xml) (ready-to-import
   Confluence storage format).

## Source

Requirement text, chapter/section structure, and levels are taken verbatim from the official
[OWASP ASVS](https://github.com/OWASP/ASVS) v5.0.0 release. This repository adds the applicability
formulas, control-type mapping, and governance model on top of that source; it does not modify the
underlying ASVS requirement text.

## Roadmap

- [ ] Auto-suggested target ASVS level (currently a documented manual decision, based on the
      characterization answers).
- [ ] Section-level applicability refinement for chapters where a whole-chapter condition is too coarse.
- [ ] Optional: automate Confluence page creation/update from the filtered spreadsheet via the Confluence
      REST API (the current workflow is a one-time template setup, then manual per-application copy).

## Status

Internal baseline, actively maintained. Update the master template centrally — changes propagate to every
application's next copy/refresh, so per-application copies should not be edited to add new requirements
directly.

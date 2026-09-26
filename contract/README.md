# Workbook contract (v2.0.0)

This folder describes [`templates/ASVS_Master_Hardening_Template.xlsx`](../templates/ASVS_Master_Hardening_Template.xlsx)
in machine-readable form, so other tools can read an application's filled-in workbook without guessing
sheet names, cell positions or answer options.

## Who consumes it

The threat modeling engine, [**app-threat-modeling**](https://github.com/Zzanoni/app-threat-modeling),
vendors a copy of this folder under
[`vendor/baseline-contract/`](https://github.com/Zzanoni/app-threat-modeling/tree/main/vendor/baseline-contract),
pinned to a release tag of this repository. It reads the application's workbook through it: both
characterization sheets, Coverage Status and Remediation Owner of every control, and the control catalog.

## Files

| File | What it holds | Source of truth |
| --- | --- | --- |
| [`characterization.yml`](characterization.yml) | Every question of both characterization sheets: key (= named range of the answer cell), sheet, question, type, options, mandatory, `shown_when` condition, help, ASVS chapters it gates, consumers | **Source** for the `Extended Characterization` sheet (built from it by `scripts/migrate_v2.py`); v1 `Characterization Form` keys are verified against the sheet |
| [`archetypes.yml`](archetypes.yml) | Architecture archetypes: ID, name (shown in the dropdown), description | **Source** for the `Archetypes` sheet and the archetype dropdowns |
| [`workbook-contract.yml`](workbook-contract.yml) | Versions; sheet names, order and visibility; header rows and column headers; computed named ranges; vocabularies; Custom Controls ID patterns; Security review triggers | Hand-written, verified by `scripts/check_contract.py` |
| [`controls.json`](controls.json) | Control catalog: every ASVS requirement and custom control with ID, chapter/category, section, level, requirement text, applicability condition and formula, requirement impact | **Generated** from the workbook by `scripts/export_contract.py` — never edit by hand |

`check_contract.py` runs in CI on every pull request and fails if the workbook and these files disagree in
any way, including formula errors after a LibreOffice recalculation.

## Reading rules for consumers

- Locate answers by **named range** (the key), and table rows by the **ID column** (`ASVS ID`,
  `Control ID`) — never by fixed row numbers.
- Answers are exact strings from `options`; "Don't know" uses a straight apostrophe.
- The answer of a key whose row is **not applicable** (its `shown_when` is false) counts as **blank** when
  evaluating any condition — a stale answer left in a hidden row must be ignored.
- Ignore Custom Controls rows listed in `example_control_ids` (`EXAMPLE-01`, `TMX-EXAMPLE-001`).
- Check `CONTRACT_VERSION` (named range on the hidden `_meta` sheet) before reading an application's
  workbook; refuse or upgrade (with `scripts/upgrade_app_workbook.py`) on a major-version mismatch.

## Changing the contract

**Any change to this folder is a breaking change for app-threat-modeling.** When changing it:

1. Change the workbook only through a migration script (`scripts/migrate_*.py`), then run
   `scripts/export_contract.py` and `scripts/check_contract.py`.
2. Bump `CONTRACT_VERSION` (in `workbook-contract.yml` and the other YAML files; the migration writes it
   into `_meta`) — major for anything that breaks an existing reader, minor for additions.
3. Add a `CHANGELOG.md` entry and, after merging, **tag a release** (e.g. `v2.1.0`); the threat engine
   pins the contract by tag.
4. **Open an issue or PR in [app-threat-modeling](https://github.com/Zzanoni/app-threat-modeling)** to
   update its vendored copy. Security review triggers must stay equal to its
   `catalog/config/review_triggers.yml`.

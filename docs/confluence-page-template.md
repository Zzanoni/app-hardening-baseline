# Confluence Page Template — Per-Application Hardening Record

This document specifies the Confluence page structure used to formalize the hardening record for a
single application, populated manually from the filtered `Master Template` spreadsheet
(see [`../templates/ASVS_Master_Hardening_Template.xlsx`](../templates/ASVS_Master_Hardening_Template.xlsx))
and, for the Threat Model and Detection Plan sections, from the output of the threat modeling engine
([app-threat-modeling](https://github.com/Zzanoni/app-threat-modeling)).

A ready-to-import storage-format file implementing this structure is provided at
[`confluence-page-template.xml`](../templates/confluence-page-template.xml).

## One-time setup: turn this into a reusable Confluence template

1. In the target Space, go to **Space settings → Content Tools → Templates → Create new template**.
2. Give it a name, e.g. `Application Hardening Record`.
3. Switch the editor to source/storage mode (Confluence Cloud: use the **Templates REST API**,
   `POST /wiki/rest/api/template`, with the body taken from `confluence-page-template.xml` — this is a
   one-time setup step, not per-application automation) and paste the provided XHTML.
4. Save the template. From now on, creating a new application record is **Create → From template →
   Application Hardening Record**, not writing a page from scratch.

## Page structure

### 1. Header — Page Properties

A **Page Properties** macro (native Confluence macro) holding the application's identity and scope, so
it can later be aggregated with a **Page Properties Report** macro across all application pages in the
space (e.g., a space-wide dashboard of hardening status).

| Field | Source |
| --- | --- |
| Application Name | Characterization Form → `APP_NAME` |
| Target ASVS Level | Characterization Form → `TARGET_LEVEL` |
| App Risk Tier | Characterization Form → `APP_RISK_TIER` (computed), as a Status macro (same palette as Criticality) |
| Sourcing Model | Extended Characterization → `SOURCING_MODEL` |
| Architecture Pattern(s) | Extended Characterization → `ARCHETYPE_PRIMARY` (+ `ARCHETYPE_SECONDARY`, if any) |
| Security Review Required | Extended Characterization → `NEEDS_SECURITY_REVIEW` (+ `REVIEW_REASONS` when Yes) |
| Owner / Team | Filled in manually (or Extended Characterization → `BUSINESS_OWNER` / `TECHNICAL_OWNER`) |
| Last Reviewed | Filled in manually (date) |
| Template Version | Instructions sheet / `_meta` → `TEMPLATE_VERSION` (e.g. 2.0.0) |
| Overall Status | One of: Not started / In progress / Complete — filled in manually |

### 2. Table of Contents

A native **Table of Contents** macro, since the checklist section below is long once expanded.

### 3. Application Characterization

A table mirroring the `Characterization Form` sheet's questions and answers, so a reader does not need
to open the spreadsheet to understand why certain ASVS chapters were excluded.

Below it, an **Expand** macro ("Extended Characterization — answers") with the `Extended
Characterization` sheet's questions and answers, grouped by the sheet's sections (A–M), plus its result
block (Security review required, review reasons). Rows the sheet marks as not applicable are recorded as
N/A.

### 4. Coverage Summary

A small table with a **Status** macro per row, giving the reviewer an at-a-glance read before scrolling
into the full checklist:

| Metric | Value |
| --- | --- |
| Total applicable requirements | *(count of `Applicable` rows for this app)* |
| 🟢 Full coverage | *(count)* |
| 🟡 Partial coverage | *(count)* |
| 🔴 Gap | *(count)* |
| ⚪ Not assessed | *(count)* |
| 🔴 Critical items | *(count of applicable rows with Criticality = Critical)* |
| 🟠 High items | *(count of applicable rows with Criticality = High)* |

The Critical/High counts are a read of the `Criticality` column (Master Template column P), not of
Coverage Status — a Critical item can still be Full coverage; this row exists so a reviewer can see at
a glance how many high-priority items this application carries, independent of how well they're
currently covered.

### 5. Hardening Checklist, grouped by ASVS chapter

One **Expand** macro per ASVS chapter that has at least one applicable requirement (collapsed by
default, to keep the page navigable — an application in scope for most chapters can easily have 150–250
rows). Inside each Expand, a table with columns:

`ASVS ID | Requirement | Level | Criticality | Control Type | Coverage Status | Tool / Evidence | Notes`

`Criticality` uses the Status macro (Red = Critical, Purple = High, Yellow = Medium, Grey = Low) — the
closest mapping onto Confluence's fixed status-macro palette (Grey/Red/Yellow/Green/Blue/Purple, which
has no orange) to the spreadsheet's own conditional formatting on column P (which does use an orange
fill for High, being unconstrained by Confluence's palette). See
[`hardening-baseline-governance.md`](hardening-baseline-governance.md#risk-tiering--criticality) for
how Criticality is computed.

`Coverage Status` uses the Status macro (Green = Full coverage, Yellow = Partial coverage, Red = Gap,
Grey = Not assessed), matching the spreadsheet's conditional formatting colors.

Only chapters and rows marked `Applicable` in the filtered spreadsheet are copied in — `N/A` rows are
left out of the page entirely (that exclusion is itself recorded in section 3, via the characterization
answers).

### 6. Company-Specific Controls

One additional **Expand** macro, kept separate from the ASVS-chapter Expand blocks in section 5, for
rows copied from the spreadsheet's `Custom Controls` sheet (organization-specific requirements that
aren't part of ASVS — see [`hardening-baseline-governance.md`](hardening-baseline-governance.md#extending-the-baseline-beyond-asvs)).
Same table columns as section 5, with `Control ID` in place of `ASVS ID`. Omit this block entirely if
the application's `Custom Controls` sheet has no applicable rows.

### 7. Threat Model

*Generated by the threat modeling engine — see [https://github.com/Zzanoni/app-threat-modeling](https://github.com/Zzanoni/app-threat-modeling).* The application team
does not write this section by hand: it is copied from the engine's output for this application.

A table, one row per threat:

`Threat ID | STRIDE | Threat | Risk | Mitigation status | Linked controls`

- `Risk` uses the Status macro with the same palette as Criticality (Red = Critical, Purple = High,
  Yellow = Medium, Grey = Low).
- `Mitigation status` uses the Status macro: Green = Mitigated, Yellow = Partially mitigated,
  Red = Unmitigated.
- `Linked controls` lists the ASVS IDs and Control IDs (sections 5 and 6) that mitigate the threat.

Placeholder text in the template: "Populated from the threat modeling engine output."

### 8. Detection Plan

*Generated by the threat modeling engine — see [https://github.com/Zzanoni/app-threat-modeling](https://github.com/Zzanoni/app-threat-modeling).* Detections proposed
for the SOC, complementing the preventive controls above. The plan is SIEM-agnostic: it names the events
and log sources needed, not a product's query language.

`Detection ID | Detects | Required log sources | Log sources available? | Status`

`Status` is Proposed (Grey) or Deployed by SOC (Green).

### 9. Gaps and Action Items

A **Task List** macro listing every row with Coverage Status = Gap, from both section 5 and section 6,
each as an assignable, due-dated task. Each task also states the row's **Remediation Owner** (Internal
dev / Configuration / Vendor / Compensating / Risk acceptance — see
[`hardening-baseline-governance.md`](hardening-baseline-governance.md#remediation-owner)) and its **Linked
threats** (Threat IDs from section 7). Tasks are ordered by Criticality, then by the highest risk among
their linked threats. This is the section a team lead actually works from day to day — the full checklist
above is the audit record, this section is the backlog.

### 10. Review History

A simple table logging each review pass: `Date | Reviewer | Changes`. Append a row every time the page
is revisited, rather than editing history away.

## Workflow per application

1. Create the page from the template (`Create → From template → Application Hardening Record`).
2. Fill in section 1 (Page Properties) and section 3 (Characterization, including the Extended
   Characterization expand block) from the spreadsheet's two characterization sheets.
3. Run the threat model on the workbook (characterization-only mode) and copy its threats into section 7
   and its detections into section 8. Its "controls to verify first" list tells you where to start step 4.
4. Filter the spreadsheet's `Master Template` sheet to `Applicable`, and for each ASVS chapter present,
   copy its rows into the matching Expand block in section 5 (create one Expand block per chapter that
   has applicable rows; delete unused chapter blocks from the template).
5. If the `Custom Controls` sheet has any applicable rows, copy them into section 6; otherwise delete
   that block.
6. Fill in section 4 (Coverage Summary) counts once sections 5 and 6 are complete.
7. Re-run the threat model with the completed workbook (full mode) and update the Mitigation status and
   Linked controls in section 7.
8. Copy every Gap row into section 9 as a task, with its Remediation Owner, linked threats, an owner and a
   due date, ordered by Criticality and then by linked-threat risk.
9. Log the pass in section 10.

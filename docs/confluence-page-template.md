# Confluence Page Template — Per-Application Hardening Record

This document specifies the Confluence page structure used to formalize the hardening record for a
single application, populated manually from the application's copy of the workbook
([`../templates/ASVS_Master_Hardening_Template.xlsx`](../templates/ASVS_Master_Hardening_Template.xlsx)). Every
section maps to a sheet of that workbook; the Threat Model, Detection Plan and Gaps sections are copied from the
workbook's `Threat Model`, `Detection Plan` and `Backlog` sheets, which calculate themselves.

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
| Template Version | Instructions sheet / `_meta` → `TEMPLATE_VERSION` (e.g. 3.0.0) |
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

The Critical/High counts are a read of the `Criticality` column (ASVS Checklist column P), not of
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

*Copied from the workbook's `Threat Model` sheet* — laid out with the same columns so it can be pasted
directly. The application team doesn't write threats by hand: the sheet computes them from the characterization
answers and the central threat catalog (see [`threat-modeling-method.md`](threat-modeling-method.md)).

Above the table, one line with the threat model mode (*Characterization-only* or *Full*) and the number of
applicable threats. Then one row per applicable threat:

`Threat ID | STRIDE | Threat | Risk | Mitigation status | Controls (Full / Partial / Gap / Not assessed) | Detections | Description`

- `Risk` uses the Status macro with the same palette as Criticality (Red = Critical, Purple = High,
  Yellow = Medium, Grey = Low).
- `Mitigation status` uses the Status macro: Green = Mitigated, Yellow = Partially mitigated,
  Red = Unmitigated, Grey = Not verified / No applicable controls.

### 8. Detection Plan

*Copied from the workbook's `Detection Plan` sheet.* Detections the SOC should deploy for this application,
complementing the preventive controls above. The rules are SIEM-agnostic Sigma files in
[`../detections/sigma/`](../detections/sigma/).

`Detection ID | Title | Linked threats | Highest threat risk | Required log sources | Missing log sources | Deployment status | Sigma rule`

`Deployment status` uses the Status macro: Grey = Not requested, Blue = Requested to SOC, Green = Deployed,
Red = Rejected. It is recorded per application in the `Deployment status` column of the workbook's
`Detections` sheet.

### 9. Gaps and Action Items

*Copied from the workbook's `Backlog` sheet*, in the order it shows. Two **Task List** macros:

1. **Controls to fix** — one task per row of the backlog's left block (Coverage Status Gap or Partial coverage,
   from both `ASVS Checklist` and `Custom Controls`), stating its coverage, **Backlog priority** (the higher of
   Criticality and Threat priority), **Remediation Owner** (Internal dev / Configuration / Vendor / Compensating /
   Risk acceptance — see
   [`hardening-baseline-governance.md`](hardening-baseline-governance.md#remediation-owner)) and **linked
   threats**, plus an owner and a due date.
2. **Log sources to enable** — one task per row of the backlog's right block: log sources that relevant
   detections need but aren't available yet.

This is the section a team lead actually works from day to day — the full checklist above is the audit record,
this section is the backlog.

### 10. Review History

A simple table logging each review pass: `Date | Reviewer | Changes`. Append a row every time the page
is revisited, rather than editing history away.

## Workflow per application

1. Create the page from the template (`Create → From template → Application Hardening Record`).
2. Fill in section 1 (Page Properties) and section 3 (Characterization, including the Extended
   Characterization expand block) from the workbook's two characterization sheets.
3. Copy the workbook's `Threat Model` sheet into section 7 and its `Detection Plan` sheet into section 8. Right
   after the characterization they are already filled in (mode *Characterization-only*); the workbook's
   `Controls to Verify` sheet tells you which checklist rows to assess first.
4. Filter the workbook's `ASVS Checklist` sheet to `Applicable`, and for each ASVS chapter present, copy its
   rows into the matching Expand block in section 5 (create one Expand block per chapter that has applicable
   rows; delete unused chapter blocks from the template).
5. If the `Custom Controls` sheet has any applicable rows, copy them into section 6; otherwise delete
   that block.
6. Fill in section 4 (Coverage Summary) counts once sections 5 and 6 are complete.
7. Once the assessment is done (mode *Full*), refresh sections 7 and 8 from the workbook — mitigation statuses
   and relevant detections change as controls are assessed.
8. Copy the workbook's `Backlog` sheet into section 9 as tasks, with an owner and a due date for each.
9. Log the pass in section 10.

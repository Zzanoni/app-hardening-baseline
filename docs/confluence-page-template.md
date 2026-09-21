# Confluence Page Template — Per-Application Hardening Record

This document specifies the Confluence page structure used to formalize the hardening record for a
single application, populated manually from the filtered `Master Template` spreadsheet
(see [`../templates/ASVS_Master_Hardening_Template.xlsx`](../templates/ASVS_Master_Hardening_Template.xlsx)).

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
| Owner / Team | Filled in manually |
| Last Reviewed | Filled in manually (date) |
| Overall Status | One of: Not started / In progress / Complete — filled in manually |

### 2. Table of Contents

A native **Table of Contents** macro, since the checklist section below is long once expanded.

### 3. Application Characterization

A table mirroring the `Characterization Form` sheet's questions and answers, so a reader does not need
to open the spreadsheet to understand why certain ASVS chapters were excluded.

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

### 6. Gaps and Action Items

A **Task List** macro listing every row with Coverage Status = Gap, each as an assignable, due-dated
task, ordered with Critical and High criticality items first. This is the section a team lead actually
works from day to day — the full checklist above is the audit record, this section is the backlog.

### 7. Review History

A simple table logging each review pass: `Date | Reviewer | Changes`. Append a row every time the page
is revisited, rather than editing history away.

## Workflow per application

1. Create the page from the template (`Create → From template → Application Hardening Record`).
2. Fill in section 1 (Page Properties) and section 3 (Characterization) from the spreadsheet's
   `Characterization Form` sheet.
3. Filter the spreadsheet's `Master Template` sheet to `Applicable`, and for each ASVS chapter present,
   copy its rows into the matching Expand block in section 5 (create one Expand block per chapter that
   has applicable rows; delete unused chapter blocks from the template).
4. Fill in section 4 (Coverage Summary) counts once section 5 is complete.
5. Copy every Gap row into section 6 as a task, with an owner and due date.
6. Log the pass in section 7.

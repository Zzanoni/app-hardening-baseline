# Threat Modeling Method

How the threat model inside the workbook works, how to maintain its catalog, and how to accept a new template
version. Everything happens in Excel for Microsoft 365 — no scripts, no macros. Sheet and column details are in
[`workbook-structure.md`](workbook-structure.md).

## The idea in plain terms

A threat model answers four questions about an application: *what could go wrong, how bad would it be, what
protects against it, and how would we notice it happening?* Doing that from a blank page for every application
doesn't scale, and two people rarely produce the same result. This workbook does it from a **central catalog**:
Security describes the realistic threats once, with the condition under which each one applies, the checklist
items that protect against it and the detections that spot it. The application team only answers the
characterization questions; the workbook picks the threats that apply and keeps them up to date as the checklist
is filled in. The same answers always give the same threats.

## STRIDE

Threats are grouped with STRIDE, six kinds of attack:

| Letter | Category | In plain terms | Example in the catalog |
| --- | --- | --- | --- |
| S | Spoofing | Pretending to be someone or something else | Credential stuffing on the public login |
| T | Tampering | Changing data or code without permission | Tampering with batch exchange files |
| R | Repudiation | Doing something and being able to deny it | Administrative actions that can't be attributed |
| I | Information disclosure | Reading data one shouldn't | Broken object-level authorization |
| D | Denial of service | Making the application unavailable | Message flooding or poison messages |
| E | Elevation of privilege | Gaining more rights than granted | Abuse of vendor remote access |

## When a threat applies

A threat applies to the application when **both** hold:

1. **Archetype match** — its `Archetypes` column is `All`, or lists the ID of the application's primary or
   secondary archetype (`ARCHETYPE_PRIMARY_ID`, `ARCHETYPE_SECONDARY_ID`, from the `Archetypes` sheet).
2. **Applicability formula** — a live formula over the characterization answers returns TRUE, e.g.
   `=AND(EXPOSURE="Public internet",AUTH_LOCAL_CREDENTIALS="Yes")`. `IS_COTS` is available as a shortcut for
   "COTS, COTS with customizations or vendor appliance".

An answer on a question that doesn't apply (a greyed-out row) should not trigger a threat; conditions on vendor
questions therefore start with `IS_COTS`, and conditions on a follow-up question include its parent (e.g.
`AND(ADMIN_INTERFACE="Yes",ADMIN_INTERFACE_REACH="Internet")`).

## How risky it is

1. **Base risk** — the threat's own *Likelihood* × *Impact* (Low / Medium / High), from `BASE_RISK_MATRIX` on
   `TM Config`.
2. **Risk** — base risk crossed with the application's Risk Tier (`APP_RISK_TIER`, the same tier that drives
   checklist Criticality), from `FINAL_RISK_MATRIX`.

Initial matrices (a proposal — calibrate them during the pilot):

| Impact \ Likelihood | Low | Medium | High |
| --- | --- | --- | --- |
| Low | Low | Low | Medium |
| Medium | Low | Medium | High |
| High | Medium | High | Critical |

| Base risk \ Risk Tier | Low | Medium | High | Critical |
| --- | --- | --- | --- | --- |
| Low | Low | Low | Low | Medium |
| Medium | Low | Medium | Medium | High |
| High | Medium | High | High | Critical |
| Critical | High | High | Critical | Critical |

## Is it mitigated?

`Threat-Control Map` links each threat to the checklist rows (`ASVS Checklist` ASVS IDs or `Custom Controls` IDs)
that protect against it. The threat's **mitigation status** comes from their Coverage Status, counting only the
controls that apply to this application:

| Status | When |
| --- | --- |
| No controls mapped | The catalog links no control to the threat (also flagged by `Catalog Health`) |
| No applicable controls | Linked controls exist, but none applies to this application |
| Not verified | No applicable linked control has been assessed yet |
| Mitigated | Every applicable linked control is Full coverage |
| Partially mitigated | At least one is Full or Partial coverage |
| Unmitigated | Otherwise (assessed, and only Gaps) |

A warning (`Control N/A for applicable threat`) appears on the map when a threat applies but one of its controls,
within the application's target level, doesn't — usually a sign that a characterization answer is wrong.

## Two phases

- **Characterization-only** — right after the two characterization sheets are answered, before any control is
  assessed. The workbook already shows the applicable threats and their risk, the relevant detections, and
  **Controls to Verify**: applicable controls linked to applicable threats, sorted by the highest threat risk
  they mitigate, then by criticality. Assessing those first is the fastest way to a meaningful threat model.
- **Full** — as soon as any linked control has a Coverage Status other than Not assessed. Threats show their
  mitigation status and the **Backlog** lists gaps by *Backlog priority* (the higher of Criticality and Threat
  priority), with each gap's Remediation Owner and linked threats.

`TM_MODE` (on `Controls to Verify`) says which phase the workbook is in. Nothing needs to be run between phases.

## Detections and log sources

Preventive controls are complemented by detections the SOC deploys. `Threat-Detection Map` links threats to
detections; `Detections` lists each detection with a **Sigma rule** (a vendor-neutral rule format the SOC converts
to its own SIEM — files in [`../detections/sigma/`](../detections/sigma/)) and the **log sources** it needs.
`Log Sources` states, from the characterization answers, whether each log source is available (`Yes` / `No` /
`Unknown`).

A detection is **relevant** to the application when at least one linked threat applies and is not Mitigated. The
`Detection Plan` sheet lists relevant detections, the log sources they miss, and their **Deployment status**
(`Not requested`, `Requested to SOC`, `Deployed`, `Rejected`) — recorded per application on the `Detections`
sheet, where it stays on the detection's own row. Log sources that relevant detections need but that aren't
available appear under "Log sources to enable" in the `Backlog`.

The SOC owns deployment and tuning. The detection plan never replaces preventive controls.

## Security review

Some applications can't be judged by the catalog alone (no archetype fits, SaaS, unknown answers, Critical tier,
permanent or unknown vendor access, unsupported product). `NEEDS_SECURITY_REVIEW` on `Extended Characterization`
flags them; see [`hardening-baseline-governance.md`](hardening-baseline-governance.md#security-review-triggers).
The threat model is still computed for them — the review adds to it.

## Maintainer guide (Excel only)

The catalog lives in the **master template** only. Catalog sheets are protected without password:
*Review → Unprotect Sheet* before editing, *Protect Sheet* afterwards. Catalog sheets are Excel Tables — add a row
by typing directly below the last row (or *Tab* in the last cell): the grey calculated columns fill in by
themselves.

**Every change ends the same way:**

1. `Catalog Health` shows **OK** (the self-check line on `Instructions` shows it too).
2. Increase `TEMPLATE_VERSION` on the hidden `_meta` sheet (*right-click a tab → Unhide*).
3. Add an entry to [`../CHANGELOG.md`](../CHANGELOG.md).

**Add a threat** — on `Threat Library`, add a row: next free `TM-<S/T/R/I/D/E>-NNN` ID, STRIDE category, plain
title and description, `All` or the relevant `ARCH-*` IDs, the condition in words, the applicability formula
(e.g. `=MESSAGING="Yes"`), references (CAPEC / ATT&CK), Likelihood, Impact, `Review status = Draft`. Then link it
to controls and detections (below). `Catalog Health` flags it until it has at least one control and one detection
— or, if no sensible detection exists, write `No detection: <reason>` in Notes.

**Link controls** — on `Threat-Control Map`, one row per control: Threat ID, Control ID (an ASVS ID from
`ASVS Checklist` — read the requirement text, never guess — or a `Custom Controls` ID), the default Remediation
Owner, and one line on how it mitigates. `Control source` must not say `NOT FOUND`.

**Add a `TMX-*` control** — when no ASVS requirement expresses the protection (typically vendor, compensating or
infrastructure controls): on `Custom Controls`, fill the next empty row with a `TMX-<AREA>-NNN` ID, category,
level, requirement text, condition in words and in column G (e.g. `=IS_COTS`), control type, nature,
verification stage and Requirement Impact. Then link it on `Threat-Control Map`.

**Add a detection** — write the Sigma rule in `detections/sigma/det-<area>-<nnn>-<short-name>.yml` (header comment
with the Detection ID, `status: experimental`), then on `Detections` add a row: `DET-<AREA>-NNN`, title, what it
detects, the file path, required log source IDs (`; `-separated), `Deployment status = Not requested`,
`Review status = Draft`. Link it to threats on `Threat-Detection Map`.

**Add a log source** — on `Log Sources`: `LOG-*` ID, name, description, condition in words, and an `Available`
formula returning `Yes`, `No` or `Unknown` from the answers, e.g.
`=IF(HOST_EDR="Yes","Yes",IF(HOST_EDR="No","No","Unknown"))`. If no question covers it yet, use `="Unknown"` and
propose a new characterization question.

**Change the risk matrices** — edit the yellow cells on `TM Config`. Keep the labels (Low / Medium / High /
Critical) unchanged.

**Approve content** — once a threat, its links and its detection have been reviewed, set `Review status` to
`Approved` on `Threat Library` / `Detections`. The starter catalog ships as `Draft`.

**Never** rename sheets, table names, column headers, keys or named ranges; never add rows to `ASVS Checklist`.

## Upgrading an application copy

Application copies are not upgraded automatically. To move a filled-in copy to a new template version, open both
files and copy **values** (*Paste Special → Values*), matching by key or ID, never by row position:

1. **Characterization answers** — column D of `Characterization Form` and `Extended Characterization`, matched by
   the key in column A.
2. **Control assessments** — columns L (Coverage Status), M (Tool / Evidence), N (Notes) and Q (Remediation
   Owner) of `ASVS Checklist` and `Custom Controls`, matched by the ID in column A. For `Custom Controls` rows the
   application added itself, copy the whole row (A–G, I–O, Q) into an empty row.
3. **Detection deployment status** — column `Deployment status` of `Detections`, matched by Detection ID.

Then check `Extended Characterization` for new questions (Status `Missing`) and `Catalog Health`.

## Excel 365 acceptance checklist

Run once on the master template after any structural change (and on first adoption):

- [ ] Open the template: no `#NAME?`, no `@` in front of `FILTER` / `SORT` formulas, and the views (`Threat Model`,
      `Controls to Verify`, `Backlog`, `Detection Plan`) spill correctly. `Catalog Health` shows OK.
- [ ] Set `EXPOSURE` to `Public internet` and `AUTH_LOCAL_CREDENTIALS` to `Yes` → `TM-S-001` (credential stuffing)
      appears in `Threat Model`.
- [ ] Set one of its linked controls (e.g. `V6.3.1`) to `Gap` → the threat becomes Unmitigated / Partially
      mitigated, and the row appears in `Backlog` with a Backlog priority.
- [ ] Set `LOG_AUTH_EVENTS` to `No` → `LOG-APP-AUTH` appears under "Log sources to enable".
- [ ] Add a new row to `Threat Library` → the calculated columns fill in; `Catalog Health` flags it until it has
      controls and detections.
- [ ] Change a Deployment status on `Detections`, then change answers so `Detection Plan` re-sorts → each
      detection keeps its own status.

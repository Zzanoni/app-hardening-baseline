# Workbook Structure — reference (template v3.0.0)

Human-readable map of [`templates/ASVS_Master_Hardening_Template.xlsx`](../templates/ASVS_Master_Hardening_Template.xlsx):
every sheet, who edits it, its columns, every named range, the closed vocabularies and the ID conventions. Use it
when maintaining the master template or when reading a filled-in copy.

**Stability rule.** Sheet names, keys, named ranges, table names and column headers are what the formulas (and any
reader) rely on. Never rename or remove them; add new ones instead. Row numbers are not stable — locate answers by
**named range** and controls/threats by their **ID column**.

Requires Excel for Microsoft 365. No macros.

## Sheets

| # | Sheet | Tab | Who edits | Purpose |
| --- | --- | --- | --- | --- |
| 1 | `Instructions` | — | — | User guide; top line shows the Catalog Health self-check. |
| 2 | `Characterization Form` | — | App team | Core questions (yellow), Application Risk Tier, criticality matrix. |
| 3 | `Extended Characterization` | — | App team | 53 more questions, Applicable/Status per row, result block, review triggers. |
| 4 | `Threat Model` | blue | — (view) | Applicable threats with risk and mitigation status; summary block. |
| 5 | `Controls to Verify` | blue | — (view) | Checklist rows to assess first; `TM_MODE`. |
| 6 | `Master Template` | — | App team (columns L, M, N, Q) | OWASP ASVS 5.0.0 checklist (345 rows). |
| 7 | `Custom Controls` | — | App team (status) / Security (rows) | Organization and threat-modeling controls (200 rows). |
| 8 | `Backlog` | blue | — (view) | Controls to fix, log sources to enable. |
| 9 | `Detection Plan` | blue | — (view) | Detections relevant to the application. |
| 10 | `Threat Library` | purple | Security (master only) | Threat catalog (table `tblThreats`). |
| 11 | `Threat-Control Map` | purple | Security (master only) | Threat ↔ control links (table `tblThreatControls`). |
| 12 | `Detections` | purple | Security (master only); **Deployment status** per application | Detection catalog (table `tblDetections`). |
| 13 | `Threat-Detection Map` | purple | Security (master only) | Threat ↔ detection links (table `tblThreatDetections`). |
| 14 | `Log Sources` | purple | Security (master only) | Log source catalog (table `tblLogSources`). |
| 15 | `TM Config` | purple | Security (master only) | Risk scale, risk matrices, Sigma base URL. |
| 16 | `Catalog Health` | blue | — (view) | Consistency checks; `CATALOG_HEALTH`. |
| 17 | `Archetypes` | — | Security | Architecture archetypes (ID, name, description). |
| 18 | `_lists` | hidden | Security | Dropdown option lists (`LIST_*`). |
| 19 | `_meta` | hidden | Security | `TEMPLATE_VERSION`, `ASVS_VERSION`. |

Purple (catalog) sheets are protected **without password** — only to prevent accidental edits. To maintain them:
*Review → Unprotect Sheet*, edit, then protect again. In the catalog tables, yellow columns are inputs, grey
columns are calculated (they extend automatically to new table rows).

Colors: yellow = input; grey = calculated; blue tab = view (formulas only); purple tab = central catalog.

## Characterization sheets

`Characterization Form` — header row 4: `Key (internal use) | Question | Possible options | Answer | Notes / Help`.
Answers in column D (rows 5–15), each a named range equal to its key.

`Extended Characterization` — header row 4:
`Key | Question | Possible options | Answer | Notes / Help | Mandatory | Shown when | Applicable | Status`.
Section header rows (A–M) separate the questions; each answer in column D is a named range equal to its key.

- **Applicable** — `Applicable` / `N/A`, from the row's "Shown when" condition. An answer on a row that is not
  applicable counts as blank in every other condition.
- **Status** — `N/A` (not applicable), `Missing` (mandatory, blank), `Optional` (optional, blank), `Review`
  (mandatory, answered `Don't know`), `OK`.
- **Result block** (rows 72–77): `EXT_MISSING_COUNT`, `NEEDS_SECURITY_REVIEW`, `REVIEW_REASONS`,
  `ARCHETYPE_PRIMARY_ID`, `ARCHETYPE_SECONDARY_ID`, `IS_COTS`.
- **Security review triggers** (rows 79–86): one row per trigger — ID (A), reason (B), Yes/No formula (D),
  cumulative reasons helper (E). `NEEDS_SECURITY_REVIEW` = Yes when any trigger row says Yes.

## Control sheets (`Master Template`, `Custom Controls`)

Header row 4. `Master Template` rows 5–349; `Custom Controls` rows 5–204 (pre-filled formulas; a row is ignored
while its Control ID is blank).

| Col | Header | Input? | Content |
| --- | --- | --- | --- |
| A | ASVS ID / Control ID | ASVS: no — Custom: yes | Requirement ID |
| B–C | Chapter, Section / Category, Sub-category | ASVS: no — Custom: yes | |
| D | Level | ASVS: no — Custom: yes | 1–3 |
| E | Requirement | ASVS: no — Custom: yes | Requirement text |
| F | Applicability Condition | ASVS: no — Custom: yes | Human-readable condition |
| G | Applicability Formula | ASVS: hidden helper — Custom: live formula | `=TRUE()` = always |
| H | Applicable? | — | `Applicable` / `N/A` |
| I–K | Control Type, Nature, Verification Stage | ASVS: no — Custom: yes | |
| L | Coverage Status | **yes** | Coverage Status vocabulary |
| M | Tool / Evidence | **yes** | |
| N | Notes | **yes** | |
| O | Requirement Impact | ASVS: no — Custom: yes | Low / Medium / High |
| P | Criticality | — | Requirement Impact × `APP_RISK_TIER` |
| Q | Remediation Owner | **yes** (Gap / Partial rows) | Remediation Owner vocabulary |
| R | Linked threats | — | Number of applicable threats linked to the control |
| S | Threat priority | — | Highest risk among those threats |
| T | Verify first? | — | `Yes` = applicable, not assessed, linked to an applicable threat |
| U | Backlog priority | — | Gap / Partial only: higher of P and S |
| V | Linked threat IDs | — | IDs of those threats |

`Master Template` columns A–G are a verbatim copy of OWASP ASVS 5.0.0 — never edit them, never add rows.

## Catalog tables

Header row 4 on each sheet; table names are used in formulas.

**`tblThreats`** (`Threat Library`) — inputs: `Threat ID`, `STRIDE`, `Title`, `Description`, `Archetypes` (`All` or
`; `-separated `ARCH-*` IDs), `Applicability condition`, `Applicability formula` (live formula per row returning
TRUE/FALSE), `References`, `Likelihood`, `Impact`, `Review status`, `Notes`. Calculated: `Archetype match`,
`Applies` (`Applies` / `N/A` / `Error`), `Base risk`, `Risk`, `Risk score` (1–4, 0 = not applicable),
`Controls linked`, `Full`, `Partial`, `Gap`, `Not assessed`, `NA controls`, `Mitigation status`,
`Detections linked`, `Archetypes valid`.

**`tblThreatControls`** (`Threat-Control Map`) — inputs: `Threat ID`, `Control ID`, `Default owner`,
`How it mitigates`. Calculated: `Control source` (`ASVS` / `Custom` / `NOT FOUND`), `Control applicable`,
`Coverage status` (`N/A` when the control doesn't apply; blank counts as `Not assessed`), `Effective owner`
(column Q of the control, else Default owner), `Threat applies`, `Threat risk`, `Threat risk score`, `Warning`
(`Control N/A for applicable threat` when a threat applies but a control within the target level doesn't — the
characterization is probably wrong), helpers `Source row`, `Raw coverage`, `Raw level`, `Raw owner`.

**`tblDetections`** (`Detections`) — inputs: `Detection ID`, `Title`, `What it detects`, `Sigma rule` (path in this
repository, e.g. `detections/sigma/det-auth-001-login-failure-spike.yml`, hyperlinked), `Required log sources`
(`; `-separated `LOG-*` IDs), **`Deployment status`** (per application — the only column editable while the sheet
is protected), `Review status`, `Notes`. Calculated: `Missing log sources`, `Linked threats` (applicable ones),
`Relevant` (Yes when a linked threat applies and is not Mitigated), `Highest threat risk`, `Risk score`,
`Log sources known`.

**`tblThreatDetections`** (`Threat-Detection Map`) — inputs: `Threat ID`, `Detection ID`. Calculated:
`Threat applies`, `Threat risk`, `Threat risk score`, `Threat mitigation`, `Detection found`.

**`tblLogSources`** (`Log Sources`) — inputs: `Log source ID`, `Name`, `Description`, `Availability condition`,
`Available` (live formula per row returning `Yes` / `No` / `Unknown`). Calculated: `Needed by detections`
(relevant detections that require it), `Risk score`, `Highest threat risk`.

## Views

| Sheet | Header row | Columns |
| --- | --- | --- |
| `Threat Model` | 12 (summary in rows 4–10) | Threat ID, STRIDE, Title, Risk, Mitigation status, Controls (Full / Partial / Gap / Not assessed), Detections, Description |
| `Controls to Verify` | 7 (`TM_MODE` in B4, count in B5) | Control ID, Requirement, Criticality, Threat priority, Linked threats, Verification stage, Control type, Sheet |
| `Backlog` | 5 — left block A–H, right block J–N | Controls to fix: Control ID, Requirement, Coverage, Criticality, Threat priority, Backlog priority, Remediation owner, Linked threats. Log sources to enable: Log source, Name, Status, Needed by detections, Highest threat risk |
| `Detection Plan` | 5 | Detection ID, Title, Linked threats, Highest threat risk, Required log sources, Missing log sources, Deployment status, Sigma rule |
| `Catalog Health` | 5 (`CATALOG_HEALTH` in B4) | Check, Issues, Offending IDs |

Each view is one dynamic-array formula that spills below its header; never type inside the spill area.

## Named ranges

**Characterization answers** — one per key, on column D of its sheet. `Characterization Form`: `APP_NAME`,
`TARGET_LEVEL`, `API_EXPOSED`, `SPA_FRONTEND`, `SESSION_STATEFUL`, `FILE_HANDLING`, `OAUTH_OIDC_USED`,
`DATA_SENSITIVITY`, `WEBRTC_USED`, `EXPOSURE`, `BUSINESS_IMPACT`. `Extended Characterization`: `APP_ID`,
`APP_DESCRIPTION`, `BUSINESS_OWNER`, `TECHNICAL_OWNER`, `LIFECYCLE_STATUS`, `FINANCIAL_TRANSACTIONS`,
`SOURCING_MODEL`, `ARCHETYPE_PRIMARY`, `ARCHETYPE_SECONDARY`, `ARCHETYPE_DEVIATION`, `ARCHETYPE_DEVIATION_DETAILS`,
`USERS_CUSTOMERS`, `USERS_EMPLOYEES`, `USERS_PARTNERS`, `ADMIN_INTERFACE`, `ADMIN_INTERFACE_REACH`,
`AUTH_CORPORATE_SSO`, `AUTH_LOCAL_CREDENTIALS`, `AUTH_MFA`, `API_AUTH`, `SERVICE_ACCOUNTS`, `MULTIPLE_ROLES`,
`MULTI_TENANT`, `FILE_EXCHANGE`, `MESSAGING`, `OUTBOUND_EXTERNAL_CALLS`, `STORES_THIRD_PARTY_SECRETS`,
`EXTERNAL_INTEGRATIONS_LIST`, `HOSTING`, `CONTAINERIZED`, `WAF_IN_FRONT`, `OPENAPI_AVAILABLE`, `IAC_AVAILABLE`,
`VENDOR_NAME`, `PRODUCT_VERSION`, `VENDOR_SUPPORTED`, `PATCH_RESPONSIBILITY`, `PATCH_SLA_DEFINED`,
`VENDOR_REMOTE_ACCESS`, `DEFAULT_CREDENTIALS_CHANGED`, `CUSTOMIZATIONS`, `CUSTOMIZATIONS_IN_REPO`, `SBOM_AVAILABLE`,
`VENDOR_SECURITY_EVIDENCE`, `OUTBOUND_VENDOR_TELEMETRY`, `LOG_AUTH_EVENTS`, `LOG_ADMIN_ACTIONS`, `LOGS_CENTRALIZED`,
`HOST_EDR`, `HOST_FIM`, `KNOWN_SECURITY_CONCERNS`, `RESPONDENT`, `RESPONSE_DATE`.

**Computed** (do not write):

| Name | Holds |
| --- | --- |
| `TARGET_LEVEL_NUM` | Target level as 1–3 (0 if blank) |
| `DATA_SENSITIVITY_SCORE`, `EXPOSURE_SCORE`, `BUSINESS_IMPACT_SCORE` | Scores of the three risk factors |
| `APP_RISK_SCORE`, `APP_RISK_TIER` | Worst factor; Application Risk Tier (Low / Medium / High / Critical) |
| `CRIT_MATRIX`, `CRIT_MATRIX_ROWS`, `CRIT_MATRIX_COLS` | Criticality matrix (Requirement Impact × Risk Tier) |
| `EXT_MISSING_COUNT` | Mandatory applicable questions still blank |
| `NEEDS_SECURITY_REVIEW`, `REVIEW_REASONS` | Security review flag and reasons (`None` when No) |
| `ARCHETYPE_PRIMARY_ID`, `ARCHETYPE_SECONDARY_ID` | `ARCH-*` IDs of the chosen archetypes (blank if none) |
| `IS_COTS` | TRUE for COTS, COTS with customizations and vendor appliances |
| `TM_MODE` | `Characterization-only` / `Full` |
| `CATALOG_HEALTH` | `OK` / `Issues found` |

**Configuration** (`TM Config`): `RISK_SCALE` (+ `RISK_SCALE_NAMES`, `RISK_SCALE_SCORES`), `BASE_RISK_MATRIX`
(+ `BASE_RISK_ROWS` = Impact, `BASE_RISK_COLS` = Likelihood), `FINAL_RISK_MATRIX` (+ `FINAL_RISK_ROWS` = Base risk,
`FINAL_RISK_COLS` = Risk Tier), `SIGMA_BASE_URL`.

**Column ranges of the control sheets** — `MT_*` (rows 5–349) and `CC_*` (rows 5–204): `IDS` (A), `LEVEL` (D),
`REQ` (E), `FORMULA` (G), `APPLICABLE` (H), `TYPE` (I), `STAGE` (K), `COVERAGE` (L), `CRIT` (P), `OWNER` (Q),
`LINKED` (R), `TPRIO` (S), `VERIFY` (T), `BACKLOG` (U), `TIDS` (V).

**Other**: `ARCHETYPE_IDS`, `ARCHETYPE_NAMES` (`Archetypes` A/B, rows 5–30), `LIST_*` dropdown lists on `_lists`,
`TEMPLATE_VERSION`, `ASVS_VERSION` on `_meta`.

## Vocabularies

| Vocabulary | Values |
| --- | --- |
| Coverage Status | Not assessed, Full coverage, Partial coverage, Gap, N/A |
| Remediation Owner | Internal dev, Configuration, Vendor, Compensating, Risk acceptance |
| Risk scale (Risk Tier, Criticality, threat Risk, priorities) | Low, Medium, High, Critical (scores 1–4) |
| Likelihood / Impact | Low, Medium, High |
| STRIDE | Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege |
| Mitigation status | Mitigated, Partially mitigated, Unmitigated, Not verified, No applicable controls, No controls mapped, N/A |
| `TM_MODE` | Characterization-only, Full |
| Deployment status | Not requested, Requested to SOC, Deployed, Rejected |
| Review status (catalog content) | Draft, Approved |
| Log source availability | Yes, No, Unknown |

## ID conventions

| Pattern | Where | Example |
| --- | --- | --- |
| `V<chapter>.<section>.<n>` | ASVS requirement (`Master Template`) | `V6.3.1` |
| `CUSTOM-NN` | Organization policy / contractual / platform-specific control (`Custom Controls`) | `CUSTOM-01` |
| `TMX-<AREA>-NNN` | Control originated by threat modeling (`Custom Controls`) | `TMX-VENDOR-001` |
| `TM-<S/T/R/I/D/E>-NNN` | Threat (`Threat Library`) | `TM-S-001` |
| `DET-<AREA>-NNN` | Detection (`Detections`) | `DET-AUTH-001` |
| `LOG-<AREA>[-<NAME>]` | Log source (`Log Sources`) | `LOG-APP-AUTH` |
| `ARCH-<NAME>` | Architecture archetype (`Archetypes`) | `ARCH-COTS-HOSTED-WEB` |

`EXAMPLE-01` in `Custom Controls` is a worked example.

**Lists in one cell** (archetypes of a threat, log sources of a detection) use `; ` as separator. Matching is
always exact per item — `ARCH-API` never matches `ARCH-API-PARTNER` — using the pattern
`ISNUMBER(SEARCH(";"&id&";", ";"&SUBSTITUTE(list," ","")&";"))`.

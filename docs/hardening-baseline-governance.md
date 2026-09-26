\
# Application Hardening — Agnostic Baseline and Coverage Matrix

## Why ASVS

The OWASP ASVS (Application Security Verification Standard) is the best-suited reference for an
application-hardening baseline, for the same reasons that make CIS work for infrastructure: it is
maintained by an independent community, versioned, split into verification levels, and organized by
verifiable control — not by individual vulnerability.

**Level structure:**

1. **L1** — controls verifiable by automated/black-box testing, applicable to every application
   regardless of criticality.
2. **L2** — covers most applications that handle sensitive data (the recommended corporate default
   baseline).
3. **L3** — high-criticality applications (financial, healthcare, critical infrastructure).

**Why not another model:**

| Model | Role | Limitation for this use case |
| --- | --- | --- |
| CIS Benchmarks | Component hardening (OS, database, container) | Does not exist for "application" as a generic concept |
| OWASP Top 10 | Risk/vulnerability list | Prioritizes, does not audit control conformance |
| NIST SP 800-53 / SSDF | Full SDLC governance | Less granular as a technical checklist |
| PCI-DSS (Req. 6) | Regulatory requirement (cardholder-data scope) | Regulatory, not a full verification framework |

In practice, the market standard tends to be **ASVS as the operational technical baseline**, cross-referenced
with NIST/PCI where compliance requires it. This solves the stack-agnostic problem, because ASVS describes the
*requirement* ("the session shall expire after inactivity"), not the *implementation* (it doesn't matter whether
the app is Spring, Django, or Express).

## Baseline categories (stack-agnostic)

These are the ASVS requirement families that make up an application-hardening baseline, with no reference to
any specific technology:

1. **Architecture and design** — layer segregation, least privilege between components, trust-boundary definition.
2. **Authentication** — password policy, MFA, brute-force protection, account recovery.
3. **Session management** — inactivity expiration, logout invalidation, fixation/hijacking protection.
4. **Access control** — authorization on every sensitive operation, IDOR prevention, deny-by-default.
5. **Validation, sanitization, and encoding** — handling of untrusted input, injection prevention.
6. **Cryptography at rest** — approved algorithms, key management, sensitive data never stored in cleartext.
7. **Error handling and logging** — no internal detail leaked to the user, security events logged without
   sensitive data.
8. **Data protection** — data classification, minimization, exposure control in cache/exports.
9. **Communication** — mandatory TLS, weak protocols/ciphers disabled, HSTS.
10. **Configuration** — minimal enabled surface, debug mode off in production, security headers.
11. **Business logic / anti-abuse** — protection against business-flow abuse (rate limiting, anti-automation).
12. **Dependencies and supply chain** — third-party component inventory, absence of known critical CVEs.

These categories are the "what"; each company applies its own stack to decide the "how" — which is what keeps
the baseline agnostic even while covering applications written in different languages and frameworks.

## Coverage matrix

For each baseline category: what type of technical control should verify it, at what stage it runs, and the
nature of the verification (deterministic/continuous vs. sampled/periodic). No specific tool is named — each
company maps the product it already uses onto each row.

| Baseline category | Technical control type | Stage | Nature |
| --- | --- | --- | --- |
| Architecture and design | Questionnaire-driven threat modeling ([threat engine](https://github.com/Zzanoni/app-threat-modeling)) + Security review for flagged cases | Design, pre-code; per assessment | Deterministic, per assessment + manual review of exceptions |
| Authentication | SAST (policy rule) + dedicated integration test | CI/CD pipeline | Deterministic, continuous |
| Session management | Authenticated DAST + integration test | Pipeline / scheduled scan | Deterministic, continuous |
| Access control (IDOR, privilege escalation) | Pentest / advanced authenticated DAST | Periodic | Sampled |
| Input validation and sanitization | SAST + DAST | Pipeline | Deterministic, continuous |
| Cryptography at rest | SAST (crypto rule) + config review | Pipeline | Deterministic, continuous |
| Error handling and logging | SAST + config review / DAST | Pipeline | Deterministic, continuous |
| Data protection | DLP / architecture review + SAST | Pipeline + one-off review | Mixed |
| Communication (TLS, HSTS) | Configuration scanner / DAST | Pipeline or scheduled scan | Deterministic, continuous |
| Configuration (surface, debug) | IaC scanning + SAST + DAST | Pipeline | Deterministic, continuous |
| Business logic / anti-abuse | Pentest / Red Team | Periodic | Sampled |
| Dependencies (SCA) | SCA | Pipeline + scheduled scan | Deterministic, continuous |

**Reading the matrix:** rows marked "deterministic, continuous" are the ones that should become a **pipeline
gate** — a failure blocks the deploy. "Sampled" rows (pentest, red team) do not gate the pipeline by nature;
their role is to validate what automation cannot reach (business logic, chained failures). An application is
only considered "hardened" once every row has a mapped, running control — a row with no corresponding control is
a **coverage gap**, not an item resolved by documentation alone.

## Risk tiering / Criticality

Coverage status alone ("Full / Partial / Gap") does not tell a team which gaps to fix first. Every
applicable hardening item also carries a **criticality classification** (Low / Medium / High /
Critical), because Critical and High items typically need to follow stricter rules (remediation SLA,
escalation, exception approval — see "Governance rules by criticality" below).

Criticality is **not fixed per ASVS requirement** — the same requirement carries different real-world
risk depending on the application it applies to (a broken-access-control gap is worse on a public,
regulated-data application than on an internal tool). It is computed per application, per applicable
item, from two independent factors:

1. **Requirement Impact** — fixed per ASVS chapter, reflecting how severe it is when that *type* of
   control fails (e.g., Authentication, Authorization, Cryptography, Session Management = High;
   Configuration = Low). Implemented in the Master Template sheet as column **O**.
2. **Application Risk Tier** — derived per application from three Characterization Form answers: Data
   Sensitivity, network Exposure, and Business Impact. The application's tier is the *worst* of the
   three (the single highest-risk factor drives the tier, rather than being diluted by an average).
   Implemented as the computed `APP_RISK_TIER` field on the Characterization Form sheet.

The two factors cross in a risk matrix (also on the Characterization Form sheet, named range
`CRIT_MATRIX`) to produce the final Criticality value, in Master Template column **P**:

| Requirement Impact \ App Risk Tier | Low | Medium | High | Critical |
| --- | --- | --- | --- | --- |
| High | Medium | High | High | Critical |
| Medium | Low | Medium | Medium | High |
| Low | Low | Low | Low | Medium |

Only requirements already marked `Applicable` receive a Criticality value; `N/A` rows are unaffected.

### Governance rules by criticality

*(TBD — fill in per your organization's governance process.)* This subsection should document, per criticality
level, what changes in how a Gap is handled: e.g., remediation SLA, who must be notified, what level
of sign-off is required to formally accept the risk instead of fixing it, and whether Critical/High
gaps block a release. Until this is filled in, the Criticality column is informational — it identifies
which gaps should be prioritized, without yet gating any process.

## Extending the baseline beyond ASVS

ASVS is comprehensive for generic application security, but it is not the full universe of requirements
an organization may need to track — an internal policy, a contractual or regulatory obligation specific
to the organization, or a control for a technology ASVS doesn't address (e.g., a specific internal
platform) may all need to be part of the same hardening record.

These go on the **`Custom Controls`** sheet of the master workbook, never appended to `Master Template`.
The separation is deliberate:

- `Master Template` must stay a byte-for-byte match of the upstream ASVS content, so a future ASVS
  release can always be diffed and merged in cleanly, and the "we don't modify the underlying ASVS
  requirement text" claim in this repo stays true without caveats.
- Custom control IDs are then guaranteed never to collide with a real or future ASVS ID, even across
  ASVS version upgrades.

**Custom control ID convention:**

| Prefix | Pattern | Use for | Example |
| --- | --- | --- | --- |
| `CUSTOM-` | `CUSTOM-NN` | Organization policy, contractual obligation, platform-specific control | `CUSTOM-01` |
| `TMX-` | `TMX-<AREA>-NNN` | Control originated by threat modeling — typically COTS/vendor, compensating or infrastructure controls ASVS doesn't express | `TMX-WAF-001`, `TMX-VENDOR-001` |

`TMX-*` controls come from the threat modeling catalog (see "Relationship with threat modeling" below);
they are added here, like any custom control, so that the hardening record and the threat model share one
control catalog. The rows `EXAMPLE-01` and `TMX-EXAMPLE-001` shipped in the template are worked examples,
ignored by the threat engine. The accepted patterns are part of the contract
([`contract/workbook-contract.yml`](../contract/workbook-contract.yml)).

`Custom Controls` mirrors `Master Template`'s columns and reuses the same underlying mechanics
(`TARGET_LEVEL_NUM` for level gating, `CRIT_MATRIX`/`APP_RISK_TIER` for Criticality) — a custom control
gets filtered and prioritized exactly like an ASVS one. The one deliberate difference: its Applicability
Formula column is a live, directly-editable formula (default `=TRUE()`, i.e. always applicable) rather
than `Master Template`'s hidden helper column, since a custom control's applicability condition is
organization-defined and can't be pre-written into the template the way ASVS chapter gating can.

When publishing to Confluence (see [`confluence-page-template.md`](confluence-page-template.md)), custom
controls get their own Expand block ("Company-Specific Controls"), kept visually separate from the
ASVS-chapter blocks so a reader can tell at a glance which requirements are the industry standard and
which are this organization's own addition.

A custom control's Applicability Formula may reference any characterization key, including the ones on
`Extended Characterization` — for example
`=OR(SOURCING_MODEL="COTS (vendor product on our infrastructure)",SOURCING_MODEL="COTS with customizations")`
for a control that only applies to vendor products.

## Remediation Owner

Coverage Status says *whether* a requirement is met; it doesn't say *who can close the gap*. For
applications built in-house that is almost always the development team, but for vendor products (COTS,
appliances) most application-level gaps can't be fixed by the organization at all. Every row with
Coverage Status `Partial coverage` or `Gap` therefore also records a **Remediation Owner** (column Q of
`Master Template` and `Custom Controls`; blank for other rows):

| Value | Use when | Typical for |
| --- | --- | --- |
| `Internal dev` | The fix is a code change by the organization's developers | In-house applications; COTS customizations |
| `Configuration` | The fix is a setting in the product, platform or infrastructure | Any; the most common owner for COTS |
| `Vendor` | Only the vendor can fix it (product change, patch, new version) | COTS, appliances |
| `Compensating` | The fix lives outside the product: WAF, network segmentation, PAM, monitoring | COTS and appliances whose gap the vendor won't fix |
| `Risk acceptance` | The gap is formally accepted instead of fixed | Any — subject to the criticality governance rules |

For COTS, expect most application-level gaps to be `Vendor` or `Configuration`; use `Compensating` when
the realistic fix is a control placed around the product rather than in it — those compensating controls
are typically the `TMX-*` custom controls above. The Remediation Owner is what turns the gap list into an
actionable backlog: it routes each item to a team, a vendor ticket, or a risk-acceptance decision.

## Relationship with threat modeling

Architecture and design weaknesses are covered by a questionnaire-driven threat model, produced by a
separate project: [**app-threat-modeling**](https://github.com/Zzanoni/app-threat-modeling). It is deterministic (the same answers always produce
the same threats) and STRIDE-based, and it is built to share everything it can with this baseline instead of
duplicating it:

- **Shared intake.** The threat engine reads this repository's workbook — both characterization sheets
  (`Characterization Form` and `Extended Characterization`) — so the application team fills in one file
  per application, not a second questionnaire.
- **Shared risk tier.** The threat engine uses the same `APP_RISK_TIER`; there is no second risk rating.
- **Shared control catalog.** Threat mitigations point to `Master Template` (ASVS) and `Custom Controls`
  (including `TMX-*`) rows, and the engine reads their Coverage Status and Remediation Owner. There is no
  second control list.
- **Prioritization.** A gap linked to a high-risk threat is prioritized above gaps of the same Criticality
  that no identified threat depends on.
- **Detection plan.** Alongside preventive controls, the threat engine proposes detections for the
  threats that matter most. The detection plan is owned by the SOC and is SIEM-agnostic (it names the
  events and log sources needed, not a product's query language). It complements the hardening controls; it
  never replaces them.

**Process order.** The threat model depends on the characterization, **not** on a completed hardening
assessment:

1. **Characterization** — the application team fills in both characterization sheets (about 20–30 minutes).
2. **Threat model, characterization-only mode** — produces the threats, the detection plan, and a
   "controls to verify first" list.
3. **Hardening assessment** — Coverage Status is filled in starting with the "controls to verify first",
   then the remaining applicable rows.
4. **Threat model, full mode** — with Coverage Status available, links remaining gaps to the threats they
   leave open and produces the prioritized backlog.

The link between the two repositories is the machine-readable contract in [`contract/`](../contract/)
(see [`contract/README.md`](../contract/README.md)); any change to it is a breaking change for the threat
engine and is versioned.

### Security review triggers

Some applications can't be judged by an automatic threat model alone. The `Extended Characterization`
sheet computes `NEEDS_SECURITY_REVIEW` (Yes/No) and `REVIEW_REASONS`; the answer is **Yes** if **any** of
the following holds:

1. `ARCHETYPE_PRIMARY` = *None of these fits* — no known architecture pattern describes the application.
2. `ARCHETYPE_DEVIATION` = *Yes* or *Don't know* — relevant components or flows outside the selected
   pattern(s).
3. `SOURCING_MODEL` = *SaaS (vendor infrastructure)* — outside the scope of the v1 threat archetypes.
4. Any mandatory question answered *Don't know* (its Status shows `Review`).
5. `APP_RISK_TIER` = *Critical*.
6. `VENDOR_REMOTE_ACCESS` = *Yes, permanent* or *Don't know* (when applicable).
7. `VENDOR_SUPPORTED` = *No* or *Don't know* (when applicable).

A question that is not applicable (greyed out, e.g. vendor questions for an in-house application) never
fires a trigger, even if an old answer is still in its cell. The same triggers are defined, in
machine-readable form, in [`contract/workbook-contract.yml`](../contract/workbook-contract.yml)
(`review_triggers`) and in the threat engine's
[`catalog/config/review_triggers.yml`](https://github.com/Zzanoni/app-threat-modeling/blob/main/catalog/config/review_triggers.yml) — **both must stay
equal**; change them together.

## Gaps and the governance role of this document

The baseline document (the company's "reduced ASVS") is not the verification mechanism itself — it is the
**inventory of requirements against which the coverage matrix is filled in**. It serves three purposes, none of
them redundant with the technical control:

1. **Define the bar** — what "hardened" means at this company, at a level of detail generic ASVS does not
   define on its own (e.g., "session expires after 15 minutes," not just "shall expire").
2. **Surface coverage gaps** — every matrix row with no tool verifying it becomes either a backlog item (build
   the automation) or a formally accepted risk — it never stays "assumed safe" with nothing on record.
3. **Serve as audit/compliance evidence** — a regulator or auditor asks for the documented baseline plus
   evidence that controls actually ran, not a separate manual inspection.

**Applying this across many applications:** the baseline (categories + matrix) is written once, in an agnostic
form. Per application, all that changes is a few extra columns: *which real tool* covers each row, *what the
status is* (full / partial / gap coverage) and, for gaps, *who can close it* (Remediation Owner). This turns "write hardening documentation for N
applications" into "fill in a status column against a single shared baseline" — instead of rewriting the whole
document for each one.

**Sign that it has become theater:** if a matrix row is never checked by any technical control and nobody flags
that as a gap, the item is pure paperwork. If it is checked and the result feeds a real decision (block the
deploy, open a ticket, formally accept the risk), the baseline is doing its job as the bar — which is different
from being one more technical control.

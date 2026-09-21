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
| Architecture and design | Threat modeling / architecture review | Design, pre-code | Manual, one-off per feature |
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

Coverage status alone ("Full / Partial / Gap") does not tell a team which gaps to fix first. The
governance team defining the formal rules for this process requested that every applicable hardening
item also carry a **criticality classification** (Low / Medium / High / Critical), because Critical
and High items need to follow stricter governance rules (remediation SLA, escalation, exception
approval — see "Governance rules by criticality" below).

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

*(TBD — to be defined by the governance team.)* This subsection should document, per criticality
level, what changes in how a Gap is handled: e.g., remediation SLA, who must be notified, what level
of sign-off is required to formally accept the risk instead of fixing it, and whether Critical/High
gaps block a release. Until this is filled in, the Criticality column is informational — it identifies
which gaps should be prioritized, without yet gating any process.

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
form. Per application, all that changes is one extra pair of columns: *which real tool* covers each row, and
*what the status is* (full / partial / gap coverage). This turns "write hardening documentation for N
applications" into "fill in a status column against a single shared baseline" — instead of rewriting the whole
document for each one.

**Sign that it has become theater:** if a matrix row is never checked by any technical control and nobody flags
that as a gap, the item is pure paperwork. If it is checked and the result feeds a real decision (block the
deploy, open a ticket, formally accept the risk), the baseline is doing its job as the bar — which is different
from being one more technical control.

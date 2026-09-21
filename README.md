# Application Hardening Baseline

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](LICENSE)
[![OWASP ASVS 5.0.0](https://img.shields.io/badge/OWASP%20ASVS-5.0.0-blue.svg)](https://github.com/OWASP/ASVS)

## What this is, in plain terms

Every application (a website, a mobile app, an internal system) needs to be checked against a list of
security best practices — things like "passwords must be strong," "user sessions must expire," "sensitive
data must be protected." Doing this checklist from scratch for every application, in a Word document, is
slow and inconsistent: every app ends up with a different checklist, some things get forgotten, and nobody
can easily compare one application's security posture to another's.

This repository solves that with **one shared checklist**, built once and reused for every application in
the company. Instead of writing a new document each time, you answer about 11 simple yes/no or
multiple-choice questions about the application, and the checklist automatically narrows itself down to
only the items that actually apply to that application.

The checklist itself is not invented here — it is the **OWASP ASVS**, an internationally recognized,
independently maintained list of application-security requirements (345 items in total). This repository
just organizes it so it's practical to use across many applications without repeating work.

## What's inside

| What | Where | What it's for |
| --- | --- | --- |
| The rulebook | [`docs/hardening-baseline-governance.md`](docs/hardening-baseline-governance.md) | Explains, in writing, what "secure enough" means at this company and why — the reasoning behind the checklist. |
| The checklist spreadsheet | [`templates/ASVS_Master_Hardening_Template.xlsx`](templates/ASVS_Master_Hardening_Template.xlsx) | The actual tool you fill in for one application. |
| The published-record template | [`docs/confluence-page-template.md`](docs/confluence-page-template.md) + [`templates/confluence-page-template.xml`](templates/confluence-page-template.xml) | Once the spreadsheet is filled in, this is how the result becomes an official, shareable page. |

## How to check one application, step by step

1. **Make a copy of the spreadsheet** (`templates/ASVS_Master_Hardening_Template.xlsx`) and rename it after
   the application you're assessing.
2. **Open the "Characterization Form" tab** and answer the questions in the yellow cells. These are simple
   questions about the application — for example, whether it has a public website, whether it stores
   sensitive information, or how serious it would be if something went wrong with it. There is no free
   text to write; every question has a small, fixed list of answers to pick from.
3. **Open the "Master Template" tab.** As soon as you finish step 2, this tab automatically:
   - Marks each of the 345 checklist items as either **Applicable** (this app needs it) or **N/A** (doesn't
     apply, based on your answers) — nothing to calculate by hand.
   - Assigns each applicable item a **Criticality** — Low, Medium, High, or Critical — so you know which
     ones to worry about first. The same checklist item can be more or less critical depending on the
     application; a login-security gap matters more on a public website handling customer data than on an
     internal tool nobody outside the company can reach.
4. **Filter the "Applicable?" column to "Applicable"** (a normal spreadsheet filter) so you're only looking
   at the items that matter for this application.
5. **For each applicable item, fill in three things**: whether it's actually covered today (Full coverage /
   Partial coverage / Gap), what proves it (a tool name, a test, a scan result), and any notes.
6. **Publish the result.** Once the spreadsheet is filled in, it becomes the application's official record —
   see [`docs/confluence-page-template.md`](docs/confluence-page-template.md) for how that record gets
   turned into a shareable page.

Everything past step 3 is manual review work — the spreadsheet does the filtering and prioritizing for you,
but a person still has to check each applicable item and record the real answer.

## A few terms explained

- **ASVS** — the security checklist standard this baseline is built on, maintained by OWASP (a nonprofit,
  vendor-neutral security organization). Think of it as an industry-standard rulebook, the same way a
  building code is a standard rulebook for construction.
- **Level (L1 / L2 / L3)** — how strict the checklist should be for a given application. L1 is the baseline
  every application should meet. L2 is stricter, for applications handling sensitive data. L3 is the
  strictest, for high-stakes applications (e.g., handling regulated financial or health data). You pick this
  once per application, in the Characterization Form.
- **Criticality (Low / Medium / High / Critical)** — how urgently a specific checklist item should be
  addressed for this specific application. It's computed automatically; you don't set it by hand.
- **Coverage status** — whether an applicable item is actually being checked today: fully (a tool or test
  verifies it automatically), partially, or not at all (a gap).

## Where the target level and criticality come from

If the company already has an official way of rating how sensitive or important an application is, use
that rating to decide the target ASVS level. Otherwise, a simple rule of thumb: no sensitive data and no
outside users → L1; the app handles sensitive data, logins, or is reachable by outside partners → L2;
regulated financial or health data, or actions that can't be undone if something goes wrong → L3.

Criticality per item works the same way but automatically, from three questions: how sensitive the data is,
how exposed the application is (internal-only vs. public internet), and how bad it would be if the
application were breached or went down. The riskiest of those three answers decides how seriously every
applicable item is treated. Full details and the exact scoring rules are in
[`docs/hardening-baseline-governance.md`](docs/hardening-baseline-governance.md#risk-tiering--criticality).

## Where the checklist content comes from

The 345 requirements, their chapters, and their levels are copied word-for-word from the official
[OWASP ASVS](https://github.com/OWASP/ASVS) version 5.0.0. Nothing about the requirements themselves has
been changed. What this repository adds on top is: the automatic filtering, the criticality scoring, and
the company's own rulebook explaining how each requirement should be checked in practice.

## Keeping it up to date

This is one shared, living baseline — not a one-time document. If something about the checklist needs to
change (a new requirement, an updated rule), it's changed once in the master spreadsheet, and every
application's *next* copy or refresh picks up the change automatically. Individual application copies
should not be edited to add new checklist items directly.

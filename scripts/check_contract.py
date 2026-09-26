#!/usr/bin/env python3
"""Assert that the master workbook and contract/ agree. Exits non-zero on any drift.

Checks:
  - contract YAML files are well-formed (JSON Schema)
  - _meta versions match workbook-contract.yml
  - sheet names, order, visibility and header rows match
  - every characterization key is a named range on column D of its sheet, with the question,
    options (vs. data validation), mandatory flag and Applicable formula the contract implies
  - Master Template chapter gating matches the `gates` of the v1 keys
  - Archetypes sheet and archetype dropdowns match archetypes.yml
  - computed named ranges, vocabularies and the review-trigger formula match
  - contract/controls.json is up to date
  - with --recalc (or when LibreOffice is found and --no-recalc isn't given): zero formula errors

Usage: python scripts/check_contract.py [--workbook PATH] [--recalc | --no-recalc]
"""

import argparse
import re
import shutil
import sys

import jsonschema
from openpyxl import load_workbook

import baseline_lib as lib
import export_contract

CONDITION = {"type": "object", "minProperties": 1}
CHARACTERIZATION_SCHEMA = {
    "type": "object",
    "required": ["contract_version", "sections", "keys"],
    "properties": {
        "keys": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["key", "sheet", "question", "type", "mandatory", "used_by"],
                "properties": {
                    "key": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
                    "sheet": {"enum": [lib.SHEET_CF, lib.SHEET_EXT]},
                    "type": {"enum": ["choice", "text", "long_text", "date"]},
                    "options": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                    "mandatory": {"type": "boolean"},
                    "shown_when": CONDITION,
                    "used_by": {"type": "array", "items": {"enum": ["hardening", "threat_model"]}},
                },
            },
        },
    },
}
ARCHETYPES_SCHEMA = {
    "type": "object",
    "required": ["contract_version", "archetypes"],
    "properties": {
        "archetypes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "description"],
                "properties": {"id": {"type": "string", "pattern": "^ARCH-[A-Z0-9-]+$"}},
            },
        },
    },
}


class Checker:
    def __init__(self):
        self.errors = []

    def eq(self, what, found, expected):
        if found != expected:
            self.errors.append("%s: found %r, expected %r" % (what, found, expected))

    def true(self, what, condition):
        if not condition:
            self.errors.append(what)


def check_schemas(chk, characterization, archetypes):
    for name, doc, schema in (
        ("characterization.yml", characterization, CHARACTERIZATION_SCHEMA),
        ("archetypes.yml", archetypes, ARCHETYPES_SCHEMA),
    ):
        for err in jsonschema.Draft7Validator(schema).iter_errors(doc):
            chk.errors.append("%s schema: %s at %s" % (name, err.message, list(err.path)))
    keys = [k["key"] for k in characterization["keys"]]
    chk.eq("duplicate keys", sorted({k for k in keys if keys.count(k) > 1}), [])
    for key in characterization["keys"]:
        chk.true("%s: choice without options" % key["key"], key["type"] != "choice" or key.get("options"))
        if key["sheet"] == lib.SHEET_EXT:
            chk.true("%s: choice without list" % key["key"], key["type"] != "choice" or key.get("list"))
        for ref in lib.referenced_keys(key.get("shown_when") or {}):
            chk.true("%s: shown_when references unknown key %s" % (key["key"], ref), ref in keys)


def check_versions(chk, wb, contract, characterization, archetypes):
    for name, field in contract["meta_named_ranges"].items():
        chk.eq("_meta %s" % name, lib.named_values(wb, name)[0], contract[field])
    chk.eq("characterization.yml contract_version", characterization["contract_version"], contract["contract_version"])
    chk.eq("archetypes.yml contract_version", archetypes["contract_version"], contract["contract_version"])


def check_sheets(chk, wb, contract):
    chk.eq("sheet order", wb.sheetnames, [s["name"] for s in contract["sheets"]])
    for spec in contract["sheets"]:
        if spec["name"] not in wb.sheetnames:
            continue
        ws = wb[spec["name"]]
        chk.eq("%s visibility" % spec["name"], ws.sheet_state, spec["state"])
        for col, header in spec.get("columns", {}).items():
            chk.eq("%s!%s%d header" % (spec["name"], col, spec["header_row"]),
                   ws["%s%d" % (col, spec["header_row"])].value, header)


def key_rows(wb, characterization):
    """key -> (sheet, row) from the named ranges; records problems instead of raising."""
    rows, problems = {}, []
    for key in characterization["keys"]:
        ref = lib.defined_name_ref(wb, key["key"])
        if not ref:
            problems.append("%s: no named range" % key["key"])
            continue
        sheet, cell = lib.parse_ref(ref)
        m = re.fullmatch(r"D(\d+)", cell)
        if sheet != key["sheet"] or not m:
            problems.append("%s: named range %s is not column D of %s" % (key["key"], ref, key["sheet"]))
            continue
        rows[key["key"]] = (sheet, int(m.group(1)))
    return rows, problems


def check_keys(chk, wb, characterization):
    rows, problems = key_rows(wb, characterization)
    chk.errors.extend(problems)
    guarded = {k["key"] for k in characterization["keys"] if k.get("shown_when") and k["key"] in rows}

    def ref(name):
        if name in guarded:
            return name, '$H$%d="Applicable"' % rows[name][1]
        return name, None

    for key in characterization["keys"]:
        if key["key"] not in rows:
            continue
        sheet, r = rows[key["key"]]
        ws = wb[sheet]
        where = "%s (%s!D%d)" % (key["key"], sheet, r)
        chk.eq(where + " key cell", ws["A%d" % r].value, key["key"])
        chk.eq(where + " question", ws["B%d" % r].value, key["question"])
        dv = lib.validation_for(ws, "D%d" % r)
        if key["type"] == "choice":
            chk.true(where + " has no dropdown", dv is not None and dv.type == "list")
            if dv is not None and dv.type == "list":
                chk.eq(where + " dropdown options", lib.validation_options(wb, dv), key["options"])
                if key.get("list"):
                    chk.eq(where + " dropdown source", dv.formula1, key["list"])
        elif key["type"] == "date":
            chk.true(where + " has no date validation", dv is not None and dv.type == "date")
        else:
            chk.true(where + " free text must not have a dropdown", dv is None or dv.type != "list")
        if sheet == lib.SHEET_EXT:
            chk.eq(where + " options label", ws["C%d" % r].value, lib.options_label(key))
            chk.eq(where + " help", ws["E%d" % r].value, key.get("help"))
            chk.eq(where + " mandatory", ws["F%d" % r].value, "Yes" if key["mandatory"] else "No")
            if key.get("shown_when"):
                expected = '=IF(%s,"Applicable","N/A")' % lib.condition_to_excel(key["shown_when"], ref)
                chk.eq(where + " shown when", ws["G%d" % r].value, lib.condition_label(key["shown_when"]))
            else:
                expected = "Applicable"
            chk.eq(where + " Applicable formula", ws["H%d" % r].value, expected)
            chk.true(where + " has no Status formula", str(ws["I%d" % r].value or "").startswith("=IF(H%d" % r))
    return rows, ref


def check_gating(chk, wb, characterization):
    expected = {}
    for key in characterization["keys"]:
        for gate in key.get("gates", []):
            expected[gate["chapter"]] = lib.condition_to_excel(gate["when"], lambda k: (k, None))
    ws = wb[lib.SHEET_MT]
    spec = next(s for s in lib.load_yaml("workbook-contract.yml")["sheets"] if s["name"] == lib.SHEET_MT)
    seen = {}
    for r in range(spec["first_data_row"], spec["last_data_row"] + 1):
        chapter = str(ws["B%d" % r].value).split(" ")[0]
        seen.setdefault(chapter, set()).add(ws["G%d" % r].value)
    for chapter, formulas in sorted(seen.items()):
        chk.eq("Master Template %s gating" % chapter, formulas, {expected.get(chapter, "TRUE")})


def check_archetypes(chk, wb, characterization, archetypes):
    ws = wb[lib.SHEET_ARCH]
    found = []
    r = 5
    while ws["A%d" % r].value:
        found.append({"id": ws["A%d" % r].value, "name": ws["B%d" % r].value, "description": ws["C%d" % r].value})
        r += 1
    chk.eq("Archetypes sheet", found, archetypes["archetypes"])
    names = [a["name"] for a in archetypes["archetypes"]]
    chk.eq("LIST_ARCHETYPES", [v for v in lib.named_values(wb, "LIST_ARCHETYPES") if v], names)
    for key in characterization["keys"]:
        if key.get("options_extra"):
            chk.eq("%s options" % key["key"], key["options"], names + key["options_extra"])


def check_named_ranges(chk, wb, contract):
    for name, spec in contract["computed_named_ranges"].items():
        ref = lib.defined_name_ref(wb, name)
        if not ref:
            chk.errors.append("computed named range %s missing" % name)
        elif "ref" in spec:
            chk.eq("named range %s" % name, ref, spec["ref"])
        else:
            sheet, cell = lib.parse_ref(ref)
            chk.true("named range %s must be column %s of %s (is %s)" % (name, spec["column"], spec["sheet"], ref),
                     sheet == spec["sheet"] and re.fullmatch(spec["column"] + r"\d+", cell))


def check_vocabularies(chk, wb, contract):
    vocab = contract["vocabularies"]
    for sheet in (lib.SHEET_MT, lib.SHEET_CC):
        ws = wb[sheet]
        for col, name in (("L", "coverage_status"), ("Q", "remediation_owner")):
            dv = lib.validation_for(ws, "%s5" % col)
            chk.true("%s!%s5 has no dropdown" % (sheet, col), dv is not None)
            if dv is not None:
                chk.eq("%s!%s dropdown" % (sheet, col), lib.validation_options(wb, dv), vocab[name])
    chk.eq("CRIT_MATRIX_COLS", lib.named_values(wb, "CRIT_MATRIX_COLS"), vocab["app_risk_tier"])
    chk.eq("CRIT_MATRIX_ROWS", sorted(lib.named_values(wb, "CRIT_MATRIX_ROWS")), sorted(vocab["requirement_impact"]))
    patterns = [re.compile(p["regex"]) for p in contract["custom_control_id_patterns"].values()]
    ws = wb[lib.SHEET_CC]
    for r in range(5, 205):
        control_id = ws["A%d" % r].value
        if control_id and control_id not in contract["example_control_ids"]:
            chk.true("Custom Controls A%d: ID %r matches no pattern" % (r, control_id),
                     any(p.match(control_id) for p in patterns))


def check_review_triggers(chk, wb, contract, rows, ref):
    ws = wb[lib.SHEET_EXT]
    ext_rows = [r for sheet, r in rows.values() if sheet == lib.SHEET_EXT]
    if not ext_rows:
        return
    special = {"status_any": lambda v: 'COUNTIF($I$5:$I$%d,"%s")>0' % (max(ext_rows), v)}
    exprs = [lib.condition_to_excel(t["when"], ref, special) for t in contract["review_triggers"]]
    needs = lib.parse_ref(lib.defined_name_ref(wb, "NEEDS_SECURITY_REVIEW"))[1]
    chk.eq("NEEDS_SECURITY_REVIEW formula", ws[needs].value, '=IF(OR(%s),"Yes","No")' % ",".join(exprs))
    reasons = ws[lib.parse_ref(lib.defined_name_ref(wb, "REVIEW_REASONS"))[1]].value or ""
    for t, expr in zip(contract["review_triggers"], exprs):
        chk.true("REVIEW_REASONS lacks trigger %s" % t["id"], 'IF(%s,"%s; ","")' % (expr, t["reason"]) in reasons)


def check_controls_json(chk, workbook_path):
    expected = export_contract.render(export_contract.build_catalog(workbook_path))
    try:
        with open(lib.CONTROLS_JSON, encoding="utf-8") as fh:
            found = fh.read()
    except FileNotFoundError:
        found = None
    chk.true("contract/controls.json is out of date — run scripts/export_contract.py", found == expected)


def check_recalc(chk, workbook_path):
    result = lib.recalculate(workbook_path)
    try:
        for sheet, cell, value in lib.formula_errors(result):
            chk.errors.append("formula error after recalculation: %s!%s = %s" % (sheet, cell, value))
    finally:
        shutil.rmtree(result.rsplit("/out/", 1)[0], ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workbook", default=lib.TEMPLATE)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--recalc", action="store_true", help="require LibreOffice recalculation")
    group.add_argument("--no-recalc", action="store_true", help="skip LibreOffice recalculation")
    args = parser.parse_args()

    characterization, archetypes, contract = lib.load_contract()
    wb = load_workbook(args.workbook)
    chk = Checker()
    check_schemas(chk, characterization, archetypes)
    check_versions(chk, wb, contract, characterization, archetypes)
    check_sheets(chk, wb, contract)
    rows, ref = check_keys(chk, wb, characterization)
    check_gating(chk, wb, characterization)
    check_archetypes(chk, wb, characterization, archetypes)
    check_named_ranges(chk, wb, contract)
    check_vocabularies(chk, wb, contract)
    check_review_triggers(chk, wb, contract, rows, ref)
    check_controls_json(chk, args.workbook)

    if args.recalc or (not args.no_recalc and lib.find_soffice()):
        check_recalc(chk, args.workbook)
        recalc_note = "recalculated with LibreOffice"
    else:
        recalc_note = "recalculation SKIPPED (LibreOffice not found)"

    if chk.errors:
        print("Contract check FAILED (%d problems):" % len(chk.errors))
        for e in chk.errors:
            print("  - " + e)
        sys.exit(1)
    print("Contract check passed (%d keys, %s)." % (len(characterization["keys"]), recalc_note))


if __name__ == "__main__":
    main()

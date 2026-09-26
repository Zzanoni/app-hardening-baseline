#!/usr/bin/env python3
"""Move a filled-in application workbook onto the current template, without retyping.

Copies, from the application's copy (any earlier template version, e.g. v1) into a fresh copy of
the current template:
  - characterization answers, matched by key (named range, or column A of the sheet in v1 files
    where a key had no named range)
  - Master Template Coverage Status / Tool / Evidence / Notes (+ Remediation Owner when present),
    matched by ASVS ID
  - Custom Controls rows (every input column), matched by Control ID; rows are written in the
    source order. Template example rows (EXAMPLE-01, TMX-EXAMPLE-001) are dropped unless the
    source still has them or --keep-examples is given.

Rows of the source whose ASVS ID no longer exists in the template are reported, never silently
dropped.

Usage: python scripts/upgrade_app_workbook.py SOURCE.xlsx OUTPUT.xlsx [--template PATH] [--keep-examples]
"""

import argparse
import copy
import sys

from openpyxl import load_workbook

import baseline_lib as lib

MT_COPY_COLUMNS = ("L", "M", "N", "Q")
CC_INPUT_COLUMNS = ("A", "B", "C", "D", "E", "F", "G", "I", "J", "K", "L", "M", "N", "O", "Q")


def find_answer_cell(wb, key, sheet):
    """(worksheet, coordinate) of a key's answer in wb, or None."""
    ref = lib.defined_name_ref(wb, key)
    if ref:
        sheet_name, cell = lib.parse_ref(ref)
        if sheet_name in wb.sheetnames:
            return wb[sheet_name], cell
    if sheet in wb.sheetnames:
        ws = wb[sheet]
        for r in range(1, ws.max_row + 1):
            if ws.cell(r, 1).value == key:
                return ws, "D%d" % r
    return None


def header_map(ws, header_row=4):
    return {ws.cell(header_row, c).value: c for c in range(1, ws.max_column + 1) if ws.cell(header_row, c).value}


def copy_characterization(src, dst, characterization, report):
    for key in characterization["keys"]:
        target = find_answer_cell(dst, key["key"], key["sheet"])
        source = find_answer_cell(src, key["key"], key["sheet"])
        if target is None:
            sys.exit("Template has no answer cell for %s" % key["key"])
        if source is None:
            continue
        value = source[0][source[1]].value
        if value in (None, ""):
            continue
        if key["type"] == "choice" and value not in key["options"]:
            report["warnings"].append("%s: answer %r is not an allowed option — copied, please review"
                                      % (key["key"], value))
        target[0][target[1]].value = value
        report["answers"] += 1


def copy_master(src, dst, contract, report):
    spec = next(s for s in contract["sheets"] if s["name"] == lib.SHEET_MT)
    s_ws, d_ws = src[lib.SHEET_MT], dst[lib.SHEET_MT]
    s_cols = header_map(s_ws)
    d_rows = {d_ws["A%d" % r].value: r for r in range(spec["first_data_row"], spec["last_data_row"] + 1)}
    vocab = contract["vocabularies"]
    for r in range(5, s_ws.max_row + 1):
        asvs_id = s_ws["A%d" % r].value
        if not asvs_id:
            continue
        values = {}
        for col in MT_COPY_COLUMNS:
            header = spec["columns"][col]
            if header in s_cols:
                values[col] = s_ws.cell(r, s_cols[header]).value
        if asvs_id not in d_rows:
            if any(v not in (None, "", "Not assessed") for v in values.values()):
                report["warnings"].append("Master Template: %s is not in the current template — its status "
                                          "(%s) was not copied" % (asvs_id, values))
            continue
        for col, value in values.items():
            d_ws["%s%d" % (col, d_rows[asvs_id])].value = value
        report["master_rows"] += 1
        status, owner = values.get("L"), values.get("Q")
        if status not in (None, "") and status not in vocab["coverage_status"]:
            report["warnings"].append("Master Template %s: Coverage Status %r not in vocabulary" % (asvs_id, status))
        if owner not in (None, "") and owner not in vocab["remediation_owner"]:
            report["warnings"].append("Master Template %s: Remediation Owner %r not in vocabulary" % (asvs_id, owner))


def copy_custom(src, dst, contract, keep_examples, report):
    spec = next(s for s in contract["sheets"] if s["name"] == lib.SHEET_CC)
    first, last = spec["first_data_row"], spec["last_data_row"]
    s_ws, d_ws = src[lib.SHEET_CC], dst[lib.SHEET_CC]
    s_cols = header_map(s_ws)
    examples = set(contract["example_control_ids"])

    rows = []
    for r in range(first, s_ws.max_row + 1):
        control_id = s_ws["A%d" % r].value
        if not control_id:
            continue
        row = {}
        for col in CC_INPUT_COLUMNS:
            header = spec["columns"][col]
            if header in s_cols:
                row[col] = s_ws.cell(r, s_cols[header]).value
        rows.append(row)
    source_ids = {row["A"] for row in rows}

    # Template rows to keep: examples, only when requested (and not overridden by the source).
    template_rows = []
    for r in range(first, last + 1):
        control_id = d_ws["A%d" % r].value
        if control_id and keep_examples and control_id in examples and control_id not in source_ids:
            template_rows.append({col: d_ws["%s%d" % (col, r)].value for col in CC_INPUT_COLUMNS})
    # Plain (non-example) row style; rows 5-6 carry the yellow example styling.
    styles = {col: d_ws["%s%d" % (col, first + 2)]._style for col in CC_INPUT_COLUMNS}

    final = rows + template_rows
    if len(final) > last - first + 1:
        sys.exit("Custom Controls: %d rows do not fit in the template's %d rows" % (len(final), last - first + 1))
    for i, r in enumerate(range(first, last + 1)):
        row = final[i] if i < len(final) else {}
        for col in CC_INPUT_COLUMNS:
            cell = d_ws["%s%d" % (col, r)]
            cell._style = copy.copy(styles[col])
            default = "=TRUE()" if col == "G" else None
            value = row.get(col, default)
            cell.value = default if (col == "G" and value in (None, "")) else value
    report["custom_rows"] = len(rows)
    report["examples_kept"] = [row["A"] for row in template_rows]


def upgrade(source, output, template, keep_examples):
    characterization, _, contract = lib.load_contract()
    src = load_workbook(source)
    dst = load_workbook(template)
    report = {"answers": 0, "master_rows": 0, "custom_rows": 0, "warnings": [],
              "new_sheets": [s for s in dst.sheetnames if s not in src.sheetnames and not s.startswith("_")]}
    copy_characterization(src, dst, characterization, report)
    copy_master(src, dst, contract, report)
    copy_custom(src, dst, contract, keep_examples, report)
    lib.save_normalized(dst, output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source", help="filled-in application workbook (older template version)")
    parser.add_argument("output", help="where to write the upgraded workbook")
    parser.add_argument("--template", default=lib.TEMPLATE, help="current master template")
    parser.add_argument("--keep-examples", action="store_true", help="keep the template's example rows")
    args = parser.parse_args()
    report = upgrade(args.source, args.output, args.template, args.keep_examples)
    print("Upgraded %s -> %s" % (args.source, args.output))
    print("  answers copied:        %d" % report["answers"])
    print("  Master Template rows:  %d" % report["master_rows"])
    print("  Custom Controls rows:  %d" % report["custom_rows"])
    if report["examples_kept"]:
        print("  example rows kept:     %s" % ", ".join(report["examples_kept"]))
    for w in report["warnings"]:
        print("  WARNING: " + w)
    if report["new_sheets"]:
        print("Next: review the sheets new in this template version: %s" % ", ".join(report["new_sheets"]))


if __name__ == "__main__":
    main()

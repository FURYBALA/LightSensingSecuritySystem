#!/usr/bin/env python3
"""
Parses light_alarm.raw (LTspice ASCII raw output, produced by
`ltspice -b -ascii light_alarm.cir`) into rows of the swept photocurrent
(Iph) against the resulting base voltage, LED current, and transistor
collector current -- the real evidence behind this repo's "more light
-> alarm activates" finding.

Usage: python parse_results.py [path/to/light_alarm.raw]
"""
import sys


def var_names_and_rows(path):
    """Returns (var_names, rows): var_names is the ordered list of
    variable names from the .raw file's header; rows is a list of
    float lists, one per simulation step, in the same column order."""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [line.rstrip('\n') for line in f]

    var_names = []
    values_start = None
    in_variables = False
    for i, line in enumerate(lines):
        if line.strip() == 'Variables:':
            in_variables = True
            continue
        if line.strip() == 'Values:':
            values_start = i + 1
            break
        if in_variables:
            parts = [p for p in line.split('\t') if p != '']
            if len(parts) >= 2 and parts[0].strip().isdigit():
                var_names.append(parts[1].strip())

    n_vars = len(var_names)
    if values_start is None or n_vars == 0:
        raise ValueError("Could not parse header -- is this a real LTspice ASCII .raw file?")

    # Each step block: a line "<step_index>\t<value0>", then (n_vars - 1)
    # more lines each holding one value, indented with a leading tab.
    rows = []
    i = values_start
    while i < len(lines) and lines[i].strip() != '':
        first = [p for p in lines[i].split('\t') if p != '']
        if len(first) < 2:
            break
        row = [float(first[1])]
        i += 1
        for _ in range(n_vars - 1):
            row.append(float(lines[i].strip()))
            i += 1
        rows.append(row)

    return var_names, rows


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'light_alarm.raw'
    var_names, rows = var_names_and_rows(path)
    idx = {name: k for k, name in enumerate(var_names)}

    def col(row, name):
        return row[idx[name]]

    print(f"{'Iph (A)':>10} | {'V(base) (V)':>12} | {'V(emit) (V)':>12} | {'I(LED) (A)':>12} | {'Ic(Q1) (A)':>12} | State")
    print('-' * 90)
    for row in rows:
        iph = col(row, 'iph')
        vbase = col(row, 'V(base)')
        vemit = col(row, 'V(emit)')
        iled = col(row, 'I(D_LED)')
        ic = col(row, 'Ic(Q1)')
        if iled < 1e-6:
            state = 'OFF (dark / below threshold)'
        elif iled < 5e-3:
            state = 'DIM (transitioning)'
        else:
            state = 'ON (LED visibly lit)'
        print(f"{iph:10.2e} | {vbase:12.4f} | {vemit:12.4f} | {iled:12.4e} | {ic:12.4e} | {state}")


if __name__ == '__main__':
    main()

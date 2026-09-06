#!/usr/bin/env python3
"""
Real regression check against light_alarm.raw: confirms the two claims
this repo actually makes -- the circuit is OFF in the dark and ON in
bright (simulated) light. Used by CI so a netlist change that breaks
either claim fails the build, not just "did LTspice exit 0".

Usage: python check_regression.py [path/to/light_alarm.raw]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_results import var_names_and_rows  # noqa: E402

path = sys.argv[1] if len(sys.argv) > 1 else 'light_alarm.raw'
var_names, rows = var_names_and_rows(path)
idx = {name: k for k, name in enumerate(var_names)}

failures = []

first, last = rows[0], rows[-1]
iph_first = first[idx['iph']]
iph_last = last[idx['iph']]
iled_first = first[idx['I(D_LED)']]
iled_last = last[idx['I(D_LED)']]

print(f"Dark point:  Iph={iph_first:.2e} A -> I(LED)={iled_first:.4e} A")
print(f"Bright point: Iph={iph_last:.2e} A -> I(LED)={iled_last:.4e} A")

if iph_first != 0:
    failures.append(f"expected the first sweep point to be Iph=0 (dark), got {iph_first!r}")
if iled_first >= 1e-6:
    failures.append(f"expected the LED to be OFF in the dark (I(LED) < 1e-6 A), got {iled_first!r}")
if iled_last <= 1e-3:
    failures.append(f"expected the LED to be clearly ON at the brightest sweep point (I(LED) > 1e-3 A), got {iled_last!r}")

if failures:
    print("\nREGRESSION CHECK: FAIL")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print("\nREGRESSION CHECK: PASS")
sys.exit(0)

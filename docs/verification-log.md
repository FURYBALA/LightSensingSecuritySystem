# Verification log

A real record of actually simulating this circuit (LTspice 26.0.2), not
a description of expected behavior. One real inconsistency was found in
the report's own narrative by reading it carefully, then independently
confirmed by simulation rather than left as a hand-wavy theoretical
claim.

The starting point was
[`docs/PCB MINI PROJECT.pdf`](PCB%20MINI%20PROJECT.pdf), a mini project
report for **21ECC101J -- Electronic System and PCB Design**,
originally submitted by a team of four (B.V. Balanilavan, P. Sukesh,
K. Hemanth, Keshav B.S.). It documents a real, physically-built and
photographed breadboard circuit (see page 4 of the report) -- this
repository does not dispute that the physical build exists or that its
demonstration photos are genuine. What's added here is an independent
circuit simulation, to check the report's own narrative claims against
the circuit's actual, modeled behavior.

## Finding: the report describes two different (and contradictory) trigger conditions

**Introduction** (page 2): *"This system uses a simple electronic
circuit to detect changes in IR light levels caused by an obstruction
(such as a person passing through a doorway) and triggers an alert..."*
-- this describes a **beam-break sensor**: a constant IR light source
normally illuminates the photodiode, and something moving through the
monitored space *blocks* it, i.e. **light decreasing** should trigger
the alarm.

**Background and Theory** (page 2) and the demonstration photos (page
4), however, describe and show the opposite: *"exposure to infrared
radiation increases conductivity"* and the test photo shows a lit torch
being brought close to the sensor, which is what makes the LED turn
on -- i.e. **light increasing** triggers the alarm. This matches a
flame/fire-detection framing (also present in the Background section),
not an obstruction/doorway framing.

**These two descriptions require opposite circuit behavior.** A real
obstruction detector (light decreasing -> alarm) would need the alarm
condition to be "photodiode current below a threshold," which is not
what this circuit's actual topology implements.

**Confirmed by simulation, not just circuit-theory reasoning**: see
[Simulation results](#simulation-results) below. At `Iph=0` (dark, i.e.
what a beam-break sensor would see when its doorway is *blocked*), the
LED is completely off (`I(LED)` on the order of `1e-20 A`, i.e. zero).
As `Iph` increases (more light, i.e. what a beam-break sensor would see
when its doorway is *clear*), the LED turns progressively on. **This is
the exact opposite of what the Introduction's "obstruction" framing
would require**: in this circuit, a person walking through the doorway
and blocking the light would turn the alarm *off*, not trigger it.

**Conclusion**: the circuit is a real, working "more light -> alarm"
design (consistent with the Background/Theory section and the
demonstration photos), but the Introduction's framing doesn't describe
what this specific circuit does. This is a narrative/documentation
inconsistency in the original report, not a claim that the built
circuit doesn't work -- it does exactly what the Background section and
the demo photos show, just not what the Introduction's doorway example
describes.

## Secondary finding: this is a breadboard build, not a fabricated PCB

The report is submitted for **21ECC101J -- Electronic System and PCB
Design**, lists "PCB breadboard-MB102" as a component, and captions its
demonstration photos "Fabricated pcb assembly image." Its own
Methodology section (step 2) also describes *"Components are mounted
on the PCB with precise soldering."*

**MB102 is a specific, well-known solderless breadboard model** (a
830-tie-point prototyping board), not a printed circuit board -- and
the report's own photos (page 4) clearly show a solderless breadboard
(visible component leads plugged into holes, jumper wires), not a
soldered/etched PCB. No soldering is visible in either photo.

This doesn't affect whether the circuit works (it's a standard,
reasonable way to prototype a course project), but "fabricated PCB" and
"precise soldering" describe a different, more involved deliverable
than what the photos actually show. Worth naming plainly rather than
repeating the "fabricated PCB" description as if it were verified here.

## Simulation methodology

`sim/light_alarm.cir` reconstructs the circuit's topology (photodiode,
100k bias resistor, BC548, LED, 100 ohm resistor, buzzer) using real,
citable SPICE models where the report specifies a part number, and
clearly-labeled generic approximations where it doesn't. Full
model-by-model breakdown, including exactly which models are real
manufacturer/library models versus which are generic approximations
and why: [`docs/circuit-analysis.md`](circuit-analysis.md).

SPICE has no native concept of "light" -- the standard modeling
technique (used here) is a real diode junction in parallel with a
current source (`I_PH`) representing photocurrent, swept across a
decade range (0 to 1mA) to stand in for light level from dark to
bright. This is not a measurement of the real photodiode's actual
sensitivity (no specific photodiode part number was given in the report
to look up real numbers for) -- it's a check of the *circuit's* response
shape (does it turn on as light increases, and if so, over what range),
which is exactly what's needed to check the Introduction-vs-Theory
inconsistency above.

## Simulation results

Real output from `sim/run.ps1` (re-run and captured for this document,
not illustrative):

```
   Iph (A) |  V(base) (V) |  V(emit) (V) |   I(LED) (A) |   Ic(Q1) (A) | State
------------------------------------------------------------------------------------------
  0.00e+00 |       0.0004 |       0.0000 |   1.0341e-20 |   9.1944e-12 | OFF (dark / below threshold)
  1.00e-09 |       0.0005 |       0.0000 |   1.0493e-20 |   9.1944e-12 | OFF (dark / below threshold)
  1.00e-08 |       0.0014 |       0.0000 |   1.1871e-20 |   9.1944e-12 | OFF (dark / below threshold)
  1.00e-07 |       0.0104 |       0.0000 |   2.7263e-20 |   9.1944e-12 | OFF (dark / below threshold)
  3.00e-07 |       0.0304 |       0.0000 |   7.6212e-20 |   9.2086e-12 | OFF (dark / below threshold)
  1.00e-06 |       0.1004 |       0.0000 |   8.4562e-19 |   1.0054e-11 | OFF (dark / below threshold)
  3.00e-06 |       0.3004 |       0.0000 |   1.1735e-15 |   2.2877e-09 | OFF (dark / below threshold)
  1.00e-05 |       0.8366 |       0.2216 |   8.3347e-10 |   4.4150e-04 | OFF (dark / below threshold)
  3.00e-05 |       2.0596 |       1.3935 |   1.4960e-04 |   2.9272e-03 | DIM (transitioning)
  1.00e-04 |       3.8173 |       3.0901 |   1.2817e-02 |   1.8935e-02 | ON (LED visibly lit)
  3.00e-04 |       7.1079 |       6.3230 |   4.3944e-02 |   5.6361e-02 | ON (LED visibly lit)
  1.00e-03 |       9.5725 |       8.7548 |   6.7833e-02 |   8.4916e-02 | ON (LED visibly lit)
```
Reproduced across multiple independent runs (deterministic operating-
point sweep, no randomness or transient behavior involved).

**Reading this table**:
- **Dark state confirmed OFF**: at `Iph=0`, `I(LED)` is on the order of
  `1e-20 A` -- effectively zero, well below anything a real LED could
  visibly emit at. The transistor is fully cut off.
- **Turn-on is gradual, not a sharp switch**: `I(LED)` rises smoothly
  across roughly two decades of `Iph` (10uA to 100uA) rather than
  snapping on at one threshold. This is expected: the circuit has no
  positive feedback/hysteresis (no Schmitt trigger or comparator), so
  it behaves as a graded light-level indicator, not a clean digital
  switch. A real build could plausibly flicker near the transition
  region rather than switching cleanly.
- **A real, lit LED needs meaningfully more light than a bare
  "just detectable" signal**: `I(LED)` only reaches typical real LED
  operating currents (order 10-70mA) once `Iph` reaches ~100uA or
  higher; at 10uA, `I(LED)` is still ~9 orders of magnitude below that.

## What this does and doesn't prove

**Proves**: the circuit's topology, as drawn in the report and
reconstructed in `sim/light_alarm.cir`, produces monotonically
increasing LED/buzzer activation as modeled photocurrent increases, and
is fully off in the dark state -- confirmed by an actual SPICE
simulation using real, citable component models where a part number was
given, not by hand-waving through the schematic. This directly confirms
the Introduction-vs-Theory inconsistency described above using
quantified simulation data, not just circuit-theory argument.

**Doesn't prove**: the exact numeric photocurrent threshold of a real,
physical IR photodiode (no specific part number was given in the report
to source real photocurrent-vs-illuminance data for); that the physical
breadboard build shown in the report's own photos behaves identically
to this simulation (the report's photos are its own independent
evidence, not re-verified here); the buzzer's real acoustic/electrical
behavior (modeled here as a plain resistor, an explicit simplification);
any performance, reliability, or environmental characteristic (never
measured, never claimed).

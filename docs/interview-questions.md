# Interview preparation

Questions an interviewer could reasonably ask about this project, with
where in the repo to find the real answer -- not a generic textbook
answer. Only questions this specific implementation can actually
answer are included.

## Analog circuit design

**How does the photodiode actually turn the transistor on?**
It's reverse-biased (cathode toward the 9V rail, anode toward the
transistor's base). A reverse-biased photodiode's leakage current
increases with incident light -- that current flows into the base node,
develops a voltage across the 100k resistor (`R1`) to ground, and that
voltage is what drives the transistor's base. See
[`docs/circuit-analysis.md`](circuit-analysis.md).

**Why is R1 100k specifically, and not some other value?**
Not independently verified against a design calculation in the
report -- it's the value given, and it's a reasonable order of
magnitude for converting a photodiode's typically small (nA-uA)
photocurrent into a usable base voltage without loading the signal
down. A larger R1 would trigger at lower light levels (more sensitive,
slower); a smaller R1 would need more light to reach the same base
voltage.

**Why BC548, and what does it actually do here?**
It's used purely as a current amplifier/switch: the small photodiode
current into its base is amplified (by its current gain, `BF` in the
SPICE model) into a much larger emitter current, enough to actually
light an LED and drive a buzzer. BC548 is a very common, cheap general-
purpose small-signal NPN, appropriate for this low-current switching
role.

**What determines whether the LED is bright or dim, in this design?**
There's no hysteresis or comparator here -- it's a simple linear
current-amplifier stage, so LED brightness tracks the photodiode's
current roughly continuously (see the simulation table in
[verification-log.md](verification-log.md#simulation-results): `I(LED)`
rises smoothly over about two decades of `Iph`, not a sharp on/off
transition). A real build could visibly flicker or sit at partial
brightness near the transition region, not switch cleanly, because
nothing in this circuit provides positive feedback.

**What's the role of the 100 ohm resistor by the LED?**
Current limiting -- without it, the LED (a low-dynamic-resistance
device once forward-biased) would be limited only by the transistor's
saturation resistance and the supply voltage, risking excessive current.

**Is this circuit an obstruction/intrusion detector, as the report's Introduction claims?**
No -- checked directly, not assumed. See
[the finding in verification-log.md](verification-log.md#finding-the-report-describes-two-different-and-contradictory-trigger-conditions):
the report's Introduction describes a beam-break sensor (light
*decreasing* should trigger the alarm), but the actual circuit -- and
the report's own Background section and demo photos -- show the
opposite (light *increasing* triggers it). A person blocking a light
source in this circuit would turn the alarm off, not on.

**Is this actually a "fabricated PCB," as the report captions it?**
No -- the report's own photos show a solderless breadboard (MB102, a
specific well-known breadboard model, listed as a component), not an
etched/soldered PCB. See
[the secondary finding in verification-log.md](verification-log.md#secondary-finding-this-is-a-breadboard-build-not-a-fabricated-pcb).
Doesn't affect whether the circuit works -- it's a completely reasonable
way to prototype a course project -- just worth naming plainly rather
than repeating the "fabricated PCB" description unverified.

## SPICE simulation

**Why LTspice, and not a manufacturer's own tool?**
Free, real, industry-standard (Analog Devices), and available for this
environment via `winget install --id=AnalogDevices.LTspice -e`. No
academic/paid license needed, unlike many vendor PCB/SPICE suites.

**How do you simulate "light" in SPICE, which has no concept of illumination?**
An ideal diode junction (the photodiode's real I-V curve when *not*
illuminated) in parallel with a current source representing
photocurrent -- the standard textbook technique. See
[circuit-analysis.md](circuit-analysis.md#spice-model-whats-real-and-whats-approximated).
The current source's value is swept across a decade range as the
simulation's independent "light level" variable.

**Are the component models in this simulation real, or made up?**
Mixed, and documented as such: the BC548 model (`BC548BP`, Zetex) and
the photodiode's diode-junction model (`D1N4148`, NXP) are both real,
citable models from public SPICE libraries -- neither was invented.
The LED model is a generic approximation (no LED part number was given
to verify against), and the buzzer is modeled as a plain resistor
(explicitly not a real buzzer model). See the table in
[circuit-analysis.md](circuit-analysis.md#spice-model-whats-real-and-whats-approximated)
for exactly which is which and why.

**How is the simulation actually run and verified, end to end?**
`sim/run.ps1` calls `LTspice.exe -b -ascii` (batch mode, no GUI) on
`sim/light_alarm.cir`, producing a real `.raw` results file, which
`sim/parse_results.py` parses into the table shown in the README --
nothing here is a hand-typed "expected" result; it's real solver
output, re-run and re-captured for this documentation.

**How did you make sure you had the SPICE current-source sign convention right?**
Tested it directly with a two-line netlist before trusting it in the
real circuit: `I1 1 0 1m` with `R1 1 0 1k` gives `V(1) = -1V` (current
pulled *out* of node 1), while `I1 0 1 1m` gives `V(1) = +1V` (current
injected *into* node 1) -- confirmed empirically rather than assumed
from memory, since getting this backwards would have silently modeled
the photodiode's current flowing the wrong direction.

## Software/verification engineering (transferable from the other two projects)

**What's the common thread between this project and your Verilog/Python repos?**
The same verification discipline applied to a different domain: don't
trust a report's narrative claims (or your own first assumption) --
check them against something that actually runs, and document exactly
what was verified versus approximated versus not checked at all. Here
that meant an actual SPICE simulation instead of a testbench or a
`pytest` suite, but the standard is the same.

**What would you need to do to make this claim production-grade?**
Get a real photodiode part number and its actual photocurrent-vs-
illuminance datasheet curve (this simulation's `Iph` sweep is a stand-in
range, not measured against a real part); get a real LED part number
for its actual forward-voltage curve; measure the physical breadboard
build's actual transition threshold with a lux meter and compare
against this simulation.

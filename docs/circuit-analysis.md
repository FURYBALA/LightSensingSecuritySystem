# Circuit analysis

How the circuit in
[`docs/PCB MINI PROJECT.pdf`](PCB%20MINI%20PROJECT.pdf) (page 3) actually
works, and how it's modeled in [`sim/light_alarm.cir`](../sim/light_alarm.cir).
For real, current simulation results, see the
[README](../README.md#simulation-results); for the full story of what
was found and why, see [`verification-log.md`](verification-log.md).

## Topology, as drawn in the report

```
        9V DC supply
              |
       +------+------+
       |             |
   [Photodiode]      C (collector)
   cathode->VCC     [Q1: BC548]
   anode->BASE       B (base)---+---[R1: 100k]---GND
                      E (emitter)
                       |
                     [LED]
                       |
                   [100 ohm]---GND
                       |
                   [Buzzer, in parallel with the LED branch]---GND
```

- **Photodiode**: cathode toward the 9V rail, anode toward the transistor's
  base -- i.e. reverse-biased. A reverse-biased photodiode's current
  increases with incident light (its normal operating mode), so more IR
  light means more current flowing from the 9V rail, through the
  photodiode, into the base node.
- **R1 (100k)**: from the base node to ground. This converts the
  photodiode's light-dependent current into a voltage at the base --
  no light, no current, `V(base)` stays near 0V; more light, higher
  `V(base)`.
- **Q1 (BC548)**: collector tied directly to the 9V rail, base driven by
  the photodiode/R1 node, emitter feeding the LED and buzzer. As
  `V(base)` rises, the transistor conducts more, pulling more current
  through the emitter into the LED/buzzer branch.
- **LED + 100 ohm resistor + buzzer**: the load. The 100 ohm resistor
  limits LED current; the buzzer branch is drawn in parallel with the
  LED, carrying current whenever the LED does (modeled here as a plain
  resistor, not a real acoustic buzzer -- see the table below).

**The resulting behavior, by construction**: more IR light -> more
photodiode current -> higher base voltage -> more collector/emitter
current -> LED brighter, buzzer-branch current higher. Darkness -> no
photodiode current -> transistor off -> LED off, buzzer-branch current
zero. See
[verification-log.md](verification-log.md#finding-the-report-describes-two-different-and-contradictory-trigger-conditions)
for why this matters: it's the opposite of what the report's own
Introduction claims the system detects.

## SPICE model: what's real and what's approximated

[`sim/light_alarm.cir`](../sim/light_alarm.cir) reconstructs this exact
topology. Three real component models are used, none fabricated -- each
is either a genuine, citable manufacturer/library SPICE model, or an
explicitly-labeled generic approximation where the report itself doesn't
specify a part number:

| Component | Model used | Status |
|---|---|---|
| Q1 (BC548) | `BC548BP`, Zetex Semiconductors, rev. 4/90 | **Real, citable** -- via the public [`juanbravo/LTSpiceIUT`](https://github.com/juanbravo/LTSpiceIUT) library. BC548BP is a specific manufacturer package/grade of the BC548 family; a verified model for a generic/unbranded BC548 wasn't found, so this stands in for it. |
| Photodiode's diode junction | `D1N4148`, NXP Semiconductors | **Real, citable** -- via the public [`neiser/spice-padiwa-amps`](https://github.com/neiser/spice-padiwa-amps) library. The report names no specific photodiode part, so a generic small-signal silicon diode junction is used for the non-photosensitive I-V characteristic; **the actual "photo" behavior comes entirely from the separate `I_PH` current source below, not from this diode model.** |
| LED | `LED_GENERIC` | **Approximate, not independently verified against a specific manufacturer datasheet** -- the report names no LED part number either. Parameterized to give a realistic ~1.7-1.8V forward voltage at a few mA, since a real LED's forward voltage is much higher than a signal diode's (~0.6-0.7V) and that difference matters for checking whether the circuit has enough voltage headroom to actually light it. |
| Buzzer | A 500 ohm resistor from the emitter node to ground | **Explicit simplification, not a real buzzer model.** A piezo/magnetic buzzer isn't representable as a simple SPICE primitive, and the report gives no electrical spec for it. This only matters for the total current drawn; it does not affect whether the LED lights up. |

**How "light level" is modeled**: SPICE has no native concept of
illumination. The standard technique -- used here -- is an ideal diode
junction (`D1N4148`, the photodiode's real I-V curve when *not*
illuminated) in parallel with a current source (`I_PH`) representing
the light-dependent photocurrent. `I_PH` is swept across a decade range
(0 to 1mA) as the simulation's independent variable, standing in for
"IR light level from dark to bright." This is a modeling technique, not
a specific manufacturer's photodiode model -- there being no part
number to model exactly.

## Reproducing the simulation

Requires [LTspice](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
(free): `winget install --id=AnalogDevices.LTspice -e`. Verified against
LTspice 26.0.2 on Windows.

```powershell
powershell -File sim/run.ps1
```

Runs `sim/light_alarm.cir` in batch mode (`ltspice -b -ascii`, no GUI),
then parses the resulting `.raw` file into the table shown in the
README. See [`sim/parse_results.py`](../sim/parse_results.py) for the
parser.

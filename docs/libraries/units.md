# Units and physical quantities { #units }

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span>

Onika stores every physical value in one **internal unit system**. Values
read from input files are converted to it, so operators never deal with
units. This page describes the units, how to choose the internal system, and
the C++ API (`onika/physics/units.h`). Examples were run against Onika 1.1.0.

## Units

| Class | Units (symbol) |
|---|---|
| length | `m`, `mm`, `um` (micron), `nm`, `ang` (ångström) |
| mass | `kg`, `g`, `Da` (Dalton, atomic mass unit) |
| time | `h`, `s`, `us`, `ns`, `ps`, `fs` |
| charge | `C`, `e-` (elementary charge) |
| temperature | `K` |
| amount | `mol`, `particle` (1/N<sub>A</sub> mol) |
| luminosity | `cd` |
| angle | `rad`, `degree` |
| energy | `J`, `kJ`, `eV`, `cal`, `kcal` |

In input files, units follow the value after a space, combined with `.`, `/`
and powers `^` (see [Values and units](../inputs/msp-language.md#values-and-units)).
An unknown unit stops the run with the list of valid symbols
(`unknown unit 'femtos' in 'femtos'. Valid units are: m mm um nm ang ...`):

``` yaml
global:
  dt: 2.0 fs
  velocity: 3.0 ang/ps
  acc: 9.81 m.s^-2
  force: 0.1 eV/ang
```

## The internal unit system { #internal-unit-system }

The default internal system is **SI** (`m, kg, s, C, K, mol, cd, rad`). Two
settings change it, and **when** a value is converted matters:

| Setting | Effect |
|---|---|
| `--physics-units` (or `configuration: { physics: { units: ... } }`) | Sets the internal system **before the graph is built**. Applies to every value, including those of `global`. |
| `unit_system` operator | Changes the internal system **when it runs**. Applies to the parameters of operators that run **after** it (operator parameters are converted when the operator first runs), but not to `global` values, already converted. |

With the same unit system (Å, Da, ps, e, K, particle, cd, rad):

``` yaml
global:
  dt: 2.0 fs                        # converted at graph construction
simulation:
  - print_real: { value: 2.0 fs, prefix: "before: ", suffix: "\n" }
  - unit_system:
      unit_system: { length: angstrom , mass: Dalton , time: picosecond , charge: elementary_charge , temperature: kelvin , amount: particle , luminosity: candela , angle: radian , energy: electron_volt }
  - print_real: { value: 2.0 fs, prefix: "after: ", suffix: "\n" }
```

``` text
before: 2.0000000000e-15
after: 2.0000000000e-03
```

and `dt` from `global` is `2.0e-15` (SI). With
`--physics-units '{ length: angstrom , mass: Dalton , time: picosecond , ... }'`,
`dt` is `2.0e-03` too.

!!! tip

    To use one unit system everywhere, set it with `--physics-units` (or in the
    `configuration` block of a default input file), and keep the
    `unit_system` operator only for its `verbose: true` report.

Unit **names** (`angstrom`, `Dalton`, `picosecond`, `elementary_charge`,
`particle`, `electron_volt`...) are used to define unit systems; they are
listed by `unit_system: { verbose: true }`. Energies are not a base unit: they
are converted through mass, length and time (1 eV = 9648.5 Da·Å²/ps²).

The CMake variable `ONIKA_INTERNAL_UNIT_SYSTEM` (C++ names of 8 units:
length, mass, time, charge, temperature, amount, luminosity, angle) sets the
initial value of the internal system in C++. `onika::app::init()` then applies
`--physics-units` (SI by default), so it only matters for code that runs
before or without `init()`.

## C++ API

A `onika::physics::Quantity` is a value with units. It converts implicitly to
`double` in the internal unit system:

``` cpp
#include <onika/physics/units.h>
#include <onika/physics/constants.h>
using namespace onika::physics;

Quantity dt = 2.0 * fetosecond;                     // from unit definitions
Quantity e  = ONIKA_QUANTITY( 1.5 * eV );           // short unit symbols inside the macro
Quantity v  = make_quantity( 3.0, "ang/ps" );       // value + unit string
Quantity f  = quantity_from_string( "0.1 eV/ang" ); // whole string, as in input files

double dt_internal = dt;                            // implicit conversion to the internal system
std::cout << "dt = " << dt.convert() << " s , e = " << e.convert() << " J , v = " << v.convert()
          << " m/s , f = " << f.convert() << " N" << std::endl;

// conversion to any other system
UnitSystem md_units = { { angstrom, atomic_mass_unit, picosecond, elementary_charge, kelvin, particle, candela, radian, electron_volt } };
std::cout << "e in Da.ang^2/ps^2: " << e.convert( md_units ) << std::endl;
```

``` text
dt = 2e-15 s , e = 2.40326e-19 J , v = 300 m/s , f = 1.60218e-10 N
e in Da.ang^2/ps^2: 14472.8
```

| API | Meaning |
|---|---|
| `value * unit`, `unit ^ p`, `q * q`, `q / q`, `q ^ p` | Build quantities from unit definitions (`meter`, `angstrom`, `fetosecond`, `electron_volt`...). All `constexpr` and usable on GPU. |
| `ONIKA_QUANTITY( expr )` | Same, with short symbols: `m mm um nm ang kg g Da h s us ns ps fs C ec K mol cd rad degree J kJ eV cal kcal`. |
| `ONIKA_CONST_QUANTITY( expr )` | Same, for `constexpr` / global constants (no capture). |
| `make_quantity(value, "units")` | Units as in input files (`"ang/ps"`, `"m.s^-2"`). |
| `quantity_from_string("3.0 ang/ps")` | Value and units; the value can be an [arithmetic expression](../inputs/msp-language.md#msp-expressions). |
| `q.convert()` | Value in the internal unit system (same as `double(q)`). |
| `q.convert(system)` | Value in another `UnitSystem`. |
| `internal_unit_system()`, `set_internal_unit_system(s)` | Read / change the internal system. |
| `unit_from_name("angstrom")`, `unit_from_symbol("ang")` | Find a `UnitDefinition`. |

A slot of type `Quantity` read from YAML accepts `3.0 ang/ps` or
`{ value: 3.0 , unity: ang/ps }`. Usually slots are simply `double`: the
conversion happens when the input file is read.

## Physical constants

`onika/physics/constants.h`, SI values in namespace `onika::physics`:
`atomicMass` (kg), `elementaryCharge` (C), `boltzmann` (J/K), `avogadro`,
`epsilonZero` (F/m), `calorie_joules`, `pi`, `e`, `phi`.

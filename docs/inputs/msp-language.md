# The input file language

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span>

An Onika input file (`.msp`) is a YAML file that describes the
**simulation graph**: which operators run, in which order, with which values.
This page describes every construct. For a guided introduction, see
[Your first input file](../getting-started/first-input.md).

## Structure of a file

The top level of an input file is a map. A few keys are special, all others
define operators or batches:

| Key | Meaning |
|---|---|
| `simulation` | Entry point: the operator (usually a list) that Onika runs. |
| `includes` | List of other input files to load first. See [Includes and merging](#msp-includes). |
| `configuration` | Settings of the Onika runtime (logging, profiling, threads, GPU...). See [The `configuration` block](configuration.md). |
| *any other name* | Default values for an operator of that name, or the definition of a new **batch** (named group of operators). |

``` yaml
includes: [ my_defaults.msp ]     # optional

configuration:                    # optional
  logging: { debug: false }

global:                           # default values for operator 'global'
  dt: 1.0

my_step:                          # a new batch
  - next_time_step
  - print_timestep

simulation:                       # what runs
  - global
  - my_step
```

## Calling operators

In a list, each item calls an operator in one of two forms:

``` yaml
- next_time_step                                  # name only: default values
- print_int: { prefix: "t = ", suffix: "\n" }     # name: map of slot values
```

The map sets the values of the operator's slots. Use `onika-exec --help <operator>` to list the slots of an operator.

!!! warning

    A key that matches no slot is silently ignored. Check the spelling of slot
    names against `--help <operator>` or `--debug-graph`.

!!! tip

    Some operators accept a shortcut. For example `message: "Hello"` is the
    same as `message: { mesg: "Hello" }`.

### Values and units

Slot values are YAML values converted to the slot type. Real values can carry
a **unit**; they are converted to the internal unit system (SI by default):

``` yaml
global:
  dt: 2.0 fs            # stored as 2.0e-15 (seconds)
  len: 1.5 ang          # stored as 1.5e-10 (meters)
  acc: 9.81 m.s^-2      # units combine with '.', powers with '^'
```

### Arithmetic expressions { #msp-expressions }

A real value can be an **arithmetic expression** (evaluated with the
[TinyExpr](https://github.com/codeplea/tinyexpr) library bundled with Onika), optionally followed by a unit. The expression must not contain spaces:
the first space separates it from the unit.

``` yaml
global:
  a: 2*3.5              # 7
  b: sqrt(2) m          # 1.4142135624 (meters)
  c: pi/4               # 0.7853981634
  d: 1.5e-3*2 fs        # 3.0e-18 (seconds)
```

Available: `+ - * / ^ %`, parentheses, the constants `pi` and `e`, and the
functions `abs acos asin atan atan2 ceil cos cosh exp fac floor ln log log10
ncr npr pow sin sinh sqrt tan tanh` and `rand()` (uniform in `[0,1)`).
`rand()` uses the seed `--physics-rngseed` (default `1812433253`), so runs are
reproducible.

The internal unit system is set with `--physics-units`, or by the
`unit_system` operator for the operators that run after it. See
[Units and physical quantities](../libraries/units.md#internal-unit-system): the
difference matters.

## Batches { #msp-batches }

A **batch** is a named sequence of operators. Define it at the top level, then
use its name like any operator. Two forms exist:

``` yaml
# short form: a list
print_and_step:
  - print_timestep
  - next_time_step

# long form: a map with a 'body' and options
compute_loop:
  loop: true
  condition: compute_loop_continue
  body:
    - print_and_step
    - compute_loop_stop
```

A batch defined as a plain name is an **alias**: `init: nop` makes `init`
run `nop`.

Batch options (long form):

| Option | Value | Effect |
|---|---|---|
| `body` | list | The operators to run, in order. Required in the long form. |
| `rebind` | map `inner: outer` | Renames slots of the body. See [Rebinding slots](#msp-rebind). |
| `condition` | slot name, or `not <slot>` | Runs the body only if the boolean slot is true (or false with `not`). |
| `loop` | `true` / `false` | Runs the body again while `condition` is true. Without a condition, the loop never ends. |
| `unroll` | integer | With `loop: true`: copies the body N times per iteration. |
| `name` | string | Name shown in graphs and profiles (default: the batch key). |
| `profiling` | `true` / `false` | Forces profiling of this batch on or off. |
| `parallel` | `true` / `false` | Runs the operators of the body concurrently (nested parallelism). `cores` gives the share of cores of each operator. |
| `task_group` | `true` / `false` | Runs the body inside an OpenMP task group, so that asynchronous GPU/CPU work of the body can overlap. |

## How operators are connected { #msp-slots }

You never connect operators explicitly. **Slots with the same name are
connected**: an input slot reads the value of the last operator before it, in
execution order, that has an output slot with the same name. `global`
creates output slots from its values, so it is a common way to provide
parameters.

``` mermaid
flowchart LR
  g["global<br/>OUT dt, timestep"] -->|dt, timestep| n["next_time_step<br/>IN dt · IN/OUT timestep"]
  n -->|timestep| p["print_int<br/>IN value ← timestep"]
```

### Rebinding slots { #msp-rebind }

Slot names are chosen by the operator author, so they rarely match.
`rebind` renames slots of a batch body, seen from outside the batch:

``` yaml
print_timestep:
  rebind: { value: timestep }     # inner slot 'value' is called 'timestep' outside
  body:
    - print_int: { prefix: "Current timestep = ", suffix: "\n" }
```

Here `print_int` reads `timestep` without knowing that name. Rebinding
applies to all operators of the body.

### Unused operators are removed { #msp-pruning }

After building the graph, Onika **removes operators whose outputs are never
read** by a later operator. The log shows them as:

``` text
*SUPPRESS* simulation.compute_loop.scale_value
```

If an operator you expect to run disappears, check that its outputs are used,
or check with `--debug-graph`. Operators that only have side effects (print,
write files) have no outputs and are kept. Developers can also force this with
`is_sink()` (see [Keeping an operator in the graph: `is_sink()`](../operators/anatomy.md#operator-sink)).

## Includes and merging { #msp-includes }

``` yaml
includes:
  - common/material.msp
  - common/outputs.msp
```

Files are loaded in this order, each one merged on top of the previous ones:

1. `main-config.msp`, always first (see [The default file: `main-config.msp`](#msp-main-config));
2. the files in `includes`, recursively, each file only once;
3. your input file;
4. command-line options (see [Overriding values from the command line](#msp-command-line)).

Merging rules:

- **maps are merged** key by key, the last file wins;
- **lists and values are replaced**;
- a key prefixed with `+` **appends** to a list instead of replacing it.

``` yaml title="base.msp"
my_sequence:
  - message: "first"
```

``` yaml title="input.msp"
includes: [ base.msp ]

+my_sequence:                 # appends to my_sequence from base.msp
  - message: "second"
```

`--debug-files` prints the list of files actually loaded.

## The default file: `main-config.msp` { #msp-main-config }

Onika always loads `data/config/main-config.msp` first (found through
`ONIKA_CONFIG_PATH`). It defines a default `simulation`:

``` yaml title="main-config.msp (simplified)"
run: nop
init: nop

simulation:
  - message: "<Onika banner>"
  - mpi_comm_world
  - init_cuda
  - global
  - unit_system: { verbose: true, unit_system: { length: meter, mass: kilogram, ... } }
  - init
  - run
  - finalize_cuda
```

So you have two ways to write an input file:

- define `run` (and `init`) only: you keep MPI, GPU and unit system
  initialization, and add your own work;
- define `simulation`: you replace everything.

Applications built on Onika (exaNBody, exaStamp...) ship their own
`main-config.msp` with many predefined batches.

## Overriding values from the command line { #msp-command-line }

Any value can be changed at launch time with `--set-<path> <value>`, the
path being the YAML keys separated by `-`:

``` bash
$ onika-exec input.msp --set-global-nsteps 100 --set-global-dt "0.5 fs"
```

!!! warning

    In Onika 1.1.0, the `onikarun` wrapper splits arguments that contain
    spaces, so `--set-global-dt "0.5 fs"` fails with a YAML parse error.
    For such values, source `setup-env.sh` and call `onika-exec` directly.

The same override can be written in the input file, under `configuration`:

``` yaml
configuration:
  set:
    global: { nsteps: 100 }
```

Runtime options such as `--omp_num_threads` are described in [Command-line options](../running/command-line.md).

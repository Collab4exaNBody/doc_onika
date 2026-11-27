# Your first input file

<span class="badge badge-user">Simulation user</span>

We now rebuild the counter loop from scratch, in three steps. Each step is a
complete input file you can run with `onikarun <file>.msp`.

## Step 1: one operator

``` yaml title="step1.msp"
simulation:
  - message: "Hello from Onika"
```

``` text
Hello from Onika
```

`simulation` is the entry point: a list of operators run in order.
`message: "..."` runs the built-in `message` operator. It is a shortcut
for `message: { mesg: "..." }`: in general, an operator takes a map of
slot values.

!!! note

    Onika always loads `main-config.msp` (from `data/config`) before your
    file. Your `simulation` replaces the default one. To keep the default
    initialization (MPI, GPU, unit system) and only add your own operators,
    define `run` instead of `simulation`. See [The default file: `main-config.msp`](../inputs/msp-language.md#msp-main-config).

## Step 2: values and slots

``` yaml title="step2.msp"
global:
  timestep: 0
  dt: 1.0

print_timestep:
  rebind: { value: timestep }
  body:
    - print_int: { prefix: "timestep = ", suffix: "\n" }

simulation:
  - global
  - next_time_step
  - print_timestep
```

``` text
timestep = 1
```

- `global` creates one output slot per entry: `timestep` (an integer) and
  `dt` (a real). The type comes from the value.
- `next_time_step` reads `dt` and updates `timestep` and `physical_time`.
- `print_timestep` is a **batch**: a named group of operators. You define it
  once at the top level, then use its name like any operator.
  Its `rebind` connects the `value` slot of `print_int` to `timestep`.

## Step 3: a loop

``` yaml title="step3.msp"
global:
  timestep: 0
  dt: 1.0
  nsteps: 5
  compute_loop_continue: true

print_timestep:
  rebind: { value: timestep }
  body:
    - print_int: { prefix: "Current timestep = ", suffix: "\n" }

compute_loop_stop:
  rebind: { end_at: nsteps , result: compute_loop_continue }
  body:
    - sim_continue

compute_loop:
  loop: true
  condition: compute_loop_continue
  body:
    - print_timestep
    - next_time_step
    - compute_loop_stop

simulation:
  - global
  - compute_loop
```

``` text
Current timestep = 0
Current timestep = 1
...
Current timestep = 5
```

- `loop: true` + `condition: compute_loop_continue`: run the body again
  while the boolean slot `compute_loop_continue` is true.
- `sim_continue` sets its `result` to false once `timestep` goes past
  `end_at`. The rebind maps them to `compute_loop_continue` and `nsteps`.

Apart from `nsteps` and the setup operators, this is the `print_loop.msp` of
[Your first run](first-run.md). Everything used here is
described in [The input file language](../inputs/msp-language.md), and the operators in [Built-in operators](../reference/builtin-operators.md).

Next step: [Your first operator](first-operator.md), to add your own operator to this loop.

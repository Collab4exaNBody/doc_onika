# Python bindings: `pyonika` { #pyonika }

<span class="badge badge-user">Simulation user</span> <span class="badge badge-core">Framework developer</span>

`pyonika` drives Onika from Python: run an input file, change values, build
a graph from Python data, inspect operators and slots, run several
simulations in one process, and read results as Python values or NumPy
arrays. Errors become Python exceptions instead of stopping the process.

The examples on this page were run with Onika `main` (Python API merged after
1.1.0). The complete API reference is `python/README.md` in the Onika sources;
examples are in `python/examples`.

## Build and install

Configure Onika with `-DONIKA_BUILD_PYTHON=ON` (pybind11 is downloaded at
configure time if it is not installed), then install the package with the
**same** Python interpreter:

``` bash
$ cmake -S onika -B build-onika -DONIKA_BUILD_PYTHON=ON \
        -DPython3_EXECUTABLE=$(which python3) \
        -DCMAKE_INSTALL_PREFIX=$PWD/install-onika
$ cmake --build build-onika -j 8 --target install
$ pip install ./install-onika/python
```

The package requires `numpy` and only works with the Python version it was
built with. The install prefix is recorded in it: `import pyonika` sets
`ONIKA_PLUGIN_PATH`, `ONIKA_CONFIG_PATH` and `ONIKA_DATA_PATH` (unless they
are already set, e.g. by `setup-env.sh`) and initializes MPI. No other
environment setup is needed.

Without `pip install`, sourcing `<install-prefix>/bin/setup-env.sh` also adds
`<install-prefix>/python` to `PYTHONPATH`.

## Run an input file

The simplest use: one call runs a whole input file, with parameter
overrides and runtime options given as dicts.

``` python
import pyonika

rc = pyonika.run_file("step3.msp",
                      overrides={"global": {"nsteps": 1}},    # values of the input file
                      config={"omp_num_threads": 2})          # 'configuration' options
```

`run_file` returns 0, or the exit code of an early stop (`--help`...).
[`step3.msp`](../getting-started/first-input.md) is the counter loop of the
getting-started pages.

## Three patterns

For more control, use `init()`, `run()` and `end()`, as in
[the C++ API](../coupling/embedding.md). `init()` takes the same arguments as
`onika-exec`, reads the files, builds the graph and returns an
`ApplicationContext`; nothing runs yet.

=== "A · run an input file"

    The input file drives everything, as with `onika-exec`.

    ``` python
    import sys
    import pyonika

    ctx = pyonika.init([sys.argv[0], "step3.msp", "--omp_num_threads", "4"])
    if ctx.error_code >= 0:        # >= 0 means early exit (--help, ...)
        sys.exit(ctx.error_code)

    # inspect the graph before running
    ctx.node("simulation").apply_graph(lambda op: print(op.pathname()))

    pyonika.run(ctx)
    pyonika.end(ctx)
    ```

    ``` text
    simulation
    simulation.global
    simulation.compute_loop
    simulation.compute_loop.print_int
    ...
    Current timestep = 5
    ```

=== "B · build the graph in Python"

    No input file of your own: batches and values are Python dicts with the
    same structure as the YAML (here, the counter loop). `init()` on
    `main-config.msp` only starts the runtime.

    ``` python
    import os, sys
    import pyonika

    main_config = os.path.join(os.environ["ONIKA_CONFIG_PATH"], "main-config.msp")
    ctx = pyonika.init([sys.argv[0], main_config])

    pyonika.set_operator_defaults({
        "print_timestep": {
            "rebind": {"value": "timestep"},
            "body": [{"print_int": {"prefix": "Current timestep = ", "suffix": "\n"}}],
        },
        "compute_loop_stop": {
            "rebind": {"end_at": "nsteps", "result": "compute_loop_continue"},
            "body": ["sim_continue"],
        },
        "compute_loop": {
            "loop": True,
            "condition": "compute_loop_continue",
            "body": ["print_timestep", "next_time_step", "compute_loop_stop"],
        },
        "global": {"dt": 1.0, "nsteps": 20, "timestep": 0, "compute_loop_continue": True},
    })

    graph = pyonika.build_simulation_graph(ctx, ["global", "mpi_comm_world", "compute_loop"])
    pyonika.run_node(ctx, graph)
    pyonika.end(ctx)
    ```

=== "C · patch an input file"

    Load an input file, change some values, rebuild the graph, run it.
    Ideal for parameter studies.

    ``` python
    import sys
    import pyonika

    ctx = pyonika.init([sys.argv[0], "step3.msp"])
    if ctx.error_code >= 0:
        sys.exit(ctx.error_code)

    pyonika.set_operator_defaults({"global": {"nsteps": 2}})   # merged, not replaced
    graph = pyonika.build_simulation_graph(ctx)                # same 'simulation' as the file
    pyonika.run_node(ctx, graph)
    pyonika.end(ctx)
    ```

    ``` text
    Current timestep = 0
    Current timestep = 1
    Current timestep = 2
    ```

    !!! warning

        `pyonika.run(ctx)` would run the graph built by `init()`,
        *before* your changes. After `set_operator_defaults()`, always
        call `build_simulation_graph()` and `run_node()`, and look up nodes
        in the returned `graph` (`ctx.node()` searches the graph of `init()`).

The `.msp` file and Python data map one to one:

| YAML (`.msp`) | Python |
|---|---|
| `loop: true` | `"loop": True` |
| `- next_time_step` | `"next_time_step"` in a list |
| `- print_int: { prefix: "t" }` | `{"print_int": {"prefix": "t"}}` |

## Command-line options from Python

`init()` takes the arguments of `onika-exec`. `pyonika.command_line()` builds
them for you:

``` python
argv = pyonika.command_line("step3.msp",
                            overrides={"global": {"nsteps": 3}},   # merged through configuration.set
                            config={"omp_num_threads": 4})         # configuration options
ctx = pyonika.init(argv)
```

Options written by hand follow the [command-line](../running/command-line.md)
rules: `"--omp_num_threads", "4"` are two list elements, a boolean option
alone means `true` (`"--nogpu"`), and `-` separates nested keys, so the
option names must be spelled exactly (`--nogpu`, not `--no-gpu`).

## Read results

After a run, slots are read from the nodes of the graph:

``` python
ctx = pyonika.init(pyonika.command_line("step3.msp", overrides={"global": {"nsteps": 3}}))
pyonika.run(ctx)

loop = ctx.node("simulation.compute_loop")
print([name for name, slot in loop.out_slots()])       # ['compute_loop_continue', 'timestep', 'physical_time']
print(dict(loop.out_slots())["timestep"].value())      # 4
pyonika.end(ctx)
```

- `slot.value()` returns scalars, strings, lists and maps as Python values
  (parsed from the slot's YAML form), or `None` without a value.
- `node.slot_as_array("name")` returns a **NumPy copy** of a vector slot
  (`std::vector` of numbers, or of `std::array<double|float,3|4>` as an
  `(N,3)` / `(N,4)` array), or `None` for other types:

``` python
graph = pyonika.build_simulation_graph(ctx, ["default_slot_value_from_ctor_args"])
pyonika.run_node(ctx, graph)
nodes = []
graph.apply_graph(lambda op: nodes.append(op))
a = nodes[0].slot_as_array("input1")       # float64 array of shape (10,)
```

Values are only available in a graph that has run: on an operator created
alone with `make_operator()`, slots have types but no values. Use
`make_operator()` and `pyonika.describe_operator(name)` to inspect what an
operator expects:

``` python
d = pyonika.describe_operator("sim_continue")
print([s["name"] for s in d["slots"]])     # ['check_freq', 'end_at', 'remain', 'result', ...]
print(len(pyonika.available_operators()))  # all operators of the loaded plugins
```

## Errors

Errors that stop `onika-exec` (unknown operator, missing file, invalid
parameter, missing slot value...) raise `pyonika.OnikaError` (a
`RuntimeError`):

``` python
try:
    pyonika.init([sys.argv[0], "missing_file.msp"])
except pyonika.OnikaError as e:
    print(e)          # configuration file 'missing_file.msp' not found
```

The process still stops in three cases, where an exception cannot be
raised safely: an error inside an OpenMP parallel region, an error while
another exception is in flight, and any error with more than one MPI process
(`MPI_Abort`, so that the other ranks do not wait forever). After an error
raised by `run()` or `run_node()`, call `end(ctx)` and start again with a new
`init()`.

## Several simulations in one process

`init()` / `run()` / `end()` can be repeated. `pyonika` defers
`MPI_Finalize()` to the end of the Python process, so MPI stays available
across cycles:

``` python
for nsteps in [1, 3]:
    ctx = pyonika.init(pyonika.command_line("step3.msp"))
    pyonika.set_operator_defaults({"global": {"nsteps": nsteps}})
    graph = pyonika.build_simulation_graph(ctx)
    pyonika.run_node(ctx, graph)
    pyonika.end(ctx)
```

Do not call `MPI_Finalize()` yourself between cycles. Under `mpirun`, run
the same script on every process.

## Capture the output

Onika writes to the process output from C++. `pyonika.capture_output()`
redirects it during a block, for example into a string:

``` python
import io
buf = io.StringIO()
with pyonika.capture_output(buf):
    pyonika.run_file("step3.msp", overrides={"global": {"nsteps": 0}})
lines = [l for l in buf.getvalue().splitlines() if "timestep" in l]   # ['Current timestep = 0']
```

## API summary

| Function | Role |
|---|---|
| `run_file(msp, *args, overrides=, config=)` | `init` + `run` + `end`. |
| `command_line(msp, *args, overrides=, config=)` | Arguments for `init()`. |
| `init(argv)` | Reads the files, builds the graph; returns an `ApplicationContext`. |
| `run(ctx)`, `run_node(ctx, node)` | Run the graph of `init()`, or any graph/node. The GIL is released while running. |
| `end(ctx)` | Profiling output, frees resources. |
| `set_operator_defaults(dict)`, `get_operator_defaults()` | Merge / read the definitions of the input files (batches, `global`...). |
| `build_simulation_graph(ctx, simulation=None)` | Builds a graph from a `simulation` list (default: the one of the input file). |
| `make_operator(name, config={})`, `describe_operator(name)`, `available_operators()` | Create and inspect operators. |
| `capture_output(stream)` | Context manager redirecting C++ output. |
| `setup_env(prefixes)` | Adds plugin/config/data directories of other install prefixes (e.g. an application built on Onika). |

| `ApplicationContext` | `OperatorNode` | Slot |
|---|---|---|
| `node(path)`, `graph`, `error_code`, `mpi_rank`, `mpi_nprocs`, `ngpus`, `cpucount`, `set_multiple_run()` | `name()`, `pathname()`, `apply_graph(f)`, `in_slots()`, `out_slots()`, `slot_values()`, `slot_as_array(name)`, `describe()`, `documentation()`, `yaml_initialize(dict)` | `name()`, `value()`, `value_as_string()`, `has_value()`, `type_name()`, `direction()`, `is_required()`, `describe()`, `yaml_initialize(value)` |

## Examples

`python/examples` in the Onika sources:

- `pyonika_dryrun_test_import_pyonika.py`: installation check;
- `pyonika_run_main_config.py`: pattern A with graph and slot inspection;
- `pyonika_execute_user_specified_msp_file.py`: run any input file;
- `pyonika_reproduce_print_loop_case.py`: pattern B, the counter loop;
- `pyonika_run_simulation.py`: several `init`/`run`/`end` cycles;
- `pyonika_read_slot_values.py`: read slot values after a run;
- `pyonika_make_operator_usage.py`: create and inspect one operator.

The `pytest` suite (`python/tests`) is run by `ctest -R pyonika` in the build
directory.

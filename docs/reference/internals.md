# Framework internals { #internals }

<span class="badge badge-core">Framework developer</span>

A map of the Onika sources, for developers of Onika itself and of
applications that extend it. Each module is a directory of
`include/onika/` (headers) and `src/` (implementation).

| Module | Content | Documented in |
|---|---|---|
| `app/` | Application API (`init`, `run`, `end`), the `configuration` block (`ApplicationConfiguration`, `default_app_config.h`), profilers, graph output | [Using Onika from C++](../coupling/embedding.md), [The `configuration` block](../inputs/configuration.md) |
| `scg/` | Simulation component graph: `OperatorNode`, slots, factory, batches | [Anatomy](../operators/anatomy.md), [Advanced operators](../operators/advanced.md) |
| `scg-builtin-components/` (src) | Built-in operators | [Built-in operators](builtin-operators.md) |
| `parallel/`, `cuda/` | CPU/GPU parallel execution | [Parallel API](../operators/parallel.md) |
| `memory/`, `soatl/` | Allocators, SOATL containers | [Memory and containers](../libraries/memory.md) |
| `math/`, `physics/` | Math types, units | [Math types](../libraries/math.md), [Units](../libraries/units.md) |
| `mpi/` | MPI helpers | [MPI utilities](../libraries/mpi.md) |
| `yaml/`, top-level headers | Utilities | [Utilities](../libraries/utilities.md) |
| `omp/` | OpenMP tools (OMPT) and `detach` support | below |
| `trace/` | Execution trace formats | below, and [Execution traces](../running/profiling-debugging.md#execution-traces) |
| `dag/` | Task dependency graphs | below |
| `test/` | Embedded unit tests | [Unit tests](../libraries/utilities.md#unit-tests) |

## How a run proceeds

`onika::app::init()` (`src/core/api.cpp`) chains these steps:

1. read `ONIKA_CONFIG_PATH` / `ONIKA_DATA_PATH`;
2. parse the command line and load the input files (with `includes`, merged
   into one YAML document); the `configuration` block becomes an
   `ApplicationConfiguration`;
3. initialize MPI, OpenMP, logging, GPU (CUDA/HIP context), random seeds;
4. read or regenerate the plugin database (`plugins.db`);
5. run unit tests if `--run_unit_tests`, print help if `--help`;
6. set the internal unit system (`--physics-units`);
7. build the simulation graph from the `simulation` entry: the
   `OperatorNodeFactory` creates operators (loading their plugins on demand),
   batches connect slots by name, unused operators are removed (`*SUPPRESS*`),
   then every node is compiled.

`run()` calls `run()` on the root batch, which runs its children in order
(`run_prolog`, `execute`, `run_epilog` for each operator). `end()` writes
profiling output and frees all slot resources.

## The `configuration` block in C++

`include/onika/app/default_app_config.h` declares every option with macros:

``` cpp
ONIKA_APP_CONFIG_Begin( debug , "debuggin and introspection features" );
  ONIKA_APP_CONFIG_Item( bool , graph , false , "print operator graph" );
  ...
ONIKA_APP_CONFIG_End();
```

Each item is a member of `ApplicationConfiguration`, an entry of the
`configuration` YAML block and a command-line option (`--debug-graph`). Its
documentation string is printed by `--help command-line`. To add an option
to Onika, add an item here; it is then available as
`ctx->m_configuration->debug.graph` in C++.

## OpenMP tools: `omp/`

When `ONIKA_HAVE_OPENMP_TOOLS` is on (OpenMP ≥ 5), Onika registers an
**OMPT** tool (`ompt_interface.h`) that records the start and end of OpenMP
tasks (`OpenMPToolTaskTiming`). Operator timings and execution traces
(`--profiling-trace-*`) are built from these events.

`task_detach.h` provides `OMP_TASK_DETACH(sharing, other_clauses, evt)` and
`omp_fulfill_event`, a portable form of the OpenMP 5 `detach` clause: a task
whose completion is signaled later (for example when a GPU stream finishes).
With compilers without `detach` support (`ONIKA_HAVE_OPENMP_DETACH=OFF`), a
fallback is used.

## Traces: `trace/`

`TraceOutputFormat` is the interface of trace writers. Onika provides
`vite_trace_format.h` (ViTE), `yaml_trace_format.h`, `dot_trace_format.h`
and `tikz_trace_format.h` (LaTeX/TikZ). They are used by
`--profiling-trace-format` and by the `trace_convert` program (see
[Execution traces](../running/profiling-debugging.md#execution-traces)).

## Task dependency graphs: `dag/`

`dag/` describes **work-sharing DAGs**: sets of work items on a 1D/2D/3D grid
(for example the cells of a domain) with dependencies between them.
`WorkShareDAG<Nd>` stores items and their dependencies,
`WorkShareDAGExecution` counts remaining dependencies at run time (CPU or
GPU, with atomics), `reorder_dag` / `reorder_fast_dep_unlock` reorder items
to unlock dependencies early, `filter_dag` extracts a sub-graph, and `dot.h`
draws a DAG with Graphviz. Applications use them to run cell-based
computations as dependent tasks.

## Debugging Onika itself

- `ONIKA_DEBUG=1` in the environment turns on debug logging, plugin and file
  messages (`--logging-debug`, `--debug-plugins`, `--debug-files`,
  `--debug-verbose 2`).
- In a debug build, `onika-exec` prints a hint at startup: put a breakpoint on
  `simulation_start_breakpoint()` (all plugin symbols loaded) or
  `plugins_loaded_breakpoint()` in `gdb`.
- `--debug-graph_exec true` prints each operator as it starts and ends.

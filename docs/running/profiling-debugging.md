# Debugging and profiling

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span>

This page groups the options you need when something goes wrong or is slow.
All options are described in [Command-line options](command-line.md).

## When an operator does not run

| Check | How |
|---|---|
| Was it removed from the graph? | Look for `*SUPPRESS* <path>` in the log: its outputs are never used. See [Unused operators are removed](../inputs/msp-language.md#msp-pruning). |
| Is it in the graph, with the expected slots? | `--debug-graph`. Add `--debug-graph_lod 2` for more detail. |
| Is a slot name misspelled in the input file? | Unknown keys are silently ignored: compare with the slots listed by `--debug-graph` or `onika-exec --help <operator>`. |
| Which files were loaded, and the final YAML? | `--debug-files` and `--debug-yaml`. |
| Which runtime settings are used? | `--debug-config`. |
| Which operator ran last before a crash? | `--profiling-exectime` prints each operator when it finishes. |
| Is the problem GPU-related? | Run again with `--nogpu`. |
| Floating point errors (NaN, division by zero)? | `--debug-fpe` stops at the first exception (not available on macOS). |

Debug messages of your operators (`ldbg`) are shown with
`--logging-debug`, and can be limited to some operators with
`--debug-filter "[regex1, regex2]"`.

## The graph as a picture

`--debug-graph_fmt dot` writes the graph to `sim_graph.dot` (Graphviz)
instead of printing it, with one box per operator or batch and its slots:

``` bash
$ onikarun input.msp --debug-graph true --debug-graph_fmt dot
$ dot -Tsvg sim_graph.dot -o sim_graph.svg
```

Add `--debug-graph_rsc true` to show the slot resources (where the values are
stored), and `--debug-graph_lod <n>` for more or less detail.

## Where does the time go?

`--profiling-summary` prints a time table at the end of the run, following
the structure of the graph:

``` text
Profiling .........................................  tot. time  ( GPU )   avginb  maxinb     count  percent
simulation ........................................  2.254e-02            0.000   0.000         1  100.00%
  global
  compute_loop ....................................  1.362e-02            0.000   0.000         1  60.44% / 100.00%
    print_int .....................................  3.794e-03            0.000   0.000         6  16.83% / 27.85%
    next_time_step ................................  1.542e-03            0.000   0.000         6   6.84% / 11.32%
    sim_continue ..................................  2.709e-03            0.000   0.000         6  12.02% / 19.88%
```

`count` is the number of calls. The two
percentages are relative to the whole run and to the parent batch.

To profile only some operators: `--profiling-filter "[regex]"`.

## Execution traces

A trace records when each operator and each parallel task ran, on each
thread. It shows idle time and load imbalance.

``` bash
$ onikarun input.msp --profiling-trace-enable
# writes trace.yml (name set with --profiling-trace-file)
```

Convert it with `trace_convert`:

``` bash
$ trace_convert -vite trace.yml out
# writes out.vite (for the ViTE trace viewer), out.vite.idle, out.vite.plot
```

Other output formats: `-dot`, `-plot`, `-tikz`. Useful filters:
`-start <event> <index>` / `-end <event> <index>` to keep a time window,
`-threads <first> <last>` to keep some threads.

!!! note

    The usage message of `trace_convert` of Onika 1.1.0 shows formats without the
    leading `-` (`vite|dot|plot`); the program actually expects `-vite`,
    `-dot`...

## Threads and GPU

| Option | Use |
|---|---|
| `--omp_num_threads N` | Number of OpenMP threads (default: all cores). |
| `--pinethreads` | Pin threads to cores. |
| `--omp_max_threads_filter "{regex: N}"` | Limit threads for some operators. |
| `--nogpu` | No GPU at all. |
| `--onika-gpu_disable_filter "[regex]"` | No GPU for some operators. |
| `--profiling-gpu_filter "[regex]"` | Limit GPU profiling to some operators. |

With MPI, run with your MPI launcher as usual
(`mpirun -n 4 onika-exec input.msp`). Logs come from rank 0 only, unless
`--logging-parallel` is set.

# Glossary

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

**operator** { #term-operator }
:   A C++ class deriving from `onika::scg::OperatorNode` that does one job. The building block of every Onika application. See [Anatomy of an operator](../operators/anatomy.md).

**slot** { #term-slot }
:   A named, typed input or output of an operator, declared with `ADD_SLOT`. Slots with the same name are connected automatically.

**batch** { #term-batch }
:   A named sequence of operators defined in an input file. It can loop and have a condition. See [Batches](../inputs/msp-language.md#msp-batches).

**rebind** { #term-rebind }
:   Renaming of slots of a batch body, to connect operators whose slot names differ. See [Rebinding slots](../inputs/msp-language.md#msp-rebind).

**simulation graph** { #term-simulation-graph }
:   The tree of operators built from the `simulation` entry of the input files. Printed with `--debug-graph`.

**sink** { #term-sink }
:   An operator without outputs (or with `is_sink()` returning true). Always kept in the graph. See [Keeping an operator in the graph: `is_sink()`](../operators/anatomy.md#operator-sink).

**pruning** { #term-pruning }
:   Removal of operators whose outputs are never used, shown as `*SUPPRESS*` in the log. See [Unused operators are removed](../inputs/msp-language.md#msp-pruning).

**plugin** { #term-plugin }
:   A shared library containing operators, loaded at run time. See [Plugins](../operators/plugins.md).

**factory** { #term-factory }
:   `OperatorNodeFactory`: the registry that creates operators from their names. Operators register with `register_factory`.

**flavor** { #term-flavor }
:   The set of slot names and types available upstream of an operator. `make_compatible_operator` uses it to choose an implementation.

**msp file** { #term-msp-file }
:   An Onika input file, in YAML. See [The input file language](../inputs/msp-language.md).

**main-config.msp** { #term-main-configmsp }
:   The default input file, always loaded first. See [The default file: `main-config.msp`](../inputs/msp-language.md#msp-main-config).

**lane** { #term-lane }
:   An execution stream of the parallel API. Operations on different lanes may run concurrently. See [Parallel API: one code for CPU and GPU](../operators/parallel.md).

**parallel execution context** { #term-parallel-execution-context }
:   The execution resources (CPU threads, GPU, streams) of an operator, given by `parallel_execution_context()`.

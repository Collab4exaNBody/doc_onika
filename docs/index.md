# Onika documentation

**Onika** (*Object Network Interface for Knit Applications*) is a component-based
HPC platform for building numerical simulation codes. You write small C++
**operators** that each do one job, and **knit** them together into a
simulation graph with a YAML input file. Onika then runs that graph with MPI,
OpenMP and CUDA/HIP.

The docs follow the knitting idea, from the thread to the finished fabric:
*discover* the yarn, *cast on* with a first run, read the *pattern* (input
files), make your own *stitches* (operators), work *on the needles*
(run and tune), and keep the *swatch book* (reference) close by.

``` mermaid
flowchart LR
  msp["input file<br/>(.msp, YAML)"] --> factory["operator factory"]
  plugins["plugins<br/>(your operators)"] --> factory
  factory --> simgraph["simulation graph"]
  simgraph --> run["parallel execution<br/>MPI · OpenMP · GPU"]
```

## Choose your path

<div class="grid cards" markdown>

-   __Simulation user__

    ---

    You run an Onika-based code (exaNBody, exaStamp, exaDEM...) and write
    input files.

    **Path:** [install](getting-started/installation.md) → [first run](getting-started/first-run.md) → [input files](inputs/msp-language.md) →
    [command line](running/command-line.md)

-   __Operator developer__

    ---

    You add physics or tools as new operators in a plugin.

    **Path:** [first operator](getting-started/first-operator.md) → [operator anatomy](operators/anatomy.md) →
    [plugins](operators/plugins.md) →
    [parallel API](operators/parallel.md)

-   __Framework developer__

    ---

    You work on Onika itself or couple codes together.

    **Path:** [motivation](discover/motivation.md) →
    [embedding and coupling](coupling/embedding.md) →
    [Python bindings](python/pyonika.md) →
    [libraries](libraries/memory.md) →
    [internals](reference/internals.md)

</div>

Each page starts with badges telling who it is for: <span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

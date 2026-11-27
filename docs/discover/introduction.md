# What is Onika?

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

**Onika** (Object Network Interface for Knit Applications) is a component-based HPC software platform for building numerical simulation codes.

Onika is the foundation of the exaNBody particle simulation platform, but it is not tied to N-Body problems, nor to any other specific application domain. Existing applications built on Onika's components include Molecular Dynamics, particle-based fluid simulations using methods such as Smoothed Particle Hydrodynamics (SPH), and rigid body simulations using methods such as the Discrete Element Method (DEM). See [Codes built on Onika](ecosystem.md) for the list of codes.

## Onika in three ideas

<div class="grid cards" markdown>

-   __Operators__

    ---

    Small C++ classes that each do one job. They declare their inputs and
    outputs as **slots** and know nothing about the other operators.
    See [Anatomy of an operator](../operators/anatomy.md).

-   __Input files__

    ---

    A YAML file (`.msp`) assembles the operators into a **simulation graph**:
    sequences, loops, conditions. No recompilation needed.
    See [The input file language](../inputs/msp-language.md).

-   __Runtime__

    ---

    Onika connects slots by name, removes operators whose results are never
    used, and runs the graph with MPI, OpenMP and CUDA/HIP.
    See [Command-line options](../running/command-line.md).

</div>

See [Why components?](motivation.md) for why Onika is built this way.

## Key characteristics

- **Language:** C++20.
- **Python:** optional `pyonika` bindings to drive simulations from Python (see [Python bindings](../python/pyonika.md)).
- **Build system:** CMake (≥ 3.26).
- **Configuration:** YAML input files (`.msp`).
- **Parallelization:** MPI and OpenMP for distributed and shared-memory parallelism.
- **GPU acceleration:** CUDA and HIP.
- **License:** Apache 2.0.

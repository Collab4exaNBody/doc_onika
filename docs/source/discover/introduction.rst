.. _introduction:

What is Onika?
==============

|user| |opdev| |core|

**Onika** (Object Network Interface for Knit Applications) is a component-based HPC software platform for building numerical simulation codes.

Onika is the foundation of the exaNBody particle simulation platform, but it is not tied to N-Body problems, nor to any other specific application domain. Existing applications built on Onika's components include Molecular Dynamics, particle-based fluid simulations using methods such as Smoothed Particle Hydrodynamics (SPH), and rigid body simulations using methods such as the Discrete Element Method (DEM). See :ref:`ecosystem` for the list of codes.

Onika in three ideas
--------------------

.. grid:: 1 1 3 3
   :gutter: 2

   .. grid-item-card:: Operators

      Small C++ classes that each do one job. They declare their inputs and
      outputs as **slots** and know nothing about the other operators.
      See :ref:`operator-anatomy`.

   .. grid-item-card:: Input files

      A YAML file (``.msp``) assembles the operators into a **simulation graph**:
      sequences, loops, conditions. No recompilation needed.
      See :ref:`msp-language`.

   .. grid-item-card:: Runtime

      Onika connects slots by name, removes operators whose results are never
      used, and runs the graph with MPI, OpenMP and CUDA/HIP.
      See :ref:`command-line`.

See :ref:`motivation` for why Onika is built this way.

Key characteristics
-------------------

* **Language:** C++20.
* **Build system:** CMake (≥ 3.26).
* **Configuration:** YAML input files (``.msp``).
* **Parallelization:** MPI and OpenMP for distributed and shared-memory parallelism.
* **GPU acceleration:** CUDA and HIP.
* **Python:** optional ``pyonika`` bindings to drive simulations from Python (see :ref:`pyonika`).
* **License:** Apache 2.0.

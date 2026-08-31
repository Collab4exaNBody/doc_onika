Onika: a Component-Based HPC Platform for Numerical Simulation
================================================================

**Onika** (Object Network Interface for Knit Applications) is a component-based HPC software platform for building numerical simulation codes.

Onika is the foundation of the exaNBody particle simulation platform, but it is not tied to N-Body problems, nor to any other specific application domain. Existing applications built on Onika's components include Molecular Dynamics, particle-based fluid simulations using methods such as Smoothed Particle Hydrodynamics (SPH), and rigid body simulations using methods such as the Discrete Element Method (DEM).

See :doc:`Motivation` for why Onika is built around a component-based architecture.

Key Characteristics
-------------------

* **Language:** Implemented in C++20.
* **Build system:** CMake.
* **Configuration:** YAML for user input files.
* **Parallelization:** MPI and OpenMP for distributed and shared-memory parallelism.
* **GPU acceleration:** CUDA and HIP.

Onika in other codes
--------------------

Onika is used by several codes:

* `ExaNBody <https://github.com/Collab4exaNBody/exaNBody>`_, for N-Body simulations (open source) :cite:`Carrard_2024`.
* `ExaStamp <https://github.com/Collab4exaNBody/exaStamp>`_, for Molecular Dynamics simulations (open source) :cite:`cieren2014exastamp`.
* `ExaDEM <https://github.com/Collab4exaNBody/exaDEM>`_, for Discrete Element Method simulations (open source) :cite:`prat2025exadem`. ExaDEM combines exaNBody for its HPC performance layer with the physical modeling capabilities of `Rockable <https://github.com/richefeu/rockable>`_ :cite:`richefeu2025rockable`, notably its R-shape particle representation.
* `HippoLBM <https://github.com/Collab4exaNBody/hippoLBM>`_, for Lattice Boltzmann Method simulations (open source). HippoLBM reuses computational kernels from an earlier code, DEMLBM3D, integrated into Onika operators, with data structures reworked for GPU execution and a domain decomposition algorithm added to support MPI+GPU parallelism.
* ExaSPH, for Smoothed Particle Hydrodynamics simulations (not open source) and Coupling ExaSPH with EuroPlexus via onika (not open source) :cite:`beccantini2022europlexus`.
* ExaCoLD, for LBM-DEM-IBM coupling (soon to be open source).
* A prototype of CEA's PLEIADES-HPC platform (not open source) :cite:`bernaud2024pleiades`.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames

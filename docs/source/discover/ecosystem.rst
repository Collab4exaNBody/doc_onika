.. _ecosystem:

Codes built on Onika
====================

|user| |core|

Onika is used by several codes:

* `ExaNBody <https://github.com/Collab4exaNBody/exaNBody>`_, for N-Body simulations (open source) :cite:`Carrard_2024`.
* `ExaStamp <https://github.com/Collab4exaNBody/exaStamp>`_, for Molecular Dynamics simulations (open source) :cite:`cieren2014exastamp`.
* `ExaDEM <https://github.com/Collab4exaNBody/exaDEM>`_, for Discrete Element Method simulations (open source) :cite:`prat2025exadem`. ExaDEM combines exaNBody for its HPC performance layer with the physical modeling capabilities of `Rockable <https://github.com/richefeu/rockable>`_ :cite:`richefeu2025rockable`, notably its R-shape particle representation.
* `HippoLBM <https://github.com/Collab4exaNBody/hippoLBM>`_, for Lattice Boltzmann Method simulations (open source). HippoLBM reuses computational kernels from an earlier code, DEMLBM3D, integrated into Onika operators, with data structures reworked for GPU execution and a domain decomposition algorithm added to support MPI+GPU parallelism.
* ExaSPH, for Smoothed Particle Hydrodynamics simulations (not open source). ExaSPH has also been coupled with EuroPlexus through Onika (not open source) :cite:`beccantini2022europlexus`.
* ExaCoLD, for LBM-DEM-IBM coupling (soon to be open source).
* A prototype of CEA's PLEIADES-HPC platform (not open source) :cite:`bernaud2024pleiades`.

.. mermaid::

   flowchart BT
     onika["Onika<br/>components · runtime · GPU"]
     exanbody["exaNBody<br/>particle platform"] --> onika
     exastamp["exaStamp<br/>MD"] --> exanbody
     exadem["exaDEM<br/>DEM"] --> exanbody
     others["HippoLBM · exaSPH · ExaCoLD<br/>PLEIADES-HPC prototype"] -.-> onika

Solid arrows: "built on top of". Dashed arrow: built on Onika's components,
directly or through exaNBody.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames

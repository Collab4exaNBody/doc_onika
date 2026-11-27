# Codes built on Onika

<span class="badge badge-user">Simulation user</span> <span class="badge badge-core">Framework developer</span>

Onika is used by several codes:

- [ExaNBody](https://github.com/Collab4exaNBody/exaNBody), for N-Body simulations (open source) [[Carrard_2024]](#ref-Carrard_2024).
- [ExaStamp](https://github.com/Collab4exaNBody/exaStamp), for Molecular Dynamics simulations (open source) [[cieren2014exastamp]](#ref-cieren2014exastamp).
- [ExaDEM](https://github.com/Collab4exaNBody/exaDEM), for Discrete Element Method simulations (open source) [[prat2025exadem]](#ref-prat2025exadem). ExaDEM combines exaNBody for its HPC performance layer with the physical modeling capabilities of [Rockable](https://github.com/richefeu/rockable) [[richefeu2025rockable]](#ref-richefeu2025rockable), notably its R-shape particle representation.
- [HippoLBM](https://github.com/Collab4exaNBody/hippoLBM), for Lattice Boltzmann Method simulations (open source). HippoLBM reuses computational kernels from an earlier code, DEMLBM3D, integrated into Onika operators, with data structures reworked for GPU execution and a domain decomposition algorithm added to support MPI+GPU parallelism.
- ExaSPH, for Smoothed Particle Hydrodynamics simulations (not open source). ExaSPH has also been coupled with EuroPlexus through Onika (not open source) [[beccantini2022europlexus]](#ref-beccantini2022europlexus).
- ExaCoLD, for LBM-DEM-IBM coupling (soon to be open source).
- A prototype of CEA's PLEIADES-HPC platform (not open source) [[bernaud2024pleiades]](#ref-bernaud2024pleiades).

``` mermaid
flowchart BT
  onika["Onika<br/>components · runtime · GPU"]
  exanbody["exaNBody<br/>particle platform"] --> onika
  exastamp["exaStamp<br/>MD"] --> exanbody
  exadem["exaDEM<br/>DEM"] --> exanbody
  others["HippoLBM · exaSPH · ExaCoLD<br/>PLEIADES-HPC prototype"] -.-> onika
```

Solid arrows: "built on top of". Dashed arrow: built on Onika's components,
directly or through exaNBody.

**References**

<a id="ref-Carrard_2024"></a>**[Carrard_2024]** Thierry Carrard, Raphaël Prat, Guillaume Latu, Killian Babilotte, Paul Lafourcade, Lhassan Amarsid and Laurent Soulard. *ExaNBody: a HPC framework for N-Body applications*. Euro-Par 2023: Parallel Processing Workshops. 342–354. 2024. [doi:10.1007/978-3-031-50684-0_27](https://doi.org/10.1007/978-3-031-50684-0_27)

<a id="ref-cieren2014exastamp"></a>**[cieren2014exastamp]** Emmanuel Cieren, Laurent Colombet, Samuel Pitoiset and Raymond Namyst. *ExaStamp: a parallel framework for molecular dynamics on heterogeneous clusters*. Euro-Par 2014: Parallel Processing Workshops: Euro-Par 2014 International Workshops, Porto, Portugal, August 25-26, 2014, Revised Selected Papers, Part II 20. 121–132. 2014. [doi:10.1007/978-3-319-14313-2_11](https://doi.org/10.1007/978-3-319-14313-2_11)

<a id="ref-prat2025exadem"></a>**[prat2025exadem]** Raphaël Prat, Thierry Carrard, Lhassan Amarsid, Vincent Richefeu, Carlo-Elia Doncecchi, Paul Lafourcade, Guillaume Latu and Jean-Mathieu Vanson. *ExaDEM: a HPC application based on exaNBody targeting scalable DEM simulations with complex particle shapes*. Journal of Open Source Software, 10. 7484. 2025. [doi:10.21105/joss.07484](https://doi.org/10.21105/joss.07484)

<a id="ref-richefeu2025rockable"></a>**[richefeu2025rockable]** Vincent Richefeu, Gaël Combe, Lhassan Amarsid, Raphaël Prat, Jean-Mathieu Vanson, Saied Nezamabadi, Patrick Mutabaruka, Jean-Yves Delenne and Farhang Radjaï. *Advanced strategies for discrete simulations with three-dimensional R-shapes in Rockable framework*. Computer Physics Communications, 320. 109997. 2025. [doi:10.1016/j.cpc.2025.109997](https://doi.org/10.1016/j.cpc.2025.109997)

<a id="ref-beccantini2022europlexus"></a>**[beccantini2022europlexus]** Alberto Beccantini, Fabienne Bliard, Pascal Bouda, Stanislas de Lambert, Florence Drui, Pascal Galon, Olivier Jamond and Nicolas Lelong. *EUROPLEXUS: un code de référence pour la dynamique rapide et l'interaction fluide-structure*. CSMA 2022-15ème Colloque National en Calcul des Structures. 2022.

<a id="ref-bernaud2024pleiades"></a>**[bernaud2024pleiades]** Stéphane Bernaud, Isabelle Ramiere, Guillaume Latu and Bruno Michel. *PLEIADES: a numerical framework dedicated to the multiphysics and multiscale nuclear fuel behaviour simulation*. Annals of Nuclear Energy, 205. 110577. 2024. [doi:10.1016/j.anucene.2024.110577](https://doi.org/10.1016/j.anucene.2024.110577)

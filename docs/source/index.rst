.. _home:

###################
Onika documentation
###################

**Onika** (*Object Network Interface for Knit Applications*) is a component-based
HPC platform for building numerical simulation codes. You write small C++
**operators** that each do one job, and **knit** them together into a
simulation graph with a YAML input file. Onika then runs that graph with MPI,
OpenMP and CUDA/HIP.

The docs follow the knitting idea, from the thread to the finished fabric:
*discover* the yarn, *cast on* with a first run, read the *pattern* (input
files), make your own *stitches* (operators), work *on the needles*
(run and tune), and keep the *swatch book* (reference) close by.

.. mermaid::

   flowchart LR
     msp["input file<br/>(.msp, YAML)"] --> factory["operator factory"]
     plugins["plugins<br/>(your operators)"] --> factory
     factory --> simgraph["simulation graph"]
     simgraph --> run["parallel execution<br/>MPI · OpenMP · GPU"]

Choose your path
================

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: Simulation user
      :class-card: sd-border-info

      You run an Onika-based code (exaNBody, exaStamp, exaDEM...) and write
      input files.

      **Path:** :doc:`install <getting-started/installation>` → :doc:`first run <getting-started/first-run>` → :doc:`input files <inputs/msp-language>` →
      :doc:`command line <running/command-line>`

   .. grid-item-card:: Operator developer
      :class-card: sd-border-success

      You add physics or tools as new operators in a plugin.

      **Path:** :doc:`first operator <getting-started/first-operator>` → :doc:`operator anatomy <operators/anatomy>` →
      :doc:`plugins <operators/plugins>` →
      :doc:`parallel API <operators/parallel>`

   .. grid-item-card:: Framework developer
      :class-card: sd-border-warning

      You work on Onika itself or couple codes together.

      **Path:** :doc:`motivation <discover/motivation>` →
      :doc:`Python bindings <python/pyonika>` →
      :doc:`reference <reference/builtin-operators>`

Each page starts with badges telling who it is for: |user| |opdev| |core|

.. toctree::
   :caption: Discover · the yarn
   :maxdepth: 2
   :hidden:

   discover/introduction
   discover/motivation
   discover/ecosystem
   discover/cite

.. toctree::
   :caption: Get started · casting on
   :maxdepth: 2
   :hidden:

   getting-started/installation
   getting-started/first-run
   getting-started/first-input
   getting-started/first-operator

.. toctree::
   :caption: Write inputs · the pattern
   :maxdepth: 2
   :hidden:

   inputs/msp-language
   inputs/configuration

.. toctree::
   :caption: Build operators · the stitches
   :maxdepth: 2
   :hidden:

   operators/anatomy
   operators/plugins
   operators/parallel

.. toctree::
   :caption: Run & tune · on the needles
   :maxdepth: 2
   :hidden:

   running/command-line
   running/profiling-debugging

.. toctree::
   :caption: Python · another hand
   :maxdepth: 2
   :hidden:

   python/pyonika

.. toctree::
   :caption: Reference · the swatch book
   :maxdepth: 2
   :hidden:

   reference/builtin-operators
   reference/cmake-options
   reference/glossary

.. toctree::
   :caption: Project
   :maxdepth: 2
   :hidden:

   project/contributing-docs

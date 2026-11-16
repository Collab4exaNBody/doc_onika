.. _first-run:

Your first run
==============

|user|

This page runs an example shipped with Onika, shows its operator graph and
changes a parameter from the command line. It uses the **counter loop**,
the running example of this guide: a loop that prints the time step until it
reaches ``nsteps``.

Run an example
--------------

Onika installs two launchers in ``<install-prefix>/bin``:

- ``onika-exec``: the application itself. Source ``bin/setup-env.sh`` first,
  so that it finds its plugins and configuration files.
- ``onikarun``: a wrapper script that sources ``setup-env.sh`` and then runs
  ``onika-exec`` with the same arguments.

.. code-block:: bash

   $ cp <install-prefix>/data/exemples/print_loop.msp .
   $ <install-prefix>/bin/onikarun print_loop.msp

The output ends with:

.. code-block:: text

   Current timestep = 0
   Current timestep = 1
   ...
   Current timestep = 20

Look at the graph
-----------------

``--debug-graph`` prints the operator graph that Onika built from the input
file, with the slots of each operator (``IN``, ``OUT`` or ``IN/OUT``):

.. code-block:: bash

   $ onikarun print_loop.msp --debug-graph

.. code-block:: text

   *SUPPRESS* simulation.mpi_comm_world
   *SUPPRESS* simulation.init_cuda
   *SUPPRESS* simulation.global

   ======= simulation graph ========
   simulation
     global
       compute_loop_continue OUT
       dt OUT
       nsteps OUT
       timestep OUT
     unit_system
       unit_system IN
       verbose IN
     compute_loop
       print_int
         prefix IN
         suffix IN
         timestep IN
       next_time_step
         dt IN
         physical_time IN/OUT
         timestep IN/OUT
       sim_continue
         check_freq IN
         compute_loop_continue IN/OUT
         nsteps IN
         remain IN
         signal_handler_priv IN/OUT
         stop_file IN
         timestep IN
   =================================

Three things to notice:

1. **Slots are connected by name.** ``next_time_step`` reads ``dt`` and
   ``timestep``, produced earlier by ``global``. No explicit wiring is needed.
2. **Rebinding renames slots.** ``print_int`` has a slot ``value``, shown here
   as ``timestep``, because the input file *rebinds* it. Same for
   ``sim_continue``, whose ``end_at`` and ``result`` become ``nsteps`` and
   ``compute_loop_continue``. See :ref:`msp-rebind`.
3. **Unused operators are removed.** ``*SUPPRESS*`` lines list operators whose
   outputs nobody reads. Here ``print_loop.msp`` calls ``global`` twice, so
   the first call is useless. See :ref:`msp-pruning`.

.. mermaid::

   flowchart LR
     global -- "dt, timestep, nsteps,<br/>compute_loop_continue" --> loop
     subgraph loop ["compute_loop (loop while compute_loop_continue)"]
       direction LR
       p["print_int<br/>value ← timestep"] --> n["next_time_step"] --> s["sim_continue<br/>end_at ← nsteps<br/>result → compute_loop_continue"]
     end

Change a value from the command line
------------------------------------

Every value of the input file can be overridden with ``--set-<path> <value>``,
where ``<path>`` is the YAML path with ``-`` as separator:

.. code-block:: bash

   $ onikarun print_loop.msp --set-global-nsteps 3

.. code-block:: text

   Current timestep = 0
   Current timestep = 1
   Current timestep = 2
   Current timestep = 3

Other options control the run itself (threads, GPU, profiling...), for
example ``--omp_num_threads 4`` or ``--profiling-summary``. See :ref:`command-line`.

Next step: :ref:`first-input`, to write this input file yourself.

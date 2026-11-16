.. _msp-language:

The input file language
=======================

|user| |opdev|

An Onika input file (``.msp``) is a YAML file that describes the
**simulation graph**: which operators run, in which order, with which values.
This page describes every construct. For a guided introduction, see
:ref:`first-input`.

Structure of a file
-------------------

The top level of an input file is a map. A few keys are special, all others
define operators or batches:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Meaning
   * - ``simulation``
     - Entry point: the operator (usually a list) that Onika runs.
   * - ``includes``
     - List of other input files to load first. See :ref:`msp-includes`.
   * - ``configuration``
     - Settings of the Onika runtime (logging, profiling, threads, GPU...).
       See :ref:`input-configuration`.
   * - *any other name*
     - Default values for an operator of that name, or the definition of a
       new **batch** (named group of operators).

.. code-block:: yaml

   includes: [ my_defaults.msp ]     # optional

   configuration:                    # optional
     logging: { debug: false }

   global:                           # default values for operator 'global'
     dt: 1.0

   my_step:                          # a new batch
     - next_time_step
     - print_timestep

   simulation:                       # what runs
     - global
     - my_step

Calling operators
-----------------

In a list, each item calls an operator in one of two forms:

.. code-block:: yaml

   - next_time_step                                  # name only: default values
   - print_int: { prefix: "t = ", suffix: "\n" }     # name: map of slot values

The map sets the values of the operator's slots. Use ``onika-exec --help
<operator>`` to list the slots of an operator.

A key that matches no slot only gives a warning, unless
``--debug-strict_slots true`` is set (then it is an error).

.. tip::

   Some operators accept a shortcut. For example ``message: "Hello"`` is the
   same as ``message: { mesg: "Hello" }``.

Values and units
~~~~~~~~~~~~~~~~

Slot values are YAML values converted to the slot type. Real values can carry
a **unit**; they are converted to the internal unit system (SI by default):

.. code-block:: yaml

   global:
     dt: 2.0 fs            # stored as 2.0e-15 (seconds)
     len: 1.5 ang          # stored as 1.5e-10 (meters)
     acc: 9.81 m.s^-2      # units combine with '.', powers with '^'

The internal unit system is set by the ``unit_system`` operator
(see :ref:`builtin-operators`).

.. _msp-batches:

Batches
-------

A **batch** is a named sequence of operators. Define it at the top level, then
use its name like any operator. Two forms exist:

.. code-block:: yaml

   # short form: a list
   print_and_step:
     - print_timestep
     - next_time_step

   # long form: a map with a 'body' and options
   compute_loop:
     loop: true
     condition: compute_loop_continue
     body:
       - print_and_step
       - compute_loop_stop

A batch defined as a plain name is an **alias**: ``init: nop`` makes ``init``
run ``nop``.

Batch options (long form):

.. list-table::
   :header-rows: 1
   :widths: 20 25 55

   * - Option
     - Value
     - Effect
   * - ``body``
     - list
     - The operators to run, in order. Required in the long form.
   * - ``rebind``
     - map ``inner: outer``
     - Renames slots of the body. See :ref:`msp-rebind`.
   * - ``condition``
     - slot name, or ``not <slot>``
     - Runs the body only if the boolean slot is true (or false with ``not``).
   * - ``loop``
     - ``true`` / ``false``
     - Runs the body again while ``condition`` is true. Without a condition,
       the loop never ends.
   * - ``unroll``
     - integer
     - With ``loop: true``: copies the body N times per iteration.
   * - ``name``
     - string
     - Name shown in graphs and profiles (default: the batch key).
   * - ``profiling``
     - ``true`` / ``false``
     - Forces profiling of this batch on or off.
   * - ``parallel``
     - ``true`` / ``false``
     - Runs the operators of the body concurrently (nested parallelism).
       ``cores`` gives the share of cores of each operator.
   * - ``task_group``
     - ``true`` / ``false``
     - Runs the body inside an OpenMP task group, so that asynchronous GPU/CPU
       work of the body can overlap.

.. _msp-slots:

How operators are connected
---------------------------

You never connect operators explicitly. **Slots with the same name are
connected**: an input slot reads the value of the last operator before it, in
execution order, that has an output slot with the same name. ``global``
creates output slots from its values, so it is a common way to provide
parameters.

.. mermaid::

   flowchart LR
     g["global<br/>OUT dt, timestep"] -->|dt, timestep| n["next_time_step<br/>IN dt · IN/OUT timestep"]
     n -->|timestep| p["print_int<br/>IN value ← timestep"]

.. _msp-rebind:

Rebinding slots
~~~~~~~~~~~~~~~

Slot names are chosen by the operator author, so they rarely match.
``rebind`` renames slots of a batch body, seen from outside the batch:

.. code-block:: yaml

   print_timestep:
     rebind: { value: timestep }     # inner slot 'value' is called 'timestep' outside
     body:
       - print_int: { prefix: "Current timestep = ", suffix: "\n" }

Here ``print_int`` reads ``timestep`` without knowing that name. Rebinding
applies to all operators of the body.

.. _msp-pruning:

Unused operators are removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After building the graph, Onika **removes operators whose outputs are never
read** by a later operator. The log shows them as:

.. code-block:: text

   *SUPPRESS* simulation.compute_loop.scale_value

If an operator you expect to run disappears, check that its outputs are used,
or check with ``--debug-graph``. Operators that only have side effects (print,
write files) have no outputs and are kept. Developers can also force this with
``is_sink()`` (see :ref:`operator-sink`).

.. _msp-includes:

Includes and merging
--------------------

.. code-block:: yaml

   includes:
     - common/material.msp
     - common/outputs.msp

Files are loaded in this order, each one merged on top of the previous ones:

1. ``main-config.msp``, always first (see :ref:`msp-main-config`);
2. the files in ``includes``, recursively, each file only once;
3. your input file;
4. command-line options (see :ref:`msp-command-line`).

Merging rules:

- **maps are merged** key by key, the last file wins;
- **lists and values are replaced**;
- a key prefixed with ``+`` **appends** to a list instead of replacing it.

.. code-block:: yaml
   :caption: base.msp

   my_sequence:
     - message: "first"

.. code-block:: yaml
   :caption: input.msp

   includes: [ base.msp ]

   +my_sequence:                 # appends to my_sequence from base.msp
     - message: "second"

``--debug-files`` prints the list of files actually loaded.

.. _msp-main-config:

The default file: ``main-config.msp``
-------------------------------------

Onika always loads ``data/config/main-config.msp`` first (found through
``ONIKA_CONFIG_PATH``). It defines a default ``simulation``:

.. code-block:: yaml
   :caption: main-config.msp (simplified)

   run: nop
   init: nop

   simulation:
     - message: "<Onika banner>"
     - mpi_comm_world
     - init_cuda
     - global
     - unit_system: { verbose: true, unit_system: { length: meter, mass: kilogram, ... } }
     - init
     - run
     - finalize_cuda

So you have two ways to write an input file:

- define ``run`` (and ``init``) only: you keep MPI, GPU and unit system
  initialization, and add your own work;
- define ``simulation``: you replace everything.

Applications built on Onika (exaNBody, exaStamp...) ship their own
``main-config.msp`` with many predefined batches.

.. _msp-command-line:

Overriding values from the command line
---------------------------------------

Any value can be changed at launch time with ``--set-<path> <value>``, the
path being the YAML keys separated by ``-``:

.. code-block:: bash

   $ onika-exec input.msp --set-global-nsteps 100 --set-global-dt "0.5 fs"

.. warning::

   In Onika 1.0.4, the ``onikarun`` wrapper splits arguments that contain
   spaces, so ``--set-global-dt "0.5 fs"`` fails with a YAML parse error.
   For such values, source ``setup-env.sh`` and call ``onika-exec`` directly.

The same override can be written in the input file, under ``configuration``:

.. code-block:: yaml

   configuration:
     set:
       global: { nsteps: 100 }

Runtime options such as ``--omp_num_threads`` are described in :ref:`command-line`.

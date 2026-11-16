.. _pyonika:

Python bindings: ``pyonika``
============================

|user| |core|

``pyonika`` drives Onika from Python: load an input file, change values,
build the graph, inspect operators and slots, run, and read results as
NumPy arrays. The full API reference is in ``python/README.md`` of the Onika
sources; this page shows the three usage patterns.

Build and install
-----------------

Configure Onika with ``-DONIKA_BUILD_PYTHON=ON`` (pybind11 is downloaded if it
is not installed), then install the package with the same Python interpreter:

.. code-block:: bash

   $ cmake -S onika -B build-onika -DONIKA_BUILD_PYTHON=ON \
           -DPython3_EXECUTABLE=$(which python3) \
           -DCMAKE_INSTALL_PREFIX=$PWD/install-onika
   $ cmake --build build-onika -j 8 --target install
   $ pip install ./install-onika/python

``import pyonika`` sets ``ONIKA_PLUGIN_PATH``, ``ONIKA_CONFIG_PATH`` and
``ONIKA_DATA_PATH`` from the install prefix, unless they are already set
(e.g. by ``setup-env.sh``), and initializes MPI.

Three patterns
--------------

.. tab-set::

   .. tab-item:: A · run an input file

      The input file drives everything, as with ``onika-exec``.
      ``init()`` takes the same arguments as the command line.

      .. code-block:: python

         import sys
         import pyonika

         ctx = pyonika.init([sys.argv[0], "step3.msp", "--omp_num_threads", "4"])
         if ctx.error_code >= 0:        # >= 0 means early exit (--help, ...)
             sys.exit(ctx.error_code)

         # inspect the graph before running
         ctx.node("simulation").apply_graph(lambda op: print(op.pathname()))

         pyonika.run(ctx)
         pyonika.end(ctx)

   .. tab-item:: B · build the graph in Python

      No input file: batches and values are Python dicts with the same
      structure as the YAML (here, the counter loop).

      .. code-block:: python

         pyonika.set_operator_defaults({
             "print_timestep": {
                 "rebind": {"value": "timestep"},
                 "body": [{"print_int": {"prefix": "Current timestep = ", "suffix": "\n"}}],
             },
             "compute_loop_stop": {
                 "rebind": {"end_at": "nsteps", "result": "compute_loop_continue"},
                 "body": ["sim_continue"],
             },
             "compute_loop": {
                 "loop": True,
                 "condition": "compute_loop_continue",
                 "body": ["print_timestep", "next_time_step", "compute_loop_stop"],
             },
             "global": {"dt": 1.0, "nsteps": 20, "timestep": 0, "compute_loop_continue": True},
         })

         graph = pyonika.build_simulation_graph(ctx, ["global", "mpi_comm_world", "compute_loop"])
         pyonika.run_node(ctx, graph)
         pyonika.end(ctx)

      ``ctx`` comes from ``pyonika.init()`` with ``main-config.msp``, only to
      start the runtime.

   .. tab-item:: C · patch an input file

      Load an input file, change some values, rebuild the graph, run it.
      Ideal for parameter studies.

      .. code-block:: python

         import sys
         import pyonika

         ctx = pyonika.init([sys.argv[0], "step3.msp"])
         if ctx.error_code >= 0:
             sys.exit(ctx.error_code)

         pyonika.set_operator_defaults({"global": {"nsteps": 2}})   # merged, not replaced
         graph = pyonika.build_simulation_graph(ctx)                # same 'simulation' as the file
         pyonika.run_node(ctx, graph)
         pyonika.end(ctx)

      .. code-block:: text

         Current timestep = 0
         Current timestep = 1
         Current timestep = 2

      .. warning::

         ``pyonika.run(ctx)`` would run the graph built by ``init()``,
         *before* your changes. After ``set_operator_defaults()``, always
         call ``build_simulation_graph()`` and ``run_node()``.

The ``.msp`` file and Python dicts map one to one:

.. list-table::
   :header-rows: 1

   * - YAML (``.msp``)
     - Python
   * - ``loop: true``
     - ``"loop": True``
   * - ``- next_time_step``
     - ``"next_time_step"`` in a list
   * - ``- print_int: { prefix: "t" }``
     - ``{"print_int": {"prefix": "t"}}``

Examples
--------

``python/examples`` in the Onika sources:

- ``pyonika_dryrun_test_import_pyonika.py``: installation check;
- ``pyonika_run_main_config.py``: pattern A with graph and slot inspection;
- ``pyonika_execute_user_specified_msp_file.py``: run any input file;
- ``pyonika_reproduce_print_loop_case.py``: pattern B, the counter loop;
- ``pyonika_read_slot_values.py``: read slot values after a run;
- ``pyonika_make_operator_usage.py``: create and inspect one operator.

``onika_mcp``
-------------

The Python package also contains ``onika_mcp``, building blocks for
`MCP <https://modelcontextprotocol.io>`_ servers of Onika-based applications:
operator catalog, static checks of quantities and units, short "smoke" runs
and background jobs, each run in a child process so that a crashing
simulation never stops the server.

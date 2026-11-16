.. _builtin-operators:

Built-in operators
==================

|user| |opdev|

These operators are part of Onika itself (``src/scg-builtin-components``) and
are always available. Applications add many more through plugins.
``onika-exec --help <operator>`` prints the up-to-date slots of any operator.

Slot directions: **IN** input, **OUT** output, **IN/OUT** both.
*req.* means the value is required.

Structure
---------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Operator
     - Description
   * - ``batch``
     - Sequence of operators. Used implicitly for every list and every batch
       definition (see :ref:`msp-batches`).
   * - ``nop``
     - Does nothing. Default value of the ``init`` and ``run`` hooks.
   * - ``global``
     - Creates one **OUT** slot per entry of its map. Type deduced from the
       value: boolean, integer, real (with optional unit), string or list.
       ``null_bool`` / ``null_double`` declare a slot without value.

Time stepping
-------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Operator
     - Slots
     - Description
   * - ``next_time_step``
     - ``dt`` IN *req.*, ``timestep`` IN/OUT, ``physical_time`` IN/OUT
     - Increments ``timestep`` and adds ``dt`` to ``physical_time``.
   * - ``sim_continue``
     - ``timestep`` IN *req.*, ``end_at`` IN *req.*, ``stop_file`` IN (``"stop"``),
       ``remain`` IN (600), ``check_freq`` IN (10), ``result`` IN/OUT
     - Sets ``result`` to false when ``timestep > end_at``, when the file
       ``stop_file`` exists, or after Ctrl-C (``SIGINT``). The file is checked every
       ``check_freq`` steps. ``remain`` (seconds) is used with the CCC job
       manager (``ONIKA_HAS_CCC_USER``) to stop before the end of the allocation.
   * - ``nth_timestep``
     - ``timestep`` IN, ``freq`` IN (1), ``first`` IN (true), ``delayed`` IN (false),
       ``at_timestep`` IN (-1), ``result`` IN/OUT
     - ``result`` is true every ``freq`` steps (and on the first call if ``first``),
       or only at ``at_timestep`` if set. Typical use: ``condition`` of an output batch.
   * - ``physical_time_interval``
     - ``physical_time`` IN/OUT, ``start_time`` IN (0), ``end_time`` IN,
       ``time_interval`` IN (0), ``previous_physical_time`` IN/OUT, ``result`` IN/OUT
     - Same as ``nth_timestep`` but based on physical time.

Logic
-----

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Operator
     - Slots
     - Description
   * - ``boolean_and`` / ``boolean_or``
     - ``in1`` IN *req.*, ``in2`` IN *req.*, ``result`` OUT
     - ``result = in1 && in2`` / ``in1 || in2``.
   * - ``boolean_set``
     - ``value`` IN/OUT, ``set`` IN
     - Sets ``value`` to ``set``.
   * - ``greater_than``
     - ``value`` IN *req.*, ``threshold`` IN *req.*, ``result`` OUT
     - ``result = value > threshold``.
   * - ``file_exists``
     - ``filename`` IN *req.*, ``result`` IN/OUT
     - ``result`` is true if the file exists.

Input and output
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Operator
     - Slots
     - Description
   * - ``message``
     - ``mesg`` IN (``""``), ``endl`` IN (true)
     - Prints a message. Shortcut: ``message: "text"``.
   * - ``print_int`` / ``print_real`` / ``print_bool``
     - ``prefix`` IN, ``value`` IN *req.*, ``suffix`` IN
     - Prints ``prefix``, the value, ``suffix``. Rebind ``value`` to print any slot.
   * - ``input_value``
     - ``mesg`` IN (``"input: "``), ``endl`` IN, ``value`` OUT
     - Asks the user for a value (with unit) on standard input.

Runtime and devices
-------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Operator
     - Slots
     - Description
   * - ``mpi_comm_world``
     - ``mpi`` IN/OUT (``MPI_COMM_WORLD``)
     - Provides the MPI communicator as slot ``mpi``.
   * - ``mpi_btree``
     - ``mpi`` IN (``MPI_COMM_WORLD``), ``mpi_btree`` OUT
     - Builds a list of sub-communicators organized as a binary tree.
   * - ``init_cuda``
     - ``mpi`` IN, ``enable_cuda`` IN/OUT (true), ``rotate_gpu`` IN (0),
       ``mpi_even_only`` IN (false), ``smem_bksize`` IN, ``device_limits`` IN
     - Initializes GPUs and assigns a device to each MPI process
       (``rotate_gpu`` shifts the device index). Prints ``vgpu disabled``
       when no GPU is used.
   * - ``finalize_cuda``
     - *(none)*
     - Releases GPU resources at the end of the run.
   * - ``unit_system``
     - ``unit_system`` IN, ``verbose`` IN (false)
     - Sets the internal unit system used to convert quantities with units.
       ``verbose`` prints the table of units.

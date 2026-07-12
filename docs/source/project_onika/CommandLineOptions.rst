Command-line Options
=====================

Onika executables (e.g. ``onikarun``) accept a common set of command-line options. The full list of available options, along with their default values, can be printed with:

.. code-block:: bash

   ./onikarun --help command-line

which produces an output similar to:

.. code-block:: text

   Version : 1.0.4
   MPI     : 1    process
   CPU     : 20   cores (max 20) : 0-19
   OpenMP  : 20   threads (v4.0)
   SIMD    : SSE2
   SOATL   : align=16 , vec=4
   * plugin scan complete, continue ...

   ==============================
   ============ help ============
   ==============================

   default configuration:
   ======================

   --logging-parallel <bool> (default: false)
   ...

To actually run a simulation with one or more of these options, pass an input file followed by the desired options:

.. code-block:: bash

   ./onikarun file.msp --option-XXX

Among all these options, a few are especially useful on a daily basis:

- ``--debug-graph``: prints the operator execution graph. This is particularly useful to check that all configured operators are actually taken into account and none of them have been silently discarded.
- ``--profiling-exectime``: prints the execution time of each operator call. This is handy while debugging, to identify the last operator that was actually executed.
- ``--profiling-summary``: prints a timetable at the end of the run. This is extremely useful for performance studies.
- ``--nogpu``: disables GPU execution. This is also handy while debugging, to rule out GPU-related issues.

Options are grouped by prefix, each corresponding to a functional area of the framework, as described below.

Logging options
----------------

Control how Onika reports log, error and debug messages.

.. option:: --logging-parallel <bool> (default: false)

   Enable per-MPI-process logging output instead of restricting output to rank 0.

.. option:: --logging-debug <bool> (default: false)

   Enable debug-level logging messages.

.. option:: --logging-log_file <std::string> (default: "")

   Path to a file where standard log output is redirected. If empty, logs are written to the standard output.

.. option:: --logging-err_file <std::string> (default: "")

   Path to a file where error output is redirected. If empty, errors are written to the standard error stream.

.. option:: --logging-dbg_file <std::string> (default: "")

   Path to a file where debug output is redirected. If empty, debug messages are written alongside the standard log output.

Profiling options
-------------------

.. option:: --profiling-resmem <bool> (default: false)

   Enable resident memory usage profiling.

.. option:: --profiling-exectime <bool> (default: false)

   Enable execution time profiling of operators.

.. option:: --profiling-summary <bool> (default: false)

   Print a profiling summary at the end of the run.

.. option:: --profiling-filter <StringVector> (default: {})

   Restrict profiling to operators whose name matches one of the given filters.

.. option:: --profiling-gpu_filter <StringVector> (default: {})

   Restrict GPU profiling to operators whose name matches one of the given filters.

Profiling trace options
--------------------------

Control the generation of detailed execution traces (e.g. for visualization in external tools).

.. option:: --profilingtrace-enable <bool> (default: false)

   Enable generation of an execution trace.

.. option:: --profilingtrace-format <std::string> (default: "yaml")

   Output format of the generated trace file.

.. option:: --profilingtrace-file <std::string> (default: "trace")

   Base name of the generated trace file.

.. option:: --profilingtrace-color <std::string> (default: "operator")

   Criterion used to color trace entries (e.g. by operator).

.. option:: --profilingtrace-total <bool> (default: false)

   Include cumulative totals in the generated trace.

.. option:: --profilingtrace-idle <bool> (default: true)

   Include idle time periods in the generated trace.

.. option:: --profilingtrace-trigger <std::string> (default: "")

   Name of the event used to trigger trace recording.

.. option:: --profilingtrace-trigger_interval <IntVector> (default: {})

   Interval, in trigger occurrences, defining when trace recording starts and stops.

.. option:: --profilingtrace-idle_resolution <long> (default: 8192)

   Time resolution, in internal clock ticks, used to detect idle periods.

.. option:: --profilingtrace-idle_smoothing <long> (default: 32)

   Smoothing window, in samples, applied to idle time detection.

Debug options
---------------

Development and troubleshooting options.

.. option:: --debug-plugins <bool> (default: false)

   Print information about loaded plugins.

.. option:: --debug-config <bool> (default: false)

   Print the resolved configuration.

.. option:: --debug-yaml <bool> (default: false)

   Print the parsed YAML input after processing.

.. option:: --debug-graph <bool> (default: false)

   Print the operator execution graph.

.. option:: --debug-ompt <bool> (default: false)

   Enable debugging output from the OpenMP tools (OMPT) interface.

.. option:: --debug-graph_addr <bool> (default: false)

   Include memory addresses when printing the operator execution graph.

.. option:: --debug-graph_lod <int> (default: 1)

   Level of detail used when printing the operator execution graph.

.. option:: --debug-graph_fmt <std::string> (default: "console")

   Output format used when printing the operator execution graph.

.. option:: --debug-graph_rsc <bool> (default: false)

   Include resource usage information when printing the operator execution graph.

.. option:: --debug-files <bool> (default: false)

   Print information about files accessed during the run.

.. option:: --debug-rng <std::string> (default: "")

   Name of the random number generator to enable debug tracing for.

.. option:: --debug-graph_filter <StringVector> (default: {})

   Restrict operator graph debugging to operators whose name matches one of the given filters.

.. option:: --debug-filter <StringVector> (default: {})

   Restrict debug output to messages matching one of the given filters.

.. option:: --debug-particle <UInt64Vector> (default: {})

   List of particle identifiers to enable detailed debug tracing for.

.. option:: --debug-particle_nbh <bool> (default: false)

   Enable debug tracing of particle neighbor lists.

.. option:: --debug-particle_ghost <bool> (default: false)

   Enable debug tracing of ghost particles.

.. option:: --debug-fpe <bool> (default: false)

   Enable trapping of floating-point exceptions.

.. option:: --debug-verbose <int> (default: 0)

   Verbosity level of debug output.

.. option:: --debug-graph_exec <bool> (default: false)

   Print the operator execution graph as it is executed.

Onika runtime options
-------------------------

Fine-tune task scheduling and GPU execution parameters.

.. option:: --onika-parallel_task_core_mult <int> (default: ONIKA_TASKS_PER_CORE)

   Multiplier applied to the number of cores to determine the number of parallel tasks.

.. option:: --onika-parallel_task_core_add <int> (default: 0)

   Number of additional parallel tasks added regardless of the core count.

.. option:: --onika-gpu_sm_mult <int> (default: ONIKA_CU_MIN_BLOCKS_PER_SM)

   Multiplier applied to the number of GPU streaming multiprocessors to determine the number of blocks.

.. option:: --onika-gpu_sm_add <int> (default: 0)

   Number of additional GPU blocks added regardless of the streaming multiprocessor count.

.. option:: --onika-gpu_block_size <int> (default: ONIKA_CU_MAX_THREADS_PER_BLOCK)

   Number of threads per GPU block.

.. option:: --onika-gpu_block_dims <IntVector> (default: DEFAULT_GPU_BLOCK_DIMS)

   Dimensions of the GPU thread block.

.. option:: --onika-gpu_disable_filter <StringVector> (default: {})

   Disable GPU execution for operators whose name matches one of the given filters.

.. option:: --onika-gpu_enable_filter <StringVector> (default: {})

   Restrict GPU execution to operators whose name matches one of the given filters.

Physics options
------------------

.. option:: --physics-units <onika::physics::UnitSystem> (default: onika::physics::SI)

   Unit system used to interpret and convert physical quantities.

.. option:: --physics-rngseed <long> (default: 1812433253)

   Seed used to initialize the random number generator.

General options
-------------------

.. option:: --nogpu <bool> (default: false)

   Disable GPU execution, even if a GPU is available.

.. option:: --mpimt <bool> (default: true)

   Enable MPI multi-threading support.

.. option:: --pinethreads <bool> (default: false)

   Pin OpenMP threads to CPU cores.

.. option:: --threadrotate <int> (default: 0)

   Rotation offset applied when pinning threads to CPU cores.

.. option:: --omp_num_threads <int> (default: -1)

   Number of OpenMP threads to use. A negative value lets OpenMP decide.

.. option:: --omp_max_nesting <int> (default: -1)

   Maximum level of nested OpenMP parallelism. A negative value means no limit.

.. option:: --omp_nested <bool> (default: false)

   Enable nested OpenMP parallelism.

.. option:: --omp_max_threads_filter <StringIntMap> (default: {})

   Per-operator maximum number of OpenMP threads.

.. option:: --plugin_dir <std::string> (default: onika::plugin_path_env())

   Directory searched for plugin libraries.

.. option:: --plugin_db <std::string> (default: "")

   Path to a plugin database file used to speed up plugin discovery.

.. option:: --plugins <StringVector> (default: {})

   List of plugins to load explicitly.

.. option:: --generate_plugins_db <bool> (default: false)

   Generate the plugin database file and exit.

.. option:: --help <std::string> (default: "")

   Print this help message and exit.

.. option:: --run_unit_tests <bool> (default: false)

   Run the built-in unit tests and exit.

.. option:: --set <YAML::Node> (default: )

   Override a configuration value from the command line, using YAML syntax.

.. _cmake-options:

CMake options
=============

|user| |opdev| |core|

Main options of Onika's ``CMakeLists.txt``, set with ``-D<OPTION>=<value>``
when configuring.

.. list-table:: GPU and Python
   :header-rows: 1
   :widths: 35 15 50

   * - Option
     - Default
     - Effect
   * - ``ONIKA_BUILD_CUDA``
     - ``OFF``
     - Enables GPU acceleration (CUDA, or HIP with the next option).
   * - ``ONIKA_ENABLE_HIP``
     - ``OFF``
     - Uses HIP instead of CUDA. Requires ``ONIKA_BUILD_CUDA=ON``.
   * - ``CMAKE_CUDA_ARCHITECTURES``
     -
     - Target GPU architectures, e.g. ``80`` (A100), ``90`` (H100).
   * - ``ONIKA_CU_ENABLE_KERNEL_BOUNDS``
     - ``OFF``
     - Uses launch bounds to restrict GPU kernels.
   * - ``ONIKA_BUILD_PYTHON``
     - ``OFF``
     - Builds the ``pyonika`` bindings (see :ref:`pyonika`).

.. list-table:: OpenMP and profiling
   :header-rows: 1
   :widths: 35 15 50

   * - Option
     - Default
     - Effect
   * - ``ONIKA_HAVE_OPENMP_TOOLS``
     - ``ON`` if OpenMP ≥ 5
     - Uses the OpenMP tools interface (OMPT) for profiling.
   * - ``ONIKA_HAVE_OPENMP_DETACH``
     - ``ON`` if OpenMP ≥ 5
     - Uses the OpenMP 5 ``detach`` clause.
   * - ``ONIKA_ENABLE_TASK_PROFILING``
     - ``ON``
     - Enables task profiling (needed for execution traces).
   * - ``ONIKA_ENABLE_EXTERNAL_PROFILER``
     - ``OFF``
     - Enables an external profiler interface (only for builds without GPU).
   * - ``ONIKA_OMP_NUM_THREADS_WORKAROUND``
     - ``ON`` with Intel compilers
     - Works around an OpenMP ``num_threads`` bug.

.. list-table:: Memory and data structures
   :header-rows: 1
   :widths: 35 15 50

   * - Option
     - Default
     - Effect
   * - ``ONIKA_MEMORY_ZERO_ALLOC``
     - ``OFF``
     - Fills new allocations with zeros.
   * - ``SOATL_SIZE_TYPE_32BITS``
     - ``ON``
     - Uses 32-bit array sizes in SOATL containers (64-bit if ``OFF``).

.. list-table:: Tests, extras and site
   :header-rows: 1
   :widths: 35 15 50

   * - Option
     - Default
     - Effect
   * - ``ONIKA_REGRESSION_TEST_ENABLE``
     - ``ON``
     - Enables regression tests (``ctest``).
   * - ``ONIKA_REGRESSION_TEST_ENABLE_SEQ`` / ``_MT`` / ``_MPI``
     - ``ON``
     - Sequential, multi-threaded and MPI tests.
   * - ``ONIKA_BUILD_CONTRIBS``
     - ``OFF``
     - Builds the ``contribs`` directory.
   * - ``ONIKA_BUILD_<Plugin>``
     - ``ON``
     - Builds plugin ``<Plugin>`` (one option per plugin, see :ref:`plugins`).
   * - ``ONIKA_HAS_CCC_USER``
     - ``OFF``
     - Uses the CCC job resource interface (remaining time, for ``sim_continue``).
   * - ``ONIKA_FUTURE_DEPRECATION``
     - ``OFF``
     - Shows warnings for features that will be deprecated.

Dependencies are found with the standard CMake variables, e.g.
``-Dyaml-cpp_DIR=<prefix>/lib/cmake/yaml-cpp``, ``-DMPI_CXX_COMPILER=mpicxx``.

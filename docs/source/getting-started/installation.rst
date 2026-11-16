.. _installation:

Installation
============

|user| |opdev|

Prerequisites
-------------

To build **Onika**, you need:

- **CMake** ≥ 3.26
- A **C++20** compiler, e.g. **GCC** ≥ 11
- **MPI** (e.g. OpenMPI or MPICH) and **OpenMP**
- **yaml-cpp**, version **0.6.3** recommended
- **CUDA** or **HIP** *(optional)*, for GPU acceleration
- **Python 3** with ``pybind11`` *(optional)*, for the :ref:`Python bindings <pyonika>`

.. note::

   Version 0.6.3 of yaml-cpp is the tested reference. Recent versions of
   Onika's CMake also find yaml-cpp ≥ 0.7 (``yaml-cpp::yaml-cpp`` target).
   If you hit a problem with a newer version, go back to 0.6.3.

Installing yaml-cpp
-------------------

.. tabs::

   .. tab:: CMake (manual build)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone --depth 1 --branch yaml-cpp-0.6.3 https://github.com/jbeder/yaml-cpp.git
         mkdir ${CURRENT_HOME}/build-yaml-cpp && cd ${CURRENT_HOME}/build-yaml-cpp
         cmake ../yaml-cpp/ \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-yaml-cpp \
             -DYAML_BUILD_SHARED_LIBS=ON \
             -DYAML_CPP_BUILD_TESTS=OFF
         make install -j 4
         cd ${CURRENT_HOME}
         export PATH_TO_YAML=${CURRENT_HOME}/install-yaml-cpp

   .. tab:: Spack

      .. code-block:: bash

         spack install yaml-cpp@0.6.3
         spack load yaml-cpp@0.6.3

   .. tab:: APT (Ubuntu/Debian)

      .. code-block:: bash

         sudo apt-get update
         sudo apt-get install libyaml-cpp-dev

      .. note::

         The version installed by ``apt`` depends on your distribution.
         Check it with ``apt show libyaml-cpp-dev``.

Installing Onika
----------------

.. tabs::

   .. tab:: CMake (CPU only)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone https://github.com/Collab4exaNBody/onika.git
         cmake -S ${CURRENT_HOME}/onika -B ${CURRENT_HOME}/build-onika \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
             -Dyaml-cpp_DIR=${PATH_TO_YAML}/lib/cmake/yaml-cpp
         cmake --build ${CURRENT_HOME}/build-onika -j 10 --target install

   .. tab:: CMake (CUDA)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone https://github.com/Collab4exaNBody/onika.git
         cmake -S ${CURRENT_HOME}/onika -B ${CURRENT_HOME}/build-onika \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
             -Dyaml-cpp_DIR=${PATH_TO_YAML}/lib/cmake/yaml-cpp \
             -DONIKA_BUILD_CUDA=ON \
             -DCMAKE_CUDA_ARCHITECTURES=86
         cmake --build ${CURRENT_HOME}/build-onika -j 10 --target install

      Set ``CMAKE_CUDA_ARCHITECTURES`` to your GPU (e.g. ``80`` for A100, ``90`` for H100).

   .. tab:: CMake (HIP)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone https://github.com/Collab4exaNBody/onika.git
         cmake -S ${CURRENT_HOME}/onika -B ${CURRENT_HOME}/build-onika \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
             -Dyaml-cpp_DIR=${PATH_TO_YAML}/lib/cmake/yaml-cpp \
             -DONIKA_BUILD_CUDA=ON \
             -DONIKA_ENABLE_HIP=ON
         cmake --build ${CURRENT_HOME}/build-onika -j 10 --target install

      HIP support uses the same code path as CUDA: ``ONIKA_BUILD_CUDA``
      enables GPU support and ``ONIKA_ENABLE_HIP`` selects HIP instead of CUDA.

   .. tab:: Spack

      .. code-block:: bash

         # Get Spack
         git clone --depth=2 --branch=v0.23.0 https://github.com/spack/spack.git
         export SPACK_ROOT=$PWD/spack
         source ${SPACK_ROOT}/share/spack/setup-env.sh

         # Add Onika's Spack repository
         git clone https://github.com/Collab4exaNBody/spack-repos.git
         spack repo add spack-repos

         # Install Onika (add +cuda for GPU support)
         spack install onika
         spack load onika

All CMake options are listed in :ref:`cmake-options`.

What gets installed
-------------------

.. code-block:: text

   <install-prefix>/
   ├── bin/
   │   ├── setup-env.sh    environment variables (plugin, config and data paths)
   │   ├── onika-exec      the Onika application
   │   ├── onikarun        wrapper: sources setup-env.sh, then runs onika-exec
   │   └── trace_convert   execution trace converter
   ├── include/  lib/      headers and libraries, to build your own plugins
   ├── onika-config.cmake  CMake package, for find_package(onika)
   ├── plugins/            operator plugins (libonikaTools-plugin.so, tutorials, ...)
   ├── python/             pyonika package (only with -DONIKA_BUILD_PYTHON=ON)
   └── data/
       ├── config/         default input files (main-config.msp, ...)
       └── exemples/       example input files (print_loop.msp, ...)

Check your installation
-----------------------

.. code-block:: bash

   $ ./install-onika/bin/onikarun /dev/null

An empty input file runs the default simulation from ``main-config.msp``, which prints:

.. code-block:: text

   Version : 1.0.4
   MPI     : 1    process
   CPU     : 12   cores (max 12) : 0-11
   OpenMP  : 4    threads (v5.0)
   SIMD    : NEON
   SOATL   : align=16 , vec=4

     ██████╗ ███╗   ██╗██╗██╗  ██╗ █████╗     ██╗   ██╗ ██╗    ██████╗
    ██╔═══██╗████╗  ██║██║██║ ██╔╝██╔══██╗    ██║   ██║███║   ██╔═████╗
    ██║   ██║██╔██╗ ██║██║█████╔╝ ███████║    ██║   ██║╚██║   ██║██╔██║
    ██║   ██║██║╚██╗██║██║██╔═██╗ ██╔══██║    ╚██╗ ██╔╝ ██║   ████╔╝██║
    ╚██████╔╝██║ ╚████║██║██║  ██╗██║  ██║     ╚████╔╝  ██║██╗╚██████╔╝
     ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝      ╚═══╝   ╚═╝╚═╝ ╚═════╝
   =========== vgpu ================
   vgpu disabled
   =================================

   Internal unit system for default conversions
   +-------------+-------------------+--------+
   | Type        | Unit              | Symbol |
   +-------------+-------------------+--------+
   | length      | meter             | m      |
   ...

The first lines describe the machine (cores, threads, SIMD). The numbers depend on your machine.
``vgpu disabled`` means no GPU was used (CPU-only build, or ``--nogpu``).

Next step: :ref:`first-run`.

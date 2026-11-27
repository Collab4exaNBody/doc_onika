# Installation

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span>

## Prerequisites

To build **Onika**, you need:

- **CMake** ≥ 3.26
- A **C++20** compiler, e.g. **GCC** ≥ 11
- **MPI** (e.g. OpenMPI or MPICH) and **OpenMP**
- **yaml-cpp**, version **0.6.3** recommended
- **CUDA** or **HIP** *(optional)*, for GPU acceleration
- **Python 3** (tested with 3.10 to 3.13) with development headers and `numpy` *(optional)*, for the [Python bindings](../python/pyonika.md)

!!! note

    Version 0.6.3 of yaml-cpp is the tested reference. Recent versions of
    Onika's CMake also find yaml-cpp ≥ 0.7 (`yaml-cpp::yaml-cpp` target).
    If you hit a problem with a newer version, go back to 0.6.3.

## Installing yaml-cpp

=== "CMake (manual build)"

    ``` bash
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
    ```

=== "Spack"

    ``` bash
    spack install yaml-cpp@0.6.3
    spack load yaml-cpp@0.6.3
    ```

=== "APT (Ubuntu/Debian)"

    ``` bash
    sudo apt-get update
    sudo apt-get install libyaml-cpp-dev
    ```

    !!! note

        The version installed by `apt` depends on your distribution.
        Check it with `apt show libyaml-cpp-dev`.

## Installing Onika

=== "CMake (CPU only)"

    ``` bash
    export CURRENT_HOME=$PWD
    git clone https://github.com/Collab4exaNBody/onika.git
    cmake -S ${CURRENT_HOME}/onika -B ${CURRENT_HOME}/build-onika \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
        -Dyaml-cpp_DIR=${PATH_TO_YAML}/lib/cmake/yaml-cpp
    cmake --build ${CURRENT_HOME}/build-onika -j 10 --target install
    ```

=== "CMake (CUDA)"

    ``` bash
    export CURRENT_HOME=$PWD
    git clone https://github.com/Collab4exaNBody/onika.git
    cmake -S ${CURRENT_HOME}/onika -B ${CURRENT_HOME}/build-onika \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
        -Dyaml-cpp_DIR=${PATH_TO_YAML}/lib/cmake/yaml-cpp \
        -DONIKA_BUILD_CUDA=ON \
        -DCMAKE_CUDA_ARCHITECTURES=86
    cmake --build ${CURRENT_HOME}/build-onika -j 10 --target install
    ```

    Set `CMAKE_CUDA_ARCHITECTURES` to your GPU (e.g. `80` for A100, `90` for H100).

=== "CMake (HIP)"

    ``` bash
    export CURRENT_HOME=$PWD
    git clone https://github.com/Collab4exaNBody/onika.git
    cmake -S ${CURRENT_HOME}/onika -B ${CURRENT_HOME}/build-onika \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
        -Dyaml-cpp_DIR=${PATH_TO_YAML}/lib/cmake/yaml-cpp \
        -DONIKA_BUILD_CUDA=ON \
        -DONIKA_ENABLE_HIP=ON
    cmake --build ${CURRENT_HOME}/build-onika -j 10 --target install
    ```

    HIP support uses the same code path as CUDA: `ONIKA_BUILD_CUDA`
    enables GPU support and `ONIKA_ENABLE_HIP` selects HIP instead of CUDA.

=== "Spack"

    ``` bash
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
    ```

### CPU architecture flags

`ONIKA_ARCH_FLAGS` sets the CPU flags used for Onika **and every code built on
it** (plugins, exaNBody...). It is empty on x86-64 (no flags added) and
`-march=armv8-a` on ARM64. Use it to target your CPU, for example
`-DONIKA_ARCH_FLAGS="-march=x86-64-v3"`, `"-march=native"`, or
`"-mcpu=neoverse-v2"` / `"-mcpu=native"` on ARM (Graviton, Grace, Apple M).

### macOS

Onika builds on macOS for **CPU** execution (no GPU support), with the
CMake commands above. Differences with Linux:

- dependencies usually come from Homebrew (yaml-cpp, an MPI library, and an
  OpenMP runtime for the compiler); Onika finds the yaml-cpp headers outside
  system directories by itself;
- plugins keep the `.so` extension, as on Linux;
- `--debug-fpe` (floating point exception trapping) and `--pinethreads`
  (thread pinning) are not available: they are ignored with a warning.

All CMake options are listed in [CMake options](../reference/cmake-options.md). To build for AMD GPUs on a machine without one, see [Building for AMD GPUs (HIP) in Docker](docker-hip.md).

## What gets installed

``` text
<install-prefix>/
├── bin/
│   ├── setup-env.sh    environment variables (plugin, config and data paths)
│   ├── onika-exec      the Onika application
│   ├── onikarun        wrapper: sources setup-env.sh, then runs onika-exec
│   └── trace_convert   execution trace converter
├── include/  lib/      headers and libraries, to build your own plugins
├── cmake/  thirdparty/ CMake helpers and bundled third-party headers
├── onika-config.cmake  CMake package, for find_package(onika)
├── plugins/            operator plugins (libonikaTools-plugin.so, tutorials, ...)
├── python/             pyonika package (only with -DONIKA_BUILD_PYTHON=ON)
└── data/
    ├── config/         default input files (main-config.msp, ...)
    └── exemples/       example input files (print_loop.msp, concurrent_block_parallel.msp)
```

## Check your installation

``` bash
$ ./install-onika/bin/onikarun /dev/null
```

An empty input file runs the default simulation from `main-config.msp`, which prints:

``` text
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
```

!!! note

    Onika 1.1.0 still prints `Version : 1.0.4`: the version number in its
    `CMakeLists.txt` was not updated for the 1.1.0 release.

The first lines describe the machine (cores, threads, SIMD). The numbers depend on your machine.
`vgpu disabled` means no GPU was used (CPU-only build, or `--nogpu`).

Next step: [Your first run](first-run.md).

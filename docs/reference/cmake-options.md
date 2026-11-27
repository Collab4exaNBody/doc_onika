# CMake options

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

Main options of Onika's `CMakeLists.txt`, set with `-D<OPTION>=<value>`
when configuring.

**GPU**

| Option | Default | Effect |
|---|---|---|
| `ONIKA_BUILD_CUDA` | `OFF` | Enables GPU acceleration (CUDA, or HIP with the next option). |
| `ONIKA_ENABLE_HIP` | `OFF` | Uses HIP instead of CUDA. Requires `ONIKA_BUILD_CUDA=ON`. |
| `CMAKE_CUDA_ARCHITECTURES` |  | Target GPU architectures, e.g. `80` (A100), `90` (H100). |
| `ONIKA_CU_ENABLE_KERNEL_BOUNDS` | `OFF` | Uses launch bounds to restrict GPU kernels. |

**OpenMP and profiling**

| Option | Default | Effect |
|---|---|---|
| `ONIKA_HAVE_OPENMP_TOOLS` | `ON` if OpenMP ≥ 5 | Uses the OpenMP tools interface (OMPT) for profiling. |
| `ONIKA_HAVE_OPENMP_DETACH` | `ON` if OpenMP ≥ 5 | Uses the OpenMP 5 `detach` clause. |
| `ONIKA_ENABLE_TASK_PROFILING` | `ON` | Enables task profiling (needed for execution traces). |
| `ONIKA_ENABLE_EXTERNAL_PROFILER` | `OFF` | Enables an external profiler interface (only for builds without GPU). |
| `ONIKA_OMP_NUM_THREADS_WORKAROUND` | `ON` with Intel compilers | Works around an OpenMP `num_threads` bug. |

**Memory and data structures**

| Option | Default | Effect |
|---|---|---|
| `ONIKA_MEMORY_ZERO_ALLOC` | `OFF` | Fills new allocations with zeros. |
| `SOATL_SIZE_TYPE_32BITS` | `ON` | Uses 32-bit array sizes in SOATL containers (64-bit if `OFF`). |
| `ONIKA_INTERNAL_UNIT_SYSTEM` | SI | Initial internal unit system, as 8 C++ unit names (see [Units](../libraries/units.md#internal-unit-system)). |
| `ONIKA_DEFAULT_DATA_DIRS` | `.:./data:<prefix>/share/data` | Default search path for data files (`ONIKA_DATA_PATH` overrides it). |

**Tests, extras and site**

| Option | Default | Effect |
|---|---|---|
| `ONIKA_ENABLE_TESTS` | `ON` | Builds the test programs of `tests/` and registers them in `ctest`. |
| `SOATL_ENABLE_BENCHMARKS` | `ON` | Builds SOATL benchmarks (with `ONIKA_ENABLE_TESTS`); size set by `SOATL_BENCHMARKS_SIZE` (10000000). |
| `ONIKA_REGRESSION_TEST_ENABLE` | `ON` | Enables regression tests (`ctest`). |
| `ONIKA_REGRESSION_TEST_ENABLE_SEQ` / `_MT` / `_MPI` | `ON` | Sequential, multi-threaded and MPI tests. |
| `ONIKA_BUILD_CONTRIBS` | `OFF` | Builds the `contribs` directory. |
| `ONIKA_BUILD_<Plugin>` | `ON` | Builds plugin `<Plugin>` (one option per plugin, see [Plugins](../operators/plugins.md)). |
| `ONIKA_HAS_CCC_USER` | `OFF` | Uses the CCC job resource interface (remaining time, for `sim_continue`). |
| `ONIKA_FUTURE_DEPRECATION` | `OFF` | Shows warnings for features that will be deprecated. |

**Advanced variables**

| Variable | Default | Effect |
|---|---|---|
| `ONIKA_SETUP_ENV_COMMANDS` | empty | Shell commands added at the top of `setup-env.sh` (e.g. `module load ...`), so that `onikarun` sets up the environment. |
| `ONIKA_HAS_GPU_ATOMIC_MIN_MAX_DOUBLE` | `OFF` | The GPU supports `atomicMin`/`atomicMax` on `double` natively (used by `ONIKA_CU_ATOMIC_MIN/MAX`). |
| `ONIKA_CUDA_COMPILE_FLAGS`, `ONIKA_HIP_COMPILE_FLAGS` | warnings as errors, `--extended-lambda` | Extra flags for GPU compilation. |
| `ONIKA_ENABLE_KERNEL_DEBUG_INFO` | `OFF` | Debug information for parallel kernels. |
| `ONIKA_PARFOR_OMPSCHED_DEFAULT`, `ONIKA_BLKPARFOR_OMPSCHED_DEFAULT` | `OMP_SCHED_GUIDED` | Default OpenMP schedule of `parallel_for` / `block_parallel_for` on CPU (see [Options](../operators/parallel.md#parallel-options)). |
| `ONIKA_OMP_MAX_DEPENDS` | 10 | Maximum number of dynamic OpenMP task dependences. |
| `ONIKA_DEFAULT_ALIGNMENT`, `ONIKA_DEFAULT_CHUNK_SIZE`, `ONIKA_MINIMUM_CUDA_ALIGNMENT` | `-1` (auto) | Force memory alignment and SIMD chunk size (see [Memory](../libraries/memory.md#cudammvector)). |
| `ONIKA_EXTERNAL_PROFILER` | `NVTX` | With `ONIKA_ENABLE_EXTERNAL_PROFILER`: `NVTX` or `ROCTX`; `ONIKA_EXTERNAL_PROFILER_INCLUDE_DIRS` / `_LIBS` locate it. |

Dependencies are found with the standard CMake variables, e.g.
`-Dyaml-cpp_DIR=<prefix>/lib/cmake/yaml-cpp`, `-DMPI_CXX_COMPILER=mpicxx`.

## Tests with CMake and `ctest` { #tests }

`find_package(onika)` also provides CMake functions to declare tests in an
application or a plugin project:

| Function | Meaning |
|---|---|
| `onika_add_test(<name> <command> [args...])` | Adds the test `onika_test_<name>` running `<command>`. |
| `onika_add_test_par(<name> <np> <nc> <command> [args...])` | Same, with `<np>` MPI processes and `<nc>` threads each. |
| `AddRegressionTestDir(<dir>)` | Adds one test per `*.msp` file of each sub-directory of `<dir>`, run with `onikarun`, in sequential (`_seq`), multi-threaded (`_mt`) and MPI (4 processes, `_par`) variants. |

The **first line** of each `.msp` file of `AddRegressionTestDir` can contain
keywords that control its variants:

| Keyword | Effect |
|---|---|
| `no-seq`, `no-mt`, `no-mpi` | Do not create this variant. |
| `nthreads=<n>` or `nthreads=max` | Threads for the `_mt` and `_par` variants (default 4). |
| `enable-if-<VAR>` / `enable-if-<VAR>=<value>` | Create the test only if the CMake variable `<VAR>` is true (or equal to `<value>`). |

``` yaml
# no-mpi nthreads=8 enable-if-ONIKA_BUILD_CUDA
simulation:
  - ...
```

The variants are switched globally by `ONIKA_REGRESSION_TEST_ENABLE_SEQ`,
`_MT` and `_MPI`. Run the tests with `ctest` in the build directory.
Unit tests embedded in plugins are run differently, with
`--run_unit_tests` (see [Unit tests](../libraries/utilities.md#unit-tests)).

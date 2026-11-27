# Parallel API: one code for CPU and GPU

<span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

Onika's parallel API lets an operator write a loop body **once** and run it
with OpenMP on CPU or with CUDA/HIP on GPU. The choice is made at run time
from the build options and the configuration (`--nogpu`,
`--onika-gpu_disable_filter`...).

The examples on this page come from the `onikaParallelTutorial` plugin,
in `plugins/onikaParallelTutorial` of the Onika sources.

## Three building blocks

| Element | Role |
|---|---|
| **Functor** | A small struct with an `operator()` marked `ONIKA_HOST_DEVICE_FUNC`: the loop body, callable on CPU and GPU. |
| `parallel_for` / `block_parallel_for` | Builds a parallel operation over `N` iterations. |
| `parallel_execution_context()` | Method of `OperatorNode` giving the execution resources of the operator (CPU threads, GPU device, streams, profiling). |

## Simple loops: `parallel_for`

One call of the functor per index `i` in `[0, N)`:

``` cpp
#include <onika/parallel/parallel_for.h>

struct ScaleFunctor
{
  double * const __restrict__ m_array = nullptr;
  const double m_factor = 1.0;

  ONIKA_HOST_DEVICE_FUNC inline void operator () ( size_t i ) const
  {
    m_array[i] *= m_factor;
  }
};

// allow GPU execution for this functor
namespace onika { namespace parallel {
  template<> struct ParallelForFunctorTraits< ScaleFunctor >
  {
    static inline constexpr bool CudaCompatible = true;
  };
} }

// in execute():
ScaleFunctor func = { my_array->data() , *factor };
onika::parallel::parallel_for( my_array->size() , func , parallel_execution_context() );
```

Without the `ParallelForFunctorTraits` specialization, the functor runs on
CPU only. Data accessed on GPU must live in GPU-accessible memory, for example
`onika::memory::CudaMMVector<T>` (unified memory).

## Two-level loops: `block_parallel_for`

For nested loops, `block_parallel_for` gives one **block** (GPU thread block,
or CPU task) per outer index `i`. Inside the functor,
`ONIKA_CU_BLOCK_SIMD_FOR` spreads the inner loop over the threads of the
block:

``` cpp
#include <onika/parallel/block_parallel_for.h>

struct ValueAddFunctor
{
  Array2DReference m_array;
  double m_value_to_add = 0.0;

  ONIKA_HOST_DEVICE_FUNC inline void operator () ( size_t i ) const
  {
    const size_t cols = m_array.columns();
    ONIKA_CU_BLOCK_SIMD_FOR(size_t, j, 0, cols)
    {
      m_array[i][j] += m_value_to_add;
    }
  }
};

namespace onika { namespace parallel {
  template<> struct BlockParallelForFunctorTraits< ValueAddFunctor >
  {
    static constexpr bool CudaCompatible = true;
  };
} }

// in execute(): runs now and waits for completion
block_parallel_for( my_array->rows() , func , parallel_execution_context() );
```

## Running on the GPU: checklist { #parallel-gpu-checklist }

An operation runs on the GPU only if **all** these conditions hold; otherwise
it silently runs on the CPU, with the same results.

1. Onika is built with `ONIKA_BUILD_CUDA=ON`.
2. The functor is in a **`.cu` file** (compiled by `nvcc`/`hipcc`) and has
   `CudaCompatible = true` in its `ParallelForFunctorTraits` /
   `BlockParallelForFunctorTraits`.
3. The data it touches is in GPU-accessible memory (`CudaMMVector`), including
   index lists.
4. **The graph contains `init_cuda`** (and `finalize_cuda`, which reads its
   output: without it `init_cuda` is removed as unused). The default
   `simulation` of `main-config.msp` has both, so the simplest way is to keep it
   and put your work in the `run` hook:

    ``` yaml
    run: my_gpu_operator        # instead of redefining 'simulation'
    ```

    If you redefine `simulation`, include them yourself:

    ``` yaml
    simulation:
      - init_cuda
      - my_gpu_operator
      - finalize_cuda
    ```

5. GPU is not disabled (`--nogpu`, `--onika-gpu_disable_filter`, or
   `enable_gpu = false` in the [options](#parallel-options)).

To check, run with `--profiling-summary true`: GPU time appears in
parentheses next to the operator's total time.

``` text
Profiling .........................................  tot. time  ( GPU )   avginb  maxinb     count  percent
  init_cuda .......................................  1.135e+02            0.000   0.000         1  97.28%
  sum_demo ........................................  2.223e+00 (4.67e-01) 0.000   0.000         1   1.91%
```

`init_cuda` prints the GPUs found (`=========== cuda ====` then `GPUs : 1`).
Inside a functor, `ONIKA_CU_BLOCK_SIZE` is greater than 1 only on the GPU.

## Asynchronous execution

When the result of `block_parallel_for` is kept, the operation is not run
right away. Send it to the **execution queue** of the operator; it then runs
asynchronously and the operator can do other work:

``` cpp
auto my_addition = block_parallel_for( my_array->rows() , func ,
                                       parallel_execution_context("my_add_kernel") );  // optional tag for profiling

parallel_execution_queue() << std::move(my_addition);   // starts execution
// ... other work ...
parallel_execution_queue() << onika::parallel::synchronize;  // wait for completion
```

## Concurrent operations: lanes

Operations sent to the same **lane** (a GPU stream) run one after the other.
Operations on different lanes may run at the same time:

``` cpp
using namespace onika::parallel;

parallel_execution_queue() << set_lane(0) << std::move(a1_op1) << std::move(a1_op2)   // a1_op2 after a1_op1
                           << set_lane(1) << std::move(a2_op1) << std::move(a2_op2);  // concurrent with lane 0
parallel_execution_queue() << flush;        // schedule everything now
parallel_execution_queue() << synchronize;  // wait for all lanes
```

Instead of choosing lanes by hand, `any_lane()` lets Onika choose, using a
description of the data each operation reads and writes
(`local_access(...)`), to overlap operations that do not conflict.

### Under the hood: queues and streams

`parallel_execution_queue()` returns the operator's
`onika::parallel::ParallelExecutionQueue`. A queue holds operations
(`ParallelExecutionWrapper`, the value returned by `parallel_for` and
`block_parallel_for`) and sends them to **streams**
(`ParallelExecutionStream`, one per lane: a CUDA/HIP stream on GPU, a group of
OpenMP tasks on CPU). The manipulators sent with `<<` are:

| Manipulator | Effect |
|---|---|
| an operation | Appended to the current lane. |
| `set_lane(n)` / `any_lane()` | Selects the lane of the next operations (`any_lane`: chosen from data accesses). |
| `local_access(...)` | Declares the data read and written by the next operation (for `any_lane`). |
| another queue | Appends all its operations (delayed queues of `hybrid_async_block_parallel`). |
| `flush` | Starts the operations not started yet. |
| `synchronize` | Waits for all lanes. |

At the end of `execute()`, Onika flushes and synchronizes the queue of the
operator, so no operation outlives the operator.

## Iteration spaces: 1D, 2D, 3D and element lists { #parallel-spaces }

Instead of a count `N`, both `parallel_for` and `block_parallel_for` accept a
`ParallelExecutionSpace<ND>`, a box `[start, end)` in 1, 2 or 3 dimensions.
In 2D and 3D the functor receives an `onikaInt3_t` (`.x`, `.y`, `.z`):

``` cpp
struct Fill3D
{
  double * __restrict__ m_data = nullptr;
  ssize_t m_n = 0;
  ONIKA_HOST_DEVICE_FUNC inline void operator () ( onikaInt3_t c ) const
  {
    m_data[ (c.z*m_n + c.y)*m_n + c.x ] = c.x + 10*c.y + 100*c.z;
  }
};

// in execute():
ParallelExecutionSpace<3> space = { {0,0,0} , {N,N,N} };
parallel_for( space, Fill3D{ data->data(), N }, parallel_execution_context() );
```

With `block_parallel_for`, a 1D space can also carry an **element list**:
one block per listed element instead of one per index. The functor receives
the element value:

``` cpp
struct AddOneBlock
{
  double * __restrict__ m_data = nullptr;
  ONIKA_HOST_DEVICE_FUNC inline void operator () ( ssize_t i ) const
  {
    if( ONIKA_CU_THREAD_IDX == 0 ) m_data[i] += 1.0;   // one thread of the block does the work
  }
};

#include <onika/cuda/stl_adaptors.h>   // onika::cuda::span

// in the operator: ADD_SLOT( onika::memory::CudaMMVector<ssize_t> , idx , PRIVATE );
idx->assign( { 0, 5, 7 } );                         // element list in GPU-accessible memory
using ElementList = onika::cuda::span<const ssize_t>;
ParallelExecutionSpace<1,1,ElementList> some = { {0} , {3} , ElementList{ idx->data(), idx->size() } };
block_parallel_for( some, AddOneBlock{ data->data() }, parallel_execution_context() );   // touches 0, 5 and 7 only
```

!!! note

    - Element lists are only accepted by `block_parallel_for`; `parallel_for`
      stops compilation with `Index list not supported yet`.
    - Use `onika::cuda::span` for the list, and store the indices in a
      `CudaMMVector`. The default list type, `std::span`, works on CPU but does
      not compile for the GPU (`calling a constexpr __host__ function
      ("operator[]") from a __global__ function`).

## Options { #parallel-options }

A last, optional argument tunes an operation: `ParallelForOptions` for
`parallel_for`, `BlockParallelForOptions` for `block_parallel_for`.

| Field | Default | Meaning |
|---|---|---|
| `enable_gpu` | `true` | `false` forces CPU execution for this operation. |
| `omp_scheduling` | `OMP_SCHED_GUIDED` | OpenMP schedule on CPU: `OMP_SCHED_DYNAMIC`, `OMP_SCHED_GUIDED` or `OMP_SCHED_STATIC`. The default is set at build time (CMake `ONIKA_PARFOR_OMPSCHED_DEFAULT`, `ONIKA_BLKPARFOR_OMPSCHED_DEFAULT`). |
| `user_cb` | none | `ParallelExecutionCallback{ func, data }`: `func(data)` is called on the CPU once the operation has completed (also for asynchronous operations). |
| `max_block_size` | 128 | *block_parallel_for only.* Maximum GPU threads per block. |
| `fixed_gpu_grid_size` | `false` | *block_parallel_for only.* Use a fixed number of GPU blocks (number of SMs × `--onika-gpu_sm_mult` + `--onika-gpu_sm_add`); blocks then loop over the iterations. |
| `n_div_blocksize` | `false` | *block_parallel_for only.* Divide the range by the block size (ranges starting at 0 only). |
| `return_data`, `return_data_size` | none | Small result buffer copied back from the device after execution. |

``` cpp
static void on_done(void* user) { onika::lout << "callback: " << static_cast<const char*>(user) << std::endl; }

static char msg[] = "fill done";
ParallelForOptions opts;
opts.enable_gpu = false;
opts.omp_scheduling = OMP_SCHED_STATIC;
opts.user_cb = ParallelExecutionCallback{ on_done, msg };
parallel_for( data->size(), AddOne{ data->data() }, parallel_execution_context(), opts );
```

``` text
callback: fill done
```

## Reductions { #parallel-reductions }

Combine partial results with atomic operations. With `block_parallel_for`,
each thread of a block accumulates a private partial sum over its share of
the inner loop, then adds it atomically:

``` cpp
struct RowSum
{
  const double * __restrict__ m_mat = nullptr;
  double * __restrict__ m_row_sum = nullptr;
  double * __restrict__ m_total = nullptr;
  size_t m_cols = 0;

  ONIKA_HOST_DEVICE_FUNC inline void operator () ( size_t i ) const
  {
    double s = 0.0;
    ONIKA_CU_BLOCK_SIMD_FOR(size_t, j, 0, m_cols) { s += m_mat[i*m_cols+j]; }   // partial sum of this thread
    ONIKA_CU_ATOMIC_ADD( m_row_sum[i] , s );                                    // combine threads of the block
    ONIKA_CU_ATOMIC_ADD( *m_total , s );                                        // combine all blocks
  }
};
```

With a 100 × 1000 matrix of ones, this gives `row 0 sum = 1000` and
`total = 100000`. `ONIKA_CU_ATOMIC_MIN` / `ONIKA_CU_ATOMIC_MAX` work the same
way.

`onika/cuda/cuda_reduction.h` also provides block-level tree reductions in
shared memory, `onika::cuda::block_reduce_add / _min / _max(x, IntConst<BlockSize>{})`,
which avoid one atomic per thread. `BlockSize` must be **exactly** the number of
threads of the block:

``` cpp
#include <onika/cuda/uninitialized_place_holder.h>   // needed before cuda_reduction.h in Onika 1.1.0
#include <onika/cuda/cuda_reduction.h>

static constexpr int GPU_BLOCK = 128;                                // threads per block on GPU
static constexpr int BLOCK = ONIKA_CU_VALUE_IF_CUDA(GPU_BLOCK, 1);   // in device code: 128, in CPU code: 1

struct RowSumReduce
{
  const double * __restrict__ m_mat = nullptr;
  double * __restrict__ m_row_sum = nullptr;
  size_t m_cols = 0;
  ONIKA_HOST_DEVICE_FUNC inline void operator () ( size_t i ) const
  {
    double s = 0.0;
    ONIKA_CU_BLOCK_SIMD_FOR(size_t, j, 0, m_cols) { s += m_mat[i*m_cols+j]; }
    s = onika::cuda::block_reduce_add( s , onika::IntConst<BLOCK>{} );   // sum over the threads of the block
    if( ONIKA_CU_THREAD_IDX == 0 ) m_row_sum[i] = s;                    // no atomic needed
  }
};

// in execute(): the block size is chosen in host code, so use the GPU value explicitly
BlockParallelForOptions opts;
opts.max_block_size = GPU_BLOCK;
block_parallel_for( *rows, RowSumReduce{ mat->data(), sums->data(), size_t(*cols) }, parallel_execution_context(), opts );
```

!!! warning

    `ONIKA_CU_VALUE_IF_CUDA(a,b)` gives `a` only in **device** code. In host
    code (in `execute()`), it gives `b`. Setting
    `opts.max_block_size = BLOCK` would launch blocks of 1 thread while the
    reduction expects 128.

## Helpers { #parallel-helpers }

| Helper | Header | Use |
|---|---|---|
| `parallel_memset(ptr, n, value, pec)` | `onika/parallel/memset.h` | Fills an array, on GPU when possible. |
| `onika::parallel::random_engine()` | `onika/parallel/random.h` | A `std::mt19937_64` per thread (CPU code only). `set_seed(s)` gives reproducible seeds (different per MPI rank and thread); `save_state()` / `load_state()` store them in YAML, e.g. for restarts. |
| `onika::memory::CudaMMVector<T>` | `onika/memory/allocator.h` | `std::vector` in unified memory, usable on CPU and GPU. See [Memory and containers](../libraries/memory.md). |
| `onika::cuda::VectorShallowCopy<T>` | `onika/cuda/ro_shallow_copy.h` | Non-owning, read-only view of a `std::vector` (pointer + size) to pass to a functor. |
| `onika::cuda::InputArraySpan<T,N>` | `onika/cuda/input_array_span.h` | Read-only array argument for a functor: up to `N` elements are copied inside the functor (avoids unified-memory latency), larger arrays are referenced. *CUDA and CPU only in Onika 1.1.0: it does not compile with HIP.* |
| `onika::cuda::cu_block_memcpy` / `cu_block_memmove` | `onika/cuda/memcpy.h`, `memmove.h` | Copy bytes cooperatively with all threads of a block. |
| `onika::cuda::CudaDeviceStorage<T>` | `onika/cuda/device_storage.h` | Reference-counted buffer in device memory. |
| `onika::cuda::min / max / numeric_limits` | `onika/cuda/cuda_math.h` | Host/device versions of the standard functions. |

Example: a functor with a small coefficient array copied at launch and a
read-only view of a large array:

``` cpp
struct Poly
{
  onika::cuda::InputArraySpan<double,4> m_coefs;   // up to 4 values copied into the functor
  onika::cuda::VectorShallowCopy<double> m_x;      // view of a CudaMMVector (no copy)
  double * __restrict__ m_y = nullptr;
  ONIKA_HOST_DEVICE_FUNC inline void operator () ( size_t i ) const
  {
    double y = 0.0, xp = 1.0;
    for(size_t k=0;k<m_coefs.size();k++) { y += m_coefs[k]*xp; xp *= m_x[i]; }
    m_y[i] = y;
  }
};

// in execute(), with x, y, coefs of type CudaMMVector<double>:
Poly p = { onika::cuda::InputArraySpan<double,4>( *coefs ),
           onika::cuda::VectorShallowCopy<double>( x->data(), x->size() ), y->data() };
parallel_for( x->size(), p, parallel_execution_context() );
```

## Portability macros { #parallel-macros }

Functors are compiled for the CPU and, in `.cu` files of a GPU build, for the
GPU. These macros from `onika/cuda/cuda.h` have a meaning on both:

| Macro | GPU | CPU |
|---|---|---|
| `ONIKA_HOST_DEVICE_FUNC` | `__host__ __device__` | nothing |
| `ONIKA_CU_THREAD_IDX` | thread index in the block | `0` |
| `ONIKA_CU_BLOCK_SIZE` | threads per block | `1` |
| `ONIKA_CU_BLOCK_IDX` | block index in the grid | OpenMP thread number |
| `ONIKA_CU_BLOCK_SIMD_FOR(T,i,s,e)` | loop over `[s,e)` spread on the threads of the block | `omp simd` loop over `[s,e)` |
| `ONIKA_CU_BLOCK_SYNC()` | `__syncthreads()` | nothing |
| `ONIKA_CU_BLOCK_SHARED` | `__shared__` | nothing |
| `ONIKA_CU_ATOMIC_ADD(x,a)`, `_SUB`, `_MIN`, `_MAX` | atomic operation | OpenMP atomic |
| `ONIKA_CU_BLOCK_FENCE()` | block memory fence | nothing |
| `ONIKA_CU_DEVICE_FENCE()` | device memory fence | `std::atomic_thread_fence` |
| `ONIKA_CU_VALUE_IF_CUDA(a,b)` | `a` | `b` |
| `ONIKA_CU_MAX_THREADS_PER_BLOCK` | 128 | 128 |

!!! warning

    Do not compute array indices from `ONIKA_CU_BLOCK_IDX`: on CPU it is the
    OpenMP thread number, not the iteration. Use the index passed to the
    functor.

## Tutorial operators

Each operator of `onikaParallelTutorial` shows one pattern (sources in
`plugins/onikaParallelTutorial`). Most run alone with the default slot
values, on the GPU when available:

``` bash
$ echo "run: concurrent_block_parallel" > t.msp
$ onikarun t.msp --profiling-summary true
```

`synchronous_block_parallel` and `async_block_parallel` require an input
array (`my_array`) produced by another operator: alone, they are removed from
the graph. `data/exemples/concurrent_block_parallel.msp` defines a batch `run_test`
with much larger sizes (`--set-run run_test`); it is a benchmark that keeps a
laptop GPU busy for several minutes.

| Operator | Pattern |
|---|---|
| `synchronous_block_parallel` | `block_parallel_for`, waits for completion. |
| `async_block_parallel` | Operation sent to the execution queue, then synchronized. |
| `concurrent_block_parallel` | Two arrays processed on two lanes (`set_lane`), concurrently. |
| `automatic_concurrent_parallel` | Same work, lanes chosen automatically from data accesses (`any_lane`, `local_access`). |
| `hybrid_async_block_parallel` | GPU-enabled and CPU-only kernels mixed, grouped in delayed queues. |
| `parallel_for_benchmark`, `parallel_for_3d_benchmark` | `parallel_for` over 1D and 3D index spaces. |

## Controlling execution at run time

- `--nogpu`: everything on CPU.
- `--onika-gpu_disable_filter "[regex]"`: no GPU for operators whose path matches.
- `--onika-gpu_block_size`, `--onika-gpu_sm_mult`: GPU grid shape.
- `--onika-parallel_task_core_mult`: number of CPU tasks per core.

See [Command-line options](../running/command-line.md).

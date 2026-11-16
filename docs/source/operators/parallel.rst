.. _parallel-api:

Parallel API: one code for CPU and GPU
======================================

|opdev| |core|

Onika's parallel API lets an operator write a loop body **once** and run it
with OpenMP on CPU or with CUDA/HIP on GPU. The choice is made at run time
from the build options and the configuration (``--nogpu``,
``--onika-gpu_disable_filter``...).

The examples on this page come from the ``onikaParallelTutorial`` plugin,
in ``plugins/onikaParallelTutorial`` of the Onika sources.

Three building blocks
---------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Element
     - Role
   * - **Functor**
     - A small struct with an ``operator()`` marked ``ONIKA_HOST_DEVICE_FUNC``:
       the loop body, callable on CPU and GPU.
   * - ``parallel_for`` / ``block_parallel_for``
     - Builds a parallel operation over ``N`` iterations.
   * - ``parallel_execution_context()``
     - Method of ``OperatorNode`` giving the execution resources of the operator
       (CPU threads, GPU device, streams, profiling).

Simple loops: ``parallel_for``
------------------------------

One call of the functor per index ``i`` in ``[0, N)``:

.. code-block:: cpp

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

Without the ``ParallelForFunctorTraits`` specialization, the functor runs on
CPU only. Data accessed on GPU must live in GPU-accessible memory, for example
``onika::memory::CudaMMVector<T>`` (unified memory).

Two-level loops: ``block_parallel_for``
---------------------------------------

For nested loops, ``block_parallel_for`` gives one **block** (GPU thread block,
or CPU task) per outer index ``i``. Inside the functor,
``ONIKA_CU_BLOCK_SIMD_FOR`` spreads the inner loop over the threads of the
block:

.. code-block:: cpp

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

Asynchronous execution
----------------------

When the result of ``block_parallel_for`` is kept, the operation is not run
right away. Send it to the **execution queue** of the operator; it then runs
asynchronously and the operator can do other work:

.. code-block:: cpp

   auto my_addition = block_parallel_for( my_array->rows() , func ,
                                          parallel_execution_context("my_add_kernel") );  // optional tag for profiling

   parallel_execution_queue() << std::move(my_addition);   // starts execution
   // ... other work ...
   parallel_execution_queue() << onika::parallel::synchronize;  // wait for completion

Concurrent operations: lanes
----------------------------

Operations sent to the same **lane** (a GPU stream) run one after the other.
Operations on different lanes may run at the same time:

.. code-block:: cpp

   using namespace onika::parallel;

   parallel_execution_queue() << set_lane(0) << std::move(a1_op1) << std::move(a1_op2)   // a1_op2 after a1_op1
                              << set_lane(1) << std::move(a2_op1) << std::move(a2_op2);  // concurrent with lane 0
   parallel_execution_queue() << flush;        // schedule everything now
   parallel_execution_queue() << synchronize;  // wait for all lanes

Instead of choosing lanes by hand, ``any_lane()`` lets Onika choose, using a
description of the data each operation reads and writes
(``local_access(...)``), to overlap operations that do not conflict.

Tutorial operators
------------------

Each operator of ``onikaParallelTutorial`` shows one pattern. Run them with
the inputs in ``data/exemples`` (e.g. ``concurrent_block_parallel.msp``).

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Pattern
   * - ``synchronous_block_parallel``
     - ``block_parallel_for``, waits for completion.
   * - ``async_block_parallel``
     - Operation sent to the execution queue, then synchronized.
   * - ``concurrent_block_parallel``
     - Two arrays processed on two lanes (``set_lane``), concurrently.
   * - ``automatic_concurrent_parallel``
     - Same work, lanes chosen automatically from data accesses (``any_lane``, ``local_access``).
   * - ``hybrid_async_block_parallel``
     - GPU-enabled and CPU-only kernels mixed, grouped in delayed queues.
   * - ``parallel_for_benchmark``, ``parallel_for_3d_benchmark``
     - ``parallel_for`` over 1D and 3D index spaces.

Controlling execution at run time
---------------------------------

- ``--nogpu``: everything on CPU.
- ``--onika-gpu_disable_filter "[regex]"``: no GPU for operators whose path matches.
- ``--onika-gpu_block_size``, ``--onika-gpu_sm_mult``: GPU grid shape.
- ``--onika-parallel_task_core_mult``: number of CPU tasks per core.

See :ref:`command-line`.

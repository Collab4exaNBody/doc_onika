# Memory and containers { #memory }

<span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

Onika provides allocators and containers that work on CPU and GPU, a
structure-of-arrays container (SOATL), and tools to measure memory use.
The examples on this page were compiled and run against Onika 1.1.0, as
standalone programs linked with Onika (see
[Build it with CMake](../coupling/embedding.md)).

## GPU-accessible vectors: `CudaMMVector` { #cudammvector }

`onika::memory::CudaMMVector<T>` (`onika/memory/allocator.h`) is a
`std::vector<T>` whose memory is allocated in **unified (managed) memory**
when Onika is built with CUDA or HIP, so that the same data can be read and
written by CPU code and by GPU kernels. Without GPU support it is plain,
aligned host memory. Use it for every array accessed by a
[parallel operation](../operators/parallel.md) that may run on GPU.

``` cpp
#include <onika/memory/allocator.h>

onika::memory::CudaMMVector<double> v( 1000, 1.0 );   // same interface as std::vector
```

It can be read from YAML like a list, so it can be the type of a slot set in
an input file.

The allocator behind it, `onika::memory::GenericHostAllocator`, allocates with
`cudaMallocManaged` / `hipMallocManaged` when GPU support is enabled at run
time, and aligned `malloc` otherwise (`--nogpu`, or no device). With the CMake
option `ONIKA_MEMORY_ZERO_ALLOC=ON`, every allocation is filled with zeros.

| Constant | Value (x86-64, AVX2) | Meaning |
|---|---|---|
| `onika::memory::DEFAULT_ALIGNMENT` | 32 | Alignment for SIMD loads. |
| `onika::memory::DEFAULT_CHUNK_SIZE` | 8 | SIMD vector length; array sizes of SOATL containers are rounded to it. |
| `onika::memory::GenericHostAllocator::DefaultAlignBytes` | 256 | Allocation alignment (at least 256 bytes for GPU). |
| `onika::memory::simd_arch()` | `"AVX2"` | SIMD instruction set the code was compiled for. |

These are the `SIMD` and `SOATL` lines printed at startup.

## Structure of arrays: SOATL { #soatl }

Particle codes store many fields per element (positions, velocities, type...).
SOATL (`onika/soatl/`) stores them as a **structure of arrays**: one array per
field, all in one aligned allocation. Loops over one field are contiguous and
vectorize well, and the whole container can be moved to or from the GPU at
once. exaNBody stores the particles of each cell this way.

When Onika runs with a GPU, SOATL containers are allocated in unified memory:
the array pointers (`c[field]`) can be passed directly to GPU functors.

### 1. Declare fields

A field is an empty type with a `FieldId` specialization giving its value type
and name. Declare a constant of each field type to use it as an index:

``` cpp
#include <onika/soatl/field_id.h>
#include <onika/soatl/field_arrays.h>
#include <onika/soatl/field_tuple.h>
#include <onika/soatl/copy.h>

struct _rx {}; struct _ry {}; struct _rz {}; struct _type {};

namespace onika { namespace soatl {
  template<> struct FieldId<_rx>   { using value_type = double;  using Id = _rx;   static const char* name() { return "rx"; } };
  template<> struct FieldId<_ry>   { using value_type = double;  using Id = _ry;   static const char* name() { return "ry"; } };
  template<> struct FieldId<_rz>   { using value_type = double;  using Id = _rz;   static const char* name() { return "rz"; } };
  template<> struct FieldId<_type> { using value_type = uint8_t; using Id = _type; static const char* name() { return "type"; } };
} }

static constexpr onika::soatl::FieldId<_rx>   field_rx;
static constexpr onika::soatl::FieldId<_ry>   field_ry;
static constexpr onika::soatl::FieldId<_rz>   field_rz;
static constexpr onika::soatl::FieldId<_type> field_type;
```

A macro makes this shorter; the Onika tests (`tests/declare_fields.h`)
define one:

``` cpp
#define SOATL_DECLARE_FIELD(__type,__name,__desc) \
struct __##__name {}; \
namespace onika { namespace soatl { template<> struct FieldId<__##__name> { \
    using value_type = __type; \
    using Id = __##__name; \
    static const char* name() { return __desc ; } \
  }; } } \
::onika::soatl::FieldId<__##__name> __name;

SOATL_DECLARE_FIELD(double , particle_rx , "Particle position X");
```

### 2. Create, fill and use a container

``` cpp
using namespace onika::soatl;

// one array per field, in a single allocation
auto particles = make_hybrid_field_arrays( field_rx, field_ry, field_rz, field_type );
using Particles = decltype(particles);

// add elements (an element is a FieldTuple)
for(int i=0;i<10;i++) particles.push_back( Particles::make_tuple( i*1.0, i*2.0, i*3.0, uint8_t(i%2) ) );

// whole arrays: fast, vectorizable loops
double* __restrict__ rx = particles[field_rx];
const double* __restrict__ ry = particles[field_ry];
for(size_t i=0;i<particles.size();i++) rx[i] += ry[i];

// one element, as a tuple
auto p3 = particles[3];
std::cout << "particle 3: rx=" << p3[field_rx] << " ry=" << p3[field_ry] << " type=" << int(p3[field_type]) << std::endl;

// only some fields of an element
FieldTuple<_rx,_rz> pos;
particles.read_tuple( 4, pos );

// copy common fields into another container
auto positions = make_hybrid_field_arrays( field_rx, field_ry, field_rz );
positions.resize( particles.size() );
copy( positions, particles, 0, particles.size(), field_rx, field_ry, field_rz );   // start, count, fields

// containers must be emptied before they are destroyed
positions.clear();
particles.clear();
```

``` text
size=10 capacity=16 alignment=32 chunksize=8
particle 3: rx=9 ry=6 type=1
particle 4 position (x,z) = 12 , 12
positions[9].rz = 27 , payload bytes = 240
```

!!! warning "Call `clear()` before destruction"

    The destructor does not free the memory: it only checks (in debug builds)
    that the container is empty. Call `clear()` (or `resize(0)`) before a
    SOATL container goes out of scope, otherwise its memory leaks, and a debug
    build stops with `Assertion 'empty()' failed`.

!!! warning "Copying a subset of fields"

    Pass the range explicitly when you list fields:
    `copy(dst, src, start, count, fields...)`. In Onika 1.1.0, the shorter
    form `copy(dst, src, fields...)` ignores the field list and copies all
    fields of `src`, which corrupts memory if `dst` lacks some of them.

### Container API

| Member | Meaning |
|---|---|
| `make_hybrid_field_arrays(f1, f2, ...)` | Creates a container (type `FieldArrays<Alignment, ChunkSize, ids...>`) with default alignment and chunk size. `make_hybrid_field_arrays(cst::align<A>{}, cst::chunk<C>{}, f1, ...)` chooses them. |
| `c[field]` | Pointer to the array of `field` (`nullptr` when empty). |
| `c[i]` | Element `i`, as a `FieldTuple` copy. |
| `Type::make_tuple(v1, v2, ...)` | Builds an element, values in field order. |
| `push_back(t)`, `resize(n)`, `assign(n, t)`, `clear()`, `shrink_to_fit()` | As for `std::vector`. |
| `set_tuple(i, t)`, `read_tuple(i, t)`, `write_tuple(i, t)` | Write / read element `i`; `read_tuple`/`write_tuple` accept tuples with a subset of the fields. |
| `swap(a, b)` | Exchanges elements `a` and `b`. |
| `size()`, `capacity()`, `empty()` | Capacity is rounded up to the chunk size. |
| `alignment()`, `chunksize()` | Static properties of the container. |
| `payload_bytes()` | Bytes used by the stored values. |
| `field_pointers()`, `make_field_arrays_view(c, fields...)` | A `FieldPointerTuple`: a light, copyable set of array pointers to pass to functors and GPU kernels. |
| `has_field(field)` | `constexpr` test. |
| `copy(dst, src, start, count, fields...)` | Copies a range of some fields (`onika/soatl/copy.h`). |

`FieldTuple<ids...>` holds one value per field, indexed the same way
(`t[field_rx]`). It converts from a tuple with other fields: common fields are
copied, others are zeroed.

**Field combiners** (`onika/soatl/field_combiner.h`) define virtual fields
computed from real ones: `c[combiner]` returns an accessor whose `[i]`
evaluates a function of the fields of element `i`. Declare them with
`ONIKA_DECLARE_FIELD_COMBINER`.

## Measuring memory { #memory-usage }

`onika::memory::memory_bytes(x...)` (`onika/memory/memory_usage.h`) returns
the memory used by objects, including what their containers allocated. It
knows standard containers, `std::pair`, `std::tuple`, arrays, and any type
with a `memory_bytes()` method:

``` cpp
#include <onika/memory/memory_usage.h>

struct MyCache
{
  std::vector<double> m_values;
  std::vector<int> m_index;
  inline size_t memory_bytes() const { return onika::memory::memory_bytes( m_values, m_index ); }
};

std::vector<double> a(1000);
MyCache c{ std::vector<double>(10), std::vector<int>(10) };
std::cout << onika::memory::memory_bytes(a)    << std::endl;   // 8024
std::cout << onika::memory::memory_bytes(a, c) << std::endl;   // 8192
```

Slot types with a `memory_bytes()` method are reported by the
[`memory_stats`](../operators/advanced.md#memory-stats) operator.

`onika::memory::MemoryResourceCounters` reads the counters of the process:

``` cpp
onika::memory::MemoryResourceCounters counters;
counters.read();
long rss = counters.stats[ onika::memory::MemoryResourceCounters::RESIDENT_SET_MB ];
```

Counters: `TOTAL_PROG_MB`, `RESIDENT_SET_MB`, `SHARED_PAGES`, `TEXT_MB`,
`LIB_MB`, `DATA_STACK_MB`, `DIRTY_PAGES`, `PAGE_RECLAIMS`, `PAGE_FAULTS`,
`SWAPS`, `BLOCK_INPUT_OPS`, `BLOCK_OUTPUT_OPS`, `MESSAGES_SENT`, ... They are
used by `--profiling-resmem`.

## Other memory tools { #memory-other }

These are building blocks for framework code:

| Type | Header | Use |
|---|---|---|
| `MemoryPartionner` / `MemoryPartionnerMT` | `onika/memory/memory_partition.h` | Sub-allocates pieces of one pre-allocated buffer (bump allocator, thread-safe for `MT`), usable in GPU code. |
| `StreamingStoragePool` | `onika/memory/streaming_storage_pool.h` | Pool of 64 ring buffers of 256 Kb for short-lived messages produced and consumed by concurrent tasks. |
| `PointerFifo<T>` | `onika/memory/pointer_fifo.h` | Thread-safe FIFO of pointers (atomics and a spin lock). |
| `ChunkLogAllocationStrategy` | `onika/memory/alloc_strategy.h` | Capacity policy of SOATL containers: capacity doubles when growing, shrinks when the size falls below half, and is rounded to the chunk size. |

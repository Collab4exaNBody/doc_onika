# MPI utilities { #mpi }

<span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

`onika/mpi/` provides helpers for common MPI patterns in operators: reducing
several values at once, checking that all processes agree, statistics over
processes, and redistributing data identified by global ids. All functions
are in namespace `onika::mpi` and take an `MPI_Comm`; in an operator, get it
from a slot:

``` cpp
ADD_SLOT( MPI_Comm , mpi , INPUT , MPI_COMM_WORLD );
```

The `mpi_comm_world` operator produces this `mpi` slot for the whole graph
(see [Built-in operators](../reference/builtin-operators.md)).

The example below was compiled and run on 3 processes with Onika 1.1.0.

## Reductions of several values: `all_reduce_multi`

`all_reduce_multi(comm, op, T{}, v1, v2, ...)` reduces any number of variables
with **one** `MPI_Allreduce`, converting them to the type `T`:

``` cpp
#include <onika/mpi/all_reduce_multi.h>

double esum = rank;
onika::mpi::all_reduce_multi( MPI_COMM_WORLD, MPI_SUM, double{}, esum );   // 0+1+2 = 3

long a = rank, b = 10*rank;
onika::mpi::all_reduce_multi( MPI_COMM_WORLD, MPI_MAX, long{}, a, b );    // a=2, b=20, in one call
```

## Do all processes agree? `all_value_equal`

``` cpp
#include <onika/mpi/all_value_equal.h>

bool same = onika::mpi::all_value_equal( MPI_COMM_WORLD, np );     // true
bool diff = onika::mpi::all_value_equal( MPI_COMM_WORLD, rank );   // false
```

Returns `true` on every process if the value (or `std::vector`) is
byte-for-byte identical to the one of process 0. Useful to check that a
parameter is consistent before a collective operation.

## Statistics over processes: `mpi_parallel_stats`

``` cpp
#include <onika/mpi/mpi_parallel_stats.h>

std::vector<double> x = { 1.0*rank, 2.0 }, vmin, vmax, vavg;
int np = 0, r = 0;
onika::mpi::mpi_parallel_stats( MPI_COMM_WORLD, x, np, r, vmin, vmax, vavg );
// vmin[0]=0  vmax[0]=2  vavg[0]=1
```

Computes, element by element, the minimum, maximum and average of `x` over the
processes. Onika uses it for the `--profiling-summary` table.
`mpi_parallel_sum(comm, in, sum, min, avg, max)` does the same for one
`unsigned long long`.

## Redistributing data by ids: `communication_scheme_from_ids` and `data_move`

A common problem: elements are identified by a global id in `[idMin, idMax)`.
Each process holds some elements (the ids *before*), and must end up with
another set (the ids *after*), for example after a load balancing step.
`onika/mpi/xs_data_move.h` solves it in two steps:

1. `communication_scheme_from_ids` computes, once, who sends what to whom;
2. `data_move` moves an array of values according to this scheme. Call it once
   per array to move (positions, velocities...), with the same scheme.

``` cpp
#include <onika/mpi/xs_data_move.h>

// ids 0..N-1: each process owns 4 consecutive ids, and wants the 4 ids of its right neighbor
const onika::mpi::id_type N = 4*np;
std::vector<onika::mpi::id_type> ids_before, ids_after;
std::vector<double> values_before;
for(onika::mpi::id_type i=4*rank; i<4*(rank+1); i++) { ids_before.push_back(i); values_before.push_back(100.0*i); }
for(onika::mpi::id_type i=0; i<4; i++) ids_after.push_back( (4*(rank+1)+i) % N );

// 1. communication scheme (collective)
std::vector<int> send_indices, send_count, send_displ, recv_indices, recv_count, recv_displ;
onika::mpi::communication_scheme_from_ids( MPI_COMM_WORLD, 0, N,
    ids_before.size(), ids_before.data(), ids_after.size(), ids_after.data(),
    send_indices, send_count, send_displ, recv_indices, recv_count, recv_displ );

// 2. move the values (collective), in the order of ids_after
std::vector<double> values_after( ids_after.size() );
onika::mpi::data_move( MPI_COMM_WORLD, send_indices, send_count, send_displ, recv_indices, recv_count, recv_displ,
                       values_before.begin(), values_after.begin() );
```

``` text
P0: after: 4->400 5->500 6->600 7->700
P1: after: 8->800 9->900 10->1000 11->1100
P2: after: 0->0 1->100 2->200 3->300
```

Every id of `[idMin, idMax)` must be in the *before* set of exactly one
process. An id can be requested by several processes (*after* sets may
overlap). `data_move` works with any copyable value type and any iterators;
input and output may be the same array.

## MPI datatypes

`onika::mpi::mpi_datatype<T>()` (`onika/mpi/data_types.h`) returns the
`MPI_Datatype` of `char`, `signed char`, `short`, `int`, `long`, `long long` (signed and unsigned), `float` and `double`,
and `mpi_typeof(x)` the one of a variable.

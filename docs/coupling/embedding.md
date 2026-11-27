# Using Onika from C++: embedding and coupling { #embedding }

<span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

`onika-exec` is a five-line program built on a small C++ API,
`onika/app/api.h`. Your own application can use the same API to:

- **embed** an Onika simulation: build the graph from input files, run it,
  read the results;
- **drive** it: run the whole graph or only a part of it, as many times as
  needed;
- **couple** it with another code: exchange values with the graph through
  its slots, at each step of a coupled loop.

The examples on this page were compiled and run against Onika 1.1.0. The
reference example of the Onika sources is `exemples/coupling`.

## The high-level API

``` cpp
#include <onika/app/api.h>

namespace onika::app
{
  std::shared_ptr<ApplicationContext> init(int argc, char const * const argv[]);
  std::shared_ptr<ApplicationContext> init(std::vector<std::string>& argv);
  void run(std::shared_ptr<ApplicationContext> ctx);                                  // whole graph
  void run(std::shared_ptr<ApplicationContext> ctx, onika::scg::OperatorNode* node);  // one node (and its children)
  void end(std::shared_ptr<ApplicationContext> ctx);
}
```

| Function | What it does |
|---|---|
| `init(argc, argv)` | Takes the same arguments as `onika-exec` (input files, then [command-line options](../running/command-line.md)). Initializes MPI (unless already done), OpenMP, logging, GPU and plugins, reads the input files and **builds** the simulation graph. Nothing runs yet. |
| `run(ctx)` | Runs the whole simulation graph. |
| `run(ctx, node)` | Runs only `node`, a part of the graph. |
| `end(ctx)` | Prints the profiling summary and traces if requested, frees all slot resources, and calls `MPI_Finalize()` if Onika initialized MPI. |

The returned `ApplicationContext` gives access to the graph:

| Member | Meaning |
|---|---|
| `get_error_code()` | `-1` if the graph is ready to run. A value `>= 0` means `init` stopped early (`--help`, unit tests, ...): return it as the exit code. |
| `node("path")` | The operator with this path name, or `nullptr`. |
| `set_multiple_run(true)` | Allows several calls to `run()` (see [Running several times](#embedding-multiple-run)). |
| `m_configuration` | The parsed [`configuration` block](../inputs/configuration.md) (`ApplicationConfiguration`). |
| `m_mpi_rank`, `m_mpi_nprocs`, `m_ngpus`, `m_cpucount` | Resources found at initialization. |
| `m_simulation_graph` | Root of the graph (`std::shared_ptr<OperatorNode>`). |

### The smallest application

This is the whole `main()` of `onika-exec`:

``` cpp title="main.cpp"
#include <onika/app/api.h>

int main(int argc, char* argv[])
{
  auto app = onika::app::init(argc, argv);
  if( app->get_error_code() >= 0 ) return app->get_error_code();
  onika::app::run( app );
  onika::app::end( app );
  return 0;
}
```

### Build it with CMake

`find_package(onika)` provides the variables needed to compile and link
against Onika:

``` cmake title="CMakeLists.txt"
cmake_minimum_required(VERSION 3.26)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(MyHostApplication VERSION 1.0 LANGUAGES CXX)

find_package(onika REQUIRED)          # configure with -Donika_DIR=<install-prefix>

add_executable(myhostapp main.cpp)
target_compile_options(myhostapp PUBLIC ${ONIKA_COMPILE_OPTIONS})
target_compile_definitions(myhostapp PUBLIC ${ONIKA_COMPILE_DEFINITIONS})
target_include_directories(myhostapp PUBLIC ${ONIKA_INCLUDE_DIRS})
target_link_directories(myhostapp PUBLIC ${ONIKA_LIBRARY_DIRS})
target_link_libraries(myhostapp PUBLIC ${ONIKA_LIBRARIES})
```

``` bash
$ cmake -S . -B build -Donika_DIR=<install-prefix>
$ cmake --build build
$ source <install-prefix>/bin/setup-env.sh     # plugin and configuration paths
$ ./build/myhostapp input.msp --omp_num_threads 4
```

The application needs the same environment as `onika-exec`
(`ONIKA_PLUGIN_PATH`, `ONIKA_CONFIG_PATH`...): source `setup-env.sh` first.

## Finding operators: path names { #embedding-paths }

Every operator has a **path name**: the names of its parents and its own
name, joined with `.`, starting from `simulation`. `apply_graph()` visits a
node and all its children; use it to print the paths of a graph:

``` cpp
app->node("simulation")->apply_graph( [](onika::scg::OperatorNode* op)
  { std::cout << op->pathname() << std::endl; } );
```

For `print_loop.msp` ([Your first run](../getting-started/first-run.md)):

``` text
simulation
simulation.global
simulation.unit_system
simulation.compute_loop
simulation.compute_loop.print_int
simulation.compute_loop.next_time_step
simulation.compute_loop.sim_continue
```

!!! note

    A batch with a single operator is **collapsed** into that operator. In
    `print_loop.msp`, `print_timestep` and `compute_loop_stop` contain one
    operator each, so the paths are `compute_loop.print_int` and
    `compute_loop.sim_continue`, not `compute_loop.compute_loop_stop`.
    Print the paths rather than guessing them; `--debug-graph` shows the same
    tree.

The slots of a node are listed with `in_slots()` and `out_slots()`.
Slot names are the names after [rebinding](../inputs/msp-language.md#msp-rebind):

``` cpp
auto loop = app->node("simulation.compute_loop");
for( auto [name, slot] : loop->in_slots() )  std::cout << "in  " << name << " : " << slot->value_type() << std::endl;
for( auto [name, slot] : loop->out_slots() ) std::cout << "out " << name << " : " << slot->value_type() << std::endl;
```

``` text
in  compute_loop_continue : b
out compute_loop_continue : b
out timestep : l
out physical_time : d
```

`value_type()` is the compiler's type name (`typeid(T).name()`): `b` is
`bool`, `l` is `long`, `d` is `double` with GCC and Clang.

## Exchanging values with the graph { #embedding-slots }

Three methods of a slot (`onika::scg::OperatorSlotBase`) connect the graph
with the host application's data:

| Method | Direction | Effect |
|---|---|---|
| `in_slot("x")->copy_input_value(v)` | host → graph | The slot gets a copy of `v`. |
| `in_slot("x")->set_value_pointer(&v)` | host → graph | The slot reads the host variable `v` directly. Later changes of `v` are seen at the next run, without another call. |
| `out_slot("x")->output_value_pointer<T>()` | graph → host | Returns a `const T*` to the value produced by the graph. |

!!! warning "Rules"

    - **The type must match exactly** the slot type, otherwise the run stops with
      `Slot ... can only copy input value of type ...`. Check the type with
      `value_type()` or `onika-exec --help <operator>`. Slots created by
      `global` are `long` for integers and `double` for reals: write
      `copy_input_value(2L)`, not `copy_input_value(2)`.
    - **Set inputs that nothing else provides.** If an upstream operator
      produces the same slot (for example `global` in the input file), the
      connection wins and the host value is not used. Leave the value out of
      the input file and let the host provide it.
    - Set inputs **after `init()` and before `run()`**.

### Example: the host provides a parameter and reads a result

Start from `print_loop.msp` and remove the line `nsteps: 20` from `global`.
Run as is, Onika stops with `Slot 'nsteps' in operator
'simulation.compute_loop.sim_continue' has no value`. The host application
provides it:

``` cpp title="main.cpp"
#include <onika/app/api.h>
#include <iostream>

int main(int argc, char* argv[])
{
  auto app = onika::app::init(argc, argv);
  if( app->get_error_code() >= 0 ) return app->get_error_code();

  // give a value to an input slot, from the host application
  auto stop = app->node("simulation.compute_loop.sim_continue");
  stop->in_slot("nsteps")->copy_input_value( 2L );     // nsteps is a long

  onika::app::run( app );

  // read an output slot
  auto loop = app->node("simulation.compute_loop");
  const long* ts = loop->out_slot("timestep")->output_value_pointer<long>();
  std::cout << "timestep after run = " << *ts << std::endl;

  onika::app::end( app );
  return 0;
}
```

``` text
Current timestep = 0
Current timestep = 1
Current timestep = 2
timestep after run = 3
```

## Running several times { #embedding-multiple-run }

By default, after an operator runs outside of a loop, Onika *finalizes* it:
the resources of its private slots are released, since the run is over.
Call `set_multiple_run(true)` before the first `run()` whenever you will call
`run()` more than once.

The state of the graph is **kept between runs**: slot values are not reset.
Running a whole graph a second time therefore continues from where it
stopped; in `print_loop.msp`, `compute_loop_continue` is already false and
the loop body does not run again. To drive a simulation step by step, run
**a part of the graph** instead, as below.

## Code coupling: a step-wise loop { #embedding-coupling }

In a coupled simulation, the host application owns the main time loop and
calls Onika once per coupling step. The input file defines one batch for
one Onika step; the host runs that batch with `run(ctx, node)` and
exchanges values through slots between two steps.

``` yaml title="coupled.msp"
global:
  timestep: 0
  physical_time: 0.0

# one step of the Onika side, called by the host application
onika_step:
  - next_time_step
  - print_time

print_time:
  rebind: { value: physical_time }
  body:
    - print_real: { prefix: "  onika: physical_time = ", suffix: "\n" }

simulation:
  - global
  - onika_step
```

`dt` is not defined in the file: the host owns it and lends it to the graph
with `set_value_pointer`:

``` cpp title="main.cpp"
#include <onika/app/api.h>
#include <iostream>

int main(int argc, char* argv[])
{
  auto app = onika::app::init(argc, argv);
  if( app->get_error_code() >= 0 ) return app->get_error_code();
  app->set_multiple_run( true );   // run() will be called several times

  // the time step is owned by the host and read by Onika through a pointer
  double dt = 0.5;
  auto step = app->node("simulation.onika_step");
  step->in_slot("dt")->set_value_pointer( &dt );

  onika::app::run( app, app->node("simulation.global") );   // initialization part only

  for(int i=0; i<3; i++)
  {
    onika::app::run( app, step );                              // one Onika step
    const double t = *step->out_slot("physical_time")->output_value_pointer<double>();
    std::cout << "host: step " << i << " done, t = " << t << std::endl;
    dt *= 2.0;                                                 // the host changes dt for the next step
  }

  onika::app::end( app );
  return 0;
}
```

``` text
  onika: physical_time = 5.0000000000e-01
host: step 0 done, t = 5.0000000000e-01
  onika: physical_time = 1.5000000000e+00
host: step 1 done, t = 1.5000000000e+00
  onika: physical_time = 3.5000000000e+00
host: step 2 done, t = 3.5000000000e+00
```

The same pattern scales to real coupling:

- **Large data** (particle arrays, fields) is exchanged the same way: point
  an input slot at the host container with `set_value_pointer`, and read the
  graph's containers with `output_value_pointer<T>()`. No copy is made.
- **Several Onika parts** can be run in any order: for example an
  `onika_predict` batch and an `onika_correct` batch around a call to the
  other code.
- **Coupling operators**: when the exchange needs computation (interpolation,
  unit conversion, MPI redistribution), write it as an
  [operator](../operators/anatomy.md) of the Onika graph, and keep only raw
  data exchange in the host code.

## MPI in a host application { #embedding-mpi }

`init()` calls `MPI_Init_thread` (with `MPI_THREAD_MULTIPLE`, or `MPI_Init`
with `--mpimt false`) **only if MPI is not initialized yet**. A host
application that uses MPI itself initializes it first; Onika then uses it as
is, and `end()` does not call `MPI_Finalize()`:

``` cpp
#include <onika/app/api.h>
#include <mpi.h>

int main(int argc, char* argv[])
{
  int provided = 0;
  MPI_Init_thread(&argc, &argv, MPI_THREAD_MULTIPLE, &provided);   // the host owns MPI

  auto app = onika::app::init(argc, argv);
  if( app->get_error_code() >= 0 ) return app->get_error_code();
  // ... run(), exchange values ...
  onika::app::end( app );   // MPI_Finalize() is NOT called here

  MPI_Finalize();
  return 0;
}
```

``` bash
$ mpirun -n 2 ./build/myhostapp coupled.msp
```

!!! note

    The high-level `init()` runs Onika on `MPI_COMM_WORLD`. To run it on a
    sub-communicator, use the low-level API below (`initialize_mpi()` takes
    an `MPI_Comm`) to write your own `init()`.

## The low-level API { #embedding-low-level }

`init()`, `run()` and `end()` are made of lower-level functions, also
declared in `onika/app/api.h`. Use them to change one step of the
initialization (sub-communicator, OpenMP set by the host, extra YAML input...).
`src/core/api.cpp` shows how `init()` chains them.

| Function | Role |
|---|---|
| `initialize()` | Reads `ONIKA_CONFIG_PATH` and `ONIKA_DATA_PATH`. |
| `parse_command_args(argc, argv)` | Splits the arguments into input files and a YAML node of options. |
| `load_yaml_input(files, cmdline)` | Loads and merges the input files; returns the input data, the `simulation` node and the `ApplicationConfiguration`. |
| `initialize_mpi(config, argc, argv, comm)` | Initializes MPI if needed; returns rank, size, thread support, and whether MPI was initialized outside. |
| `intialize_openmp(config, rank, allow_openmp_conf)` | Applies the OpenMP settings (pass `false` when the host controls OpenMP). |
| `initialize_gpu(config)` | Initializes CUDA/HIP; returns the number of GPUs. |
| `initialize_plugins(config)` | Loads the plugin database and the plugins. |
| `run_embedded_tests(config)` | Runs unit tests if `--run_unit_tests` is set. |
| `initialize_profiling(config, rank, nprocs)` | Prepares traces and timers. |
| `print_help(config, appname, plugin_db)` | Prints help if `--help` was given. |
| `build_simulation_graph(config, simulation_node)` | Builds the graph. |
| `run_simulation_graph(node, profiling)` | Runs a node. |
| `node_from_path(graph, path)` | Finds a node by path name. |
| `finalize(config, graph, trace, external_mpi_init)` | Profiling output, resource release, `MPI_Finalize()`. |

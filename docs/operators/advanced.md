# Advanced operators { #advanced-operators }

<span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

This page goes beyond [Anatomy of an operator](anatomy.md): your own types in
slots, several implementations behind one operator name, custom factories,
error handling and the life cycle of an operator. All examples were compiled
as a plugin and run against Onika 1.1.0.

## Your own types in slots { #custom-slot-types }

Any C++ type can be a slot type. To give it a value **from an input file**,
provide a `YAML::convert` specialization (from yaml-cpp). Onika uses it when
the slot is set in the input file; without it, the slot can still be
connected to other operators, but not set from YAML.

``` cpp
#include <yaml-cpp/yaml.h>

struct Interval
{
  double lo = 0.0;
  double hi = 0.0;
};

namespace YAML
{
  template<> struct convert<Interval>
  {
    static bool decode(const Node& node, Interval& v)
    {
      if( ! node.IsSequence() || node.size() != 2 ) return false;   // expects [ lo , hi ]
      v.lo = node[0].as<double>();
      v.hi = node[1].as<double>();
      return true;
    }
  };
}
```

``` cpp
ADD_SLOT( Interval , range , INPUT , REQUIRED , DocString{"[ min , max ]"} );
```

``` yaml
- clamp_value: { range: [ 0.0 , 5.0 ] }
```

If `decode` returns `false`, the run stops with:

``` text
could not convert key range to type Interval in node clamp_value
YAML data is :
...
```

Onika already provides conversions for its own types: `Vec3d`, `IJK`,
`Mat3d`, `AABB`, `Plane3d`, `Quaternion` (see [Math types](../libraries/math.md)), quantities with units
(see [Units and physical quantities](../libraries/units.md)), and the standard containers
(`std::vector`, `std::map`...) of convertible types.

!!! note "Type promotion"

    `ADD_SLOT` turns `int` into `long` and `unsigned int` into
    `unsigned long`, so that integer slots match the values created by
    `global` and the input file. Prefer `long` in your own code.

## Several implementations, one name: `make_compatible_operator` { #compatible-operators }

`make_compatible_operator<T1, T2, ...>` registers several classes under one
name. When the graph is built, Onika looks at the types of the slots
connected upstream (the *flavor*) and creates the first class whose input
slot types match.

``` cpp
template<class T>
class ClampValue : public OperatorNode
{
  ADD_SLOT( T        , value , INPUT_OUTPUT , REQUIRED , DocString{"value to clamp"} );
  ADD_SLOT( Interval , range , INPUT        , REQUIRED , DocString{"[ min , max ]"} );

public:
  inline std::string documentation() const override final { return "Clamps value into range."; }

  inline void execute() override final
  {
    if( range->lo > range->hi )
    {
      onika::fatal_error() << "clamp_value: empty range [" << range->lo << "," << range->hi << "]" << std::endl;
    }
    if( *value < range->lo ) *value = range->lo;
    if( *value > range->hi ) *value = range->hi;
  }
};

ONIKA_AUTORUN_INIT(clamp_value)
{
  OperatorNodeFactory::instance()->register_factory( "clamp_value",
    make_compatible_operator< ClampValue<double> , ClampValue<long> > );
}
```

The same operator name then works on a `double` and on a `long`:

``` yaml
global:
  x: 7.5        # double
  n: 12         # long

clamp_x:
  rebind: { value: x }
  body: [ clamp_value: { range: [ 0.0 , 5.0 ] } ]

clamp_n:
  rebind: { value: n }
  body: [ clamp_value: { range: [ 0 , 10 ] } ]

simulation:
  - global
  - clamp_x
  - clamp_n
  # ... print x and n
```

``` text
x = 5.0000000000e+00
n = 10
```

When no class matches, the error lists why each candidate was rejected:

``` text
ERR:   | Couldn't find a compatible operator. flavor was :
ERR:   | Available factories failed for the following reasons :
ERR:   | 	slot value with type double incompatible with flavor type string
ERR:   | 	slot value with type long incompatible with flavor type string
```

## Custom factories { #custom-factories }

`make_simple_operator` and `make_compatible_operator` are *factory functions*.
You can write your own, with this signature:

``` cpp
std::shared_ptr<OperatorNode> factory( const YAML::Node& node, const OperatorNodeFlavor& flavor );
```

`node` is the YAML given to the operator in the input file, `flavor` maps
upstream slot names to their types. Return the operator, or throw
`OperatorCreationException` to refuse. For example, choose the class from a
key of the input file:

``` cpp
template<class T>
class MakeCounter : public OperatorNode
{
  ADD_SLOT( T , counter , OUTPUT );
public:
  inline void execute() override final
  {
    *counter = T(42);
    onika::lout << "make_counter: created a " << onika::pretty_short_type<T>() << std::endl;
  }
};

static std::shared_ptr<OperatorNode> make_counter_factory( const YAML::Node& node, const OperatorNodeFlavor& flavor )
{
  std::string type = "long";
  if( node.IsMap() && node["type"] ) type = node["type"].as<std::string>();
  if( type == "long" )   return std::make_shared< MakeCounter<long> >();
  if( type == "double" ) return std::make_shared< MakeCounter<double> >();
  throw OperatorCreationException( "make_counter: unknown type '" + type + "'" );
}

ONIKA_AUTORUN_INIT(make_counter)
{
  OperatorNodeFactory::instance()->register_factory( "make_counter", make_counter_factory );
}
```

``` yaml
simulation:
  - make_counter: { type: double }
  - print_counter          # batch printing 'counter' with print_real
```

``` text
make_counter: created a double
counter = 4.2000000000e+01
```

A name can be registered **several times**, for example by several plugins:
the factories are tried in registration order, and the first one that does
not throw wins. If all fail, every reason is printed.

## Errors: `fatal_error()` { #fatal-error }

`onika::fatal_error()` (in `onika/log.h`) is a log stream that stops the
whole run (all MPI processes) when the line ends, after printing the message
and a stack trace:

``` cpp
onika::fatal_error() << "clamp_value: empty range [" << range->lo << "," << range->hi << "]" << std::endl;
```

``` text
ERR: *****************************************
************* FATAL ERROR ***************
clamp_value: empty range [5,0]
```

In Python ([`pyonika`](../python/pyonika.md#errors)), it raises `pyonika.OnikaError` instead of stopping
the process, when it is safe to do so.

Use it for invalid input that cannot be recovered. The same mechanism is
used by Onika itself, for example `Slot 'nsteps' in operator ... has no value`.

## Default values from constructor arguments { #ctor-default-values }

A slot default value can be any value the slot type can be constructed from.
A `std::tuple` is unpacked as the arguments of a constructor. From the
`default_slot_value_from_ctor_args` operator of `plugins/onikaBasicTutorial`:

``` cpp
static const std::vector<double> myvec = { 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0 };

ADD_SLOT( std::vector<double> , input1, INPUT, std::make_tuple(size_t(10),5.0) );                   // 10 values equal to 5
ADD_SLOT( std::vector<double> , input2, INPUT, std::make_tuple(myvec.begin()+1,myvec.begin()+6) );  // iterator pair: 2 3 4 5 6
ADD_SLOT( std::vector<double> , input3, INPUT, myvec );                                             // copy
```

## Slot API summary { #slot-api }

Inside `execute()`, a slot `s` declared with `ADD_SLOT( T , s , ... )`
provides:

| Expression | Meaning |
|---|---|
| `*s`, `s->member` | The value (stops with an error if there is none). |
| `s.has_value()` | `true` if a value is available (use it with `OPTIONAL`). |
| `s.get_pointer()` | `T*` to the value, or `nullptr`. |
| `s.name()`, `s.pathname()` | Slot name, and full path (`operator.path.slot`). |
| `s.value_type()` | Type name of the slot. |
| `s.is_input()`, `s.is_output()`, `s.is_private()` | Direction tests. |

From outside the operator (host application, tools), slots are reached with
`op->in_slot("name")` / `op->out_slot("name")`, see
[Using Onika from C++](../coupling/embedding.md#embedding-slots).

### Connecting slots of different types

Slots are connected by name **and** type. Integer types of the same size are
convertible: `int64_t` ↔ `uint64_t`, `int32_t` ↔ `uint32_t`, and on most
platforms 64-bit to 32-bit integers. You can declare other conversions,
typically between a type and its base class, once at plugin load:

``` cpp
ONIKA_AUTORUN_INIT(my_conversions)
{
  onika::scg::OperatorSlotBase::register_type_conversion< Derived , Base >();
}
```

## Operator life cycle { #operator-life-cycle }

The virtual methods of `OperatorNode`, in the order Onika calls them:

| Step | Method | Default behavior / when to override |
|---|---|---|
| Creation | factory function | See [Custom factories](#custom-factories). |
| Configuration | `yaml_initialize(const YAML::Node&)` | Sets the slots from the YAML of the input file. Override to read extra keys, then call the base version. |
| Graph built | `post_graph_build()` | Called once the whole graph exists. |
| Compilation | `compile()` | Slots and names are frozen after this call. |
| Each run | `run()` → `run_prolog()`, `execute()`, `run_epilog()` | `run_prolog/epilog` handle profiling, memory statistics and slot resources. Override only `execute()`. |
| End | `finalize()` | Called after the last run (not inside loops, or with `set_multiple_run`). Frees the resources of `PRIVATE` slots. |

Other virtual methods change how the graph treats the operator:

| Method | Default | Meaning |
|---|---|---|
| `documentation()` | empty | Help text of `--help <operator>`. |
| `is_sink()` | `true` if no output | Keep the operator even if its outputs are unused, see [`is_sink()`](anatomy.md#operator-sink). |
| `is_terminal()` | `true` | `false` for operators that contain others (batches). |
| `is_looping()` | `false` | `true` for loops (batches with `loop: true`). |

### OpenMP tasks: operators in a `task_group` batch

In a batch with `task_group: true` ([Batch options](../inputs/msp-language.md#msp-batches)), Onika opens one
OpenMP parallel region for the batch, and calls `execute()` of each operator
from a single thread, inside an `omp taskgroup`. Operators of such a batch
should create OpenMP tasks (`#pragma omp task`) rather than parallel regions:
tasks of successive operators can then overlap, and the batch waits for all of
them at the end. The [parallel API](parallel.md) operations sent to
`parallel_execution_queue()` follow the same rule.

### Number of threads per operator

`--omp_max_threads_filter` limits the number of OpenMP threads of some
operators, by path name (regular expressions):

``` bash
$ onika-exec input.msp --omp_max_threads_filter '{ ".*print.*": 1 }'
```

## Selecting operators by path: `operator_set_from_regex` { #operator-set-from-regex }

Several options (`--profiling-filter`, `--debug-filter`,
`--onika-gpu_disable_filter`...) select operators with regular expressions on
their path names. The same helper is available to your own code, in
`onika/scg/operator_set_from_regex.h`:

``` cpp
#include <onika/scg/operator_set_from_regex.h>

std::unordered_set<size_t> hashes =
  onika::scg::operator_set_from_regex( graph, { ".*compute_loop.*" , "simulation\\.global" } );

graph->apply_graph( [&](onika::scg::OperatorNode* op)
{
  if( hashes.count( op->hash() ) ) { /* op is selected */ }
});
```

It returns the `hash()` of every operator whose `pathname()` matches one of
the expressions. The optional `message` argument prints each match with
`ldbg`.

## Operator memory statistics: `memory_stats` { #memory-stats }

The `memory_stats` operator of the `onikaTools` plugin prints the memory used
by the process and by slot values. Insert it anywhere in the graph:

``` yaml
simulation:
  - global
  - compute_loop
  - memory_stats: { graph_res_mem: true }
```

| Slot | Default | Meaning |
|---|---|---|
| `mpi` | `MPI_COMM_WORLD` | Communicator for min/max/average over processes. |
| `rusage_stats` | `true` | Print process memory usage (`getrusage`). |
| `graph_slots` | `true` | Print the memory used by the values of the slots, per type. |
| `graph_res_mem` | `false` | Print the resident memory increase of each operator (values are 0 unless `--profiling-resmem true`). |
| `page_size` | `4096` | Memory page size, for resident memory estimates. |

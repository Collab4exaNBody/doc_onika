# Utilities { #utilities }

<span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

Smaller tools of `onika/` used by operators and applications: logging,
strings, files, YAML helpers, small containers and unit tests. Examples were
compiled and run against Onika 1.1.0.

## Logging { #logging }

`onika/log.h` declares the log streams. Use them instead of `std::cout`:

| Stream | Use |
|---|---|
| `onika::lout` | Normal output. Printed by MPI rank 0 only, unless `--logging-parallel true`. Redirected with `--logging-log_file`. |
| `onika::lerr` | Errors and warnings (`--logging-err_file`). |
| `ldbg` | Debug messages, printed only with `--logging-debug true`. Inside an operator, `ldbg` is filtered by `--debug-filter` (regular expressions on operator paths). |
| `onika::fatal_error()` | Prints the message and a stack trace, then aborts all processes. See [Errors](../operators/advanced.md#fatal-error). |

``` cpp
onika::lout << "normal" << std::endl;
ldbg << "only with --logging-debug true" << std::endl;
onika::lout.progress_bar( "computing ", 0.42 );   // progress bar on a terminal
```

In lambdas and OpenMP blocks, use `onika::lout_stream()`,
`lerr_stream()` and `ldbg_stream()` to avoid capturing globals.

## Strings { #strings }

`onika/string_utils.h`:

``` cpp
onika::format_string("step %05d , t = %.3e", 42, 1.5e-3);   // "step 00042 , t = 1.500e-03" (printf formats)
onika::split_string("rx,ry,rz", ',');                         // { "rx", "ry", "rz" }
onika::large_integer_to_string(123456789);                    // "123,456,789"
"particle" + onika::plurial_suffix(3);                        // "particles"
```

Also: `str_tolower`, `str_indent`, `format_string_buffer` (into a fixed
buffer, usable without allocation), `function_name_and_args("f(a,b)", name, args)`.

`onika/print_utils.h` and `onika/type_utils.h`: `pretty_short_type<T>()`
(readable type names, used in error messages), `print_if_possible`,
`append_to_file`.

## Files { #files }

`onika/file_utils.h`:

| Function | Meaning |
|---|---|
| `data_file_path(path)` | Finds a data file: a relative `path` is searched in the directories of `ONIKA_DATA_PATH` (`.:./data:<install>/share/data` by default), the first match is returned. Use it for every input data file read by an operator. |
| `config_file_path(path)` | Same for input files (`.msp`), in `ONIKA_CONFIG_PATH`. Used by `includes`. |
| `set_data_file_dirs("dir1:dir2")` | Changes the data search path. |
| `dirname`, `is_relative_path`, `concat_dir_path`, `resolve_file_path` | Path helpers. |

``` cpp
onika::set_data_file_dirs( ".:/tmp" );
std::string f = onika::data_file_path( "potential.dat" );   // "./potential.dat" or "/tmp/potential.dat"
```

## YAML helpers { #yaml-helpers }

**Enumerations read from input files.** `EXANB_YAML_ENUM(namespace, Name, values...)`
(`onika/yaml/yaml_enum.h`) declares a small enum type with a YAML
conversion and `operator <<`:

``` cpp
#include <onika/yaml/yaml_enum.h>

EXANB_YAML_ENUM(my_plugin, Integrator, VERLET, LEAPFROG);

// in an operator:
ADD_SLOT( my_plugin::Integrator , scheme , INPUT , my_plugin::Integrator::VERLET );
if( *scheme == my_plugin::Integrator::LEAPFROG ) { ... }
```

``` yaml
- my_operator: { scheme: LEAPFROG }
```

An unknown name gives the value `UNDEFINED`.

**Node helpers** (`onika/yaml/yaml_utils.h`, namespace `onika::yaml`):

``` cpp
long steps = onika::yaml::read<long>( node, "steps", 1 );   // value, or default if the key is missing
YAML::Node m = onika::yaml::merge_nodes( a, b );           // b overrides a (as for 'includes')
onika::yaml::dump_node_to_stream( onika::lout, m );        // print
```

Also `remove_map_key`, `dump_node_to_file`, `resolve_config_file_includes`,
`yaml_load_file_abort_on_except`.

## Small containers { #small-containers }

Fixed-size containers usable in GPU functors:

| Type | Header | Meaning |
|---|---|---|
| `onika::oarray_t<T,N>` | `onika/oarray.h` | Like `std::array`, usable on GPU. |
| `onika::inplace_vector<T,N>` | `onika/oarray.h` | Vector with at most `N` elements, stored inline. |
| `onika::FixedCapacityVector<T>` | `onika/fixed_capacity_vector.h` | Vector interface over storage you provide (`FixedCapacityVector<int> v(ptr, capacity)`); never allocates. |
| `onika::nd_array<T,I,J,...>` | `onika/nd_array.h` | Multi-dimensional fixed array. |
| `onika::FlatTuple<T...>` | `onika/flat_tuple.h` | Tuple usable on GPU (element access with `tuple_index<I>`). |

Others: `onika/hash_utils.h` (`multi_hash(a, b, ...)`, combined `std::hash`),
`onika/thread.h` (`atomic_lock_spin_mutex`, usable on GPU, and
`omp_spin_mutex`), `onika/color_scale.h` (RGB colors), `onika/plot1d.h`
(`Plot1D`, sampled curves).

## Unit tests { #unit-tests }

`onika/test/unit_test.h` lets plugins embed unit tests, run with
`--run_unit_tests true`:

``` cpp
#include <onika/test/unit_test.h>
#include <onika/string_utils.h>

ONIKA_UNIT_TEST(my_string_tests)
{
  ONIKA_TEST_ASSERT( onika::format_string("%03d", 7) == "007" );
  ONIKA_TEST_ASSERT( onika::split_string("a b c").size() == 3 );
}
```

``` bash
$ onika-exec /dev/null --run_unit_tests true --generate_plugins_db true
```

``` text
Unit test 1/6 : my_failing_test ... Assertion '1 + 1 == 3' failed
FAILED
Unit test 2/6 : my_string_tests ... Ok
Unit test 3/6 : onika_physics_units_conversion ... ...
Unit test 4/6 : xsdatamove_process_id_range_size ... Ok
...
Executed 6 unit tests : 4 passed, 2 failed
```

The tests of Onika itself and of the **loaded** plugins are run, then the
program exits. The exit code is the number of failed tests, so it can be used
in CI.

!!! warning "Load the plugins"

    Plugins are loaded on demand (when an input file uses one of their
    operators). With an empty input file, only the tests of Onika itself run,
    unless the plugin database is being regenerated: add
    `--generate_plugins_db true` to load all plugins and run all tests.

For tests driven by CMake (`ctest`), see
[CMake options](../reference/cmake-options.md#tests).

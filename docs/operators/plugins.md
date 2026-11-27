# Plugins

<span class="badge badge-opdev">Operator developer</span>

Operators are compiled into **plugins**: shared libraries that Onika loads at
run time. An application is Onika plus a set of plugins; adding an operator
never requires rebuilding Onika itself.

## Build a plugin with CMake

Onika installs a CMake package. `find_package(onika)` gives you the
`onika` target and the `onika_add_plugin` function:

``` cmake
cmake_minimum_required(VERSION 3.26)
project(MyOnikaPlugins LANGUAGES C CXX)

find_package(onika REQUIRED)               # configure with -Donika_DIR=<install-prefix>

set(myPlugin_LINK_LIBRARIES onika)
onika_add_plugin(myPlugin ${CMAKE_CURRENT_SOURCE_DIR}/src)
```

`onika_add_plugin(<Name> <dir>)`:

- compiles every `*.cpp` and `*.cu` file of `<dir>` into
  `plugins/lib<Name>-plugin.so` in the build directory;
- compiles `*.cu` files with CUDA (or HIP) when Onika was built with GPU
  support, and as plain C++ otherwise, so the same source works everywhere.
  With a **HIP** build of Onika, configure your project with
  `-DONIKA_USE_HIP=ON` (see [HIP in Docker](../getting-started/docker-hip.md#5-build-plugins-and-applications-against-the-hip-installation));
- compiles files in `<dir>/lib`, if this directory exists, into a separate
  shared library `lib<Name>.so` for code shared between plugins;
- includes `<dir>/<Name>.cmake` if it exists, for plugin-specific settings;
- adds a CMake option `ONIKA_BUILD_<Name>` (`ON` by default).

!!! warning "New source files"

    The list of source files is read when CMake **configures** the project.
    After adding a new `.cpp` or `.cu` file, re-run
    `cmake -S my-plugins -B build-my-plugins` before building, otherwise the
    new file is not compiled and its operators are unknown.

Variables read by `onika_add_plugin` (set them before the call):

| Variable | Meaning |
|---|---|
| `<Name>_LINK_LIBRARIES` | Libraries to link, at least `onika`. |
| `<Name>_INCLUDE_DIRS` | Extra include directories. |
| `<Name>_COMPILE_DEFINITIONS` | Extra preprocessor definitions. |
| `<Name>_EXTERNAL_SRCS` | Extra source files outside `<dir>`. |

See `cmake/OnikaPlugin.cmake` in the Onika sources for the full list.

## Load a plugin

Onika searches plugins in the directories of `ONIKA_PLUGIN_PATH`
(`:`-separated, set by `setup-env.sh`), or of `--plugin_dir`. It does
not load every plugin: when an input file uses an unknown operator name, it
loads the plugin that provides it.

``` bash
$ export ONIKA_PLUGIN_PATH=$ONIKA_PLUGIN_PATH:/path/to/build/plugins
$ onika-exec --help plugins        # list available plugins and their operators
```

Useful options:

- `--debug-plugins`: print which plugins are loaded and why;
- `--generate_plugins_db true` and `--plugin_db <file>`: build and use a
  database of plugin contents, to speed up startup with many plugins.

### The plugin database: `plugins.db`

To know which plugin provides which operator without loading them all, Onika
keeps a small text database, `plugins.db` **in the current directory** (or
the file given by `--plugin_db`). It is created on the first run, and
regenerated automatically when a plugin of the search path is missing from it
or is newer than the file. Each line gives a plugin file, an item kind and its
name:

``` text
/path/to/build/plugins/libmyPlugin-plugin.so operator clamp_value
```

Delete it, or run once with `--generate_plugins_db true`, if it ever gets out
of sync.

## Plugins shipped with Onika

- `onikaTools`: tools operators.
- `onikaBasicTutorial`: slot default values built from constructor arguments.
- `onikaParallelTutorial`: examples of the parallel API (see [Parallel API: one code for CPU and GPU](parallel.md)).

They are good templates for your own plugins.

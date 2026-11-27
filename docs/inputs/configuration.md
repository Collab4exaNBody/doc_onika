# The `configuration` block

<span class="badge badge-user">Simulation user</span>

The `configuration` block of an input file sets the Onika runtime: logging,
profiling, debugging, threads, GPU, plugins. It does not change the physics.

Every item has two equivalent forms: a YAML key in the input file, or a
command-line option. The option name is the YAML path joined with `-`:

| In the input file | On the command line |
|---|---|
| .. code-block:: yaml configuration: omp_num_threads: 8 profiling: summary: true trace: enable: true debug: graph: true | .. code-block:: bash --omp_num_threads 8 --profiling-summary true --profiling-trace-enable true --debug-graph true |

A boolean option given without a value is set to `true`: `--debug-graph`
is the same as `--debug-graph true`.

Command-line options are merged last, so they override the input file.

## Print the configuration

``` bash
$ onika-exec --help default-config    # every item with its default value, as YAML
$ onika-exec --help command-line      # every item as a command-line option
$ onika-exec input.msp --debug-config # values actually used for this run
```

The full list of items is in [Command-line options](../running/command-line.md).

## Environment variables

`bin/setup-env.sh` sets the variables Onika needs. You can extend them:

| Variable | Meaning |
|---|---|
| `ONIKA_PLUGIN_PATH` | `:`-separated list of directories searched for plugins. |
| `ONIKA_CONFIG_PATH` | Directory of the default input files (`main-config.msp`...). |
| `ONIKA_DATA_PATH` | `:`-separated list of directories searched for data files. |
| `ONIKA_DEBUG` | If set (and not `0` / `false`), turns on the debug stream and startup diagnostics, as `--logging-debug --debug-plugins --debug-files --debug-verbose 2`. |

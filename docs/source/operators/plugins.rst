.. _plugins:

Plugins
=======

|opdev|

Operators are compiled into **plugins**: shared libraries that Onika loads at
run time. An application is Onika plus a set of plugins; adding an operator
never requires rebuilding Onika itself.

Build a plugin with CMake
-------------------------

Onika installs a CMake package. ``find_package(onika)`` gives you the
``onika`` target and the ``onika_add_plugin`` function:

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.26)
   project(MyOnikaPlugins LANGUAGES C CXX)

   find_package(onika REQUIRED)               # configure with -Donika_DIR=<install-prefix>

   set(myPlugin_LINK_LIBRARIES onika)
   onika_add_plugin(myPlugin ${CMAKE_CURRENT_SOURCE_DIR}/src)

``onika_add_plugin(<Name> <dir>)``:

- compiles every ``*.cpp`` and ``*.cu`` file of ``<dir>`` into
  ``plugins/lib<Name>-plugin.so`` in the build directory;
- compiles ``*.cu`` files with CUDA (or HIP) when Onika was built with GPU
  support, and as plain C++ otherwise, so the same source works everywhere;
- compiles files in ``<dir>/lib``, if this directory exists, into a separate
  shared library ``lib<Name>.so`` for code shared between plugins;
- includes ``<dir>/<Name>.cmake`` if it exists, for plugin-specific settings;
- adds a CMake option ``ONIKA_BUILD_<Name>`` (``ON`` by default).

Variables read by ``onika_add_plugin`` (set them before the call):

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Variable
     - Meaning
   * - ``<Name>_LINK_LIBRARIES``
     - Libraries to link, at least ``onika``.
   * - ``<Name>_INCLUDE_DIRS``
     - Extra include directories.
   * - ``<Name>_COMPILE_DEFINITIONS``
     - Extra preprocessor definitions.
   * - ``<Name>_EXTERNAL_SRCS``
     - Extra source files outside ``<dir>``.

See ``cmake/OnikaPlugin.cmake`` in the Onika sources for the full list.

Load a plugin
-------------

Onika searches plugins in the directories of ``ONIKA_PLUGIN_PATH``
(``:``-separated, set by ``setup-env.sh``), or of ``--plugin_dir``. It does
not load every plugin: when an input file uses an unknown operator name, it
loads the plugin that provides it.

.. code-block:: bash

   $ export ONIKA_PLUGIN_PATH=$ONIKA_PLUGIN_PATH:/path/to/build/plugins
   $ onika-exec --help plugins        # list available plugins and their operators

Useful options:

- ``--plugins "[myPlugin]"``: force loading of some plugins;
- ``--debug-plugins``: print which plugins are loaded and why;
- ``--generate_plugins_db true`` and ``--plugin_db <file>``: build and use a
  database of plugin contents, to speed up startup with many plugins.

Plugins shipped with Onika
--------------------------

- ``onikaTools``: tools operators.
- ``onikaBasicTutorial``: slot default values built from constructor arguments.
- ``onikaParallelTutorial``: examples of the parallel API (see :ref:`parallel-api`).

They are good templates for your own plugins.

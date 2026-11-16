.. _first-operator:

Your first operator
===================

|opdev|

We write a new operator, ``scale_value``, build it as a plugin outside the
Onika source tree, and plug it into the counter loop.

1. Project layout
-----------------

.. code-block:: text

   my-plugins/
   ├── CMakeLists.txt
   └── src/
       └── scale_value.cpp

2. The operator
---------------

.. code-block:: cpp
   :caption: src/scale_value.cpp

   #include <onika/scg/operator.h>
   #include <onika/scg/operator_factory.h>
   #include <onika/scg/operator_slot.h>
   #include <onika/log.h>

   namespace my_plugin
   {
     using namespace onika::scg;

     class ScaleValue : public OperatorNode
     {
       ADD_SLOT( double , value  , INPUT  , REQUIRED , DocString{"value to scale"} );
       ADD_SLOT( double , factor , INPUT  , 2.0      , DocString{"multiplication factor"} );
       ADD_SLOT( double , result , OUTPUT ,            DocString{"value * factor"} );

     public:
       inline std::string documentation() const override final
       {
         return "Multiplies a value by a factor.";
       }

       inline void execute() override final
       {
         *result = (*value) * (*factor);
         onika::lout << "scale_value: " << *value << " x " << *factor << " = " << *result << std::endl;
       }
     };

     ONIKA_AUTORUN_INIT(scale_value)
     {
       OperatorNodeFactory::instance()->register_factory( "scale_value", make_simple_operator<ScaleValue> );
     }
   }

- Each ``ADD_SLOT`` declares a slot: type, name, direction, then optional
  markers, default value and description.
- Slots work like pointers: ``*value`` reads the value, ``*result = ...`` writes it.
- ``ONIKA_AUTORUN_INIT`` runs when the plugin is loaded and registers the
  operator under the name used in input files.

All details are in :ref:`operator-anatomy`.

3. Build it as a plugin
-----------------------

.. code-block:: cmake
   :caption: CMakeLists.txt

   cmake_minimum_required(VERSION 3.26)
   project(MyOnikaPlugins LANGUAGES C CXX)

   find_package(onika REQUIRED)

   set(myPlugin_LINK_LIBRARIES onika)
   onika_add_plugin(myPlugin ${CMAKE_CURRENT_SOURCE_DIR}/src)

.. code-block:: bash

   $ cmake -S my-plugins -B build-my-plugins -Donika_DIR=<install-prefix>
   $ cmake --build build-my-plugins
   ...
   [100%] Linking CXX shared library plugins/libmyPlugin-plugin.so

Use the same compiler as for Onika. Then tell Onika where to find the plugin
(``ONIKA_PLUGIN_PATH`` is a ``:``-separated list):

.. code-block:: bash

   $ source <install-prefix>/bin/setup-env.sh
   $ export ONIKA_PLUGIN_PATH=$ONIKA_PLUGIN_PATH:$PWD/build-my-plugins/plugins

Check that Onika sees it. The help is generated from your ``DocString`` and
``documentation()``:

.. code-block:: bash

   $ onika-exec --help scale_value

.. code-block:: text

   Operator    : scale_value

   Description : Multiplies a value by a factor.
   Slots       :
     factor
       flow IN
       type double
       desc multiplication factor
     result
       flow OUT
       type double
       desc value * factor
     value
       flow IN
       type double
       desc value to scale

4. Plug it into the loop
------------------------

Start from ``step3.msp`` (:ref:`first-input`), add ``physical_time`` to
``global`` and a batch that scales it:

.. code-block:: yaml
   :emphasize-lines: 5,18-21,28

   global:
     timestep: 0
     dt: 1.0
     nsteps: 3
     physical_time: 0.0
     compute_loop_continue: true

   print_timestep:
     rebind: { value: timestep }
     body:
       - print_int: { prefix: "Current timestep = ", suffix: "\n" }

   compute_loop_stop:
     rebind: { end_at: nsteps , result: compute_loop_continue }
     body:
       - sim_continue

   scaled_time:
     rebind: { value: physical_time }
     body:
       - scale_value: { factor: 10.0 }

   compute_loop:
     loop: true
     condition: compute_loop_continue
     body:
       - print_timestep
       - next_time_step
       - scaled_time
       - compute_loop_stop

   simulation:
     - global
     - compute_loop

Run it with ``onika-exec step4.msp``... and ``scale_value`` prints nothing:

.. code-block:: text

   *SUPPRESS* simulation.compute_loop.scale_value
   Current timestep = 0
   Current timestep = 1
   ...

.. important::

   **Onika removes operators whose outputs are never used.** Nobody reads
   ``result``, so ``scale_value`` is useless for the graph and Onika drops it.
   This keeps graphs lean, but it surprises everybody once. Fix it by reading
   the output, or, for operators that only have side effects (writing files...),
   see :ref:`operator-sink`.

Add a consumer for ``result``:

.. code-block:: yaml

   print_scaled:
     rebind: { value: result }
     body:
       - print_real: { prefix: "  scaled physical time = ", suffix: "\n" }

and put ``- print_scaled`` right after ``- scaled_time`` in ``compute_loop``:

.. code-block:: text

   Current timestep = 0
   scale_value: 1.0000000000e+00 x 1.0000000000e+01 = 1.0000000000e+01
     scaled physical time = 1.0000000000e+01
   Current timestep = 1
   scale_value: 2.0000000000e+00 x 1.0000000000e+01 = 2.0000000000e+01
     scaled physical time = 2.0000000000e+01
   ...

You now know the full cycle: write an operator, build a plugin, use it in an
input file. Go further with :ref:`operator-anatomy`, :ref:`plugins` and
:ref:`parallel-api`.

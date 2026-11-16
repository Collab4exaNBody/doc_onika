.. _operator-anatomy:

Anatomy of an operator
======================

|opdev|

An operator is a C++ class with four parts: a base class, slots, an
``execute()`` method and a registration. :ref:`first-operator` shows them in
a complete example; this page describes each part.

.. mermaid::

   flowchart LR
     subgraph op ["class MyOperator : public OperatorNode"]
       direction TB
       s["ADD_SLOT(...) × N<br/>interface"] --- e["execute()<br/>work"] --- d["documentation()<br/>help text"]
     end
     op -->|"register_factory(&quot;my_operator&quot;, ...)"| f["OperatorNodeFactory"]
     f -->|"my_operator: { ... }"| y["input file"]

.. _inherit-from-operatornode:

Base class
----------

Every operator inherits from ``onika::scg::OperatorNode`` and implements
``execute()``. ``documentation()`` is optional but recommended: it is shown by
``onika-exec --help <operator>``.

.. code-block:: cpp

   #include <onika/scg/operator.h>
   #include <onika/scg/operator_factory.h>
   #include <onika/scg/operator_slot.h>

   class MyOperator : public onika::scg::OperatorNode
   {
   public:
     inline std::string documentation() const override final
     {
       return "Example operator that processes data.";
     }

     inline void execute() override final
     {
       // operator body
     }
   };

``execute()`` is called each time the operator runs in the simulation graph
(once per iteration inside a loop).

.. _add-slots-with-add-slot:

Slots
-----

Slots are the interface of the operator. Declare them with ``ADD_SLOT``:

.. code-block:: text

   ADD_SLOT( type , name , direction [, REQUIRED | OPTIONAL] [, default value] [, DocString{"..."}] );

.. list-table:: Directions
   :header-rows: 1
   :widths: 20 80

   * - Direction
     - Meaning
   * - ``INPUT``
     - The operator reads the value. It comes from an earlier operator with an
       output of the same name, or from the input file.
   * - ``OUTPUT``
     - The operator produces the value for later operators.
   * - ``INPUT_OUTPUT``
     - The operator reads and updates the value in place.
   * - ``PRIVATE``
     - Internal state, not visible in the graph and never connected. It keeps
       its value between two calls of ``execute()``.

.. list-table:: Markers
   :header-rows: 1
   :widths: 20 80

   * - Marker
     - Meaning
   * - ``REQUIRED``
     - The value must be provided (connected or set in the input file),
       otherwise the run stops with an error.
   * - ``OPTIONAL``
     - The value may be missing. Test it with ``has_value()`` before use.
   * - *none*
     - Default behavior. Give a default value so the slot always has one.

Examples:

.. code-block:: cpp

   ADD_SLOT( double      , dt        , INPUT , REQUIRED );
   ADD_SLOT( long        , freq      , INPUT , 1 );
   ADD_SLOT( bool        , verbose   , INPUT , false , DocString{"Enable verbose output"} );
   ADD_SLOT( UnitSystem  , units     , INPUT , OPTIONAL , DocString{"Unit system, if any"} );
   ADD_SLOT( double      , timestep  , INPUT_OUTPUT );
   ADD_SLOT( bool        , result    , OUTPUT , DocString{"true when done"} );
   ADD_SLOT( MyCache     , cache     , PRIVATE );

The default value can also be a tuple of constructor arguments, for example
``std::make_tuple(size_t(10), 5.0)`` for a ``std::vector<double>`` of 10 values
equal to 5 (see ``plugins/onikaBasicTutorial`` in the Onika sources).

Using slots
~~~~~~~~~~~

A slot behaves like a pointer to its value:

.. code-block:: cpp

   inline void execute() override final
   {
     double x = *value;              // read
     *result = x * (*factor);        // write
     my_vector->push_back( x );      // call a member
     if( units.has_value() ) { ... } // OPTIONAL slot: check before use
   }

``DocString`` texts and slot types are printed by ``onika-exec --help <operator>``.

.. _register-the-operator:

Registration
------------

Register the class in the operator factory, with the name used in input files:

.. code-block:: cpp

   ONIKA_AUTORUN_INIT(my_operator)
   {
     OperatorNodeFactory::instance()->register_factory( "my_operator", make_simple_operator<MyOperator> );
   }

``ONIKA_AUTORUN_INIT`` runs this code when the plugin is loaded. Two helpers
create the operator:

- ``make_simple_operator<T>``: always creates a ``T``. Use it by default.
- ``make_compatible_operator<T1, T2, ...>``: chooses the first class whose
  input slot types match the types of the connected upstream slots.
  Use it to register several implementations (e.g. one per data type) under
  one name.

The operator is then used in an input file by its name:

.. code-block:: yaml

   simulation:
     - global
     - my_operator: { value: 1.0 }

.. _mark-the-operator-as-a-sink:
.. _operator-sink:

Keeping an operator in the graph: ``is_sink()``
-----------------------------------------------

Onika removes operators whose outputs are never read (see
:ref:`msp-pruning`). An operator without any output (only inputs and
private slots) is a **sink**: it is always kept, like ``print_int`` or
``message``.

If an operator has outputs but must run even when they are not used, override
``is_sink()``:

.. code-block:: cpp

   inline bool is_sink() const override final
   {
     return true;
   }

.. warning::

   This is rarely needed. Prefer reading the outputs, or making the operator
   output-free. Forcing ``is_sink()`` on an operator with ``OUTPUT`` slots
   hides graph problems.

Logging
-------

Use Onika's log streams instead of ``std::cout``, so that output follows the
``--logging-*`` options (rank 0 only by default, redirection to files):

.. code-block:: cpp

   #include <onika/log.h>

   onika::lout << "normal message" << std::endl;
   onika::lerr << "error message" << std::endl;
   ldbg << "debug message, shown with --logging-debug" << std::endl;

Inside an operator, ``ldbg`` is filtered by ``--debug-filter``.

Next
----

- Build your operators as a plugin: :ref:`plugins`.
- Run them on CPU and GPU: :ref:`parallel-api`.

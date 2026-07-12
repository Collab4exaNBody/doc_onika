Create your Onika Operator
==========================

This page explains the basic steps to create a new operator in Onika.

A minimal operator is made of four steps:

- :ref:`inherit-from-operatornode`
- :ref:`mark-the-operator-as-a-sink`
- :ref:`add-slots-with-add-slot`
- :ref:`register-the-operator`

.. _inherit-from-operatornode:

Inherit from OperatorNode
-------------------------

Every operator must inherit from ``onika::scg::OperatorNode`` and implement ``execute()``.
The ``documentation()`` method is also recommended, because it provides a human-readable description of what the operator does.

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

The ``execute()`` method is the core of the operator. It is called when the node is executed in the simulation graph.

.. _mark-the-operator-as-a-sink:

Mark the operator as a sink when needed
---------------------------------------

If your operator has a side effect, such as writing a file, updating a rendering context, or terminating a workflow, you can override ``is_sink()`` and return ``true``.

.. code-block:: cpp

   inline bool is_sink() const override final
   {
     return true;
   }

This tells Onika that the operator is terminal-like from the graph point of view. In practice, it is useful for operators that should not be removed just because they have no downstream output connection.

If you do not override this method, the default behavior is to behave like a regular batch operator.

.. _add-slots-with-add-slot:

Add slots with ADD_SLOT
-----------------------

Slots define the interface of the operator. They are declared with the ``ADD_SLOT`` macro and expose members that can be accessed directly from the operator implementation.

A typical example is:

.. code-block:: cpp

   class MyOperator : public onika::scg::OperatorNode
   {
     ADD_SLOT( std::string , input_data , INPUT , "default" );
     ADD_SLOT( std::string , output_data , OUTPUT );
     ADD_SLOT( double , value , INPUT_OUTPUT , 0.0 );
     ADD_SLOT( bool , enabled , OPTIONAL , true );
     ADD_SLOT( std::string , internal_cache , PRIVATE );

   public:
     inline std::string documentation() const final
     {
       return "Example operator with several slot types.";
     }

     inline void execute() final
     {
       // use input_data, output_data, enabled, internal_cache here
     }
   };

The meaning of the main slot kinds is the following:

- ``INPUT``: the slot is consumed by the operator. It is typically connected from an upstream operator.
- ``OUTPUT``: the slot produces data for downstream operators.
- ``INPUT_OUTPUT``: the slot can be used both as an input and as an output. It is useful when data is read and updated in place.

The ``ADD_SLOT`` macro can also be enriched with additional modifiers:

- ``REQUIRED``: this is not a default value; it is a marker indicating that the slot must be connected or provided by the configuration. If it is missing, the operator is considered incomplete and the execution fails.
- ``OPTIONAL``: the slot is not mandatory. It can remain unconnected, and a default value can be provided if needed.
- ``PRIVATE``: the slot is internal to the operator and is not meant to be connected in the graph. It is hidden from the regular dataflow interface. Because it is not part of the normal graph contract, you should not assume that its underlying storage is already allocated or initialized before the operator runs.


  .. note::

     If you want to know whether a value was actually provided, you can test the slot with ``has_value()`` and check the resulting boolean.

Several forms are possible depending on the needs of the operator:

.. code-block:: cpp

   ADD_SLOT( std::string , input_data , INPUT );
   ADD_SLOT( std::string , output_data , OUTPUT );
   ADD_SLOT( std::string , state , INPUT_OUTPUT , "initial" );
   ADD_SLOT( std::string , prefix , INPUT , "" );
   ADD_SLOT( bool , enabled , INPUT , OPTIONAL , true );
   ADD_SLOT( bool , must_exist , INPUT , REQUIRED );
   ADD_SLOT( bool , verbose , INPUT , OPTIONAL , false , DocString{"Enable verbose output"} );
   ADD_SLOT( std::string , message , INPUT , "hello" , DocString{"Message to display"} );
   ADD_SLOT( SomeInternalType , cache , PRIVATE );

In practice:

- a default value can be given directly after the direction;
- ``REQUIRED`` and ``OPTIONAL`` are markers that modify the slot contract;
- ``DocString{...}`` can be added to give a description that appears in the operator interface.
- ``PRIVATE`` is used for internal state that should not be exposed in the graph.

Once a slot is declared, it can be accessed from the operator implementation through the generated member. For example, a slot named ``value`` can be used as follows:

.. code-block:: cpp

   ADD_SLOT( double , value , INPUT_OUTPUT , 0.0 );
   ...
   double& value_ref = *value;

This gives direct access to the underlying value stored in the slot.

.. _register-the-operator:

Register the operator
---------------------

Once the operator class is implemented, it must be registered in the factory so that Onika can instantiate it from the graph configuration.

.. code-block:: cpp

   ONIKA_AUTORUN_INIT(my_operator)
   {
     OperatorNodeFactory::instance()->register_factory(
       "my_operator",
       make_compatible_operator< MyOperator >
     );
   }

The string passed to ``register_factory()`` is the name used to reference the operator in the configuration. For example, a YAML graph can instantiate it with:

.. code-block:: yaml

   operators:
     - type: my_operator
       value: 1.0

This is the final step that makes your operator available to the execution engine.

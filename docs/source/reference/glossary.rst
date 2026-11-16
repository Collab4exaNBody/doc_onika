.. _glossary:

Glossary
========

|user| |opdev| |core|

.. glossary::
   :sorted:

   operator
      A C++ class deriving from ``onika::scg::OperatorNode`` that does one job.
      The building block of every Onika application. See :ref:`operator-anatomy`.

   slot
      A named, typed input or output of an operator, declared with ``ADD_SLOT``.
      Slots with the same name are connected automatically.

   batch
      A named sequence of operators defined in an input file. It can loop and
      have a condition. See :ref:`msp-batches`.

   rebind
      Renaming of slots of a batch body, to connect operators whose slot names
      differ. See :ref:`msp-rebind`.

   simulation graph
      The tree of operators built from the ``simulation`` entry of the input
      files. Printed with ``--debug-graph``.

   sink
      An operator without outputs (or with ``is_sink()`` returning true).
      Always kept in the graph. See :ref:`operator-sink`.

   pruning
      Removal of operators whose outputs are never used, shown as
      ``*SUPPRESS*`` in the log. See :ref:`msp-pruning`.

   plugin
      A shared library containing operators, loaded at run time.
      See :ref:`plugins`.

   factory
      ``OperatorNodeFactory``: the registry that creates operators from their
      names. Operators register with ``register_factory``.

   flavor
      The set of slot names and types available upstream of an operator.
      ``make_compatible_operator`` uses it to choose an implementation.

   msp file
      An Onika input file, in YAML. See :ref:`msp-language`.

   main-config.msp
      The default input file, always loaded first. See :ref:`msp-main-config`.

   lane
      An execution stream of the parallel API. Operations on different lanes
      may run concurrently. See :ref:`parallel-api`.

   parallel execution context
      The execution resources (CPU threads, GPU, streams) of an operator,
      given by ``parallel_execution_context()``.

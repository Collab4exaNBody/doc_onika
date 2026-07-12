Motivation
==========

Onika is built around **component-based programming**: software is decomposed into independent building blocks (components), assembled through a formalism external to the programming language itself. This section explains why this architectural choice matters, both from a software engineering and an HPC perspective.

Why software tends to become rigid
-----------------------------------

As an application grows, two factors tend to work against its long-term maintainability: an increasing number of dependencies between different parts of the code, and a decreasing visibility of how the code works as a whole.

Several kinds of dependencies can exist between different parts of a code base:

- **Data dependencies**, which occur when a piece of code can modify a shared piece of data that in turn conditions or affects the execution of another, unrelated piece of code:

  .. code-block:: cpp

     // global variable
     int X;

     void F() { /* ... */ X += 2; /* ... */ }
     void G() { /* ... */ if (X < 10) { /* ... */ } /* ... */ }

- **Functional dependencies**, where a function ``f`` calls a function ``g``, which itself calls a function ``h``, and so on.

- A third, mixed kind of dependency can also appear through the uncontrolled use of object-oriented concepts (member data, virtual methods), though this is not detailed further here.

Depending on how a software project is developed, its source files and their dependencies can either stay bounded — each unit keeping a roughly fixed number of dependencies over time — or drift towards a "complete graph", where the number of dependencies of every element keeps growing along with the overall size of the code, as illustrated below.

.. figure:: /_static/software_deps.png
   :align: center

   Depending on how the code is developed, dependencies between source units can stay bounded (left) or drift towards a complete graph (right).

This distinction matters because of two very common situations in the life of a piece of software: the need to understand (or fix) part of the application, and the need to modify or transform part of its structure. In both cases, a developer needs to be able to focus on one part of the application and understand its logic in isolation. When the dependency graph is highly interconnected, the developer instead has to examine and understand an amount of surrounding code that grows with the size of the whole application.

This has several negative consequences: developers become more reluctant to change existing code, which encourages piling up new code on top of the existing one instead of transforming it, making the code base heavier over time. The time and effort required to get into the code keeps increasing as the application grows, making development more tedious and less appealing. Left unchecked, the maintenance burden of an application keeps growing, deep transformations become harder to carry out, and the motivation to undertake them decreases as the application grows.

Component-based programming, from this point of view, provides a framework that strongly guides development so that software dependencies remain local and "step by step", guaranteeing a flexibility and an ability to evolve that is stronger and lasts longer over time.

Concretely, a component has one specific function and knows nothing about other components: it only knows its input data and the data it produces as output. Components are assembled and connected to one another through a mechanism external to the programming language, which reinforces the fact that a component cannot create dependencies on, or make assumptions about, how it is chained with other components.

Using a uniform formalism to express functional units together with their inputs and outputs has further benefits, discussed below: automatic documentation generation, automatic generation of command-line options, dataflow visualization, and performance optimization.

Benefits for HPC
-----------------

Software engineering and HPC, the same fight?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In an environment that mixes industrial constraints (production, guaranteed results, deadlines) with research constraints (scientific breakthroughs, technological barriers to overcome, permanent questioning), the need to run numerical simulation on HPC platforms adds yet another layer of difficulty. Applications must not only implement advanced, constantly evolving physical models and guarantee their correctness and validity, but also make them able to exploit supercomputers whose characteristics are as advanced as their scale is large. In short, the software must combine two levels of complexity — advanced and changing physical models, together with deep optimization for equally complex machines — while remaining maintainable over the long run.

As explained above, the way a software project is decomposed, and the dependencies between its functional units, condition how easily it can be transformed over time. The component-based approach lets the code carry the necessary complexity and evolve frequently without becoming rigid and hard to maintain, all while guaranteeing long-term adaptability. This is essential, because nobody knows exactly which physical models will need to be implemented next, nor what the architecture of the next supercomputer will look like — but we do know that both will change.

Data flow: the crux of the matter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Beyond the software construction process itself, component-based programming is, and remains, a major asset for HPC, because it makes the data flow between functional units explicit and clearly identifiable, as illustrated below.

.. figure:: /_static/exemples_composants.png
   :align: center

   Data flow between components: inputs and outputs of each functional unit are made explicit.

Parallelism, in essence, comes down to knowing which data goes in and out of a computational kernel, and which data flows can be processed independently from which others. In a classical programming model, data flows come in many different forms — function parameters, calls to third-party functions, side effects, global variables, and so on — and keeping them under control is left to the expertise of one or several seasoned developers. By making inputs and outputs explicit at the level of each component, Onika's component-based model removes much of that ambiguity, and makes the resulting dataflow graph a first-class, analyzable artifact rather than something a developer has to reconstruct by hand.

Onika: an environment to build your dependencies explicitly
--------------------------------------------------------------

Onika implements this component-based model directly. An operator (see :doc:`CreateYourOperator`) only exposes its interface through ``ADD_SLOT``-declared ``INPUT``, ``OUTPUT`` and ``INPUT_OUTPUT`` slots, and knows nothing about the operators it is connected to — the same application-structure obliviousness described above, enforced here at the language level. Operators are assembled into a simulation graph from a YAML configuration, a formalism external to C++, so dependencies between operators can never be hard-coded in the source code itself.

Because a whole subgraph is itself just another assembly of components with explicit inputs and outputs, entire portions of a simulation graph can be reused as-is or copied into another configuration, without having to touch the C++ code behind them. The same explicitness also makes it possible to couple several Onika-based codes together: coupling is expressed by adding dedicated coupling operators to the graph, which connect the input/output slots of one code to those of another, rather than by entangling their internal implementations.

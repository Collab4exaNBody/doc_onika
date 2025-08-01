Installation
============


Prerequisites
^^^^^^^^^^^^^

To install a minimal version of **Onika**, the following dependencies are required:

- **CMake** ≥ 3.26
- **GCC** ≥ 11.0.0 with full **C++20** support
- **yaml-cpp** version 0.6.3  

  .. warning:: 
      
     yaml-cpp version 0.7.0 is **not** supported. Please use version 0.6.3.

- **CUDA** *(optional)*  
  Onika can be built without CUDA if GPU acceleration is not needed.


Installing ``yaml-cpp``
-----------------------

Onika requires version **0.6.3** of ``yaml-cpp``.

.. tabs::

   .. tab:: CMake (manual build)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone --depth 1 --branch yaml-cpp-0.6.3 https://github.com/jbeder/yaml-cpp.git
         mkdir ${CURRENT_HOME}/build-yaml-cpp && cd ${CURRENT_HOME}/build-yaml-cpp
         cmake ../yaml-cpp/ \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-yaml-cpp \
             -DYAML_BUILD_SHARED_LIBS=ON \
             -YAML_CPP_BUILD_TESTS=OFF
         make install -j 4
         cd ${CURRENT_HOME}
         export PATH_TO_YAML=$PWD/install-yaml-cpp

   .. tab:: Spack

      .. code-block:: bash

         spack install yaml-cpp@0.6.3
         spack load yaml-cpp@0.6.3

   .. tab:: APT (Ubuntu/Debian)

      .. code-block:: bash

         sudo apt-get update
         sudo apt-get install libyaml-cpp-dev

      .. note::
         The ``apt`` package may install version 0.6.3 or higher depending on your distribution.
         Please ensure that the version is exactly **0.6.3** to avoid compatibility issues.


Installing Onika
^^^^^^^^^^^^^^^^

You can install **Onika** either manually using **CMake**, or using **Spack**.  
CUDA support is optional.

.. tabs::

   .. tab:: CMake (without CUDA)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone https://github.com/Collab4exaNBody/onika.git
         mkdir ${CURRENT_HOME}/build-onika && cd ${CURRENT_HOME}/build-onika
         cmake ${CURRENT_HOME}/onika \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika
         make install -j 10

   .. tab:: CMake (with CUDA)

      .. code-block:: bash

         export CURRENT_HOME=$PWD
         git clone https://github.com/Collab4exaNBody/onika.git
         mkdir ${CURRENT_HOME}/build-onika && cd ${CURRENT_HOME}/build-onika
         cmake ${CURRENT_HOME}/onika \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=${CURRENT_HOME}/install-onika \
             -DONIKA_BUILD_CUDA=ON \
             -DCMAKE_CUDA_ARCHITECTURES=86
         make install -j 10

   .. tab:: Spack (without CUDA)

      .. code-block:: bash

         # Get Spack
         git clone --depth=2 --branch=v0.23.0 https://github.com/spack/spack.git
         export SPACK_ROOT=$PWD/spack
         source ${SPACK_ROOT}/share/spack/setup-env.sh

         # Add Onika's custom Spack repository
         git clone https://github.com/Collab4exaNBody/spack-repos.git
         spack repo add spack-repos

         # Install Onika
         spack install onika
         spack load onika

   .. tab:: Spack (with CUDA)

      .. code-block:: bash

         # Get Spack
         git clone --depth=2 --branch=v0.23.0 https://github.com/spack/spack.git
         export SPACK_ROOT=$PWD/spack
         source ${SPACK_ROOT}/share/spack/setup-env.sh

         # Add Onika's custom Spack repository
         git clone https://github.com/Collab4exaNBody/spack-repos.git
         spack repo add spack-repos

         # Install Onika with CUDA support
         spack install onika+cuda
         spack load onika

# Building for AMD GPUs (HIP) in Docker { #docker-hip }

<span class="badge badge-user">Simulation user</span> <span class="badge badge-core">Framework developer</span>

Onika can be compiled for AMD GPUs (HIP) on a machine **without** an AMD GPU:
only the ROCm/HIP toolchain is needed, provided by the `rocm/dev-ubuntu-22.04`
Docker image. This page builds Onika for `gfx90a` (MI250) in such a container.
It follows `doc/tuto_docker_rocm.md` of the Onika sources; the steps below
were run as written (with Podman) on Onika 1.1.0.

!!! tip "Podman"

    The same commands work with `podman` instead of `docker`. On systems with
    SELinux, add `:z` to the volume options (`-v dir:dir:z`), otherwise the
    container cannot read the mounted files (`Permission denied`).

## 1. Get the image

``` bash
docker pull rocm/dev-ubuntu-22.04:latest
```

Behind a proxy, configure the Docker daemon first, in
`/etc/systemd/system/docker.service.d/http-proxy.conf`:

``` ini
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1"
```

then `sudo systemctl daemon-reload && sudo systemctl restart docker`.

## 2. Start the container

Mount the Onika sources, a work directory and the install directory at the
**same paths** as on the host, so that paths in scripts stay valid:

``` bash
docker run -it --rm \
  -e HOME=${HOME} \
  -v ${HOME}/hipdir:${HOME}/hipdir \
  -v /path/to/onika:/path/to/onika:ro \
  -v ${HOME}/local:${HOME}/local \
  -w ${HOME}/hipdir \
  rocm/dev-ubuntu-22.04:latest bash
```

- `hipdir`: build directory and build script (read-write);
- `onika`: the sources (read-only);
- `~/local`: receives the installation.

## 3. Install CMake, yaml-cpp and MPI in the container

The image contains none of them. Behind a proxy, export it in the container
too (the daemon configuration does not apply to the container's shell):

``` bash
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080
```

**CMake ≥ 3.26.** Ubuntu 22.04 provides CMake 3.22, too old. Use Kitware's
repository (it also provides a working `ccmake`):

``` bash
apt-get update && apt-get install -y wget gpg
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc \
  | gpg --dearmor - | tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ jammy main" \
  | tee /etc/apt/sources.list.d/kitware.list
apt-get update
apt-get install -y cmake cmake-curses-gui
cmake --version
```

??? note "Alternative: CMake from pip"

    `pip3 install --upgrade cmake` gives a recent `cmake` in
    `/usr/local/bin`, but no working `ccmake`. If you install `ccmake`
    separately, remove the pip stub first: `rm -f /usr/local/bin/ccmake && hash -r`.

**yaml-cpp** from the distribution: found automatically, no
`-Dyaml-cpp_DIR` needed.

``` bash
apt-get install -y libyaml-cpp-dev
```

**MPI** (otherwise CMake stops with `Could NOT find MPI`):

``` bash
apt-get install -y libopenmpi-dev openmpi-bin
```

## 4. Build

``` bash title="build_install_onika_hip.sh"
#!/bin/bash
mkdir -p build_onika_hip && cd build_onika_hip

ONIKA_SRC_DIR=/path/to/onika
ONIKA_INSTALL_DIR=${HOME}/local/onika_hip

cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=${ONIKA_INSTALL_DIR} \
      -DONIKA_BUILD_CUDA=ON \
      -DONIKA_ENABLE_HIP=ON \
      -DCMAKE_HIP_ARCHITECTURES=gfx90a \
      -DONIKA_HAS_GPU_ATOMIC_MIN_MAX_DOUBLE=ON \
      ${ONIKA_SRC_DIR}
make -j8 install
```

- `ONIKA_BUILD_CUDA=ON` + `ONIKA_ENABLE_HIP=ON`: GPU support through HIP;
- `CMAKE_HIP_ARCHITECTURES`: the target GPU (`gfx90a` for MI250, `gfx942` for MI300);
- `ONIKA_HAS_GPU_ATOMIC_MIN_MAX_DOUBLE=ON`: native atomic min/max on `double`
  (see [CMake options](../reference/cmake-options.md)).

If a previous configuration failed (missing MPI...), remove the build
directory before trying again, so that CMake does not reuse its cache.

If HIP's `clang++` picks an unsuitable GCC installation (errors in standard
headers), point it to the right one:
`-DCMAKE_HIP_FLAGS="--gcc-install-dir=$(dirname $(g++ -print-libgcc-file-name))"`.

## 5. Build plugins and applications against the HIP installation

Projects that use this installation (your plugins, exaNBody...) must also
pass **`-DONIKA_USE_HIP=ON`**:

``` bash
cmake -S my-plugins -B build-my-plugins -Donika_DIR=${HOME}/local/onika_hip -DONIKA_USE_HIP=ON
```

Without it, `onika_add_plugin` does not compile `.cu` files as HIP and CMake
stops with `Cannot determine link language for target "myPlugin-plugin"`.

The installation in `~/local/onika_hip` is then used on the target machine
like any other (see [Installation](installation.md)), with the same ROCm
version available there.

# Math types { #math }

<span class="badge badge-opdev">Operator developer</span>

`onika/math/` provides small geometric types, usable on CPU and GPU, readable
from input files and printable. They live in `onika::math`. The examples
below were compiled and run against Onika 1.1.0.

| Type | Content | YAML form |
|---|---|---|
| `Vec3d` | `x, y, z` (double) | `[ 1.0 , 2 ang , 0 ]` |
| `IJK` | `i, j, k` (`ssize_t`), grid coordinates | `[ 1 , 2 , 3 ]` |
| `Mat3d` | `m11 ... m33` (line, column) | `[ [1,0,0] , [0,1,0] , [0,0,1] ]` (lines) |
| `AABB` | `bmin, bmax` (Vec3d), axis-aligned box | `[ [0,0,0] , [10,10,10] ]` or `{ min: [...] , max: [...] }` |
| `Plane3d` | `N` (normal), `D` (distance to origin) | `[ nx , ny , nz , d ]` |
| `GridBlock` | `start, end` (IJK), a block of grid cells | |
| `Complexd` | `r, i` | |
| `Quaternion` | `w, x, y, z` (`onika/math/quaternion.h`) | `[ w , x , y , z ]` |

Components of `Vec3d` (and therefore `Mat3d`, `AABB`) read from YAML accept
**units**, converted to the internal unit system (see [Units](units.md)).

## Example

``` cpp
#include <onika/math/basic_types.h>          // types, operators, functions
#include <onika/math/basic_types_yaml.h>     // YAML conversions
#include <onika/math/basic_types_stream.h>   // operator <<
#include <onika/math/quaternion.h>
#include <onika/math/quaternion_operators.h>
#include <onika/math/quaternion_to_matrix.h>

using namespace onika::math;

Vec3d a = { 1.0, 0.0, 0.0 };
Vec3d b = { 0.0, 2.0, 0.0 };
Vec3d c = cross(a, b);
std::cout << "a+b = " << a+b << " , dot = " << dot(a,b) << " , cross = " << c << " , norm(c) = " << norm(c) << std::endl;

Mat3d m = diag_matrix( Vec3d{ 2.0, 3.0, 4.0 } );
std::cout << "det = " << determinant(m) << " , inverse * m = " << inverse(m) * m << " , m*a = " << m*a << std::endl;

IJK cell = make_ijk( 1, 2, 3 );
std::cout << "cell + 1 = " << cell + 1 << std::endl;

// rotation of 90 degrees around z
Quaternion q = { std::cos(onika::physics::pi/4), 0.0, 0.0, std::sin(onika::physics::pi/4) };
std::cout << "rotated a = " << quaternion_to_matrix(q) * a << std::endl;

// from YAML, with units
YAML::Node n = YAML::Load( "{ box: [ [0,0,0] , [10 ang, 10 ang, 20 ang] ] }" );
AABB box = n["box"].as<AABB>();
std::cout << "box max = " << box.bmax << std::endl;
```

``` text
a+b = 1,2,0 , dot = 0 , cross = 0,0,2 , norm(c) = 2
det = 24 , inverse * m = {(1,0,0),(0,1,0),(0,0,1)} , m*a = 2,0,0
cell + 1 = 2,3,4
rotated a = 2.22045e-16,1,0
box max = 1e-09,1e-09,2e-09
```

## Functions

All are `ONIKA_HOST_DEVICE_FUNC`: usable in [parallel](../operators/parallel.md) functors.

**Vec3d**: `+ - * /` (component-wise, and with a scalar), `dot`, `cross`,
`norm`, `norm2`, `angle`, `min`, `max`, `floor`, `ceil`, `vabs`,
`reciprocal`, `inverse`, `make_vec3d(double[3])`, `make_vec3d(IJK)`.

**IJK**: `+ - * / %` (component-wise, and with an integer), `<`, `vclamp`,
`make_ijk(i,j,k)`, `make_ijk(Vec3d)`.

**Mat3d**: `+ -`, `*` (matrix product, matrix × vector, scalar), `/` (scalar),
`transpose`, `inverse`, `determinant`, `comatrix`, `trace_matrix`,
`diag_matrix(Vec3d)`, `diagonal`, `tensor(u,v)` (u vᵀ), `make_mat3d(a,b,c)`
(columns), `line1..3`, `column1..3`, `set_line1..3`, `set_diagonal`,
`comp_multiply` (component-wise), `l2_norm`, `diff_l2_norm`, tests
`is_identity`, `is_diagonal`, `is_symmetric`, `is_triangular`,
`is_uniform_scale`, `is_zero`, `has_nan`.

**Quaternion**: `+ - * /`, `norm`, `normalize`, `get_conjugated`, `dot`,
`quaternion_to_matrix`, `q * Vec3d` (rotation).

**GridBlock**: `+ -` an `IJK` offset. **Complexd**: `* double`,
`complex_norm`.

!!! note "Namespace"

    An application can also export these names into its own namespace by
    defining `ONIKA_MATH_EXPORT_NAMESPACE` (exaNBody uses this to provide
    `exanb::Vec3d`, ...).

## Other math helpers

| Header | Content |
|---|---|
| `onika/math/math_utils.h` | `icbrt64` (integer cube root) and small helpers. |
| `onika/math/matrix4d.h` | 4×4 matrices. |
| `onika/math/matrix_band_solver.h` | Solver for banded linear systems. |
| `onika/physics/constants.h` | `onika::physics::pi`, `e`, `phi`, `boltzmann`, `avogadro`, `atomicMass`, `elementaryCharge`, `epsilonZero`, `calorie_joules` (SI values). |

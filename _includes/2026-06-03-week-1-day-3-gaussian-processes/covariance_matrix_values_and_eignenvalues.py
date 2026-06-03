import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../_includes/shared"))

import numpy as np
from kernels import radial_basis_function_kernel, generate_covariance_matrix_from_points

x_three = np.array([-1.0, 0.0, 1.0])

K = generate_covariance_matrix_from_points(x_three, radial_basis_function_kernel, length_scale=1.0, variance=1.0)

print("Symmetric:", np.allclose(K, K.T))
print("Eigenvalues:", np.linalg.eigvalsh(K))

# Output:
# Symmetric: True
# Eigenvalues: [0.2072388  0.86466472 1.92809648]
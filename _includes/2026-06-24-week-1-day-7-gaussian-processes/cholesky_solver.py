import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import cholesky, solve_triangular

SHARED_INCLUDE_DIR = Path(__file__).resolve().parents[1] / "shared"
sys.path.insert(0, str(SHARED_INCLUDE_DIR))

from kernels import generate_covariance_matrix_from_points, radial_basis_function_kernel


x_train = np.linspace(-3, 3, 5)
f_train = np.sin(x_train)

x_star = np.linspace(-6, 6, 200)

k_train_train = generate_covariance_matrix_from_points(
    x_train,
    x_train,
    radial_basis_function_kernel,
    length_scale=1.0,
    variance=1.0,
)
k_train_star = generate_covariance_matrix_from_points(
    x_train,
    x_star,
    radial_basis_function_kernel,
    length_scale=1.0,
    variance=1.0,
)
k_star_star = generate_covariance_matrix_from_points(
    x_star,
    x_star,
    radial_basis_function_kernel,
    length_scale=1.0,
    variance=1.0,
)

# Cholesky
noise_std = 0.2

k_train_train_noisy = k_train_train + noise_std**2 * np.eye(len(x_train))

chol_l = cholesky(k_train_train_noisy, lower=True)

# Solve K alpha = y using the triangular Cholesky factors.
forward_v = solve_triangular(chol_l, f_train, lower=True)
alpha = solve_triangular(chol_l.T, forward_v, lower=False)

posterior_mean = k_train_star.T @ alpha

chol_v = solve_triangular(chol_l, k_train_star, lower=True)
posterior_var = k_star_star - chol_v.T @ chol_v

# Inversion
# Direct inversion reference
K_inv = np.linalg.inv(k_train_train_noisy)
mean_direct = k_train_star.T @ K_inv @ f_train
cov_direct = k_star_star - k_train_star.T @ K_inv @ k_train_star

assert np.allclose(posterior_mean, mean_direct, atol=1e-10), "Means don't match"
assert np.allclose(posterior_var, cov_direct, atol=1e-10), "Covariances don't match"
print("Cholesky matches direct inversion to 1e-10")


sin_points = np.linspace(-3, 3, 300)
std_dev = np.sqrt(np.diagonal(posterior_var))

assets_dir = Path(__file__).resolve().parents[2] / "assets/2026_06_24_week_1_day_7_gaussian_processes"
assets_dir.mkdir(parents=True, exist_ok=True)
output_path = assets_dir / f"cholesky_posterior_noise_{noise_std}.png"


def draw_plot() -> None:
    plt.plot(
        sin_points,
        np.sin(sin_points),
        label="sin(x)",
        color="steelblue",
        linestyle="solid",
        linewidth=1,
        alpha=0.7,
    )
    plt.fill_between(
        x_star,
        posterior_mean - 2 * std_dev,
        posterior_mean + 2 * std_dev,
        label="2 std dev",
        color="orange",
        alpha=0.3,
    )
    plt.plot(
        x_star,
        posterior_mean,
        label="posterior mean",
        color="darkorange",
        linestyle="dashed",
        linewidth=2,
    )
    plt.scatter(
        x_train,
        f_train,
        label="x_train",
        color="red",
        edgecolors="black",
        linewidths=0.5,
        s=60,
        zorder=5,
    )
    plt.legend()


plt.figure()
draw_plot()
plt.savefig(output_path, dpi=150, bbox_inches="tight")
plt.close()

print(f"Saved plot to {output_path}")

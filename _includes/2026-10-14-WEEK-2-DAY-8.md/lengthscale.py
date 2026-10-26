import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../_includes/shared"))

import numpy as np
from scipy.linalg import cholesky, solve_triangular
from kernels import (
    radial_basis_function_kernel,
    exponential_sin_squared_kernel,
    generate_covariance_matrix_from_points,
)

import matplotlib.pyplot as plt


def log_marginal_likelihood_terms(
    cholesky_decomposition, posterior_weight_vector, function_vector
):
    number_of_samples = len(function_vector)
    data_fit = -0.5 * function_vector @ posterior_weight_vector
    complexity = -np.sum(np.log(np.diag(cholesky_decomposition)))
    normalization = -0.5 * number_of_samples * np.log(2 * np.pi)
    return data_fit, complexity, normalization


def lml_over_lengthscales(kernel, lengthscales, **kernel_kwargs):
    data_fit_values, complexity_values, normalization_values, lml_values = [], [], [], []
    for length_scale in lengthscales:
        K = generate_covariance_matrix_from_points(
            x_train, x_train, kernel, length_scale=length_scale, **kernel_kwargs
        )
        K_noisy = K + noise_std**2 * np.eye(len(x_train))
        L = cholesky(K_noisy, lower=True)
        v = solve_triangular(L, f_train, lower=True)
        alpha = solve_triangular(L.T, v, lower=False)
        data_fit, complexity, normalization = log_marginal_likelihood_terms(L, alpha, f_train)
        data_fit_values.append(data_fit)
        complexity_values.append(complexity)
        normalization_values.append(normalization)
        lml_values.append(data_fit + complexity + normalization)
    return data_fit_values, complexity_values, normalization_values, lml_values


def plot_lml(lengthscales, data_fit_values, complexity_values, normalization_values, lml_values, title, filename):
    plt.figure()
    plt.plot(lengthscales, lml_values, label="total LML", color="black", linewidth=2)
    plt.plot(lengthscales, data_fit_values, label="data fit", linestyle="--")
    plt.plot(lengthscales, complexity_values, label="complexity penalty", linestyle="--")
    plt.plot(lengthscales, normalization_values, label="normalization", linestyle="--")
    plt.xscale("log")
    plt.xlabel("lengthscale")
    plt.ylabel("log marginal likelihood")
    plt.title(title)
    plt.legend()

    output_path = assets_dir / filename
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {output_path}")

    best_idx = int(np.argmax(lml_values))
    print(f"Best lengthscale: {lengthscales[best_idx]:.4f}, LML: {lml_values[best_idx]:.4f}")


x_train = np.linspace(-3, 3, 300)
f_train = np.sin(x_train)

noise_std = 0.2
lengthscales = np.logspace(-1, 1, 50)  # 0.1 to 10

assets_dir = Path(__file__).resolve().parents[2] / "assets/2026_07_08_week_2_day_8_gaussian_processes"
assets_dir.mkdir(parents=True, exist_ok=True)

rbf_terms = lml_over_lengthscales(radial_basis_function_kernel, lengthscales, variance=1.0)
plot_lml(lengthscales, *rbf_terms, "RBF kernel", "lml_vs_lengthscale.png")

periodic_terms = lml_over_lengthscales(
    exponential_sin_squared_kernel, lengthscales, variance=1.0, period=2 * np.pi
)
plot_lml(lengthscales, *periodic_terms, "Periodic (sine) kernel, period = 2π", "lml_vs_lengthscale_periodic.png")

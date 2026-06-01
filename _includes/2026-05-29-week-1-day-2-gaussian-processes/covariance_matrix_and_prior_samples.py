import numpy as np
from typing import Callable
import matplotlib.pyplot as plt
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../../assets/2026_05_29_gaussian_processes")

NUMBER_OF_POINTS = 50

# Kernel definitions
def radial_basis_function_kernel(x_0: np.ndarray, x_1: np.ndarray, length_scale: float = 1.0, variance: float = 1.0) -> np.ndarray:
    return variance * np.exp(- np.sum((x_0 - x_1)**2) / (2 * length_scale**2))

def inhomogeneous_linear_kernel(x_0: np.ndarray, x_1: np.ndarray, bias_variance: float = 1.0, slope_variance: float = 1.0):
    return bias_variance + slope_variance * np.dot(x_0, x_1)

def exponential_sin_squared_kernel(x_0: np.ndarray, x_1: np.ndarray, length_scale: float = 1.0, variance: float = 1.0, period: float = 1.0):
    return variance * np.exp(- 2 * np.sin(np.pi * np.linalg.norm(x_0 - x_1) / period)**2 / length_scale**2)

# Helper
def generate_covariance_matrix(func: Callable, **kwargs):
    cov = np.zeros((NUMBER_OF_POINTS, NUMBER_OF_POINTS))
    points = np.linspace(-3, 3, NUMBER_OF_POINTS)
    for idx in range(NUMBER_OF_POINTS):
        for idy in range(NUMBER_OF_POINTS):
            cov[idx, idy] = func(points[idx], points[idy], **kwargs)
    return cov

length_scales = [0.1, 0.5, 1.0, 5.0, 10.0]
x = np.linspace(-3, 3, NUMBER_OF_POINTS)

bias_variances = [0.1, 0.5, 1.0, 5.0, 10.0]
REPLICATES = 5

fig, axes = plt.subplots(REPLICATES, 3, figsize=(18, 6 * REPLICATES))

for rep in range(REPLICATES):
    # RBF
    for scale in length_scales:
        cov = generate_covariance_matrix(radial_basis_function_kernel, length_scale=scale)
        sample = np.random.multivariate_normal(np.zeros(NUMBER_OF_POINTS), cov)
        axes[rep, 0].plot(x, sample, alpha=0.8, label=f"l={scale}")
    axes[rep, 0].set_xlabel("x")
    axes[rep, 0].set_ylabel("f(x)")
    axes[rep, 0].set_title(f"RBF Kernel Prior Samples (rep {rep + 1})")
    axes[rep, 0].legend()

    # Linear
    for bias_var in bias_variances:
        cov = generate_covariance_matrix(inhomogeneous_linear_kernel, bias_variance=bias_var, slope_variance=1.0)
        sample = np.random.multivariate_normal(np.zeros(NUMBER_OF_POINTS), cov)
        axes[rep, 1].plot(x, sample, alpha=0.8, label=f"bias_var={bias_var}")
    axes[rep, 1].set_xlabel("x")
    axes[rep, 1].set_ylabel("f(x)")
    axes[rep, 1].set_title(f"Linear Kernel Prior Samples (rep {rep + 1})")
    axes[rep, 1].legend()

    # Exponential Sine Squared
    for scale in length_scales:
        cov = generate_covariance_matrix(exponential_sin_squared_kernel, length_scale=scale, period=1.0)
        sample = np.random.multivariate_normal(np.zeros(NUMBER_OF_POINTS), cov)
        axes[rep, 2].plot(x, sample, alpha=0.8, label=f"l={scale}")
    axes[rep, 2].set_xlabel("x")
    axes[rep, 2].set_ylabel("f(x)")
    axes[rep, 2].set_title(f"Exp Sine Squared Kernel Prior Samples (rep {rep + 1})")
    axes[rep, 2].legend()

plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, "kernel_prior_samples.png"), dpi=150)
plt.show()

# Comparison plot: all three kernels at scale=1, 5 replicates stacked
kernels = [
    (radial_basis_function_kernel, {"length_scale": 1.0}, "RBF"),
    (inhomogeneous_linear_kernel, {"bias_variance": 1.0, "slope_variance": 1.0}, "Linear"),
    (exponential_sin_squared_kernel, {"length_scale": 1.0, "period": 1.0}, "Exp Sine Squared"),
]

fig2, axes2 = plt.subplots(REPLICATES, 1, figsize=(10, 6 * REPLICATES))

for rep in range(REPLICATES):
    for kernel_fn, kwargs, name in kernels:
        cov = generate_covariance_matrix(kernel_fn, **kwargs)
        sample = np.random.multivariate_normal(np.zeros(NUMBER_OF_POINTS), cov)
        axes2[rep].plot(x, sample, alpha=0.8, label=name)
    axes2[rep].set_xlabel("x")
    axes2[rep].set_ylabel("f(x)")
    axes2[rep].set_title(f"Kernel Comparison (scale=1, rep {rep + 1})")
    axes2[rep].legend()

plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, "kernel_comparison_scale1.png"), dpi=150)
plt.show()
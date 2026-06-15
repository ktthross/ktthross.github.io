import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../_includes/shared"))

from kernels import radial_basis_function_kernel, generate_covariance_matrix_from_points
import numpy as np

import matplotlib.pyplot as plt

np.random.seed(505)
x_train = np.linspace(-3, 3, 10)
f_train = np.sin(x_train)

x_star = np.linspace(-3, 3, 200)

k_train_train = generate_covariance_matrix_from_points(x_train, x_train, radial_basis_function_kernel, length_scale=1.0, variance=1.0)
k_train_star = generate_covariance_matrix_from_points(x_train, x_star, radial_basis_function_kernel, length_scale=1.0, variance=1.0)
k_star_star = generate_covariance_matrix_from_points(x_star, x_star, radial_basis_function_kernel, length_scale=1.0, variance=1.0)

noise = 1e-4
k_train_train_stable = k_train_train + noise * np.eye(len(x_train))

posterior_mean = k_train_star.T @ np.linalg.inv(k_train_train_stable) @ f_train
posterior_var = k_star_star - k_train_star.T @ np.linalg.inv(k_train_train_stable) @ k_train_star

print("posterior_mean[:5]:", posterior_mean[:5])

sin_points = np.linspace(-3, 3, 300)

std_dev = np.sqrt(np.diagonal(posterior_var))

assets = os.path.join(os.path.dirname(__file__), "../../assets/2026_06_15_gaussian_processes")

def draw_plot():
    plt.plot(sin_points, np.sin(sin_points), label="sin(x)", color="steelblue", linestyle="solid", linewidth=1, alpha=0.7)
    plt.fill_between(x_star, posterior_mean - std_dev, posterior_mean + std_dev, label="std dev", color="orange", alpha=0.3)
    plt.plot(x_star, posterior_mean, label="posterior mean", color="darkorange", linestyle="dashed", linewidth=2)
    plt.scatter(x_train, f_train, label="x_train", color="red", edgecolors="black", linewidths=0.5, s=60, zorder=5)
    plt.legend()

plt.figure()
draw_plot()
plt.savefig(os.path.join(assets, "posterior.png"), dpi=150, bbox_inches="tight")

plt.figure()
draw_plot()
plt.xlim(0, 0.1)
plt.savefig(os.path.join(assets, "posterior_zoom.png"), dpi=150, bbox_inches="tight")


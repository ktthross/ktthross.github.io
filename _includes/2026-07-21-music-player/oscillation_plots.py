import os

import numpy as np
import matplotlib.pyplot as plt

assets = os.path.join(os.path.dirname(__file__), "../../assets/2026_07_21_music_player")
os.makedirs(assets, exist_ok=True)

t = np.linspace(0, 1, 500)
frequencies = [1, 2, 3, 5]
colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED)
    ax.set_xlabel("t", color=INK)
    ax.set_ylabel("y(t)", color=INK)


fig, ax = plt.subplots(figsize=(7, 4.5))
for f, color in zip(frequencies, colors):
    ax.plot(t, np.sin(2 * np.pi * f * t), label=f"f = {f}", color=color, linewidth=2)
ax.set_title("y(t) = sin(2πft) — f oscillations fit in [0, 1]", color=INK)
style_axes(ax)
ax.legend()
fig.savefig(os.path.join(assets, "scaled_oscillations.png"), dpi=150, bbox_inches="tight")

fig, ax = plt.subplots(figsize=(7, 4.5))
for f, color in zip(frequencies, colors):
    ax.plot(t, np.sin(f * t), label=f"f = {f}", color=color, linewidth=2)
ax.set_title("y(t) = sin(ft) — missing the 2π factor", color=INK)
style_axes(ax)
ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
fig.savefig(os.path.join(assets, "unscaled_oscillations.png"), dpi=150, bbox_inches="tight")

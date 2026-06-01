---
layout: post
title: "Week 1, Day 2 Gaussian Processes"
date: 2026-05-29
categories: machine-learning statistics
tags: [gaussian-processes, covariance-matrix, prior-sampling, kernels, python, machine-learning]
math: true
---

Here are three kernels:

Radial Basis Function

$$
k(x, x') = \exp \left( - \frac{\|x - x'\|^{2}}{2 \sigma^{2}} \right)
$$

Inhomogeneous Linear Kernel

$$
k(x, x') = \sigma^{2} + x \cdot x'
$$

Exponential Sin Squared Kernel

$$
k(x, x') = \exp \left(- \frac{2 \sin^{2} \left( \frac{\pi \|x - x'\|_{2} }{p} \right)}{l^{2}}  \right)
$$

Since the kernel is encoding the covariance between our function signals, the choice of kernel is a prior on the signal.  For RBF, we are saying the functions will correlation according to a gaussian distribution, for inhomogeneious linear kernel we are asserting that the functions will match linearly with some shift of the mean $\simga^{2}$ and with the exponential sin squared kernel we are saying that they will be periodic in their correlation.

Lets take a look at sampling 5 functions from each prior and visualize what they look like.


{% highlight python %}
{% include 2026-05-29-week-1-day-2-gaussian-processes/covariance_matrix_and_prior_samples.py %}
{% endhighlight %}

![Prior samples from RBF, Linear, and Exp Sine Squared kernels across length scales]({{ "/assets/2026_05_29_gaussian_processes/kernel_prior_samples.png" | relative_url }})

![Comparison of all three kernels at scale=1]({{ "/assets/2026_05_29_gaussian_processes/kernel_comparison_scale1.png" | relative_url }})

The length scale changes how quickly the kernel decays. When the length scale is short, there is no correlation between points and the fit becomes jagged.  As the length scale is extended, correlation between points is stronger so the functions become smoother to fit to the points. You can see the tradeoffs between the two. You may be too short and overfit or too long and miss local correlations by over smoothing.
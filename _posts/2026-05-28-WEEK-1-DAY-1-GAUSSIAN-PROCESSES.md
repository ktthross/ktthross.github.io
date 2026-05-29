---
layout: post
title: "Week 1, Day 1 Gaussian Processes"
date: 2026-05-28
categories: machine-learning statistics
tags: [gaussian-processes, kernels, radial-basis-function, probabilistic-modeling, python, machine-learning]
---

{% highlight python %}
{% include 2026-05-28-week-1-day-1-gaussian-processes/radial_basis_function_kernel.py %}
{% endhighlight %}


When using Gaussian Processes, our foundation is based on the assertion that the the probability of function outputs is jointly Gaussian with mean and covariance.  If the values xi and xj are seen as similar then we expect that the function outputs will be very similar at f(xi), f(xj). If our kernel function sees them as similar then we assume the functions are similar.  In this way we are sampling the function space and not parameters because we do not assert an sort of form for the function. We assign no prior to the function but to the function values.

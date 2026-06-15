---
layout: post
title: "Week 1, Day 5 Gaussian Processes"
date: 2026-06-15
categories: machine-learning statistics
tags: []
math: true
---

All the basic pieces are in place. We have the posterior mean to get a prediction at every single test point. We have the posterior covariance to get the uncertainty.

The posterior covariance is an nxn matrix but you only need the diagonal to determine the uncertainty of the test point. This is because the covariance between the test and train points is already accounted for in the construction of the posterior covariance.

$$
\Sigma_{*} = K_{xx} - K_{xX}^{T}K^{-1}_{XX}K_{Xx}
$$

The first term is the covariance of the test term with itself and represents our prior uncertainty. That is modified by the second term. As we view more points in training, the covariance with the test points has more contributions when we condition them on the Gaussian prior. The more information we get, the more variance we will subtract from the test points. 

We only want to know the marginal uncertainty for, our test points so we on;y care about looking at the diagonal rather than any variance in between points.

The posterior mean contains the inverse of the correlation matrix of training points
$$
K_{XX}^{-1}
$$
If we want to predict at 1000 more test points we don't need to recompute $K_{XX}^{-1}f$. The weights needed to best approximate the function points will not change with the test size. This means that predictions will scale as O(mn) where m is the number of test points and n is the number of train points.

If we are fitting noisy observations we do not want to directly pass our function points through the covariance matrix.  If the functions are noisy we are not using the true function values.  Forcing the posterior through the noise would be fitting to measurement error. We would want to model the uncertainty in the measurements as well.

{% highlight python %}
{% include 2026-06-11-week-1-day-5-gaussian-processes/posterior.py %}
{% endhighlight %}

![Posterior mean and uncertainty](/assets/2026_06_15_gaussian_processes/posterior.png)

![Posterior zoom (x: 0 to 0.1)](/assets/2026_06_15_gaussian_processes/posterior_zoom.png)
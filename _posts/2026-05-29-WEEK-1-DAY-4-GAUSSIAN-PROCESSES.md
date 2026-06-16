---
layout: post
title: "Week 1, Day 4 Gaussian Processes"
date: 2026-06-04
categories: machine-learning statistics
tags: []
math: true
---

If we have our Gaussian distribution for points $X$ and observed values $f$ we will want to predict on test points $X^{\*}$ to get $f^{\*}$. The joint distribution is given by

$$
\begin{pmatrix}
f \\ f^{*}
\end{pmatrix} ~ N \begin{pmatrix}
0, &
\begin{bmatrix}
K(X, X) & K(X, X_{*}) \\
K(X_{*}, X) & K(X_{*}, X_{*})
\end{bmatrix}
\end{pmatrix}
$$

and the mean and covariance are defined by

$$
\mu^{*} = \mu(X_{*}) + K_{*}^{T}K^{-1}(f - \mu(X))
$$

$$
\Sigma_{*} = K_{**} - K_{*}^{T}K^{-1}K_{*}
$$

In the posterior mean the covariance component $K(X_{*}, X)$ is the variance between the function outputs we have seen and those we wish to predict. It maps the data that we have to the data we want to predict on. If the training data and test data are similar, there will be a large value and if the data are dissimilar it will be small. This will influence how much our prediction is informed by our previous data.

The inverse term $K(X, X)^{-1}f$ is solving for a vector

$$
a = K(X, X)^{-1}f
$$

such that

$$
K(X,X)a = f
$$

It shows us the weights to apply to the sample data such that we can recover the function value.

When the two terms are combined, we first get the weights needed to solve for our function output, then we use that with the correlation between the space we want to predict in with what we have.  The cross dataset correlation is weighted by the data points most likely to contribute to the function output.

Lets look at a simple example


{% highlight python %}
{% include 2026-06-11-week-1-day-4-gaussian-processes/posterior.py %}
{% endhighlight %}

As I move my `x_star` from 0.5 to 0.0, I expect that the variance and mean will approach zero. This is because the model will be interpolating close and closer to a real value so the contribution from the closest point will dominate the contribution in fitting that point, and the mean will approach -0.2 because I am approaching the value at 0.0 which will make a larger contribution to the mean.
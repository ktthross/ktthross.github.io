---
layout: post
title: "Week 1, Day 3 Gaussian Processes"
date: 2026-06-03
categories: machine-learning statistics
tags: []
math: true
---
Lets do the definition to pad out the word count shall we?

A Gaussian process is a collection $\lbrace f(x), x \in \mathcal{X} \rbrace$ such that, for any $n \in \mathbb{N}$ and $x_{1},\dots,x_{n} \in \mathcal{X}$, the random vector $\left( f(x_{1}), \dots, f(x_{n}) \right)$ has a joint multivariate Gaussian distribution.

From this, the distribution is defined by its mean and the covariance function (or kernel)

$$
m(x) = \mathbb{E}[f(x)]
$$

$$
K(x, x') = \mathbb{E}\left[(f(x) - m(x))(f(x') - m(x')) \right]
$$

This is defined at infinitely many points but we will only ever see it on a finite number of points. Lets evaluate our covariance matric for a real example.

$$
K = \begin{bmatrix}
K(x_1, x_1) & K(x_1, x_2) & K(x_1, x_3) \\
K(x_2, x_1) & K(x_2, x_2) & K(x_2, x_3) \\
K(x_3, x_1) & K(x_3, x_2) & K(x_3, x_3)
\end{bmatrix}
$$

For the set of points $[-1.0, 0.0, 1.0]$ using the [RBF kernel]({% post_url 2026-05-29-WEEK-1-DAY-2-GAUSSIAN-PROCESSES %})
, the covariance matrix is

$$
K = \begin{bmatrix}
1 & 0.6065 & 0.1353 \\
0.6065 & 1 & 0.6065 \\
0.1353 & 0.6065 & 1
\end{bmatrix}
$$

The matrix is symmetric and we can confirm that all the eigenvalues are non-negative.


{% highlight python %}
{% include 2026-06-03-week-1-day-3-gaussian-processes/covariance_matrix_values_and_eignenvalues.py %}
{% endhighlight %}

The kernel metric must be positive definite because it is a measure of variance.  There cannot be negative variance and all points are perfectly correlated with themselves. We see this reflected in our toy example.

The GP requires that any finite collection is jointly Gaussian. If that was not the case you could not marginalize out one variable and get a Gaussian distribution.
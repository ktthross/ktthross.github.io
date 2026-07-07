---
layout: post
title: "Week 1, Day 7 Gaussian Processes"
date: 2026-06-24
categories: machine-learning statistics
tags: [gaussian-processes, cholesky-decomposition, numerical-stability, linear-algebra, posterior-inference, python, machine-learning]
math: true
---

Gaussian Processes depend on matrix inversion, and that can get numerically ugly fast. Rather than explicitly calculate $K^{-1}$, we can solve the same system with a Cholesky decomposition.

For any positive definite matrix, there is a lower triangular matrix such that

$$
K = LL^{T}
$$

We can then solve our linear equation in two steps. Let us take a look at what that means.

$$
K \alpha = y \to LL^{T} \alpha = y
$$

If we define $L^{T} \alpha = v$, then the first problem becomes

$$
Lv = y
$$

Once we solve that for $v$, we can solve for $\alpha$ with

$$
L^{T} \alpha = v
$$

Each triangular solve scales as $O(n^{2})$, so the full solve is still much cheaper than treating the inverse as the main event.

## Digression

To understand why inversion is less favorable than a Cholesky solve, we need to talk about condition numbers. That means first defining the norm.

### Vector norm

There are a few common definitions of the vector norm:

$$
\begin{aligned}
||v||_{1} &= \sum_{i}^{n}|v_{i}| \\
||v||_{2} &= \sqrt{\sum_{i}^{n}v_{i}^{2}} \\
||v||_{\infty} &= \max(|v_{0}|, |v_{1}|, ..., |v_{n}|)
\end{aligned}
$$

### Induced matrix norm

We define the matrix norm as

$$
||A|| = \underset{\vec{v} \in \mathbb{R}^{n}, \vec{v} \neq 0}{\max} \frac{||A\vec{v}||}{||\vec{v}||}
$$

We need a way to compute the matrix norm from the vector norms. This example shows the form for

$$
||A||_{\infty}
$$

Start with the identity

$$
\begin{aligned}
A \vec{v} &= \vec{b} \\
||A \vec{v}||_{\infty} &= ||\vec{b}||_{\infty} \\
\underset{i}{\max} \left|\sum_{j}a_{ij}v_{j}\right| &= \underset{i}{\max} |b_{i}|
\end{aligned}
$$

Now we can show an upper bound:

$$
\begin{aligned}
||A \vec{v}||_{\infty} &= \underset{i}{\max} \left|\sum_{j}a_{ij}v_{j}\right| \\
\underset{i}{\max} \left|\sum_{j}a_{ij}v_{j}\right| &\leq \underset{i}{\max} \sum_{j}|a_{ij}||v_{j}| \\
\underset{i}{\max} \sum_{j}|a_{ij}||v_{j}| &\leq \underset{i}{\max} \sum_{j}|a_{ij}| \, ||\vec{v}||_{\infty} \\
\underset{i}{\max} \sum_{j}|a_{ij}| \, ||\vec{v}||_{\infty} &= ||\vec{v}||_{\infty} \underset{i}{\max} \sum_{j}|a_{ij}|
\end{aligned}
$$


In the third line, we replace each $\lvert v_{j} \rvert$ with the largest absolute component of the vector. That lets us pull it outside the summation.

Now we can write

$$
||A||_{\infty}
= \underset{\vec{v} \in \mathbb{R}^{n}, \vec{v} \neq 0}{\max}
\frac{||A\vec{v}||_{\infty}}{||\vec{v}||_{\infty}}
\leq \underset{i}{\max} \sum_{j}|a_{ij}|
$$

By definition, we also know that for any $\vec{v}$

$$
||A||_{\infty} \geq \frac{||A\vec{v}||_{\infty}}{||\vec{v}||_{\infty}}
$$

Because we have that freedom, we can choose $\vec{v}$ so that $\lvert \lvert \vec{v} \rvert \rvert_{\infty} = 1$ and each entry is either $1$ or $-1$. That lets the signs align with a chosen row:

$$
||A||_{\infty}
\geq \frac{||A\vec{v}||_{\infty}}{||\vec{v}||_{\infty}}
= \underset{i}{\max} \left|\sum_{j}a_{ij}v_{j}\right|
\geq \left|\sum_{j}a_{pj}v_{j}\right|
= \sum_{j}|a_{pj}|
$$

So the infinity norm is just the maximum absolute row sum.

### Condition number

Now let us look at a linear system. We want to know how much a change in the output vector $\vec{b}$ can amplify the change in the recovered input $\vec{x}$:

$$
A \vec{x} = \vec{b} \to A (\vec{x} + \delta \vec{x}) = \vec{b} + \delta \vec{b}
$$

Subtract the original equation from both sides:

$$
A \delta \vec{x} = \delta \vec{b} \to \delta \vec{x} = A^{-1} \delta \vec{b}
$$

Take the norm of the perturbation:

$$
\delta \vec{x} = A^{-1} \delta \vec{b}
\to
||\delta \vec{x}||
=
||A^{-1} \delta \vec{b}||
\leq
||A^{-1}|| \, || \delta \vec{b}||
$$

And for the original equation:

$$
A \vec{x} = \vec{b} \to ||A|| \, || \vec{x} || \geq || \vec{b} ||
$$

To compare the relative changes in $\vec{x}$ and $\vec{b}$, divide through:

$$
\frac{|| \delta \vec{x} ||}{||A|| \, || \vec{x} ||}
\leq
\frac{ ||A^{-1}|| \, || \delta \vec{b}||}{|| \vec{b} ||}
$$

$$
\frac{|| \delta \vec{x} ||}{|| \vec{x} ||}
\leq
||A|| \, ||A^{-1}|| \frac{ || \delta \vec{b}||}{|| \vec{b} ||}
$$

The multiplier $\vert \lvert A \rvert \rvert  \vert \lvert A^{-1} \rvert \rvert$ is the condition number. That is the quantity telling us how much relative error can get amplified.

For a symmetric positive definite matrix, the Cholesky factor is usually the better numerical object to work with. In the 2-norm, its condition number is the square root of the condition number of the original matrix, so the solve is typically better behaved than explicitly forming the inverse.

### Personal note

I still find this derivation a little unsatisfying. It is more math and more formal language, but it still does not quite explain *why* Cholesky feels better in practice. It mostly gives a disciplined way to say that it is better conditioned.

## Back to the main program

The posterior mean is

$$
\mu_{x} = \mu(x) + K_{xX}K^{-1}_{XX}(f - \mu(X))
$$

We only need to factor $K_{XX}$ once, then solve two triangular systems to get the term $K^{-1}_{XX}(f - \mu(X))$. After that, the rest is just matrix multiplication.

For the posterior covariance,

$$
\Sigma_{xx} = K_{xx} - K_{xX}K^{-1}_{XX}K_{Xx}
$$

we need the same kind of object again:

$$
K^{-1}_{XX}K_{Xx}
$$

Naively, that looks like another pair of triangular solves. But with a little refactoring:

$$
K = LL^{T} \to K^{-1} = L^{-T}L^{-1}
$$

$$
K_{xX}L^{-T}L^{-1}K_{Xx} = (L^{-1}K_{Xx})^{T}(L^{-1}K_{Xx})
$$

So for the covariance term, we can solve one lower-triangular system,

$$
L \alpha = K_{Xx}
$$

and then use $\alpha^{T}\alpha$ directly.

That leaves us doing four $O(n^{2})$ triangular solves to get both posterior quantities, while avoiding the explicit inverse altogether.

Whether we do direct inversion or a Cholesky solve, caching the expensive pieces matters. But I would still rather have the numerically stable version, because a badly conditioned matrix will leak error straight into the posterior. That error is not aleatoric uncertainty. It is just the algorithm being less trustworthy, and I do not want to confuse those two things.

{% highlight python %}
{% include 2026-06-24-week-1-day-7-gaussian-processes/cholesky_solver.py %}
{% endhighlight %}

![Posterior mean and uncertainty computed with a Cholesky solve]({{ "/assets/2026_06_24_week_1_day_7_gaussian_processes/cholesky_posterior_noise_0.2.png" | relative_url }})

---
layout: post
title: "Week 1, Day 6 Gaussian Processes"
date: 2026-06-17 12:00:00 -0500
categories: machine-learning statistics
tags: [gaussian-processes, noisy-observations, predictive-uncertainty, aleatoric-uncertainty, covariance-matrix, kernels, python, machine-learning]
math: true
---

GP interpolation will likely be executed on real measurements which have noise.  We want to ensure our model reflects the uncertainty in the measurements as well. A measurement can be written as:
$$
y_{i} = f(X_{i}) + \epsilon_{i}
$$

The covariance matrix then becomes
$$
K_{XX}' = K_{XX} + \sigma^{2}_{n}I
$$

We can then insert this into our previous definitions for posterior mean and covariance.

$$
\mu_{x} = \mu(x) + K_{xX}[K_{XX} + \sigma^{2}_{n}I]^{-1}(f - \mu(X))
$$

$$
\Sigma_{x} = K_{xx} - K_{xX}[K_{XX} + \sigma^{2}_{n}I]^{-1}K_{Xx}
$$

to incorporate the uncertainty in the estimates into our posterior.

In the previous exercise, we had to add some small values to the diagonal elements of the covariance matrix in order to calculate the inverse. In the expression above, the noise contribution looks very similar to this: it is elements added to the diagonal.  These are serving different purposes however.

The Cholesky Decomposition requires strictly positive eigenvalues.  Adding the small components to the diagonal shifts the eigenvalues away from negative and 0 values that occur from rounding artifacts to ensure that the inverse can be calculated.

The noise in the function itself is a quantification in the uncertainty of the measurement itself and is encoding that value. It is not done to ensure the inversion algorithm is stable.

As the uncertainty in the measurements gets large, the diagonal terms come to dominate the covariance matrix
$$
K_{XX} \approx \sigma^{2}_{n}I
$$

in which case the posterior is simply a conditioning on the uncertainty in the measurements and the variance between measures does not matter.

In the other extreme, the variance in the measurement goes towards zero. As this gets smaller we approach the previous implementation where there is no noise term. In this case, the train values have absolute confidence and the variance near them is 0. The posterior mean contributions from the train measurements will take contributions from all the covariance terms rather than be dominated by the uncertainty in the measurements themselves.  Similarly, the contributions to the covariance matrix are inversely proportional to the size of the uncertainty in the measurements. As they get smaller, the reduction in uncertainty term in the covariance matrix

$$
K_{xX}[K_{XX} + \sigma^{2}_{n}I]^{-1}K_{Xx}
$$

gets larger and removes more uncertainty from the baseline value.

The noise term only shows up on the diagonal because, barring special circumstances, the uncertainty in one measurement is not correlated with the uncertainty in another.  Measurements are independent so the variance in one measurement should not affect the outcome of another.


{% highlight python %}
{% include 2026-06-17-week-1-day-6-gaussian-processes/noisy_uncertainty.py %}
{% endhighlight %}

![Posterior with measurement noise std = 0.05](/assets/2026_06_17_week_1_day_6_gaussian_processes/posterior_noise_0.05.png)

![Posterior with measurement noise std = 0.2](/assets/2026_06_17_week_1_day_6_gaussian_processes/posterior_noise_0.2.png)

![Posterior with measurement noise std = 1.0](/assets/2026_06_17_week_1_day_6_gaussian_processes/posterior_noise_1.0.png)

Its easy to see that as the noise increases, uncertainty around the training points grows and the interpolations get worse as well. When the uncertainty is 1.0 the interpolations are totally dominated by the uncertainty in the training data.

The uncertainty in the measurements is the "aleatoric noise" and cannot be reduced any further. We just cannot get more precise than that. In bands where there are lots of observations and a wide band, we will need to refine our method of measurement to be more accurate and reduce the aleatoric noise.  In a band with sparse points but a lot of epistemic uncertainty, the right move is to add new data points to reduce uncertainty.  If the measurements are not accurate it will be only so helpful but is the best way to reduce the epistemic uncertainty.

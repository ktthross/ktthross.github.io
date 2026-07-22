---
layout: post
title: "Music Player"
date: 2026-07-21
categories: music mathematics signal-processing
tags: [least-squares, fourier, music, midi, piano, signal-processing, synthesis, web-audio, javascript]
math: true
---

In the previous post, we [`fit notes as a linear combination of all other notes`]({% post_url 2026-07-07-linear-combination-of-notes %}).  There is also a snazzy visualizer to show you the notes that contribute and their weights to get the best fit.  You can also tune the fit to include the top N notes or % energy.  Now we actually want to listen to these notes.  There are a couple things we need to address before we can listen however.

In the previous post, we derived the fits using the function

$$
y(t) = A \sin(f t)
$$

For our fit, because all functions used this same basic form, there was no problem. But now that we want to hear the notes, we need an additional factor of $2 \pi$ in the term. This is because the frequency term is supposed to tell us the number of oscillations per period.

So for example, when $t = 1$, the function should have gone through $f$ cycles.  Since trigonometric functions take radians as input this means sine will complete a cycle every $2 \pi$ radians.

$$
y(t) = A \sin(2 \pi f t)
$$

![y(t) = sin(2πft) fits f oscillations into [0, 1]](/assets/2026_07_21_music_player/scaled_oscillations.png)

Without the $2 \pi$ factor, the frequency term no longer maps to cycles per unit time, so $f$ oscillations don't fit in the same domain:

![y(t) = sin(ft) does not fit f oscillations into [0, 1]](/assets/2026_07_21_music_player/unscaled_oscillations.png)

The other issue we need to address is interpreting the coefficient infront of each note. The coeffcient in front of the sine function is the volume of that note.  Notice that some of our linear combinations have negative values however. lets look at the first few terms of A4.

Using the integration window of one period of A4 (the same $b$ used in the previous post), here are the largest contributors by coefficient energy, both positive and negative:

| Note | Frequency (Hz) | Coefficient | % of Energy |
| --- | --- | --- | --- |
| D1 | 36.71 | -5.7464 | 5.5% |
| D5 | 587.33 | -4.3523 | 4.2% |
| G#3/Ab3 | 207.65 | 4.2700 | 4.1% |
| A1 | 55.00 | 3.4976 | 3.3% |
| G5 | 783.99 | -3.4143 | 3.3% |
| C#5/Db5 | 554.37 | 3.0935 | 3.0% |
| B1 | 61.74 | 2.8841 | 2.8% |

A negative coefficient doesn't mean negative volume, since volume has to be positive. This indicates that the note needs to destructively interfere with the other notes in the mix.  We can use the identity $-\sin(2 \pi f t) = \sin(2 \pi f t + \pi)$, to show that the note enters the mix $\pi$ radians out of phase and the amplitude retains its meaning as volume.

With this two pieces resolved, lets make some notes!

## Try it

The player below reuses the fits precomputed for the [`explorer in the previous post`]({% post_url 2026-07-07-linear-combination-of-notes %}). Press and hold a key on the first keyboard to hear that note rebuilt as a chord — the surviving contributors after your chosen window/cutoff, each one's coefficient setting both its volume and its phase exactly as derived above. Press the matching key on the second keyboard to hear the real tone, for comparison.

{% include 2026-07-21-music-player/note_synth_player.html %}


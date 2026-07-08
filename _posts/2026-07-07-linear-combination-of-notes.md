---
layout: post
title: "Linear Combination of Notes"
date: 2026-07-07 12:00:00 -0500
categories: music mathematics signal-processing
tags: [least-squares, fourier, music, midi, piano, linear-algebra, python, numpy, signal-processing]
math: true
---

A mathematical process I was introduced to during my formal education is that of fitting a function as a linear combination of other functions. An extremely powerful tool used across many disciplines and something that has stuck with me.  In particular I started wondering if you could use the same technique to model musical notes: playing a note by not playing it.

The idea is to choose a note, then find the best combination of other notes which can reproduce it, then play all those
notes together.  

The mathematical form of a note is given by a sine function with the frequency of the sine function determining the note.

$$
y(t) = A \sin(f t)
$$

where f is the frequency of the oscillation.  The frequency of a note is related to the MIDI number through the equation

$$
f = 440 * 2 ^ {\frac{n - 69}{12}}
$$

where 440 is A4 and middle C has MIDI note 60. The range for a standard piano is MIDI note 21 (A0) to MIDI note 108 (C8).

Let's take a look at the notes on a standard piano.

<style>
.note-table { margin: 1em 0; border: 1px solid rgba(128,128,128,.3); border-radius: 6px; padding: 0 14px; }
.note-table > summary { cursor: pointer; padding: 12px 4px; font-weight: 600; list-style-position: inside; }
.note-table > summary:hover { color: #b07d24; }
.note-table[open] > summary { border-bottom: 1px solid rgba(128,128,128,.2); margin-bottom: 10px; }
.note-table table { margin-bottom: 12px; }
</style>

| MIDI Number | Piano Key | Note Name | Frequency |
| --- | --- | --- | --- |
| 108 | 88 | C8 | 4186.01 |
| 107 | 87 | B7 | 3951.07 |
| 106 | 86 | A#7/Bb7 | 3729.31 |
| 105 | 85 | A7 | 3520.00 |
| 104 | 84 | G#7/Ab7 | 3322.44 |
| 103 | 83 | G7 | 3135.96 |
| 102 | 82 | F#7/Gb7 | 2959.96 |
| 101 | 81 | F7 | 2793.83 |

<details class="note-table" markdown="1">
<summary>Show remaining 80 keys (E7 &rarr; A0)</summary>

| MIDI Number | Piano Key | Note Name | Frequency |
| --- | --- | --- | --- |
| 100 | 80 | E7 | 2637.02 |
| 99  | 79  | D#7/Eb7 | 2489.02 |
| 98  | 78  | D7 | 2349.32 |
| 97  | 77  | C#7/Db7 | 2217.46 |
| 96  | 76 | C7 | 2093.00 |
| 95  | 75 | B6 | 1975.53 |
| 94  | 74 | A#6/Bb6 | 1864.66 |
| 93  | 73 | A6 | 1760.00 |
| 92  | 72 | G#6/Ab6 | 1661.22 |
| 91  | 71 | G6 | 1567.98 |
| 90  | 70 | F#6/Gb6 | 1479.98 |
| 89  | 69 | F6 | 1396.91 |
| 88  | 68 | E6 | 1318.51 |
| 87  | 67 | D#6/Eb6 | 1244.51 |
| 86  | 66 | D6 | 1174.66 |
| 85  | 65 | C#6/Db6 | 1108.73 |
| 84  | 64 | C6 | 1046.50 |
| 83  | 63 | B5 | 987.77 |
| 82  | 62 | A#5/Bb5 | 932.33 |
| 81  | 61 | A5 | 880.00 |
| 80  | 60 | G#5/Ab5 | 830.61 |
| 79  | 59 | G5 | 783.99 |
| 78  | 58 | F#5/Gb5 | 739.99 |
| 77  | 57 | F5 | 698.46 |
| 76  | 56 | E5 | 659.26 |
| 75  | 55 | D#5/Eb5 | 622.25 |
| 74  | 54 | D5 | 587.33 |
| 73  | 53 | C#5/Db5 | 554.37 |
| 72  | 52 | C5 | 523.25 |
| 71  | 51 | B4 | 493.88 |
| 70  | 50 | A#4/Bb4 | 466.16 |
| 69  | 49 | A4 | 440.00 |
| 68  | 48 | G#4/Ab4 | 415.30 |
| 67  | 47 | G4 | 392.00 |
| 66  | 46 | F#4/Gb4 | 369.99 |
| 65  | 45 | F4 | 349.23 |
| 64  | 44 | E4 | 329.63 |
| 63  | 43 | D#4/Eb4 | 311.13 |
| 62  | 42 | D4 | 293.66 |
| 61  | 41 | C#4/Db4 | 277.18 |
| 60  | 40 | C4 | 261.63 |
| 59  | 39 | B3 | 246.94 |
| 58  | 38 | A#3/Bb3 | 233.08 |
| 57  | 37 | A3 | 220.00 |
| 56  | 36 | G#3/Ab3 | 207.65 |
| 55  | 35 | G3 | 196.00 |
| 54  | 34 | F#3/Gb3 | 185.00 |
| 53  | 33 | F3 | 174.61 |
| 52  | 32 | E3 | 164.81 |
| 51  | 31 | D#3/Eb3 | 155.56 |
| 50  | 30 | D3 | 146.83 |
| 49  | 29 | C#3/Db3 | 138.59 |
| 48  | 28 | C3 | 130.81 |
| 47  | 27 | B2 | 123.47 |
| 46  | 26 | A#2/Bb2 | 116.54 |
| 45  | 25 | A2 | 110.00 |
| 44  | 24 | G#2/Ab2 | 103.83 |
| 43  | 23 | G2 | 98.00 |
| 42  | 22 | F#2/Gb2 | 92.50 |
| 41  | 21 | F2 | 87.31 |
| 40  | 20 | E2 | 82.41 |
| 39  | 19 | D#2/Eb2 | 77.78 |
| 38  | 18 | D2 | 73.42 |
| 37  | 17 | C#2/Db2 | 69.30 |
| 36  | 16 | C2 | 65.41 |
| 35  | 15 | B1 | 61.74 |
| 34  | 14 | A#1/Bb1 | 58.27 |
| 33  | 13 | A1 | 55.00 |
| 32  | 12 | G#1/Ab1 | 51.91 |
| 31  | 11 | G1 | 49.00 |
| 30  | 10 | F#1/Gb1 | 46.25 |
| 29  | 9  | F1 | 43.65 |
| 28  | 8  | E1 | 41.20 |
| 27  | 7  | D#1/Eb1 | 38.89 |
| 26  | 6  | D1 | 36.71 |
| 25  | 5  | C#1/Db1 | 34.65 |
| 24  | 4  | C1 | 32.70 |
| 23  | 3  | B0 | 30.87 |
| 22  | 2  | A#0/Bb0 | 29.14 |
| 21  | 1  | A0 | 27.50 |

</details>

For this I will use the notes of the piano as not only the notes I intend to fit but also the notes that will be used
for the fit. For each note in the piano, I will use all other notes to try and create the best fit possible.  Let's start on the process and see where it gets us.

For the fit our sine functions are not in general orthogonal and we want to fit over an interval, so we can use an unconstrained least squares fit.

$$
E = \int_{a}^{b}\left ( f(x) - \sum_{i=1}^{n}c_{i}\phi_{i}(x) \right )^{2} dx
$$

To solve this we take the derivative w.r.t. each component and set it to 0

$$
\begin{aligned}
\frac{d E}{d c_{j}} &= 0 \\
\frac{d}{d c_{j}} \int_{a}^{b}\left ( f(x) - \sum_{i=1}^{n}c_{i}\phi_{i}(x) \right )^{2} dx &= 0 \\
\int_{a}^{b} \frac{d}{d c_{j}} \left ( f(x) - \sum_{i=1}^{n}c_{i}\phi_{i}(x) \right )^{2} dx &= 0 \\
\int_{a}^{b} - 2 * \left ( f(x) - \sum_{i=1}^{n}c_{i}\phi_{i}(x) \right ) * \phi_{j} dx &= 0 \\
\int_{a}^{b} \left ( f(x) - \sum_{i=1}^{n}c_{i}\phi_{i}(x) \right ) * \phi_{j} dx &= 0 \\
\int_{a}^{b} \left ( f(x) \phi_{j} - \sum_{i=1}^{n}c_{i}\phi_{i}(x) \phi_{j} \right ) dx &= 0 \\
\int_{a}^{b} f(x) \phi_{j} dx &= \int_{a}^{b} \sum_{i=1}^{n} c_{i}\phi_{i}(x) \phi_{j} dx \\
\int_{a}^{b} f(x) \phi_{j} dx &= \sum_{i=1}^{n} c_{i} \int_{a}^{b} \phi_{i}(x) \phi_{j} dx
\end{aligned}
$$

We can write this as a system of linear equations.  We define the vector $\vec{b}$ with elements

$$
b_{j} = \int_{a}^{b} f(x) \phi_{j} dx
$$

We have a matrix with elements

$$
G_{ij} = \int_{a}^{b} \phi_{i}(x) \phi_{j} dx
$$

which means our term on the right is just a vector-matrix multiplication

$$
\sum_{i=1}^{n} c_{i} G_{ij} = \vec{c} G
$$

Since the matrix is symmetric, we can simply take the transpose of our terms and get a nice linear equation

$$
G \vec{c} = \vec{b}
$$

Now all we need is a way to evaluate the matrix elements $G_{ij}$ and the elements $b_{j}$.

$$
G_{ij} = \int_{a}^{b} \phi_{i}(x) \phi_{j} dx = \int_{a}^{b} \sin(\mu_{i} x) \sin(\mu_{j} x) dx
$$

Our integral now has a nice closed form:

For the diagonal terms:

$$
\int \sin(\mu_{i}x)^{2} dx = \frac{x}{2} - \frac{1}{4 \mu_{i}}\sin(2 \mu_{i} x) + C
$$

and for the off diagonal terms:

$$
\int \sin( \mu_{i} x) \sin( \mu_{j} x) dx = \frac{\sin ((\mu_{j} - \mu_{i}) x )}{2(\mu_{j} - \mu_{i})}  - \frac{\sin ((\mu_{i} + \mu_{j}) x )}{2(\mu_{i} + \mu_{j})} + C
$$

We need these indefinite integrals evaluated at the bounds of our integral. For a given $a$ and $b$, the expressions
are

$$
\int_{a}^{b} \sin(\mu_{i}x)^{2} dx = \frac{b}{2} - \frac{1}{4 \mu_{i}}\sin(2 \mu_{i} b) - \frac{a}{2} + \frac{1}{4 \mu_{i}}\sin(2 \mu_{i} a)
$$


$$
\int_{a}^{b} \sin( \mu_{i} x) \sin( \mu_{j} x) dx = \frac{\sin ((\mu_{j} - \mu_{i}) b )}{2(\mu_{j} - \mu_{i})}  - \frac{\sin ((\mu_{i} + \mu_{j}) b )}{2(\mu_{i} + \mu_{j})} - \frac{\sin ((\mu_{j} - \mu_{i}) a )}{2(\mu_{j} - \mu_{i})}  + \frac{\sin ((\mu_{i} + \mu_{j}) a )}{2(\mu_{i} + \mu_{j})}
$$

For the bounds, we know that it will always start at 0 so $a = 0$.  Now let's figure out what b should be set to. My first thought is to set b to the period of the note that we are trying to fit.  My thinking is that the frequency is what defines the note and so going beyond the period of oscillation does not provide any new information.  However, since we are fitting to other frequencies, the additional period may show that other frequencies which do not cleanly fit into that period can still make meaningful contributions when fit across multiple oscillations.  To test this, we will use 1 period as the reference point for b, then try various multiples of that value to see how it changes.

Here is a small python script that demonstrates how to fit a note using the other 87.

{% highlight python %}
{% include linear_combination_of_notes/fit_note.py %}
{% endhighlight %}

## Try it

The explorer below shows the fit for every key on the piano, precomputed with the script above. Click any key to hold it out — it becomes the target tone, reconstructed as a weighted sum of the other 87. Choose the integration window (as a multiple of the held note's period), then decide what counts as a *meaningful* contributor: an absolute coefficient threshold, the top $N$ weights, or the smallest set of notes capturing a share of the total coefficient energy. The keyboard heat-maps the surviving coefficients.

{% include linear_combination_of_notes/note_fit_explorer.html %}


For the next post we will try making some of these tones to see what they sound like!
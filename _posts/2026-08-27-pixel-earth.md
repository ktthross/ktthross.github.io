---
layout: post
title: "Pixel Earth"
date: 2026-08-27 12:00:00
categories: computer-graphics game-development
tags: [pixel-art, satellite-imagery, nasa, dscovr-epic, image-processing, color-quantization, hsv, python, game-development]
---

I needed a spinning pixel art earth for a project I'm working on. I didn't want to hand draw it because I don't have that much time, but also I wanted the freedom to be able to change resolution and coloring quickly without needing to go through lots of recoloring.

The plan was to get satellite images of the earth which encompass the entire surface. From these, cut out the earth from the background and then do pixelation.

I discovered there is a wealth of absolutely breathtaking images of our planet online. It was inspiring and moved me to a sort of sublime melancholy. I wish I could be watching it right now from space.

The source I used is from DSCOVR/EPIC: [epic.gsfc.nasa.gov](https://epic.gsfc.nasa.gov). It contains images for full days so that you can see the entire earth for that day.

There were a couple things to address. Cloud cover. Cloud cover makes the world even more beautiful, but cloud cover did not suit my needs. I want a bare naked earth that I can later layer clouds on top of if I need to.

To remove clouds, the app downloads images from many different days and composites them, selecting the best pixel values which are not clouds.

Even with this, the result was underwhelming. The earth without clouds is quite brown. Perhaps this is accurate from space, but it is not consistent with the idea I have in my head or my experience with the planet. The truth very much seems to be less real than the fiction in my head.

In this case my idea about how colorful the earth is from space is what I wanted to see, so I compromised between what the satellite shows and what is in my mind.

To this end we needed to brighten the earth and shift some of the brown areas towards green. Using HSV, colors that were closest to green on land were rotated. This had to be offset by a brightness check because deserts tend to reflect more light, and without taking this into consideration the deserts lit up bright green!

Finally, there was the issue of inconsistency between rotating frames. One spot on the globe would have different colors assigned for each individual frame. While it looked nice on its own, when visualizing the entire sequence the earth sort of sparkled.

This was solved by quantizing the color palette across all frames of the globe, then matching each pixel to a lat/long pair. Then for each frame, the pixel associated with a lat/long was selected based on a winner for every frame.

Anyway, here is the repo:

[github.com/ktthross/pixel-earth](https://github.com/ktthross/pixel-earth)

and a gif made from the data.

![Spinning pixel art earth generated from DSCOVR/EPIC satellite imagery]({{ "/assets/2026-08-27-PIXEL-EARTH/rotation.gif" | relative_url }})

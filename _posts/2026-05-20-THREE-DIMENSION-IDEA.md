---
layout: post
title: "Generating three-dimensional objects"
date: 2026-05-20
categories: machine-learning generative-ai video-games
---

I would like to push my experience and knowledge of generative AI. I have been pondering what an engaging project might be, and the idea I kept coming back to started with a spark of inspiration I received when visiting Plovdiv, Bulgaria. I was awestruck by how seamlessly the ancient ruins of past empires connected to the recent cultural heritage and history, all as a backdrop to a modern and vibrant city. This sort of time traveling while just going to get groceries or coffee is fascinating. I wish I was there now!

The **Stadium of Philippopolis** is what resonated with me the most.  You descend from the street level down into the old stadium. Tens of street cats relax in the warm sun and heat emanating from the ancient structure.

<figure>
  <img src="{{ '/assets/2026_05_20_three_dimension_idea/960px-Roman_stadium.jpg' | relative_url }}" alt="The Roman stadium in Plovdiv, Bulgaria, surrounded by the modern city.">
  <figcaption>
    Image: <a href="https://commons.wikimedia.org/wiki/File:Roman_stadium.jpg">Община Пловдив</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0</a>, via Wikimedia Commons.
  </figcaption>
</figure>

The modern bridge that passes over it is such a cool visual juxtaposition. The stadium has some tunnels and dark entry ways.  It is simultaneously separate from the surrounding city and immediately in the middle -- both out of time and entirely present. Lovely.

The stadium directly abuts a nearly 700 year old mosque.

<figure>
  <img src="{{ '/assets/2026_05_20_three_dimension_idea/960px-Dzhumayata.jpg' | relative_url }}" alt="Dzhumaya Square in Plovdiv, Bulgaria, with the mosque and surrounding city buildings.">
  <figcaption>
    Image: <a href="https://commons.wikimedia.org/wiki/File:Dzhumayata.jpg">Ivelin Vraykov</a>, <a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY-SA 3.0</a>, via Wikimedia Commons.
  </figcaption>
</figure>

This is a truly inspiring location and I strongly recommend you visit and experience this magical place if you have the means and opportunity!

Walking through Plovdiv what I really wanted was a digital copy of this space that I could explore. The mixed architecture and contrasting buildings were so surreal I felt like I was in an imagined space.  It actually inspired a larger narrative and game idea but that is for another day (hopefully -- life is short).  I wished I had a drone that could fly through the space and take pictures that could be used to generate assets for a game.

That is what brings us to today.  How can I build a 3D digital object purely from pictures?  The idea is that you put in N pictures and it returns a 3D model colored to match the images.

When thinking about this there are three things I want to be cognizant of. 
- The returned object should be easily editable. The worst case would be to generate an object that is 90% of the way there, but the complexity of converting it into an object which could be edited is greater than just hammering on the model 20 times until you get 95% of the way there and decide it's good enough.
- I want to use images only and not need to train on difficult-to-acquire measurements of things for training data. Ideally, it will get better with the number of images we add.  Perhaps a later implementation can introduce additional modalities.
- This likely has been attempted and accomplished by someone. I would like to approach this problem myself for the learning experience. I will try as much as I can to avoid copying others' work.

With that in mind, the first question to answer is: what should the output be? More specifically, what output format is renderable, editable, and/or can easily be converted to different formats. My imagination is that this will basically create some set of points making up triangles defining the surface. This would generally be extensible and renderable into any program.

According to the internet I want an OBJ file which is really a list of vertices followed by a list of faces.

I have a generated version of this for a cube, in particular a cube rendered with triangles.

```
# Vertex List (8 corners of the cube)
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0

# Face List (12 triangles)
# Front Face (split 1 2 3 4)
f 1 2 3
f 1 3 4
# Back Face (split 8 7 6 5)
f 8 7 6
f 8 6 5
# Top Face (split 4 3 7 8)
f 4 3 7
f 4 7 8
# Left Face (split 5 1 4 8)
f 5 1 4
f 5 4 8
# Bottom Face (split 5 6 2 1)
f 5 6 2
f 5 2 1
# Right Face (split 2 6 7 3)
f 2 6 7
f 2 7 3
```

This should be the minimal information needed to convert and render in other programs.  Before we wrap this up however, let's confirm that this file can indeed be rendered in a couple programs!

I first tried to upload the file above to `babylon.js` and I think it may have worked but I am missing some configuration of the color of the faces! Or not.  I did render the object in Meshy AI OBJ Viewer no problem. Ok. That's enough for today. I will confirm on Blender.

It looks like the hardest step is done. We came up with an idea and did the smallest test of feasibility and defined a goal.

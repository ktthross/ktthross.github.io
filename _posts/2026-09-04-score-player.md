---
layout: post
title: "Score Player"
date: 2026-09-04
categories: music mathematics signal-processing
tags: [least-squares, fourier, music, midi, musicxml, piano, signal-processing, synthesis, web-audio, javascript]
math: false
---

Well, we made these fits and listened to the notes so the natural next step is to listen to a song with it!

I played around with this a bit.  To be honest, hearing some of these made me laugh with surprise the first few times I heard them.  You can genuinely hear the song.  Dramamine is likely the hardest for me to parse through the cacophony.

I also added a "Can be played by hand" option, which is not really what it says. This presumes that a single note can be played by hand, but when there are multiple voices in a song, it could not be played by a single person.  More like multiple people at multiple pianos playing each one.

After the initial fun and novelty wore off, to be honest it sounds awful. It's muddy and many of the notes use really low notes on the piano.  It does not resonate as music and comes across as discordant noise much of the time.  Single notes are overwhelming to listen to and two notes together can become totally unparseable by the ear.

I don't want to stop pulling on this thread yet. The conclusion is that pure mathematical fits are suboptimal when it comes to playing a note without playing that note.  We need some principled way to move forward that can keep the idea but make the notes sound more musical.  I will examine this in a later post.

For now, try it yourself, have fun and listen to some music not played.

## Try it

{% include 2026-09-01-score-player/score_player.html %}

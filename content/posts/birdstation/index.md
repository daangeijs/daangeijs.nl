---
title: "A bird detector from a drawer of old electronics"
date: 2026-11-20T09:00:00+01:00
draft: true

tags:
- homeautomation
- birds
- raspberrypi
- kubernetes

summary: "A Raspberry Pi 2 from 2015, an old headset and a PoE splitter from the attic: a 24/7 bird listening station that buys nothing new, because the Pi only streams audio and my home cluster does the listening."
---
There is a long-eared owl living in my backyard. I know, because I hear it. I wanted a machine that hears it too, and every other bird that passes, day and night, and tells me what it was.

That idea is not new. BirdNET, a neural network from the Cornell Lab of Ornithology and Chemnitz University of Technology, recognises thousands of species by sound, and projects like BirdNET-Pi and its forks turn a Raspberry Pi into a 24/7 bird listening station. The catch: they run the analysis on the device. You end up with a Raspberry Pi 4 or 5, a decent microphone, maybe a fan, and a few hundred euros spent before the first robin.

So I gave myself one rule: **buy nothing new.** Whatever this would become had to come out of the boxes of old electronics that every tinkerer has in the attic.

## The junk pile

This is what I found:

- A **Raspberry Pi 2 Model B** from 2015. Four slow ARM cores, 1 GB of RAM, no Wi-Fi, no Bluetooth. It cannot run the modern BirdNET models at all.
- A **PoE splitter**: Ethernet in, micro-USB power out. One cable for power and network.
- An old **Logitech USB headset**. A voice mic, not a nature recording mic.
- A **32 GB microSD card** that still had a Proxmox installer on it.
<!-- TODO Daan: add the EM272 microphone and Sound Blaster Play! 3 here, and Sound Blaster Play! 3, from a box or bought? -->

On paper, the Pi 2 is the problem. BirdNET-Go's own documentation calls it "marginal and RAM-limited". But the same paragraph has the hint that made the whole project work: it "works well as a dedicated RTSP mic feeding a Pi 4/5 that does the inference".

## Split the ear from the brain

I don't have a Pi 5. What I do have is a small Kubernetes cluster at home, running things like photo backup and document management, with a 16-core mini PC that is bored most of the day. So the design became:

- The **Pi is the ear**: it captures audio and puts it on the network as a stream. Nothing else.
- The **cluster is the brain**: it pulls the stream, runs BirdNET, keeps the detections and audio clips, and tells Home Assistant what it heard.

The Pi runs no code I wrote. ffmpeg reads the microphone, and MediaMTX, a small media server, serves the audio as an RTSP stream, the same protocol IP cameras use. The Pi doesn't even know the cluster exists. If the stream drops, the cluster simply reconnects.

The audio goes over the network uncompressed: 16-bit, 48 kHz, mono. That is about 770 kbit/s, nothing for a home network, and it matters: compressed formats like MP3 save bandwidth by throwing away high frequencies, and that is exactly where much of birdsong lives.

Because the Pi only copies samples and never encodes or analyses anything, the 2015 board barely notices. ffmpeg takes about a quarter of one core, the whole board sits at a load of 1 out of 4, uses 147 MB of its 920 MB of RAM, and stays at 32 °C.

That is the point I want to make: **the heavy compute does not have to live where the sensor is.** If you already have a home server, a NAS or an old laptop doing nothing, your sensor can be the cheapest thing in the drawer.

## Old hardware, outdoor life

Two practical problems with putting an old Pi in the garden.

**Power cuts.** Someone unplugs the cable, the switch reboots, a fuse trips. A Raspberry Pi that loses power while writing to its SD card can corrupt it, and that is how most of them die. The fix is to make the system read-only: the OS runs from an overlay in RAM, logs live in RAM, there is no swap. Nothing is written to the card during normal use, so you can pull the plug any time.
<!-- TODO Daan: power-cut test result. -->

**Changing microphones.** The headset is a stopgap, and I wanted the real microphone to be a swap, not a rebuild. The setup picks the sound card by name instead of by number and automatically chooses the best sample rate it supports. The headset surprised me there: it captures natively at 48 kHz.

Everything is scripted. One script writes the SD card, with safety checks so it can never touch the laptop's own disk, and an Ansible playbook does the rest. If the card ever dies, a new one is fifteen minutes away.

## What it hears

On the cluster runs BirdNET-Go, an open-source rewrite of BirdNET-Pi. It has a web interface with a live spectrogram, a list of detections with audio clips, and an MQTT connection to Home Assistant, where a "BirdNET-Go" device shows the last species, its scientific name and the confidence. That makes it easy to build things like a phone notification when a kingfisher or an owl is heard.

The first real detection came the same afternoon: a great tit, at 97 to 99 percent confidence.

I run two models side by side on the same stream: the classic BirdNET v2.4 and the newer v3.0 with a regional Central European model. When both hear the same bird, the detections are merged and the best confidence wins. Two models agreeing is a good sign. v3.0 also knows frogs, grasshoppers, crickets and bats, so the bird station is quietly becoming a garden sound station. On the cluster, both models together cost about one and a half CPU cores. On the Pi 2 that would have been impossible.

Privacy matters with an outdoor mic, because it can pick up neighbours and people walking by. Clips are only saved around detections, never as continuous recordings, they are deleted after two weeks, and a speech detector discards any clip with human voices.

## Why it couldn't hear an ortolan

This turned out to be the most interesting part of the project.

BirdNET knows about 6,500 species, but it doesn't listen for all of them. First, a "range filter" picks the species that are plausible for your location and the current week. In Renkum in November, that was 173 species. Everything else is ignored, no matter how clearly it sings.

I wondered about night migrants. On autumn nights thousands of birds fly over, calling to stay in contact, and a microphone pointed at the sky can pick them up. The ortolan bunting is a classic example. So I asked the range filter for its score in every week of the year. The highest was 0.0011. The cut-off is 0.01. **An ortolan could fly right over the microphone and the system would never report it.** The same for the nightjar, which breeds on the heath a few kilometres from here.

So I checked the model against reality. waarneming.nl, the Dutch observation platform, has five years of records for the Renkum area: 17,333 bird observations of 181 species. The long-eared owl in my backyard? The range filter would have blocked it in 51 of its 69 recorded sightings.

And reality under-reports too: waarneming.nl hides observations of sensitive species, such as owls and nesting raptors, to protect them. The birds you would most like to catch are exactly the ones the data hides.

The fix became a hand-made species list in three layers:

1. **Always allowed**: species seen locally that the model under-rates, species that waarneming.nl hides, all Dutch owls, and night migrants. 38 species.
2. **Rarities**: species that are possible inland but rarely or never reported here. Catching those is the whole fun of a device that listens 24/7, but rare species are also where BirdNET's false positives live. So they are allowed, but need 85 percent confidence instead of 70. 52 species.
3. **Only Dutch species**: everything checked against its status on waarneming.nl. That removed, for example, the Ural owl and the great grey owl, which only occur here as escaped birds.

The newer range model added its own surprises: it rated an American red squirrel and a trumpeter swan as just plausible enough for a Dutch village (0.0101 and 0.0108, against a cut-off of 0.01). Those went on an exclude list by hand.

## What the headset hears

A minute of audio from the live stream told me a lot:

- No clipping, plenty of headroom.
- Most of the energy is low rumble from wind, traffic and the house, below 150 Hz. No bird lives there, so a high-pass filter in BirdNET-Go is free.
- A faint whine at 16 to 19 kHz, probably electrical noise from the USB or the PoE splitter. BirdNET only looks up to 15 kHz, so it doesn't matter.
- The weak link is the headset itself. Faint flight calls high in the night sky need a real microphone.

## Next: into the bird house

It works, but it is still a Pi with a cable. The next step is to shrink it and polish it until the whole thing fits inside a bird house. There are power outlets in my garden but no network cables, so it will run on Wi-Fi instead of PoE. 770 kbit/s is easy for Wi-Fi, and the cluster already reconnects when the stream drops.

The Pi 2 has no Wi-Fi, so that is the next junk-box hunt: a USB Wi-Fi dongle, a newer Pi, or an ESP32 microcontroller with a tiny digital microphone as an even smaller streamer. The cluster side is already prepared for more devices pushing their streams to it, including a nest-box camera I would like to add.

And bats? They call far above human hearing and need a microphone that samples at 192 kHz or more. That would break the rule, so maybe that's a story for another time.

<!-- TODO Daan: closing paragraph, ideally with a nice detection from the first nights outside. -->

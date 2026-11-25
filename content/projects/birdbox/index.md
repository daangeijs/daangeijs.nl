---
title: "The birdbox: a garden that reports what lives in it"
summary: "A 2015 Raspberry Pi in a weatherproof box in the garden that streams bird sound to my home cluster, where BirdNET names every bird it hears, day and night."
description: "The birdbox: a Raspberry Pi 2 audio streamer in the garden feeding BirdNET-Go on a home Kubernetes cluster, built from old hardware without buying anything new."
role: "Builder, only listener"
timeframe: "2026"
thumbnail: ./birdbox.jpg
weight: 18
tags:
  - homeautomation
  - birds
  - raspberrypi
  - kubernetes
draft: true
---

A white box on a shelf in the garden, with a microphone outside and a 2015 Raspberry Pi inside. It listens around the clock and tells me which birds were singing, including the long-eared owl that lives behind the house.

## How it works

- **The Pi is only the ear.** ffmpeg reads the microphone and MediaMTX serves it as an uncompressed RTSP stream (16-bit, 48 kHz, mono). The Pi runs no code of my own and uses about a quarter of one core.
- **The cluster is the brain.** BirdNET-Go runs on my home Kubernetes cluster, pulls the stream, and keeps detections with short audio clips. Home Assistant gets the last species over MQTT.
- **Built to be unplugged.** A read-only system with logs in RAM, so a power cut can't corrupt the SD card.
- **Nothing new bought.** The Pi, the PoE splitter, an old USB headset as a stopgap microphone and the SD card all came from boxes in the attic.

## Tuned on real detections

BirdNET only listens for species that are plausible for the place and the week. I checked that filter against five years of local observations from waarneming.nl and a few hundred of my own reviewed detections, then kept the newer BirdNET v3.0 model alone at a 70% threshold, and let a short list of local rarities through with a stricter bar.

The full story is in [A bird detector from a drawer of old electronics](/posts/birdstation/).

<!-- TODO Daan: check the numbers and the owl line; add a photo of the microphone outside if you have one. -->

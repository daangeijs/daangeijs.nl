---
title: "The birdbox: a garden that reports what lives in it"
summary: "A 2015 Raspberry Pi in a weatherproof box in the garden that listens for birds and, with an old ESP32, collects footage from cheap trail cameras. Everything lands on my home server: BirdNET names the birds it hears, Robin the animals on camera."
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

A white box on a shelf in the garden, with a microphone outside, a 2015 Raspberry Pi inside and a small antenna sticking out. It listens around the clock and tells me which birds were singing. Since the antenna, it also empties the trail cameras in the garden.

## How it works

- **The Pi is only the ear.** ffmpeg reads the microphone and MediaMTX serves it as an uncompressed RTSP stream (16-bit, 48 kHz, mono). The Pi runs no code of my own and uses about a quarter of one core.
- **The cluster is the brain.** BirdNET-Go runs on my home Kubernetes cluster, pulls the stream, and keeps detections with short audio clips. Home Assistant gets the last species over MQTT.
- **Built to be unplugged.** A read-only system with logs in RAM, so a power cut can't corrupt the SD card.
- **Nothing new bought.** The Pi, the PoE splitter, an old USB headset as a stopgap microphone and the SD card all came from boxes in the attic.

## Tuned on real detections

BirdNET only listens for species that are plausible for the place and the week. I checked that filter against five years of local observations from waarneming.nl and about 150 of my own reviewed detections, then kept the newer BirdNET v3.0 model alone at a 70% threshold, and let a short list of local rarities through with a stricter bar.

## Trail cameras without the app

A Denver WSW-8120 trail camera (USB-C, solar panel) only hands over its clips to a phone standing next to it. An old ESP32 on the Pi's USB now does that from the birdbox: it wakes the camera over Bluetooth, joins its hotspot and passes the packets to the Pi, which downloads the clips, deletes them from the camera and serves them to Robin.

- **Robin**, my multi wildlife camera app, decides when each camera is checked, pulls the clips and lets three models vote on the species (SpeciesNet, DeepFaune and Claude).
- **One dashboard** for every camera, with signal, battery, solar charging, temperature and free space, and a check-now button.
- **Settings from a distance**, like switching off the camera's own date stamp. Robin draws its own bar with the weather and the moon instead.

The stories: [A bird detector from a drawer of old electronics](/posts/birdstation/) and [The birdbox gets eyes](/posts/birdbox-trail-camera/).

<!-- TODO Daan: check the numbers. -->

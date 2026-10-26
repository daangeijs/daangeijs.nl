---
title: "HA Paper: a calm Home Assistant display"
summary: "Open-source firmware that turns a Xteink X4 Pro e-reader into an e-ink Home Assistant dashboard: energy, rooms and climate on a shelf, without a glowing screen."
description: "HA Paper: e-ink Home Assistant dashboard firmware for the Xteink X4 Pro, with QR sign-in, a web console, over-the-air updates with rollback and an API for scripts and agents."
role: "Product owner, only user"
timeframe: "2026"
repo: "daangeijs/ha-paper"
thumbnail: ./cover.png
weight: 15
tags:
  - homeautomation
  - esp32
  - e-ink
  - open source
draft: false
---

Home Assistant knows the energy price for the next hour, what the solar panels do and how warm every room is. To see it I had to pick up my phone or a tablet, which light up the room at night and have every other app one swipe away. HA Paper puts those numbers on an e-ink screen on a shelf, and nothing else.

<!-- TODO Daan: github.com/daangeijs/ha-paper must be public before this page goes live (the repo card and the links below point there). -->

<!-- IMAGE: photo of the X4 Pro on the shelf showing the Home page, Daan to add -->

## Why an e-reader

The usual route is a bare e-ink panel, an ESP32 board and a 3D-printed case. The Xteink X4 Pro is a 4.3-inch e-reader of about a hundred euros with all of that already done: an ESP32-S3 with 16 MB of flash and 8 MB of PSRAM, an 800 × 480 panel with touch, a front light, a battery, buttons and a real case. Its bootloader isn't locked, and the open-source [CrossPoint](https://github.com/crosspoint-reader/crosspoint-reader) reader firmware already runs on it. HA Paper uses CrossPoint's hardware library for the panel and touch drivers.

## What it does

- **Screens of tiles.** After you link it, the display builds its screens from your own Home Assistant: the energy dashboard, rooms, lights, climate. Navigation uses the fast e-ink waveform; a tap shows the next page in about a second.
- **Setup from a web page.** Flash it from Chrome or Edge over USB. The flasher checks that the chip isn't locked, saves the full 16 MB stock firmware to a file so you can go back, leaves the factory panel calibration alone and sends your Wi-Fi details over the same cable with [Improv](https://www.improv-wifi.com/serial/). Without the cable you pick a network on the display or join a setup hotspot from your phone.
- **Sign in with a QR code.** No long-lived token to paste. Scan the code on the display and log in with your normal Home Assistant account through its own OAuth sign-in. The display doesn't need a public hostname.
- **A web console on the device.** Edit screens and tiles with live values next to them, change settings, edit the YAML directly, create API tokens. Home Assistant admins get full access, other users a view-only console.
- **Updates that undo themselves.** A new image is checked against the SHA-256 in the release manifest and written to the second of two app slots. It is kept after a minute online. If it crashes, hangs (12 minutes) or can't get online (10 minutes), the device goes back to the previous image.
- **An API for scripts and agents.** Read or write tokens. `/status`, `/diagnostics` and `/logs` show the last eight boots and why they happened, the heap low point, a 64 KB log ring and the log from before the last reset. Remote input and a framebuffer endpoint are off by default.

![The Solar and battery page, as the framebuffer of the real X4 Pro](solar-battery.png)

## Status

The first public beta is v0.2.0-beta.1, on [GitHub](https://github.com/daangeijs/ha-paper). It runs in my living room. Battery life isn't measured yet: about 50 days in glance mode is an estimate from [TRMNL](https://usetrmnl.com)'s numbers. The power button can still switch the device off so hard that only USB brings it back, and the browser flasher hasn't run against a real X4 yet.

<!-- TODO Daan: update the status against the board on the day you publish (#225 power button, #227 HTTP stall, flasher on hardware). -->

I wrote almost none of the code. Claude Code built it as a small team of agents, mostly in emulators before the device arrived. That story is in [Handing the build to a team of agents](/posts/handing-the-build-to-agents/).

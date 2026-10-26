---
title: "HA Paper: e-ink firmware for a device I didn't own yet"
date: 2026-10-27T09:00:00+01:00
draft: true

tags:
- homeautomation
- esp32
- ai

cover:
    image: "cover.png"
    alt: "The Home page of HA Paper as the X4 Pro's framebuffer: a black clock card and tiles for inside temperature, solar, home use, home battery, grid and outside temperature"

summary: "HA Paper turns a Xteink X4 Pro e-reader into a calm Home Assistant display. I wrote almost none of the code. Claude Code ran the project as a small team of agents, and most of the firmware was tested in emulators before the device arrived. This is what worked, and what only the real hardware could show."
---
I have wanted an e-ink display for Home Assistant for years. Energy prices, solar, the heating per room, a clock. Something that hangs on the wall or sits on a shelf and doesn't glow at you in the evening. Every time I looked into it I ended up at the same place: a bare panel, an ESP32 board, and a 3D-printed case. That is a nice weekend project. It is not an object I want in my living room.

<!-- TODO Daan: the 3D-printed-case reason comes from your brief, not from the project docs. Confirm or rephrase in your own words. -->

So two weeks ago I started HA Paper: firmware that turns an Xteink X4 Pro e-reader into a Home Assistant dashboard. The first public beta is v0.2.0-beta.1, and the code is at [github.com/daangeijs/ha-paper](https://github.com/daangeijs/ha-paper).

<!-- TODO Daan: check the repo URL and the beta tag are live before publishing. -->

I wrote almost none of that code. Claude Code did, organised as a small team of agents, and I acted as the product owner and the only user. That turned out to be the more interesting part of the project, so most of this post is about how that worked.

<!-- IMAGE: photo of the X4 Pro on the shelf showing the Home page, Daan to add -->

### Why an e-reader

The X4 Pro is a 4.3-inch e-reader that costs about a hundred euros. Inside is an ESP32-S3 with 16 MB of flash and 8 MB of PSRAM, an 800 × 480 e-ink panel with a touch controller, a front light and a battery. It is a finished product: a proper case, buttons, a magnetic USB-C cable. It looks like something you bought on purpose.

The part that makes it usable is that the bootloader isn't locked. An open-source reader firmware, [CrossPoint](https://github.com/crosspoint-reader/crosspoint-reader), already runs on it, and its hardware library, freeink-sdk, has a pin map and display drivers that its authors checked on real devices. HA Paper uses that library as a submodule. We wrote none of the drivers for the pins, the panel controllers or the touch chip ourselves.

### My role: product owner and user

On day three I set up the project the way I would set up a small team. Every piece of work is a GitHub issue. A GitHub Project board holds them with a status, a priority and a size, and the milestones are the releases. I wrote down what the thing is for, and every plan gets judged against that list: easy to install, easy to set up, easy to configure, a connection that stays up, long battery life, and a calm object that looks good in the house.

The main Claude Code session is the coordinator. It owns the board and the plan, and it hands work to subagents, each with one job:

- **Discovery agents** read other people's code (CrossPoint, TRMNL, Home Assistant's own OAuth implementation, datasheets) or dig into a stuck issue, and post their findings on the issue.
- **Builders** take one issue each, in their own git worktree, with their own pair of ports for the emulator so four or five can test at the same time without testing each other's firmware.
- **Reviewers** audit merged work for security, concurrency and flasher safety before a release. In the first audit, one of eleven findings was real; the coordinator checks each one before acting.
- **A council** of three strategy agents (product, onboarding, visual design) proposes themes and issues before each sprint. The coordinator decides, and anything that is my call gets a `decision` label and a question instead of a guess.
- **A writer** keeps a build log of what happened, in the repo.

Every change reaches `main` through a pull request. Builders leave their work uncommitted and report back; the coordinator commits, opens the PR, runs the full test list, and merges. Across two weeks that came to 134 issues and 88 merged pull requests.

My part was smaller than it sounds and more important than I expected. I am the user. Anything with a visible change gets a `verify` label and a "how to verify" block, and before each release I get one checklist of at most ten items to try on a test device. Most of my useful contributions were short. When the coordinator built "roll back a firmware update if it can't reach Home Assistant", I pointed out that updates come from GitHub, so a Home Assistant outage should never undo a good update. When the default screens turned out to be my own house, with my meters and my rooms, I asked that a fresh display builds its screens from the user's own Home Assistant instead.

### Building without the device

The device arrived two weeks after the first commit. Everything before that ran in emulators, and that shaped the project more than anything else.

I started with a design: an interactive mock-up made in Claude Design with the device screen, a web console and a panel of "what if" switches (never linked, Home Assistant token revoked, a broken firmware download). It became the specification. Its config parser generated test cases, and the C++ firmware has to give the same answer for each: same line number, same error message.

The second was the real firmware in Espressif's QEMU fork, which emulates the ESP32-S3 on a Mac. It doesn't emulate Wi-Fi or the e-ink panel, but it does emulate the CPU, flash, PSRAM and an Ethernet controller. That is enough to run the web server, the API, the Home Assistant connection and firmware updates against a fake Home Assistant: OAuth sign-in, the WebSocket, TLS, and faults on purpose. The contract suite that runs against it is now 88 tests.

It found real bugs that unit tests never would have. Firmware rollback had never worked: the function that tells Arduino to wait before trusting a new image was declared in C++ instead of C, the linker never matched it, and every update was accepted on first boot. The fix was two words, `extern "C"`. Home Assistant sends the entity list as one 74 KB string, and the JSON library on a 32-bit chip caps a string at 65,535 bytes, so a big house showed an empty list.

On top of that runs an endurance harness: the firmware in QEMU for a day, with faults injected (Home Assistant restarts, dropped WebSockets, a clock jump of two hours, link drops). The run before v0.1.0-alpha.6 did 1440 polls with 273 injected faults, recovered from all of them within 94 seconds, and the heap stayed flat. We shipped six alpha releases before the device existed.

### The night the device arrived

The X4 Pro came in at midnight on 26 October. The plan was boring on purpose: check that the chip isn't locked, back up the full 16 MB of stock firmware (53 seconds, checked four ways), flash. It booted, joined Wi-Fi and linked to my Home Assistant on the first try. Two weeks of emulators had produced firmware that worked on first flash.

Then I used it for a while and wrote down what I saw. None of it had shown up in QEMU, because QEMU has no panel and no radio:

- **Every page change flashed three or four times.** Navigation used the full refresh waveform. In 23 minutes of use it did 77 full refreshes.
- **A clock tick turned the screen black.** The panel controller has two RAM planes and compares them on every partial refresh, even for a one-line window. The driver left gray data in one of them, so a clock update drove every pixel where the planes differed.
- **The internal heap fell to 10.9 KB.** QEMU had shown about 117 KB. The Wi-Fi driver asks for 64 receive and transmit buffers in internal RAM, and QEMU's Ethernet card never does.
- **Every boot showed the setup screens**, three full refreshes before Home. The real panel's boot refresh takes longer than a 1.6-second timer, so the app decided the display was new before the network task had loaded the stored Wi-Fi state.
- **The text was too small.** 14 px on this panel is about 1.1 mm. The browser preview scales the image up, and for two weeks that hid it.

I went to bed and left the device on USB. The coordinator flashed each fix overnight, read the device's log, and only then merged the pull request. By the morning five of the six were merged. Navigation uses the fast waveform and only every tenth page change does a clean refresh. The heap low point went from 7.6 KB to 23.9 KB. The device boots straight to Home.

One thing was still slow. A tap took about 1.7 seconds before the page started to draw, and the drawing itself took seconds more. A discovery agent found why: the rounded corners of every card were computed with `double` math per pixel, and the ESP32-S3's FPU only does single precision. Every one of those operations became a software call. The Home page needed 7.8 seconds just to render. On my Mac the same code takes 2 ms, so no test had noticed. A builder rewrote the drawing code in integers, with all 408 host renders byte-identical to before. Home now renders in 262 ms, and a tap shows the new page in about one second, most of it the panel's own waveform.

To measure that, the coordinator needed to tap the device without me. So I asked for an API endpoint that injects input and one that returns the framebuffer, and from then on it paged through the screens itself and read the timings from the log. My verdict after trying it: "speed is now perfect".

![The Solar and battery page, as the framebuffer of the real X4 Pro](solar-battery.png)

The screenshots in this post are that framebuffer: 800 × 480 pixels, four gray levels, exactly what is on the glass.

### What it does

**Setup.** You flash it from a web page in Chrome or Edge over USB. The page checks that the chip isn't locked, reads the full stock backup to a file so you can always go back, and installs without touching the partition where the factory stored the panel calibration. It then sends your Wi-Fi name and password over the same cable with [Improv](https://www.improv-wifi.com/serial/). Without the cable you can pick a network on the display, or join a setup hotspot from your phone.

**Sign-in.** Most ESP32 Home Assistant projects ask you to paste a long-lived token. HA Paper shows a QR code and its address on the display. Scan it with your phone, press *Sign in with Home Assistant*, and log in with your normal account. It is a regular OAuth sign-in, the same flow Home Assistant's own apps use. A discovery agent read Home Assistant's source first to check this would work without the device needing its own public hostname. After the first link, the display builds its screens from what your Home Assistant has: energy dashboard, rooms, lights, climate.

<!-- IMAGE: photo of the display showing the sign-in QR code, Daan to add -->

**The web console.** The device serves its own web console. You edit screens and tiles with live values next to them, change device settings, edit the YAML directly if you prefer, and create API tokens. A Home Assistant admin gets full access; any other user gets a view-only console.

<!-- IMAGE: screenshot of the web console screen editor, Daan to add (check no entity names or hostname are visible) -->

**Updates.** Firmware goes in over the API: upload an image, the device checks it against the SHA-256 in the release manifest, writes it to the other of two app slots, and boots it. A new image is kept once it has run for a minute with a network connection. If it crashes or reboots before that, the bootloader goes back to the old one. If it hangs, it restarts itself after 12 minutes and rolls back. If it can't get online within ten minutes, it rolls back too, because an image that can't get online can never be fixed over the air. Once the repository is public, the device can check GitHub releases on its own.

**An API for agents.** I wanted the device to be something an agent can work with, not only a person. API tokens are either read or write. `/status`, `/diagnostics` and `/logs` say what the device is doing: the last eight boots and why they happened, the heap low point, a 64 KB log ring in PSRAM, and the tail of the log from before the last reset. The remote input and framebuffer endpoints are off by default and switched on in the settings. The coordinator used exactly these to debug and measure the real device overnight. That loop, an agent flashing a device on my desk, reading its log, tapping it and looking at its screen, is the part of this project I didn't expect to work as well as it did.

![The page overview before (left) and after (right) the larger text sizes](text-size.png)

### What is still rough

- **Battery life is not measured.** On paper, glance mode (deep sleep, wake every 15 minutes) gets about 50 days, but that uses [TRMNL](https://usetrmnl.com)'s published numbers, not ours. On the real device, on battery, it has not been tested yet.
- **The power button cuts the power.** Pressing it turned the device off in a way only plugging in USB could undo. That is open and has the highest priority.
- **One overnight soak stopped answering.** The device stopped responding over HTTP for 55 minutes without resetting itself. Not explained yet.
- **Text sizes just changed.** I approved the larger sizes on the device for the beta. They need a few days of living with it.
- **The browser flasher has not run against a real X4 yet.** So far only the backup and flash from the repo have.

<!-- TODO Daan: update this list against the board on the day you publish (#225 power button, #227 HTTP stall, #205 text sizes, flasher on hardware). -->

### What I learned

The emulators were worth every hour. They gave me firmware that booted, linked and drew the right things on the first flash. They could not tell me how it looked or how it felt, and those are exactly the things the first night on hardware found.

The agent team mostly needed the same things a human team needs: one place for the plan, small pieces of work, someone who decides, and a user who actually uses the thing. The difference is the pace. Bugs I found at midnight were flashed, checked and merged by the time I woke up.

This post was drafted by the project's writer agent from its own build log, and edited by me.

<!-- TODO Daan: confirm this sentence matches how you edited the post, or rewrite it. -->

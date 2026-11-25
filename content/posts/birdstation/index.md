---
title: "A bird detector from a drawer of old electronics"
date: 2026-11-20T09:00:00+01:00
draft: true

tags:
- homeautomation
- birds
- raspberrypi
- kubernetes

cover:
    image: "birdnet-dashboard.jpg"
    alt: "The BirdNET-Go dashboard for 25 November: thirteen species by hour, with redwing, blue tit, blackbird, jackdaw, chaffinch, great tit and robin heard most"

summary: "A Raspberry Pi 2 from 2015, an old headset and a PoE splitter from the attic: a 24/7 bird listening station that buys nothing new, because the Pi only streams audio and my home cluster does the listening."
---
There is a long-eared owl living behind my house. I know, because I hear it. I wanted a machine that hears it too, and every other bird that passes, day and night, and tells me what it was.

That idea isn't new. [BirdNET](https://birdnet.cornell.edu/), a neural network from the Cornell Lab of Ornithology and Chemnitz University of Technology, recognises thousands of species by sound, and projects like BirdNET-Pi and the lovely [Avian Visitors](https://theodore.net/projects/AvianVisitors/) turn a Raspberry Pi into a bird listening station. But they all run the analysis on the Pi itself, so you need a Raspberry Pi 4 or 5, a decent microphone, maybe a fan, and a few hundred euros before you've heard a single robin.

So I gave myself a rule: buy nothing new. Whatever this became had to come out of the boxes of old electronics every tinkerer has in the attic.

### The junk pile

- A **Raspberry Pi 2 Model B** from 2015. Four slow ARM cores, 1 GB of RAM, no Wi-Fi, no Bluetooth. It can't run the modern BirdNET models at all.
- A **PoE splitter**: network cable in, micro-USB power out. One cable for both.
- A **Logitech USB headset** that came free with Ghost Recon on the PlayStation 2. I don't think I ever used it for the game. During covid it became my favourite headset for calls, until a webcam with a built-in mic made it redundant. A voice mic, not exactly a nature recording setup, but it has had a long life and here was another job for it.
- A **32 GB microSD card** that still had a Proxmox installer on it.

<!-- TODO Daan: the EM272 microphone and Sound Blaster Play! 3, from a box or bought? That decides how strict the "buy nothing" line is. -->

On paper, the Pi 2 is the problem. BirdNET-Go's own documentation calls it "marginal and RAM-limited". But the same paragraph has the hint that made the whole thing work: it "works well as a dedicated RTSP mic feeding a Pi 4/5 that does the inference".

I don't have a Pi 5. I do have a home server that's bored most of the day.

### An ear and a brain

It's a small Kubernetes cluster for things like photo backup and documents, and one of its nodes is a 16-core mini PC. So the Pi became the ear and the cluster the brain. The Pi reads the microphone and puts the sound on the network as a stream, nothing else. The cluster pulls that stream, runs BirdNET, keeps the detections and short audio clips, and tells Home Assistant what it heard.

The Pi runs no code I wrote. ffmpeg reads the microphone, and MediaMTX, a tiny media server, serves the audio as an RTSP stream, the same protocol IP cameras use. The Pi doesn't even know the cluster exists. If the stream drops, the cluster just reconnects.

The audio goes over the wire uncompressed: 16-bit, 48 kHz, mono. That's about 770 kbit/s, which is nothing for a home network, and it matters. MP3 and friends save bandwidth by throwing away the high frequencies, and that's exactly where a lot of birdsong lives.

Because the Pi only copies samples and never encodes or analyses anything, the 2015 board barely notices. ffmpeg takes about a quarter of one core, the load sits around 1 out of 4, it uses 147 MB of its 920 MB of RAM, and it stays at 32 °C.

That's what I like most about it. The heavy work doesn't have to happen where the microphone is, so if you have a NAS or an old laptop doing nothing, the sensor can be the cheapest thing in the drawer.

### Built to be unplugged

Power cuts are the first problem. Someone pulls the cable, the switch reboots, a fuse trips. A Pi that loses power while writing to its SD card can corrupt it, and that's how most of them die. So the system is read-only: the OS runs from an overlay in RAM, logs live in RAM, and there's no swap. Nothing gets written to the card in normal use, so you can pull the plug whenever you like.

<!-- TODO Daan: result of the power-cut test. -->

The headset is a stopgap, and I wanted to plug in a real microphone later without rebuilding anything. The setup picks the sound card by name instead of by number and picks the best sample rate it supports. The headset surprised me there: it records natively at 48 kHz. A minute of the live stream showed no clipping, low rumble from wind and traffic, and a 50 Hz hum from its cable. No bird lives down there, so BirdNET-Go's high-pass filter takes that out for free. The real limit is the headset itself: faint flight calls high in the night sky need a proper microphone.

Everything is scripted. One script writes the SD card, with checks so it can never touch the laptop's own disk, and an Ansible playbook does the rest. If the card ever dies, a new one is fifteen minutes away.

It now lives in a white weatherproof box on a shelf in the garden, on its one network cable. I've started calling it the birdbox.

![The white weatherproof box on a wooden shelf against the brick wall, a network cable going into one of its cable glands and an antenna that came later](birdbox.jpg)

### What it hears

On the cluster runs [BirdNET-Go](https://github.com/tphakala/birdnet-go), an open-source rewrite of BirdNET-Pi. It has a web interface with a live spectrogram, a list of detections with their audio clips, and an MQTT connection to Home Assistant, where a "BirdNET-Go" device shows the last species, its scientific name and how sure it is. That makes it easy to get a notification on my phone when an owl or a kingfisher is heard.

The first real detection came the same afternoon: a great tit, at 97 to 99%.

![The BirdNET-Go dashboard for one day: species down the side, hours across, with the counts per hour, redwing, blue tit and blackbird busiest in the morning](birdnet-dashboard.jpg)

A microphone in the garden also hears the neighbours and anyone walking past. So clips are only saved around a detection, never as a continuous recording, they're deleted after two weeks, and a speech detector throws away any clip with a human voice in it.

### Two models walk into a garden

BirdNET comes in two flavours: the classic v2.4 and the newer v3.0 with a regional model for Central Europe. At first I ran both on the same stream and let them merge their detections. Two models agreeing sounded like a good sign.

Then I went through 156 detections by hand and marked each one right or wrong. Of the ones only v2.4 heard, 8% were right. Of the ones only v3.0 heard, 60% were right, and 92% of those it was at least 70% sure about. So v2.4 went out, v3.0 stays alone at a 70% threshold, and the cluster saves a CPU core.

v3.0 also knows frogs, grasshoppers, crickets and bats, so the bird station is slowly becoming a garden sound station.

### Why it couldn't hear an ortolan

BirdNET knows about 6,500 species, but it doesn't listen for all of them. A "range filter" first picks the species that are plausible for your location and the current week. Everything else is ignored, no matter how clearly it sings.

I was curious about night migrants. On autumn nights thousands of birds fly over, calling to keep in touch, and a microphone pointed at the sky can pick them up. The ortolan bunting is a classic one. So I asked the range filter for its score in every week of the year. The highest was 0.0011, and the cut-off was 0.01. An ortolan could fly right over the microphone and the system would never say so. The same went for the nightjar, which breeds on the heath a few kilometres away.

So I checked the filter against reality. waarneming.nl, the Dutch observation platform, has five years of records for the Renkum area: 17,333 bird observations of 181 species. Even the long-eared owl behind my house would have been blocked in 51 of its 69 recorded sightings.

And reality under-reports too. waarneming.nl hides observations of sensitive species like owls and nesting raptors to protect them, so the birds you'd most like to catch are exactly the ones the data hides.

The fix was the newer range model with a different cut-off, chosen so it only blocks 6 of those local observations, all out of season. On top of that, a short list of 16 Dutch rarities that the model never lets through are allowed anyway, but need 85% confidence instead of 70%. Catching a rarity is the whole fun of a device that listens day and night, but that's also where BirdNET makes most of its mistakes.

The range model had its own surprises: it thought an American red squirrel and a trumpeter swan were just plausible enough for a Dutch village. Those went on an exclude list by hand.

### So far

On a grey Wednesday in November it heard thirteen species, from redwings passing through to the robin that walked up to a trail camera that same morning.

<!-- TODO Daan: has it heard the long-eared owl by now? If so, that's the line to end on. -->

It didn't stay a bird station for long, though. A cheap trail camera moved in next to it, and an old ESP32 in the same box now empties that camera too. That's [the next story](/posts/birdbox-trail-camera/).

<!-- TODO Daan: mention that an AI assistant did much of the setup, or keep it about the hardware? -->

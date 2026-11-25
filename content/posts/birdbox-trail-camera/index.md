---
title: "The birdbox gets eyes"
date: 2026-11-25T18:00:00+01:00
draft: true

tags:
- homeautomation
- esp32
- birds
- raspberrypi

cover:
    image: "robin.jpg"
    alt: "A robin with its face right in front of the trail camera lens, a brick wall and a wooden fence in the autumn garden behind it"

summary: "A cheap trail camera has none of the premium features: no app sync, no cloud, no remote status. An old ESP32 and the Raspberry Pi in my birdbox fixed that. Clips now come in by themselves, from any number of cameras, into one dashboard. The first visitor was a very curious robin."
---
A few weeks ago I turned a 2015 Raspberry Pi into a [bird listening station](/posts/birdstation/). It sits in a weatherproof box on a shelf in the garden, streams what it hears to my home server, and that server tells me which birds were singing. I was pretty happy with that.

Then I bought a trail camera.

### A cheap camera with no tricks

I wanted to see what walks through the garden at night, and I explicitly went for the **Denver WSW-8120**. Not because it has great specs, but because it charges over USB-C and has a small solar panel on the front to keep itself going. I don't want to climb into the bushes every two weeks with a box of AA batteries. It's strapped to the apple tree now, which is why it's called Appelboom in the dashboard.

![The camouflage-green Denver trail camera strapped to the trunk of the apple tree, solar panel on top, autumn leaves on the grass around it](camera_mounted.jpg)

<!-- TODO Daan: what did it cost? A line like "for about €XX" fits here. -->

The catch is the usual one with cheap trail cameras. The expensive ones upload clips over 4G or Wi-Fi and show you their battery level in an app. This one records to an SD card, and if you want the footage you walk up to it with your phone and its app, TrailCam Go.

I never opened that app. Not once. And I didn't want to walk into the garden for every fox.

What gave me hope was a Hackaday story about someone who [found a hidden API in an abandoned trail camera](https://hackaday.com/2023/07/18/reverse-engineering-reveals-hidden-api-in-abandonware-trail-camera): wake it over Bluetooth, and it opens up. Mine turned out to be a close relative.

### How the camera talks

So instead of using the app, I took it apart. I pulled the Android APK of TrailCam Go and decompiled it: the Java side for the command numbers and the settings it can change, and its native library `libArLink.so` for the encryption key. Together with the work of people who had poked at the same family of cameras before, that told me exactly how a phone gets the clips off:

- The camera sleeps, but it keeps a little Bluetooth beacon on (mine calls itself `TC100_9B39`).
- The phone connects over Bluetooth and writes a magic value to it. The camera answers with the name and password of a Wi-Fi hotspot it just switched on.
- The phone joins that hotspot and talks to the camera over UDP, with commands as encrypted JSON: give me your status, list your files, send me this video, delete that one, change these settings.
- The moment Bluetooth disconnects, the hotspot goes off again.

Two projects saved me a lot of guessing: [TrailCamHub](https://github.com/HeikoGr/TrailCamHub), which wakes these cameras from an ESP32-S3, and [trailcam-automation](https://github.com/pwnb0t/trailcam-automation), a working Python client.

That last point turned out to be important. Whatever fetches the clips has to hold on to Bluetooth and sit on the camera's Wi-Fi at the same time.

### The ESP32 in the drawer

The birdbox Pi was out: a Pi 2 has no Wi-Fi and no Bluetooth. But I had an old **ESP32** dev board in a drawer, the same kind of board that already runs half of my house through Home Assistant. Bluetooth and Wi-Fi in one chip, for a few euros. Perfect, I thought: the ESP32 wakes the camera, grabs the clips and uploads them.

It wasn't perfect.

An ESP32 has one Wi-Fi radio. It is either on my home network or on the camera's hotspot, never both. So a clip has to fit in its memory while it switches back home. My board has about 0.5 MB of RAM, and a 10-second clip in 1080p is around 7 MB. Streaming the video through it to the house, which was my next idea, runs into the same wall: there is no second way out.

A bigger ESP32 with PSRAM and an SD card slot would have done it. But that meant buying something, and I liked the board I already had.

### …so we plugged it into the birdbox

Then the obvious thing clicked. The birdbox Pi is on a network cable, it's in the garden anyway, and it has USB ports. So the ESP32 went into the birdbox, on a USB cable to the Pi:

```
camera ──Bluetooth + Wi-Fi── ESP32 ──USB serial── Pi 2 ──network cable── home server
```

Now each one does what it's good at:

- The **ESP32** wakes the camera over Bluetooth, keeps the connection open, joins the camera's hotspot, and from then on just passes packets. Every UDP packet from the camera goes down the USB cable to the Pi, and every packet from the Pi goes back up to the camera. It doesn't understand a byte of it and doesn't have to store anything.
- The **Pi** speaks the camera's protocol over that cable as if it were a network: log in, list the files, download them, glue the video and audio into an MP4, check it, and delete it from the camera.

The cable runs at 921,600 baud, about 90 KB per second on paper. In practice a 10-second clip takes a bit over two minutes to come in. That sounds slow, but nobody is waiting for it. It's the middle of the night and the fox is long gone.

![The white weatherproof box on a wooden shelf against the brick wall, a black antenna sticking out of one of its cable glands and a network cable going into another, a bag of straw next to it](birdbox.jpg)

Which is also why I now call that box **the birdbox**. It holds the logic for listening to birds and for collecting footage from the garden. The only thing that gives the new job away is a small antenna poking out of the side.

### One dashboard for every camera

The Pi doesn't decide anything by itself. It has a small web API and waits until it's asked. The asking is done by Wildcam, a web app on my home server that I'd built earlier to sort trail camera footage:

- At the check hours, mostly at night, it asks the birdbox to start a session, waits until it's done, downloads the new clips and tells the Pi it can delete them. The camera's SD card never fills up.
- Every clip gets looked at by three models: Google's SpeciesNet, DeepFaune (trained on European trail camera footage) and Claude. They vote, and I can correct them. Once I've approved a clip, it stays approved.
- A side panel shows each camera: Bluetooth signal, battery, whether the sun is charging it, temperature, free space on the card, and when it was last and next checked. There's a "check now" button with a progress bar that shows which clip is coming in.

![The Wildcam timeline with the camera panel open: camera Appelboom in range, signal -67 dBm, battery 60% charging from the sun, 2 °C, 255 of 255 MB free, last check 14:00, next check 18:00](dashboard.jpg)

Adding a camera is a name and the address of its bridge. Another camera in the front garden is another ESP32 next to another Pi, and it lands in the same timeline. That's the part I like most: a cheap camera with no tricks now does what the expensive ones do, and it's not one camera, it's as many as I want, in one place.

### Settings from a distance

I still have no idea how big the battery in this camera is. It reports its charge in steps of 20%, and whether it's charging and whether that's the sun doing it, and that's all it says. But at least I can now see that without walking over, and I can change things too.

The camera burns a bar into every video: a Denver logo, a battery icon, the moon, the temperature and the date in American order. The command the app uses to change settings works for us as well, so the birdbox switched that bar off. Wildcam now draws its own bar over the video instead: the camera's name on the left, date and time in the middle (ticking along while the clip plays), and on the right the sun or the moon, the weather of that hour and the temperature. The weather comes from Open-Meteo, and the moon is the actual phase for that night. When I download a clip I can choose whether that bar gets burnt in.

### A tick in the bird recordings

One side effect I didn't see coming. The day the ESP32 moved into the birdbox, the bird stream got a faint high beep and little ticks in it.

The ESP32 was scanning for the camera's Bluetooth beacon almost all the time, and actively: every scan sends out requests. All that radio activity on the same USB power as the headset that serves as the microphone ended up in the audio. Now it listens for five seconds once a minute, and only listens, without sending anything. The beep is gone. There are still a few clicks, and the Pi logged an undervoltage when I plugged the ESP32 in, so a better power supply is next.

<!-- TODO Daan: check after the power supply / cable fix whether the clicks are gone, and update this paragraph. -->

### The first visitor

The first clip came in on 25 November at 10:37, while I was still busy mounting that antenna on the birdbox. Not a fox, not a marten. A robin, who walked straight up to the camera and looked right into the lens, as if checking who'd moved into its garden.

<video controls muted playsinline preload="metadata" poster="/posts/birdbox-trail-camera/roodborst-poster.jpg" src="/posts/birdbox-trail-camera/roodborst.mp4" style="width:100%;border-radius:8px"></video>

That clip still has the camera's own bar burnt in; it came in just before the birdbox switched it off.

The models said "bird, 98%". I filled in the rest.

And there you have it: a trail camera that couldn't do anything clever, an ESP32 that was too small for the job on its own, and a 2015 Raspberry Pi in a birdbox that ties it together. Next up is a second camera, and a real microphone for the birdbox, so it hears the birds better than it hears the ESP32.

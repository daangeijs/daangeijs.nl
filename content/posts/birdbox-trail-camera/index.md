---
title: "The birdbox gets eyes"
date: 2026-11-25T18:00:00+01:00
draft: false

tags:
- homeautomation
- esp32
- birds
- raspberrypi

cover:
    image: "robin.jpg"
    alt: "A robin with its face right in front of the trail camera lens, a brick wall and a wooden fence in the autumn garden behind it"

summary: "A cheap trail camera can't send you its clips. An old ESP32 and the Raspberry Pi in my birdbox now fetch them, from any number of cameras, into one dashboard. The first visitor was a very curious robin."
---
A few weeks ago I turned a 2015 Raspberry Pi into a [bird listening station](/posts/birdstation/). It sits in a weatherproof box on a shelf in the garden, streams what it hears to my home server, and that server tells me which birds were singing. I was pretty happy with that.

Then I bought a trail camera.

### Research first, then the camera

I wanted to see what moves through the garden at night. The previous owners once spotted a fox here, so you never know.

This time I did the research before buying anything. Cheap trail cameras record to an SD card, and if you want the footage you walk up to them with your phone and an app. The expensive ones upload over 4G or Wi-Fi. I wanted the cheap kind, but with the clips pulled out of it automatically, from the garden, by an ESP32.

That wasn't a crazy idea. Geek IT Guide had already shown in [Wifi BLE Trailcam Investigation](https://geekitguide.com/wifi-ble-trailcam-investigation-part-1/) that one of these cameras wakes up when you write `BT_KEY_ON` to it over Bluetooth, and then opens a Wi-Fi hotspot of its own ([Hackaday picked it up too](https://hackaday.com/2023/07/18/reverse-engineering-reveals-hidden-api-in-abandonware-trail-camera)). So I went looking for a camera in that family that also fit the garden, and ended up with the Denver WSW-8120. It charges over USB-C and has a small solar panel on the front, so I don't have to climb into the bushes every two weeks with a box of AA batteries. It's strapped to the apple tree now, which is why it's called Appelboom in the dashboard.

![The camouflage-green Denver trail camera strapped to the trunk of the apple tree, solar panel on top, autumn leaves on the grass around it](camera_mounted.jpg)

<!-- TODO Daan: what did it cost? A line like "for about €XX" fits here. -->

For the brain I had an old ESP32 dev board in a drawer, the same kind of board that already runs half my house through Home Assistant. Wi-Fi and Bluetooth on one chip, and another piece of old hardware with a new job. It looked like a good bet. (Spoiler: I didn't do my research quite as thoroughly here.)

### On the desk

Like with [HA Paper](/posts/handing-the-build-to-agents/), I wanted the software sorted out before anything went outside. Luckily the camera arrived the next day this time. I gave it some charge over USB-C, put it next to my MacBook, and started taking it apart from there.

I never opened its app, TrailCam Go. Instead I used REA (Reverse Engineer Anything) on the Android APK of that app, and this time it really worked: the Java side gave up the command numbers and every setting it can change, and its native library `libArLink.so` the encryption key. Together with what others had found on the same family of cameras, that told me how a phone gets the clips off:

- The camera sleeps, but keeps a little Bluetooth beacon on (mine calls itself `TC100_9B39`).
- The phone connects over Bluetooth and writes the wake-up value. The camera answers with the name and password of a Wi-Fi hotspot it just switched on.
- The phone joins that hotspot and talks to the camera over UDP, with commands as encrypted JSON: give me your status, list your files, send me this video, delete that one, change these settings.
- The moment Bluetooth disconnects, the hotspot goes off again.

<!-- TODO Daan: link to REA if there is a public page for it. -->

Two projects saved me a lot of guessing as well: [TrailCamHub](https://github.com/HeikoGr/TrailCamHub), which wakes these cameras from an ESP32-S3, and [trailcam-automation](https://github.com/pwnb0t/trailcam-automation), a working Python client.

By the end of it, the Mac could wake the camera, pull every video off it, and read and change all of its settings. All that was left was to put that on the ESP32 and hang it in the garden.

### The ESP32 in the drawer, again

That's where my research hadn't gone far enough. An ESP32 has one Wi-Fi radio, so it's either on my home network or on the camera's hotspot, never both. A clip has to sit somewhere while it switches back home, and my board has about 0.5 MB of RAM and no storage at all. A 10-second clip in 1080p is around 7 MB. Streaming the video through it to the house runs into the same wall: there's no second way out.

If only there was one device in my garden with a USB port to dump the files on, that was also on my network...

Right. The birdbox. The Pi is on a network cable, it's in the garden anyway, and it has USB ports. So the ESP32 went into the birdbox, on a USB cable to the Pi:

```
camera ──Bluetooth + Wi-Fi── ESP32 ──USB serial── Pi 2 ──network cable── home server
```

- The **ESP32** wakes the camera over Bluetooth, keeps the connection open, joins the camera's hotspot, and from then on just passes packets. Every UDP packet from the camera goes down the USB cable to the Pi, and every packet from the Pi goes back up. It doesn't understand a byte of it and doesn't store anything.
- The **Pi** speaks the camera's protocol over that cable as if it were a network: log in, list the files, download them, glue the video and audio into an MP4, check it, and delete it from the camera.

The cable runs at 921,600 baud, about 90 KB per second on paper. In practice a 10-second clip takes a bit over two minutes to come in. That sounds slow, but nobody's waiting. The checks run at night, mostly.

![The white weatherproof box on a wooden shelf against the brick wall, a black antenna sticking out of one of its cable glands and a network cable going into another, a bag of straw next to it](birdbox.jpg)

The only thing that gives away the birdbox's new job is a small antenna poking out of the side.

### One dashboard for every camera

The Pi doesn't decide anything by itself. It has a small web API and waits until it's asked. The asking is done by Wildcam, a web app on my home server that I'd built earlier to sort trail camera footage:

- At the check hours, mostly at night, it asks the birdbox to start a session, waits until it's done, downloads the new clips and tells the Pi it can delete them. The camera's SD card never fills up.
- Every clip gets looked at by three models: Google's SpeciesNet, DeepFaune (trained on European trail camera footage) and Claude. They vote, and I can correct them. Once I've approved a clip, it stays approved.
- A side panel shows each camera with its Bluetooth signal, battery, whether the sun is charging it, temperature, free space on the card, and when it was last and next checked. A "check now" button shows which clip is coming in.

![The Wildcam timeline with the camera panel open: camera Appelboom in range, signal -67 dBm, battery 60% charging from the sun, 2 °C, 255 of 255 MB free, last check 14:00, next check 18:00](dashboard.jpg)

Adding a camera is a name and the address of its bridge. A camera in the front garden would be another ESP32 next to another Pi, and its clips land in the same timeline. A cheap camera now does what the expensive ones do, and a second or third one just shows up next to it.

### Settings from a distance

I still have no idea how big the battery in this camera is. It reports its charge in steps of 20%, whether it's charging, and whether that's the sun doing it, and that's all it says. At least I can now see that without walking over, and I can change things too.

The camera burns a bar into every video: a Denver logo, a battery icon, the moon, the temperature and the date in American order. The command the app uses to change settings works for me as well, so the birdbox switched that bar off. Wildcam draws its own bar over the video instead: the camera's name on the left, date and time in the middle (ticking along while the clip plays), and on the right the sun or the moon, the weather of that hour and the temperature. The weather comes from Open-Meteo, and the moon is the actual phase for that night. When I download a clip I can choose whether that bar gets burnt in.

### A tick in the bird recordings

The day the ESP32 moved into the birdbox, the bird stream got a faint high beep and little ticks in it.

The ESP32 was scanning for the camera's Bluetooth beacon almost all the time, and actively, so every scan sent out requests. All that radio activity, on the same USB power as the headset that serves as the microphone, ended up in the audio. Now it listens for five seconds once a minute and sends nothing while it does. The beep is gone. There are still a few clicks, and the Pi logged an undervoltage when I plugged the ESP32 in, so a better power supply is next.

<!-- TODO Daan: check after the power supply / cable fix whether the clicks are gone, and update this paragraph. -->

### The first visitor

The first clip came in on 25 November at 10:37, while I was still busy mounting that antenna on the birdbox. It was a robin, who walked straight up to the camera and looked right into the lens, as if checking who'd moved into its garden.

<video controls muted playsinline preload="metadata" poster="/posts/birdbox-trail-camera/roodborst-poster.jpg" src="/posts/birdbox-trail-camera/roodborst.mp4" style="width:100%;border-radius:8px"></video>

That clip still has the camera's own bar burnt in; it came in just before the birdbox switched it off. The models said "bird, 98%". I filled in the rest.

Next up is a second camera, and a real microphone for the birdbox, so it hears the birds better than it hears the ESP32.

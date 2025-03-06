---
title: "Fixing ASPM and Deep C-States on Intel NUC 7th gen"
date: 2025-03-06T12:48:00+01:00
draft: false

tags:
- nuc
- linux
- homeautomation

cover:
    image: "cover.png"
    alt: "powertop menu"

summary:
    If you own an Intel NUC and are struggling to reach deep power-saving states like C8 or C9, your issue might be related to PCIe Active State Power Management (ASPM). I recently ran into this problem with my Intel NUC 7th Gen, where the system was stuck at C3 states despite my best efforts to tweak Linux power settings.
---
### Introduction

If you own an Intel NUC and are struggling to reach deep power-saving states like C8 or C9, your issue might be related to PCIe Active State Power Management (ASPM). I recently ran into this problem with my Intel NUC 7th Gen, where the system was stuck at C3 states despite my best efforts to tweak Linux power settings. Through trial and error, I discovered that an outdated BIOS was blocking ASPM on my NVMe SSD, preventing the system from reaching deeper C-states. A BIOS update ultimately resolved the issue! If you're facing a similar problem, this guide will walk you through the solution.

### The Problem: Why Was My Intel NUC Stuck at C3?

I started with PowerTOP, an essential diagnostic tool for Linux power management. To install it on most Linux distributions, use one of these commands:

```bash
sudo apt-get install powertop
```

After installation, you can run PowerTOP with privileges:

```bash
sudo powertop
```

### Checking Power States with PowerTOP

After running PowerTOP and going to the 'Idle Stats' tab, I noticed that my system was only reaching C3 states, instead of the deeper C8-C10 states that Intel CPUs support. So clearly, something was blocking my system from reaching deeper states. The first thing that I tried was to run auto-tune. PowerTOP includes this feature that applies various power-saving settings:

```bash
sudo powertop --auto-tune
```

This command applies recommended settings for all power management features. However, in my case, even after running auto-tune, the system remained stuck at C3 states, indicating a deeper issue.

### Investigating PCIe ASPM with `lspci`

Since NVMe SSDs and PCIe devices can block deep C-states, I checked their ASPM support, and I easily found one device not being ASPM enabled.

```bash
sudo lspci -vv | awk '/ASPM/{print $0}' RS= | grep --color -P '(^[a-z0-9:.]+|ASPM )'
```

I noticed multiple things:

- My Samsung SM961 NVMe SSD (3a:00.0) supports ASPM L1, but it was disabled.
- The PCIe Root Port (00:1d.0) did not support ASPM.
- Another PCIe Root Port (00:1c.0) did support ASPM, but nothing was connected to it.

This suggested that my NVMe SSD was stuck on a PCIe port that does not support ASPM, blocking deep sleep states.

### Forcing ASPM Enable

Before diving into BIOS updates, I tried a helpful script from GitHub called AutoASPM, which attempts to enable ASPM for all devices, hoping this would enable ASPM.

```bash
# Clone the repository
git clone https://github.com/notthebee/AutoASPM
cd AutoASPM

# Run the script (requires sudo)
sudo python3 autoaspm.py
```

This script tries to enable ASPM across all PCI devices by writing to the appropriate kernel interface files. However, in my case, since the BIOS had disabled ASPM at a hardware level, the script couldn't overcome this limitation. After running again:

```bash
sudo lspci -vv | awk '/ASPM/{print $0}' RS= | grep --color -P '(^[a-z0-9:.]+|ASPM )'
```

I still noticed that my ASPM was disabled for the NVMe.

If you're facing similar issues, try this script first—it may solve your problem without requiring a BIOS update.

### Checking BIOS Configuration for ASPM

After trying software solutions without success, I decided to check if my BIOS was configured correctly for ASPM. I confirmed that **PCIe ASPM Support** was enabled in the BIOS.

{{< figure src="image_bios.jpg" >}}

Despite this correct configuration in the BIOS, my system still could not reach deeper C-states. This led me to conclude that either the port my NVMe SSD was using did not allow lower power states. However, this conclusion did not make sense to me—why would an Intel NUC engineer design it this way? So the next day, I decided to give it one last try and check if this was an issue that was solved by a BIOS update.

### The Fix: Updating My BIOS

As a last resort, I checked Intel's website for a newer BIOS version (which is now moved to ASUS) for my NUC model (NUC7i5BNK). I found a BIOS update [here](https://www.asus.com/supportonly/nuc7i5bnk/helpdesk_bios/) on the ASUS website. 

I followed the instructions:
- Downloaded the ZIP file.
- Unzipped and added the `.bio` file to a USB flash drive.
- Booted my NUC with the USB flash drive while spamming `F7`.
- Selected the `.bio` file from the menu and let the system update itself.

Once the BIOS update was complete, I quickly verified that my BIOS settings were still untouched— PCIe ASPM Support was still enabled. After rebooting, I ran the same power state checks:

Now I was able to run AutoASPM and verify that it was working with:

```bash
sudo lspci -vv | awk '/ASPM/{print $0}' RS= | grep --color -P '(^[a-z0-9:.]+|ASPM )'
```

And after running:

```bash
sudo powertop
```

I noticed that the output now showed C8 and even C9 states, with 20% less power consumption! Okay, I'll be honest with you— 3 watts saved. But hey, free energy savings!

### Bonus: Enabling ASPM for Other Devices

Through this process, I became faster in checking the ASPM states of all devices, which really helped me in another project. For example, there I immediately identified one device that was not ASPM-enabled. Back then enabled it manually with:

```bash
echo 1 | sudo tee /sys/bus/pci/drivers/r8169/0000:01:00.0/link/l1_aspm
```

However, by going all the way on this NUC, I now discovered this useful Python script. I think for each system, you could run AutoASPM, along with `powertop --auto-tune`, and verify with the regex `lspci` command to get a very high success rate of reaching deep C-states.


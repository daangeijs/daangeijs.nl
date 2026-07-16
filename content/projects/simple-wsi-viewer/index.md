---
title: "Simple WSI viewer"
summary: "An open-source, browser-based viewer for gigapixel pathology slides, so looking at your data doesn't need a workstation or a license."
description: "Open-source web viewer for pathology whole-slide images."
role: "Author & maintainer"
timeframe: "2022 – present"
repo: "daangeijs/simple_wsi_viewer"
weight: 40
tags:
  - computational pathology
  - whole slide imaging
  - open source
draft: false
---

In pathology, the images are enormous. A single scanned slide can be several gigapixels, saved in vendor-specific formats that normal image tools simply refuse to open. The usual answer is to install heavy proprietary software on a powerful machine, which means the person who just wants a quick look, a student, a collaborator, an engineer checking what a model actually saw, often can't.

I built the Simple WSI Viewer to remove that step. Point it at a folder of slides and it gives you a browsable catalog and a smooth pan-and-zoom viewer in the browser. No install on the viewer's side, no license, no workstation.

## The idea

The trick is to not send the whole image. When you open a slide, the viewer serves only the small piece you're currently looking at, at the zoom level you're at, and streams in more as you move around. So a five-gigapixel slide feels as responsive as an online map, even though your browser only ever holds a fraction of it at a time. It reads the native pathology formats directly, so there's no slow conversion step or duplicated copies to manage.

It ships as a small self-contained package you can run locally or drop on a shared server, so a whole team can look at the same slides from a link.

## Why I made it

Good tools lower the cost of looking at your data, and in research that cost gets paid over and over. I wanted something I could hand to a colleague without a page of setup instructions, and something I could reach for myself when I needed to sanity-check a result. It's open source because everyone in this field keeps hitting the same wall, and a shared, simple viewer is more useful than yet another private script.

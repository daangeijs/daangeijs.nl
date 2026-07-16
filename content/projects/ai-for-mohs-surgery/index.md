---
title: "AI for Mohs surgery: from research question to the clinic"
summary: "Five years of turning a pathologist's bottleneck into a working deep learning pipeline for basal cell carcinoma, and learning that the model is the easy part."
description: "Case study: developing and clinically integrating deep learning for basal cell carcinoma detection and subtyping during Mohs surgery, from PhD research at Radboudumc to practice."
role: "PhD researcher, Radboudumc"
timeframe: "2019 – 2024"
weight: 10
tags:
  - computational pathology
  - deep learning
  - product
draft: false
---

## The problem worth solving

Mohs micrographic surgery removes skin cancer layer by layer; after each layer, a clinician examines frozen tissue sections under a microscope while the patient literally waits in the next room. It is precise, but slow and scarce: capacity is limited by the people qualified to read those slides.

The obvious framing was "build a model that finds basal cell carcinoma." The more useful framing, which took longer to see, was: **where in this workflow does a machine actually remove waiting time, and what does a surgeon need to trust it?**

## Discovery

I spent as much time in the lab and at the microscope as behind a GPU. What mattered:

- Frozen sections look different from the standard slides most public
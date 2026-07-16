---
title: "A self-hosted home platform that pays rent"
summary: "Proxmox, VLANs, Dockerized services and automated backups: a homelab run like a product, where the user happens to live in the house."
description: "My self-hosted infrastructure: Proxmox virtualization, network isolation, self-hosted analytics and backup automation."
role: "Owner, operator, only user"
timeframe: "2022 – present"
weight: 30
tags:
  - proxmox
  - docker
  - homeautomation
  - linux
draft: true
---

I like technology best when it changes how I live, not just how I work. My home runs on a self-hosted stack I treat like a product: it has users (my household), uptime expectations (very real ones), and a maintenance budget (my evenings).

## The stack

- **Proxmox virtualization** on Intel NUC hardware, including the fun of [debugging ASPM and deep C-states](/posts/cstates-nuc/) to get idle power draw where it should be.
- **Network isolation** with [VLANs on Ubiquiti gear](/posts/ubiquiti-vlan/), so experimental services can't take the house down.
- **Dockerized services** with [automated database backups](/posts/mariadb-backup/) and a [tested restore path](/posts/dockerized-backup/), because a backup you've never restored is a rumour, not a backup.
- **Self-hosted analytics**: this site's visitor stats ran on [Umami on my own infrastructure](/posts/umami-netlify/) instead of Google Analytics.

## Why it matters beyond the hobby

Running your own infrastructure keeps engineering judgment honest. Every convenience you'd get from a managed service becomes a conscious trade-off you feel personally: complexity you added is complexity you patch on a Sunday. It's the cheapest product-management training there is: you are the user, the stakeholder and the on-call engineer at once. Much of it is written up in my [posts](/posts/).

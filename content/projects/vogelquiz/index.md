---
title: "Vogelquiz: a bird quiz that fights back"
summary: "A bird identification quiz that gets genuinely hard, using CLIP image embeddings and pairwise similarity to serve lookalike species instead of easy birds."
description: "An embedding-powered bird identification quiz that scales difficulty by serving visually similar species, built by a birder who wanted a real challenge."
role: "Author & maintainer"
timeframe: "2024 – present"
external_url: "https://vogelquiz.nl"
thumbnail: ./logo.png
weight: 20
tags:
  - deep learning
  - CLIP
  - embeddings
  - birding
draft: false
---

I'm an avid birder, and most bird quizzes online are too easy. They mix a robin with a heron with a mallard, three birds no one confuses, and call it a test. What I actually wanted was practice on the hard calls: the near-identical species that make you second-guess yourself in the field. So I built [vogelquiz.nl](https://vogelquiz.nl).

## The problem worth solving

Difficulty in a quiz isn't about obscure birds, it's about *confusable* birds. A hard question isn't "name this exotic species," it's "is this a Common Snipe or a Jack Snipe," where two birds look almost the same and only a few field marks separate them. To generate questions like that automatically, I needed a way to measure how visually similar any two birds are.

## The deep learning part

I leaned on what I know from computational pathology: embeddings. Every bird image is passed through a [CLIP](https://openai.com/research/clip) image encoder (`ViT-B/32`), which turns a picture into a normalized feature vector. Two birds that look alike land close together in that vector space; two that look nothing alike land far apart.

With normalized embeddings, similarity is just a dot product, so a single matrix multiply gives me the full pairwise similarity matrix across every bird at once:

```python
similarity_matrix = embeddings @ embeddings.T  # cosine similarity, vectors are normalized
np.fill_diagonal(similarity_matrix, -np.inf)   # mask self-similarity
```

For each bird I then sort its neighbours by similarity and store the ranked distances in a small SQLite table (`source_id`, `target_id`, `distance`, `rank`). At quiz time, difficulty becomes a lookup: I don't judge difficulty by hand, I just pick decoys from different bands of that similarity ranking.

## Tuning the difficulty

Each answer option is a decoy pulled from one of three rank bands: `similar` (the nearest lookalikes), `semi` (moderately close), and `far` (obviously different birds). A difficulty level is nothing more than which ranks each band draws from:

```python
# Difficulty configuration
DIFFICULTY_CONFIG = {
    "makkelijk": {"similar": range(1, 6),   "semi": range(20, 51),  "far": range(100, 201)},
    "gemiddeld": {"similar": range(1, 3),   "semi": range(10, 31),  "far": range(60, 121)},
    "moeilijk":  {"similar": range(1, 2),   "semi": range(2, 11),   "far": range(10, 41)},
}
```

Read the ranks and the mechanic falls out:

- **makkelijk (easy):** the closest decoy is only the 1st–5th most similar bird, and the other options come from far down the list (ranks 100–200), birds that look nothing alike. Easy to tell apart.
- **gemiddeld (average):** the bands tighten. The nearest decoy is a top-2 lookalike, the "far" option is now only rank 60–120, so even the easy option is no longer a gift.
- **moeilijk (hard):** everything collapses toward the top of the ranking. The nearest decoy is *the* single most similar bird (rank 1), and even the "far" option is drawn from ranks 10–40, birds that are still genuinely confusable. Every option looks plausible.

So the same similarity matrix drives the whole difficulty curve: easy rounds spread the decoys across the ranking, hard rounds squeeze them all into the lookalike zone.

## Why I like this one

It's a small project, but it's the whole loop I enjoy: a real problem I personally had, a bit of domain knowledge (which birds are actually confusable), and a machine learning technique used exactly where it earns its keep, no more. The embedding trick that powers medical image retrieval is the same trick that makes a bird quiz sting.

The code for the embedding and similarity pipeline is on [GitHub](https://github.com/daangeijs/bird-quiz).

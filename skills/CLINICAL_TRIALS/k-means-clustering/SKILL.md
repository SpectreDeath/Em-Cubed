---
name: k-means-clustering
domain: "CLINICAL_TRIALS"
description: Multi-surface K-means clustering with Python surface for iterative centroid optimization and SQLite surface for cluster persistence and member assignment tracking. Supports configurable K and convergence testing.
compatibility: UNIVERSAL
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---
﻿---
name: k-means-clustering
domain: CLINICAL_TRIALS
version: "1.0.0"
surfaces: [python]
---

# Purpose

Partition n-dimensional data points into k clusters using iterative centroid optimization.

# Description

K-means clustering algorithm using Euclidean distance with k-means++ style centroid initialization and Newton-Raphson sqrt approximation for zero-dependency distance calculation.

## Python Surface

```python
import random

def my_sqrt(x):
    if x <= 0:
        return 0.0
    guess = x / 2.0
    for _ in range(20):
        guess = 0.5 * (guess + x / guess)
        if abs(guess * guess - x) < 1e-10:
            break
    return guess

def euclidean_distance(p1, p2):
    dist_sq = 0.0
    for i in range(len(p1)):
        diff = p1[i] - p2[i]
        dist_sq = dist_sq + diff * diff
    return my_sqrt(dist_sq)

def initialize_centroids(data, k):
    centroids = [data[random.randint(0, len(data) - 1)]]
    for _ in range(1, k):
        distances = []
        for point in data:
            min_d = float("inf")
            for c in centroids:
                d = euclidean_distance(point, c)
                if d < min_d:
                    min_d = d
            distances.append(min_d * min_d)
        total = sum(distances)
        r = random.random() * total
        acc = 0.0
        for i, d in enumerate(distances):
            acc = acc + d
            if acc >= r:
                centroids.append(data[i])
                break
    return centroids

def kmeans(data, k, max_iters=100):
    if not data or len(data) == 0:
        return [], []
    num_features = len(data[0])
    centroids = initialize_centroids(data, k)
    for _ in range(max_iters):
        clusters = [[] for _ in range(k)]
        for point in data:
            min_idx = 0
            min_d = euclidean_distance(point, centroids[0])
            for i in range(1, k):
                d = euclidean_distance(point, centroids[i])
                if d < min_d:
                    min_d = d
                    min_idx = i
            clusters[min_idx].append(point)
        for i in range(k):
            if len(clusters[i]) > 0:
                new_centroid = [0.0] * num_features
                for p in clusters[i]:
                    for j in range(num_features):
                        new_centroid[j] = new_centroid[j] + p[j]
                for j in range(num_features):
                    new_centroid[j] = new_centroid[j] / len(clusters[i])
                centroids[i] = new_centroid
            else:
                centroids[i] = random.choice(data)
    return centroids, clusters
```

---
name: k-means-clustering
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python]
---

# Purpose
Partition unlabeled data into k distinct clusters by minimizing within-cluster sum of squares.

# Description
Core inputs: data points (list of coordinate tuples), number of clusters k (int). Mechanical steps: initialize centroids randomly, assign each point to nearest centroid, recompute centroids as cluster means, repeat until convergence. Expected outputs: cluster assignments (list of int cluster ids), final centroids (list of coordinate tuples).

## Python Surface

```python
def euclidean_distance(p1, p2):
    """Compute Euclidean distance between two points using Newton-Raphson sqrt."""
    total = 0.0
    for i in range(len(p1)):
        total = total + (p1[i] - p2[i]) ** 2
    if total < 0.0000001:
        return 0.0
    x = total
    for _ in range(20):
        x = 0.5 * (x + total / x)
    return x

def k_means(data_points, k, max_iterations=100):
    """
    K-means clustering algorithm.
    
    Args:
        data_points: List of tuples representing coordinates (e.g., [(1.2, 3.4), (5.6, 7.8)])
        k: Number of clusters to form
        max_iterations: Maximum iterations before stopping
    
    Returns:
        tuple of (cluster_assignments, centroids) where:
        - cluster_assignments: List of cluster indices for each point
        - centroids: List of final centroid coordinates
    """
    points = [list(p) for p in data_points]
    n = len(points)
    if n == 0 or k <= 0:
        return ([], [])
    
    dimension = len(points[0])
    # Initialize centroids using first k data points (simple approach)
    centroids = []
    for i in range(min(k, n)):
        centroids.append([float(points[i][d]) for d in range(dimension)])
    # If we need more centroids than data points, repeat the last one
    while len(centroids) < k:
        centroids.append([float(points[-1][d]) for d in range(dimension)] if n > 0 else [0.0] * dimension)
    
    assignments = [0] * n
    for _ in range(max_iterations):
        changed = False
        
        for i in range(n):
            min_dist = float('inf')
            best_cluster = 0
            for j in range(k):
                dist = euclidean_distance(points[i], centroids[j])
                if dist < min_dist:
                    min_dist = dist
                    best_cluster = j
            if assignments[i] != best_cluster:
                changed = True
            assignments[i] = best_cluster
        
        if not changed:
            break
        
        sums = [[0.0 for _ in range(dimension)] for _ in range(k)]
        counts = [0] * k
        for i in range(n):
            c = assignments[i]
            counts[c] = counts[c] + 1
            for d in range(dimension):
                sums[c][d] = sums[c][d] + points[i][d]
        
        for j in range(k):
            if counts[j] > 0:
                for d in range(dimension):
                    centroids[j][d] = sums[j][d] / counts[j]
            else:
                centroids[j] = [0.0 for _ in range(dimension)]
    
    return (assignments, centroids)
```
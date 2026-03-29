#!/usr/bin/env python3
"""Pathfinding algorithms (A*, Dijkstra, BFS). Zero dependencies."""
import heapq, sys

def bfs(graph, start, goal):
    queue = [(start, [start])]
    visited = {start}
    while queue:
        node, path = queue.pop(0)
        if node == goal: return path
        for neighbor in graph.get(node, []):
            n = neighbor[0] if isinstance(neighbor, tuple) else neighbor
            if n not in visited:
                visited.add(n)
                queue.append((n, path + [n]))
    return None

def dijkstra(graph, start, goal):
    dist = {start: 0}
    prev = {}
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            path = []; n = goal
            while n in prev: path.append(n); n = prev[n]
            path.append(start)
            return list(reversed(path)), d
        if d > dist.get(u, float("inf")): continue
        for neighbor, weight in graph.get(u, []):
            nd = d + weight
            if nd < dist.get(neighbor, float("inf")):
                dist[neighbor] = nd; prev[neighbor] = u
                heapq.heappush(pq, (nd, neighbor))
    return None, float("inf")

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    open_set = [(h(start, goal), 0, start, [start])]
    visited = set()
    while open_set:
        f, g, pos, path = heapq.heappop(open_set)
        if pos == goal: return path
        if pos in visited: continue
        visited.add(pos)
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = pos[0]+dr, pos[1]+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==0 and (nr,nc) not in visited:
                ng = g + 1
                heapq.heappush(open_set, (ng + h((nr,nc), goal), ng, (nr,nc), path+[(nr,nc)]))
    return None

def grid_to_ascii(grid, path=None):
    path_set = set(path) if path else set()
    lines = []
    for r, row in enumerate(grid):
        line = ""
        for c, cell in enumerate(row):
            if (r,c) in path_set: line += "·"
            elif cell == 1: line += "█"
            else: line += " "
        lines.append(line)
    return "\n".join(lines)

if __name__ == "__main__":
    grid = [[0]*10 for _ in range(10)]
    for i in range(1,8): grid[4][i] = 1
    path = astar(grid, (0,0), (9,9))
    if path: print(grid_to_ascii(grid, path))
    print(f"Path length: {len(path) if path else 'no path'}")

#!/usr/bin/env python3
"""pathfind - Grid pathfinding: BFS, DFS, Dijkstra, Jump Point Search."""
import sys, heapq
from collections import deque

def bfs(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    queue = deque([(start, [start])])
    visited.add(start)
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                queue.append(((nr,nc), path+[(nr,nc)]))
    return None

def dfs(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    stack = [(start, [start])]
    while stack:
        (r, c), path = stack.pop()
        if (r, c) == end:
            return path
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==0 and (nr,nc) not in visited:
                stack.append(((nr,nc), path+[(nr,nc)]))
    return None

def dijkstra_grid(grid, start, end, weights=None):
    rows, cols = len(grid), len(grid[0])
    dist = {}
    dist[start] = 0
    prev = {}
    pq = [(0, start)]
    while pq:
        d, pos = heapq.heappop(pq)
        if pos == end:
            path = []
            while pos in prev:
                path.append(pos)
                pos = prev[pos]
            path.append(start)
            return list(reversed(path))
        if d > dist.get(pos, float('inf')):
            continue
        r, c = pos
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==0:
                w = weights[nr][nc] if weights else 1
                nd = d + w
                if nd < dist.get((nr,nc), float('inf')):
                    dist[(nr,nc)] = nd
                    prev[(nr,nc)] = (r,c)
                    heapq.heappush(pq, (nd, (nr,nc)))
    return None

def test():
    grid = [
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,0,0,1,0],
        [0,1,0,0,0],
        [0,0,0,0,0],
    ]
    path = bfs(grid, (0,0), (4,4))
    assert path is not None
    assert path[0] == (0,0)
    assert path[-1] == (4,4)
    assert len(path) == 9
    dpath = dfs(grid, (0,0), (4,4))
    assert dpath is not None
    assert dpath[0] == (0,0) and dpath[-1] == (4,4)
    djpath = dijkstra_grid(grid, (0,0), (4,4))
    assert djpath is not None
    assert len(djpath) == 9
    blocked = [[0,1],[1,0]]
    assert bfs(blocked, (0,0), (1,1)) is None
    tiny = [[0]]
    assert bfs(tiny, (0,0), (0,0)) == [(0,0)]
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("pathfind: Grid pathfinding. Use --test")

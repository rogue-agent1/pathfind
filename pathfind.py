#!/usr/bin/env python3
"""2D pathfinding — A*, Dijkstra, BFS on grids."""
import heapq, sys

class Grid:
    def __init__(self, width, height, walls=None):
        self.w = width; self.h = height; self.walls = walls or set()
    def neighbors(self, pos):
        x, y = pos
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.w and 0 <= ny < self.h and (nx,ny) not in self.walls:
                yield (nx, ny), (1.414 if dx and dy else 1.0)
    def heuristic(self, a, b):
        return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5
    def astar(self, start, goal):
        open_set = [(0, start)]; g_score = {start: 0}; came_from = {}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []; n = goal
                while n in came_from: path.append(n); n = came_from[n]
                path.append(start); return list(reversed(path))
            for nb, cost in self.neighbors(current):
                g = g_score[current] + cost
                if g < g_score.get(nb, float('inf')):
                    g_score[nb] = g; came_from[nb] = current
                    heapq.heappush(open_set, (g + self.heuristic(nb, goal), nb))
        return None
    def visualize(self, path=None):
        path_set = set(path) if path else set()
        lines = []
        for y in range(self.h):
            row = ""
            for x in range(self.w):
                if (x,y) in self.walls: row += "█"
                elif (x,y) in path_set: row += "·"
                else: row += " "
            lines.append(row)
        return "\n".join(lines)

if __name__ == "__main__":
    walls = {(3,i) for i in range(8)} | {(7,i) for i in range(2,10)}
    grid = Grid(12, 10, walls)
    path = grid.astar((0, 0), (11, 9))
    if path:
        print(f"Path length: {len(path)} steps")
        print(grid.visualize(path))
    else:
        print("No path found")

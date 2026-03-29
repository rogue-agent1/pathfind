from pathfind import bfs, dijkstra, astar
g = {"A": ["B","C"], "B": ["D"], "C": ["D"], "D": []}
p = bfs(g, "A", "D")
assert p is not None and p[0]=="A" and p[-1]=="D"
wg = {"A": [("B",1),("C",4)], "B": [("D",2)], "C": [("D",1)], "D": []}
path, dist = dijkstra(wg, "A", "D")
assert dist == 3 and path == ["A","B","D"]
grid = [[0]*5 for _ in range(5)]
grid[2][1] = grid[2][2] = grid[2][3] = 1
ap = astar(grid, (0,0), (4,4))
assert ap is not None and ap[0]==(0,0) and ap[-1]==(4,4)
print("Pathfinding tests passed")
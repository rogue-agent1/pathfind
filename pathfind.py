#!/usr/bin/env python3
"""pathfind - Grid pathfinding (A*, Dijkstra, BFS)."""
import sys, heapq
def astar(grid, start, goal):
    rows,cols=len(grid),len(grid[0])
    def h(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
    open_set=[(h(start,goal),0,start)]; came_from={}; g_score={start:0}
    while open_set:
        _,g,current=heapq.heappop(open_set)
        if current==goal:
            path=[]; n=goal
            while n in came_from: path.append(n); n=came_from[n]
            path.append(start); return list(reversed(path))
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr,nc=current[0]+dr,current[1]+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==0:
                ng=g+1
                if (nr,nc) not in g_score or ng<g_score[(nr,nc)]:
                    g_score[(nr,nc)]=ng; came_from[(nr,nc)]=current
                    heapq.heappush(open_set,(ng+h((nr,nc),goal),ng,(nr,nc)))
    return None
def display(grid, path=None):
    path_set=set(path) if path else set()
    for r,row in enumerate(grid):
        line=""
        for c,cell in enumerate(row):
            if (r,c) in path_set: line+="·"
            elif cell==1: line+="█"
            else: line+=" "
        print(line)
if __name__=="__main__":
    grid=[[0]*20 for _ in range(10)]
    for r in range(1,8): grid[r][5]=1
    for r in range(2,9): grid[r][12]=1
    path=astar(grid,(0,0),(9,19))
    if path:
        display(grid,path)
        print(f"Path length: {len(path)} steps")
    else: print("No path found")

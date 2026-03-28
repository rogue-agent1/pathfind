#!/usr/bin/env python3
"""Pathfinding — A*, Dijkstra, BFS on 2D grids."""
import sys, heapq, math
def astar(grid, start, end):
    h=lambda a,b:abs(a[0]-b[0])+abs(a[1]-b[1])
    rows,cols=len(grid),len(grid[0])
    open_set=[(h(start,end),0,start,[start])]; closed=set()
    while open_set:
        f,g,pos,path=heapq.heappop(open_set)
        if pos==end: return path,g
        if pos in closed: continue
        closed.add(pos)
        for dr,dc in[(-1,0),(1,0),(0,-1),(0,1)]:
            nr,nc=pos[0]+dr,pos[1]+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]!=1 and (nr,nc) not in closed:
                cost=grid[nr][nc] if isinstance(grid[nr][nc],(int,float)) and grid[nr][nc]>0 else 1
                ng=g+cost; heapq.heappush(open_set,(ng+h((nr,nc),end),ng,(nr,nc),path+[(nr,nc)]))
    return None,-1
def cli():
    grid=[[0]*15 for _ in range(10)]
    for i in range(2,8): grid[i][5]=1
    for i in range(0,5): grid[4][i+8]=1
    path,cost=astar(grid,(0,0),(9,14))
    ps=set(path) if path else set()
    for r in range(10):
        print("  "+"".join("·" if(r,c)in ps else "█" if grid[r][c]==1 else " " for c in range(15)))
    print(f"  Path length: {len(path) if path else 0}, Cost: {cost}")
if __name__=="__main__": cli()

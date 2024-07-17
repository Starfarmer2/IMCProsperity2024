import numpy as np
from typing import List, Tuple

graph = np.array([[1, 0.48, 1.52, 0.71],
                  [2.05, 1, 3.26, 1.56],
                  [0.64, 0.3, 1, 0.46],
                  [1.41, 0.61, 2.08, 1]])

starting_node = 3

list: List[Tuple[List[int], float]] = []

for a in range(4):
    if a == starting_node:
        continue

    for b in range(4):
        if b == a:
            continue
        if b == starting_node:
            new_e = ([starting_node, a, b], graph[starting_node][a] * graph[a][b])
            # print(f'combination: {(starting_node, a, b, c, d)} profits: {graph[starting_node][a] * graph[a][b] * graph[b][c] * graph[c][d] * graph[d][e]}')
            list.append(new_e)

        for c in range(4):
            if c == b:
                continue
            if c == starting_node:
                new_e = ([starting_node, a, b, c], graph[starting_node][a] * graph[a][b] * graph[b][c])
                # print(f'combination: {(starting_node, a, b, c, d)} profits: {graph[starting_node][a] * graph[a][b] * graph[b][c] * graph[c][d] * graph[d][e]}')
                list.append(new_e)

            for d in range(4):
                if d == c:
                    continue

                if d == starting_node:
                    new_e = ([starting_node, a, b, c, d], graph[starting_node][a] * graph[a][b] * graph[b][c] * graph[c][d])
                    # print(f'combination: {(starting_node, a, b, c, d)} profits: {graph[starting_node][a] * graph[a][b] * graph[b][c] * graph[c][d] * graph[d][e]}')
                    list.append(new_e)
                for e in range(4):
                    if e == d or e != starting_node:
                        continue
                    new_e = ([starting_node, a, b, c, d, e], graph[starting_node][a] * graph[a][b] * graph[b][c] * graph[c][d] * graph[d][e])
                    list.append(new_e)
                    # print(f'combination: {(starting_node, a, b, c, d, e)} profits: {graph[starting_node][a] * graph[a][b] * graph[b][c] * graph[c][d] * graph[d][e]}')

list.sort(key=lambda x: x[1])
print(list)
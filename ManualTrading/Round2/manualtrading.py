import numpy as np

graph = np.array([[1, 0.48, 1.52, 0.71],
                  [2.05, 1, 3.26, 1.56],
                  [0.64, 0.3, 1, 0.46],
                  [1.41, 0.61, 2.08, 1]])

log_graph = np.log(graph)
print(log_graph)

def find_cycles_from_node(adj_matrix, weights, start_node):
    n = len(adj_matrix)  # Number of vertices
    visited = [False] * n
    all_cycles = []

    def dfs(current, path, current_weight):
        if current == start_node and len(path) > 1:
            # Found a cycle, append it along with its weight
            all_cycles.append((path[:], current_weight))
            return
        if visited[current]:
            return

        visited[current] = True
        for neighbor in range(n):
            if adj_matrix[current][neighbor] != 0:  # There is an edge
                if not visited[neighbor] or neighbor == start_node:
                    edge_weight = weights[current][neighbor]
                    dfs(neighbor, path + [neighbor], current_weight + edge_weight)
        visited[current] = False

    # Initialize DFS from the start node
    dfs(start_node, [start_node], 0)

    # Sort cycles based on their weights (distances)
    all_cycles.sort(key=lambda x: x[1])

    return all_cycles

adj_matrix = [
    [0, 1, 1, 1],
    [1, 0, 1, 1],
    [1, 1, 0, 1],
    [1, 1, 1, 0],
]


start_node = 3
cycles = find_cycles_from_node(adj_matrix, log_graph, start_node)
for cycle, weight in cycles:
    print("Cycle:", cycle, "Weight:", np.e ** weight)


import numpy as np

matrix = np.array([[24, 70, 41, 21, 60],
                   [47, 82, 87, 80, 35],
                   [73, 89, 100, 90, 17],
                   [77, 83, 85, 79, 55],
                   [12, 27, 52, 15, 30]])

hunters = np.array([[2, 4, 3, 2, 4],
                   [3, 5, 5, 5, 3],
                   [4, 5, 8, 7, 2],
                   [5, 5, 5, 5, 4],
                   [2, 3, 4, 2, 3]])

ratioed = matrix / hunters
print(ratioed)

indices = []
for i in range(5):
    for j in range(5):
        indices.append((i, j))

indices = sorted(indices, key=lambda x: ratioed[x[0], x[1]], reverse=True)

print(f'sorted indices: {indices}')



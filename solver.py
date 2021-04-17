import numpy as np


# Checking if current value is valid
def possible(grid, x, y, n):
    if grid[x][y] != 0 and grid[x][y] != n:
        return False

    temp = grid[x][y]
    grid[x][y] = 0

    for i in range(0, 9):
        if grid[x][i] == n or grid[i][y] == n:
            grid[x][y] = temp
            return False

    x0 = (x // 3) * 3
    y0 = (y // 3) * 3

    for i in range(0, 3):
        for j in range(0, 3):
            if grid[x0 + i][y0 + j] == n:
                grid[x][y] = temp
                return False

    grid[x][y] = temp
    return True


# Checking if puzzle can be solved and then provide solution
def solve(grid):
    for x in range(0, 9):
        for y in range(0, 9):
            if grid[x][y] == 0:
                for n in range(1, 10):
                    if possible(grid, x, y, n):
                        grid[x][y] = n
                        if solve(grid):
                            return True
                        grid[x][y] = 0
                return False

    # print(np.matrix(grid))
    # print()
    return True

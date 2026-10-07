import numpy as np
from maze import Maze


def get_safe_squares(maze, seen):
    """Make a True/False grid of squares it has seen that are floor and not a pit"""
    safe = np.zeros(maze.shape, dtype=bool)
    for row in range(maze.shape[0]):
        for col in range(maze.shape[1]):
            if seen[row, col] and maze.maze[row, col] and (row, col) not in maze.hazards:
                safe[row, col] = True
    return safe


def next_move(maze, position, seen, visited):
    """Pick the next square to step to only using squares its seen"""
    safe = get_safe_squares(maze, seen)
    path = None

    # see goal? go there
    if seen[maze.goal_position]:
        goal_grid = np.zeros(maze.shape, dtype=bool)
        goal_grid[maze.goal_position] = True
        path = maze.find_path(position, goal_grid, safe)

    # walk to the closest unvisited safe square 
    if path is None:
        unexplored = np.zeros(maze.shape, dtype=bool)
        for row in range(maze.shape[0]):
            for col in range(maze.shape[1]):
                if safe[row, col] and not visited[row, col]:
                    unexplored[row, col] = True
        path = maze.find_path(position, unexplored, safe)

    if path is None:
        return None 
    return path[1] # path[0] is where i am now, path[1] is the next step


def solve_maze(maze):
    position = maze.start_position
    seen = np.zeros(maze.shape, dtype=bool)     # squares its seen
    visited = np.zeros(maze.shape, dtype=bool)  # squares its stood on
    path = [position]

    for square in maze.line_of_sight(position):
        seen[square] = True

    while position != maze.goal_position:
        visited[position] = True
        position = next_move(maze, position, seen, visited)
        if position is None:
            print("robots stuck")
            return path
        path.append(position)

        # Look around in new position
        for square in maze.line_of_sight(position):
            seen[square] = True

    return path


if __name__ == "__main__":
    m = Maze(10)
    path = solve_maze(m)
    m.display(path)
    print("the solver did it")
import numpy as np

_FLOOR = True
_WALL = False

# The 4 directions: up, down, left, right
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Maze:

    def __init__(self, size=8):
        """Initialize a new, random maze using depth first search"""
        self.size = size
        self.shape = (2*size + 1,)*2 
        self.maze = np.zeros(shape=self.shape, dtype=bool) # all walls at first

        # Randomly make maze with a depthfirst search
        visited = np.zeros(shape=(size,size), dtype=bool)
        def generate_maze_from_cell(position):
            x, y = position # get position
            visited[x, y] = True # position = visited
            self.maze[2*x+1, 2*y+1] = _FLOOR # make position floor color

            # Make sure we've visited each neighbor
            neighbor_coords = (x+1, y), (x, y+1), (x-1, y), (x, y-1)
            for neighbor in np.random.permutation(neighbor_coords):
                neighbor_x, neighbor_y = neighbor

                # check ifcoords = valid
                if not (0 <= neighbor_x < size) or not (0 <= neighbor_y < size):
                    continue 

                # if neighboring cell has been visited, skip
                if visited[neighbor_x, neighbor_y]:
                    continue 
                else:
                    # knock down the wall between current cell and neighbor
                    self.maze[x+neighbor_x+1, y+neighbor_y+1] = _FLOOR
                    generate_maze_from_cell(neighbor)
        generate_maze_from_cell((0, 0))

        self.add_loops()
        self.place_items()

    def add_loops(self):
        """Knock down some random walls so the maze has loops"""
        for row in range(1, self.shape[0] - 1):
            for col in range(1, self.shape[1] - 1):
                #wall between two rooms has one odd index and one even index
                if row % 2 != col % 2:
                    # 10% chance to knock it down
                    if np.random.rand() < 0.1:
                        self.maze[row, col] = _FLOOR

    def place_items(self):
        """Randomly place player, goal, map, and red squares of death"""
        # Make a list of all the rooms/cells
        rooms = []
        for x in range(self.size):
            for y in range(self.size):
                rooms.append((2*x + 1, 2*y + 1))

        # checks over and over until its fair and valid
        while True:
            order = np.random.permutation(len(rooms))
            self.start_position = rooms[order[0]]
            self.goal_position = rooms[order[1]]
            self.map_position = rooms[order[2]]
            self.hazards = []
            for i in range(4):
                self.hazards.append(rooms[order[3 + i]])

            # Check 1: i cant see it right at the start
            if self.goal_position in self.line_of_sight(self.start_position):
                continue 

            # Check 2: actual way to get to the goal
            can_walk = self.maze.copy()
            for pit in self.hazards:
                can_walk[pit] = False
            goal_grid = np.zeros(self.shape, dtype=bool)
            goal_grid[self.goal_position] = True
            if self.find_path(self.start_position, goal_grid, can_walk) is not None:
                break 

        # The map shows a path from a random room to the goal
        route_start = self.goal_position
        while route_start == self.goal_position:
            route_start = rooms[np.random.randint(len(rooms))]
        goal_grid = np.zeros(self.shape, dtype=bool)
        goal_grid[self.goal_position] = True
        self.map_route = self.find_path(route_start, goal_grid, self.maze)

    def line_of_sight(self, position):
        """shows the squares visible from this position"""
        row, col = position

        # Look in each direction until a wall
        looking_at = [position]
        for d_row, d_col in DIRECTIONS:
            r = row + d_row
            c = col + d_col
            while self.maze[r, c] == _FLOOR:
                looking_at.append((r, c))
                r = r + d_row
                c = c + d_col

        # see on the other sides of walls
        visible = []
        for (r, c) in looking_at:
            for d_row in [-1, 0, 1]:
                for d_col in [-1, 0, 1]:
                    visible.append((r + d_row, c + d_col))
        return visible

    def find_path(self, start, is_target, can_walk):
        """Breadth-first search.
        is_target and can_walk are True/False grids the same size as the maze.
        Returns the list of squares from start to the closest target, or None."""
        came_from = {} # wha square i just came from
        came_from[start] = None
        queue = [start]

        while len(queue) > 0:
            current = queue.pop(0)

            # no target? follow came_from the other way to get the path
            if is_target[current]:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            # Add the neighbors i haven't been to yet
            row, col = current
            for d_row, d_col in DIRECTIONS:
                next_square = (row + d_row, col + d_col)
                if can_walk[next_square] and next_square not in came_from:
                    came_from[next_square] = current
                    queue.append(next_square)

        return None 

    def display(self, path=[]):
        """Display maze using blocks for floors and empty spaces for walls"""
        str_maze = np.where(self.maze, '██', '  ')
        for square in path:
            str_maze[square] = '░░'
        for square in self.hazards:
            str_maze[square] = '^^'
        str_maze[self.map_position] = 'MM'
        str_maze[self.start_position] = 'SS'
        str_maze[self.goal_position] = 'GG'
        for row in str_maze:
            print(''.join([c for c in row]))
        print('SS = start   GG = goal   MM = map   ^^ = pit   ░░ = path')



if __name__ == "__main__":
    m = Maze(16)
    m.display()
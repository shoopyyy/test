import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button
import numpy as np
from maze import Maze
from maze_solver import next_move

# Turn off matplotlib's keyboard shortcuts that keys i wanna use
plt.rcParams['keymap.save'] = []     
plt.rcParams['keymap.back'] = []     
plt.rcParams['keymap.forward'] = []  

# Each square in the picture gets a number, and each number has a color
UNKNOWN = 0
WALL = 1
FLOOR = 2
PLAYER = 3
GOAL = 4
MAP = 5
PIT = 6
ROUTE = 7
ROUTE_START = 8
COLORS = ListedColormap(['black', 'dimgray', 'beige', 'blue', 'limegreen',
                         'gold', 'red', 'lightskyblue', 'purple'])

VIEW_RADIUS = 9 # how many squares you can see on screen in each direction


def new_game():
    global maze, player_pos, lives, seen, visited, game_over, won, showing_map, message
    stop_solver()
    maze = Maze(10)
    player_pos = maze.start_position
    lives = 3
    seen = np.zeros(maze.shape, dtype=bool)
    for square in maze.line_of_sight(player_pos):
        seen[square] = True
    visited = np.zeros(maze.shape, dtype=bool) # visited squares
    game_over = False
    won = False
    showing_map = False
    message = "Find the goal"
    draw()


def move(d_row, d_col):
    global player_pos, lives, game_over, won, showing_map, message
    new_pos = (player_pos[0] + d_row, player_pos[1] + d_col)

    # Can't walk through walls
    if maze.maze[new_pos] == False:
        message = "Ouch a wall."
        return

    player_pos = new_pos
    showing_map = False
    message = ""

    # Look around from the new spot
    for square in maze.line_of_sight(player_pos):
        seen[square] = True

    if player_pos == maze.map_position:
        message = "You got a map, press M to read it."

    if player_pos in maze.hazards:
        lives = lives - 1
        message = "thats a pit if you didnt know. Lives left: " + str(lives)
        if lives == 0:
            game_over = True

    if player_pos == maze.goal_position:
        game_over = True
        won = True


def on_key(event):
    global showing_map, message

    # When the game is over, only y and n do anything
    if game_over:
        if event.key == 'y':
            new_game()
        elif event.key == 'n':
            plt.close(fig)
        return

    # While the solver is going ignore other inputs
    if solver_on:
        return

    if event.key == 'up' or event.key == 'w':
        move(-1, 0)
    elif event.key == 'down' or event.key == 's':
        move(1, 0)
    elif event.key == 'left' or event.key == 'a':
        move(0, -1)
    elif event.key == 'right' or event.key == 'd':
        move(0, 1)
    elif event.key == 'm':
        if showing_map:
            showing_map = False
        elif player_pos == maze.map_position:
            showing_map = True
        else:
            message = " no map here"
    draw()


def start_solver():
    global solver_on, showing_map, message
    solver_on = True
    showing_map = False
    message = "The solver is playing"
    solver_button.label.set_text("Stop the solver")
    timer.start() # calls solver_step over and over


def stop_solver():
    global solver_on
    solver_on = False
    timer.stop()
    solver_button.label.set_text("Let the solver play")


def on_solver_button(event):
    global message
    if game_over:
        return
    if solver_on:
        stop_solver()
        message = "You're in control."
    else:
        start_solver()
    draw()


def solver_step():
    """ The solver takes one step using only what we've seen."""
    global message
    if game_over or not solver_on:
        stop_solver()
        return

    visited[player_pos] = True
    next_square = next_move(maze, player_pos, seen, visited)
    if next_square is None:
        message = "robots stuck"
        stop_solver()
    else:
        move(next_square[0] - player_pos[0], next_square[1] - player_pos[1])
        if game_over:
            stop_solver()
    draw()


def make_player_view():
    """makes a fixed size window around the player that moves with it and shows everything unknown as black"""
    size = 2 * VIEW_RADIUS + 1
    picture = np.zeros((size, size), dtype=int) # starts all as unknown

    for i in range(size):
        for j in range(size):
            row = player_pos[0] - VIEW_RADIUS + i
            col = player_pos[1] - VIEW_RADIUS + j

            # outside of maze = unknown
            if row < 0 or row >= maze.shape[0] or col < 0 or col >= maze.shape[1]:
                continue
            if seen[row, col] == False:
                continue

            if (row, col) == player_pos:
                picture[i, j] = PLAYER
            elif (row, col) == maze.goal_position:
                picture[i, j] = GOAL
            elif (row, col) == maze.map_position:
                picture[i, j] = MAP
            elif (row, col) in maze.hazards:
                picture[i, j] = PIT
            elif maze.maze[row, col] == True:
                picture[i, j] = FLOOR
            else:
                picture[i, j] = WALL
    return picture


def make_map_picture():
    picture = np.zeros(maze.shape, dtype=int)
    for row in range(maze.shape[0]):
        for col in range(maze.shape[1]):
            if maze.maze[row, col] == True:
                picture[row, col] = FLOOR
            else:
                picture[row, col] = WALL

    for square in maze.map_route:
        picture[square] = ROUTE
    for square in maze.hazards:
        picture[square] = PIT
    picture[maze.map_route[0]] = ROUTE_START
    picture[maze.goal_position] = GOAL
    return picture


def draw():
    ax.clear()
    ax.axis('off') # hide axes so there are no coordinates

    if showing_map:
        picture = make_map_picture()
        ax.set_title("follow the path to get to the goal")
    else:
        picture = make_player_view()
        ax.set_title("Lives: " + str(lives) + "\n" + message)

    ax.imshow(picture, cmap=COLORS, vmin=0, vmax=8, interpolation='nearest')

    if game_over:
        if won:
            text = "yay you won\nPlay again? (y/n)"
            color = 'green'
        else:
            text = "howd you lose that\nPlay again? (y/n)"
            color = 'red'
        ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center',
                fontsize=24, color='white', bbox=dict(facecolor=color))

    fig.canvas.draw_idle() 


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(7, 7.5))
    fig.subplots_adjust(bottom=0.17) 
    fig.text(0.5, 0.01, "Arrow keys / WASD: move    M: read the map\n"
             "Blue = you   Green = goal   Yellow = map   Red = pit", ha='center')
    fig.canvas.mpl_connect('key_press_event', on_key) # call on_key when a key is pressed

    # solver button
    button_area = fig.add_axes([0.33, 0.07, 0.34, 0.05])
    solver_button = Button(button_area, "Let the solver play")
    solver_button.on_clicked(on_solver_button)

    # A timer so the solver keeps moving
    timer = fig.canvas.new_timer(interval=150)
    timer.add_callback(solver_step)
    solver_on = False

    new_game()
    plt.show()
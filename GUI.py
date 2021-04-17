import numpy as np
import pygame
from solver import possible, solve
from puzzle import get_puzzle

import time
import os

pygame.init()

WIDTH, HEIGHT = 540, 600
ROWS, COLS = 9, 9

B_WIDTH, B_HEIGHT = 60, 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (207, 68, 68)
GREEN = (117, 172, 112)
BLUE = (27, 142, 207)

DEFAULT_FONT = pygame.font.SysFont('comicsans', 40)
SMALL_FONT = pygame.font.SysFont('comicsans', 25)
LARGE_FONT = pygame.font.SysFont('comicsans', 60)

BORDER_FONT = pygame.font.SysFont('comicsans', 82)

WINNER_FONT = pygame.font.SysFont('comicsans', 60)
LOSE_FONT = pygame.font.SysFont('comicsans', 60)

# Border Rendering
_circle_cache = {}


def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


# Rendering Border
def render(text, font, gfcolor=BLACK, ocolor=WHITE, opx=2):
    textsurface = font.render(text, True, gfcolor).convert_alpha()
    w = textsurface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textsurface, (opx, opx))
    return surf


# Board Class representing sudoku board containing list of object of class Cubes as cells
class Board:

    def __init__(self, rows, cols, width, height, diff):
        self.rows = rows
        self.cols = cols

        self.width = width
        self.height = height

        self.diff = diff

        # Calling get_puzzle function to extract puzzle from sudoku website according to difficulty
        self.grid = get_puzzle(diff)

        # Initializing list of Cube objects with the grid values
        self.cubes = [[Cube(self.grid[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in
                      range(self.rows)]

        self.model = None
        self.selected = None
        self.auto = False

    # Updating model to current grid values
    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    # Inserting value to the selected cell
    def insert(self, val):
        x, y = self.selected

        if self.cubes[x][y].value == 0:
            self.cubes[x][y].set(val)
            self.update_model()

            if possible(self.model, x, y, val) and solve(self.model):
                self.cubes[x][y].flag = 2
                return True
            else:
                self.cubes[x][y].set(0)
                self.cubes[x][y].set_temp(0)
                self.cubes[x][y].flag = 1
                self.update_model()
                return False

    # Setting temporary value to the selected cell
    def temp(self, val):
        x, y = self.selected
        self.cubes[x][y].set_temp(val)

    # Draw the sudoku grid and all the values and temporary values of each cells
    def draw_window(self, window):

        # Draw Grid Lines
        gap = self.width / 9

        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                line_width = 4
            else:
                line_width = 1

            pygame.draw.line(window, BLACK, (0, i * gap), (self.width, i * gap), line_width)
            pygame.draw.line(window, BLACK, (i * gap, 0), (i * gap, self.height), line_width)

        # Draw Cubes
        for j in range(self.cols):
            for i in range(self.rows):
                self.cubes[i][j].draw(window)
                if self.auto:
                    pygame.time.delay(50)
                    pygame.display.update()

        self.auto = False

    # Selecting a cell by given coordinates
    def select(self, x, y):

        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False
                self.cubes[i][j].flag = 0

        self.cubes[x][y].selected = True
        print((x, y), self.cubes[x][y].value)
        self.selected = (x, y)

    # Clearing temporary values from the selected cell
    def clear(self):
        x, y = self.selected
        if self.cubes[x][y].value == 0:
            self.cubes[x][y].set_temp(0)

    # Returning coordinates of a cell according to the the clicked position of mouse
    def click(self, pos):

        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9

            y = int(pos[0] / gap)
            x = int(pos[1] / gap)

            return (x, y)
        else:
            return None

    # Checking if puzzle is finished
    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True


# Cube class for representing each cell
class Cube:
    ROWS = 9
    COLS = 9

    def __init__(self, value, x, y, width, height):
        self.value = value
        self.temp = 0

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.selected = False
        self.flag = 0

    # Draw the values inside the cell and color of border according the type of selection
    def draw(self, window):

        gap = self.width / 9

        x1 = self.x * gap
        y1 = self.y * gap

        # Drawing main value if valid or the temporary value if set and main value is 0
        if self.value == 0 and self.temp != 0:
            text = DEFAULT_FONT.render(str(self.temp), True, GREY)
            window.blit(text, (y1 + 5, x1 + 5))
        elif self.value != 0:
            text = DEFAULT_FONT.render(str(self.value), True, BLACK)
            window.blit(text, (y1 + (gap - text.get_width()) / 2, x1 + (gap - text.get_height()) / 2))

        # Draw the color of border of cell according to flag value
        if self.selected:
            if self.flag == 1:
                pygame.draw.rect(window, RED, (y1, x1, gap, gap), 3)
            elif self.flag == 2:
                pygame.draw.rect(window, GREEN, (y1, x1, gap, gap), 3)
            else:
                pygame.draw.rect(window, BLUE, (y1, x1, gap, gap), 3)

    # Setting main value of cell
    def set(self, val):
        self.value = val

    # Setting temporary value of cell
    def set_temp(self, val):
        self.temp = val


# Redrawing window at every iteration
def redraw_window(window, board, time, strikes, diff):
    window.fill(WHITE)

    # Draw time
    text = DEFAULT_FONT.render("Time: " + format_time(time), True, BLACK)
    window.blit(text, (WIDTH - text.get_width() - 20, HEIGHT - text.get_height() - 15))

    # Draw buttons
    gap = board.width // 9

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    x, y = 3 * gap, HEIGHT - B_HEIGHT - 15

    b1 = pygame.Rect(x, y, B_WIDTH, B_HEIGHT)
    b2 = pygame.Rect(x + 2 * gap, y, B_WIDTH, B_HEIGHT)

    if y < mouse[1] < y + B_HEIGHT and x < mouse[0] < x + B_WIDTH:
        pygame.draw.rect(window, GREEN, b1)
    else:
        pygame.draw.rect(window, GREEN, b1, 3)

    if y < mouse[1] < y + B_HEIGHT and x + 2 * gap < mouse[0] < x + 2 * gap + B_WIDTH:
        pygame.draw.rect(window, RED, b2)
    else:
        pygame.draw.rect(window, RED, b2, 3)

    # Button Texts
    text1 = SMALL_FONT.render("Solve", True, BLACK)
    text2 = SMALL_FONT.render("Quit", True, BLACK)

    window.blit(text1, (x + (B_WIDTH - text1.get_width()) // 2, y + (B_HEIGHT - text1.get_height()) // 2))
    window.blit(text2, (x + 2 * gap + (B_WIDTH - text2.get_width()) // 2, y + (B_HEIGHT - text2.get_height()) // 2))

    # Draw Strikes
    if strikes == 1:
        text = LARGE_FONT.render("X", True, RED)
        window.blit(text, (20, HEIGHT - text.get_height() - 10))
    elif strikes == 2:
        text = LARGE_FONT.render("O", True, GREEN)
        window.blit(text, (20, HEIGHT - text.get_height() - 10))

    text3 = SMALL_FONT.render("[Difficulty: {}]".format(diff), True, BLACK)
    window.blit(text3, (gap, HEIGHT - text.get_height() - 10))

    # Draw grid and board
    board.draw_window(window)


# Converting Current Time for each iteration to string data
def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    t = " " + str(minute).zfill(2) + ":" + str(sec).zfill(2)
    return t


# Auto solver function
def auto_solve(window, board):
    board.update_model()

    if solve(board.model):
        for i in range(board.rows):
            for j in range(board.cols):
                board.cubes[i][j].value = board.model[i][j]
                board.auto = True
        return True
    else:
        return False


# Winner Text
def draw_winner(window, text, color=GREEN):
    # border_text = BORDER_FONT.render(text, True, BLACK)
    draw_text = WINNER_FONT.render(text, True, WHITE)

    # Drawing border using border rendering function
    window.blit(render(text, WINNER_FONT, color, BLACK),
                ((WIDTH - draw_text.get_width()) / 2, (WIDTH - draw_text.get_height()) / 2))

    # window.blit(border_text, ((WIDTH - draw_text.get_width()) / 2, (WIDTH - draw_text.get_height()) / 2))
    # window.blit(draw_text, ((WIDTH - draw_text.get_width()) / 2, (WIDTH - draw_text.get_height()) / 2))

    # Updating display on the screen
    pygame.display.update()

    # Waiting for 3000 milliseconds for keeping the text at display
    pygame.time.delay(3000)


# Looser Text
def draw_lose(window, text, color=RED):
    # border_text = BORDER_FONT.render(text, True, BLACK)
    draw_text = LOSE_FONT.render(text, True, WHITE)

    # Drawing border using border rendering function
    window.blit(render(text, LOSE_FONT, color, BLACK),
                ((WIDTH - draw_text.get_width()) / 2, (WIDTH - draw_text.get_height()) / 2))

    # window.blit(border_text, ((WIDTH - draw_text.get_width()) / 2, (WIDTH - draw_text.get_height()) / 2))
    # window.blit(draw_text, ((WIDTH - draw_text.get_width()) / 2, (WIDTH - draw_text.get_height()) / 2))

    # Updating display on the screen
    pygame.display.update()

    # Waiting for 1400 milliseconds for keeping the text at display
    pygame.time.delay(1400)


# Menu for selecting difficulty
def menu(window):
    run = True
    clock = pygame.time.Clock()

    diff = 0

    while run:
        for event in pygame.event.get():
            # If quit button of window pressed
            if event.type == pygame.QUIT:
                text = "Exiting ..."
                draw_lose(window, text, RED)
                run = False
                pygame.quit()

            # If any key is pressed
            if event.type == pygame.KEYDOWN:
                # Exiting if pressed X on the keyboard
                if event.key == pygame.K_x:
                    text = "Exiting ..."
                    draw_lose(window, text, RED)
                    run = False
                    pygame.quit()

            # If mouse is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()  # Mouse pointer position

                b_WIDTH = B_WIDTH + 20
                b_HEIGHT = B_WIDTH + 10

                gap = WIDTH // 9
                x1, x2, x3, x4 = gap * 1, gap * 3, gap * 5, gap * 7
                y = (HEIGHT - B_HEIGHT) // 2

                # Selection of difficulty according to the position of clicked pointer
                if y < mouse[1] < y + b_HEIGHT and x1 < mouse[0] < x1 + b_WIDTH:
                    diff = 1
                    run = False

                if y < mouse[1] < y + b_HEIGHT and x2 < mouse[0] < x2 + b_WIDTH:
                    diff = 2
                    run = False

                if y < mouse[1] < y + b_HEIGHT and x3 < mouse[0] < x3 + b_WIDTH:
                    diff = 3
                    run = False

                if y < mouse[1] < y + b_HEIGHT and x4 < mouse[0] < x4 + b_WIDTH:
                    diff = 4
                    run = False

        # Grayish background
        window.fill((230, 230, 230))

        # Draw buttons
        mouse = pygame.mouse.get_pos()

        b_WIDTH = B_WIDTH + 20
        b_HEIGHT = B_WIDTH + 10

        gap = WIDTH // 9
        x1, x2, x3, x4 = gap * 1, gap * 3, gap * 5, gap * 7
        y = (HEIGHT - b_HEIGHT) // 2

        # Draw buttons
        b1 = pygame.Rect(x1, y, b_WIDTH, b_HEIGHT)
        b2 = pygame.Rect(x2, y, b_WIDTH, b_HEIGHT)
        b3 = pygame.Rect(x3, y, b_WIDTH, b_HEIGHT)
        b4 = pygame.Rect(x4, y, b_WIDTH, b_HEIGHT)

        # Button colors
        if y < mouse[1] < y + b_HEIGHT and x1 < mouse[0] < x1 + b_WIDTH:
            pygame.draw.rect(window, (117, 172, 112), b1)
        else:
            pygame.draw.rect(window, (117, 172, 112), b1, 3)

        if y < mouse[1] < y + b_HEIGHT and x2 < mouse[0] < x2 + b_WIDTH:
            pygame.draw.rect(window, (204, 197, 110), b2)
        else:
            pygame.draw.rect(window, (204, 197, 110), b2, 3)

        if y < mouse[1] < y + b_HEIGHT and x3 < mouse[0] < x3 + b_WIDTH:
            pygame.draw.rect(window, (199, 129, 48), b3)
        else:
            pygame.draw.rect(window, (199, 129, 48), b3, 3)

        if y < mouse[1] < y + b_HEIGHT and x4 < mouse[0] < x4 + b_WIDTH:
            pygame.draw.rect(window, (207, 68, 68), b4)
        else:
            pygame.draw.rect(window, (207, 68, 68), b4, 3)

        # Button Texts
        text1 = SMALL_FONT.render("Easy", True, BLACK)
        text2 = SMALL_FONT.render("Medium", True, BLACK)
        text3 = SMALL_FONT.render("Hard", True, BLACK)
        text4 = SMALL_FONT.render("Evil", True, BLACK)

        window.blit(text1, (x1 + (b_WIDTH - text1.get_width()) // 2, y + (b_HEIGHT - text1.get_height()) // 2))
        window.blit(text2, (x2 + (b_WIDTH - text2.get_width()) // 2, y + (b_HEIGHT - text2.get_height()) // 2))
        window.blit(text3, (x3 + (b_WIDTH - text3.get_width()) // 2, y + (b_HEIGHT - text3.get_height()) // 2))
        window.blit(text4, (x4 + (b_WIDTH - text4.get_width()) // 2, y + (b_HEIGHT - text4.get_height()) // 2))

        # Updating display at every iteration
        pygame.display.update()

        # Fixing number of iterations every second
        clock.tick(60)

    # Returning selected difficulty to main loop
    return diff


# Main function containing main loop for the game
def main():
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    # Game title
    pygame.display.set_caption("Sudoku")

    # Game icon
    SUDOKU_ICON = pygame.image.load(os.path.join('Images', 'sudoku_icon.jpg'))
    pygame.display.set_icon(SUDOKU_ICON)

    # Difficulty selected from main menu window
    diff = menu(window)

    # Initializing the Board
    board = Board(ROWS, COLS, WIDTH, WIDTH, diff)

    # Stores last key pressed
    key = None

    # Stores Current time
    clock = pygame.time.Clock()

    # Stores starting time of the game
    start = time.time()

    # Stores type of strike
    strikes = 0

    run = True
    while run:
        # Time since game has started
        play_time = round(time.time() - start)

        # Iterating every pygame events
        for event in pygame.event.get():
            # If quit button on the window is pressed
            if event.type == pygame.QUIT:
                text = "Exiting.."
                draw_lose(window, text, RED)
                run = False
                pygame.quit()

            # If any keyboard key is pressed
            if event.type == pygame.KEYDOWN and board.selected:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9

                # Navigating to neighbouring cells using keyboard arrows
                if event.key == pygame.K_UP:
                    if board.selected:
                        x, y = board.selected
                        board.select(max(0, x - 1), y)
                if event.key == pygame.K_DOWN:
                    if board.selected:
                        x, y = board.selected
                        board.select(min(board.rows - 1, x + 1), y)
                if event.key == pygame.K_LEFT:
                    if board.selected:
                        x, y = board.selected
                        board.select(x, max(0, y - 1))
                if event.key == pygame.K_RIGHT:
                    if board.selected:
                        x, y = board.selected
                        board.select(x, min(board.cols - 1, y + 1))

                # Removing temporary value from selected cell if empty
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                # Entering the temporary value of selected cell and checking if valid if selected cell is empty,
                # by pressing Return Key on the keyboard
                if event.key == pygame.K_RETURN:
                    x, y = board.selected

                    if board.cubes[x][y].temp != 0:

                        if board.insert(board.cubes[x][y].temp):
                            print("Success!")
                            strikes = 2
                        else:
                            print("Wrong.")
                            strikes = 1

                        key = None

                    # Checking if puzzle finished
                    if board.is_finished():
                        print("Puzzle completed !!")
                        text = "Puzzle Completed: [{}]".format(format_time(play_time))
                        draw_winner(window, text)
                        run = False

            # If any key pressed on keyboard
            if event.type == pygame.KEYDOWN:
                # Auto solving the puzzle if possible on pressing Space key on the keyboard
                if event.key == pygame.K_SPACE:
                    if auto_solve(window, board):
                        print("Puzzle auto solved !!")
                    else:
                        print("Puzzle cannot be solved..")
                        text = "Puzzle cannot be solved.."
                        draw_lose(window, text, RED)
                        run = False

                # Exiting the game if X key is pressed on the keyboard
                if event.key == pygame.K_x:
                    text = "Exiting ..."
                    draw_lose(window, text, RED)
                    run = False

            # If mouse button clicked selecting a cell if exists at the position
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Getting the position of the mouse pointer
                pos = pygame.mouse.get_pos()

                # Getting coordinates on the grid of the pointer
                clicked = board.click(pos)

                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

                gap = board.width // 9
                x, y = 3 * gap, HEIGHT - B_HEIGHT - 15

                # Auto solving if possible when Solve button is clicked
                if y < pos[1] < y + B_HEIGHT and x < pos[0] < x + B_WIDTH:
                    if auto_solve(window, board):
                        print("Puzzle auto solved !!")
                    else:
                        print("Puzzle cannot be solved..")
                        text = "Puzzle cannot be solved.."
                        draw_lose(window, text, RED)
                        run = False

                # Quiting when Quit button is clicked
                if y < pos[1] < y + B_HEIGHT and x + 2 * gap < pos[0] < x + 2 * gap + B_WIDTH:
                    text = "Exiting ..."
                    draw_lose(window, text, RED)
                    run = False

            # Setting the temporary value on the selected key if number key is pressed
            if board.selected and key != None:
                board.temp(key)

            # Drawing the board at every iteration
            redraw_window(window, board, play_time, strikes, diff)

            # Updating display at every iteration
            pygame.display.update()

            # Fixing number of iterations per second
            clock.tick(60)


if __name__ == "__main__":
    main()

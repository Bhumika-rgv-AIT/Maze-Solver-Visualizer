import pygame
import random
import time
import heapq
from collections import deque

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 50, 50
CELL_SIZE = WIDTH // COLS
VISUALIZATION_DELAY = 0.002
WALL_PROBABILITY = 0.35

# Colors
BLACK = (0, 0, 0)  # Walls
WHITE = (200, 200, 200)  # Paths
RED = (255, 0, 0)  # Start
GREEN = (0, 255, 0)  # End
BLUE = (0, 0, 255)  # Visited nodes
YELLOW = (255, 255, 0)  # Final shortest path

# Algorithm Colors
DFS_COLOR = (247, 37, 133)
BFS_COLOR = (114, 9, 183)
ASTAR_COLOR = (58, 12, 163)
DIJKSTRA_COLOR = (67, 97, 238)

screen = None
solve_button = None
stop_button = None
randomize_button = None
toggle_button = None


# Heuristic function for A*
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Check if a maze is solvable using BFS
def is_solvable(maze, start, end):
    queue = deque([start])
    visited = set()
    rows, cols = len(maze), len(maze[0])
    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < rows and 0 <= new_y < cols and maze[new_x][new_y] == 0:
                queue.append((new_x, new_y))
    return False


# Carve a random route so larger mazes are always generated quickly.
def carve_guaranteed_path(maze, start, end):
    x, y = start
    maze[x][y] = 0

    while (x, y) != end:
        choices = []
        if x < end[0]:
            choices.append((x + 1, y))
        elif x > end[0]:
            choices.append((x - 1, y))
        if y < end[1]:
            choices.append((x, y + 1))
        elif y > end[1]:
            choices.append((x, y - 1))

        x, y = random.choice(choices)
        maze[x][y] = 0


# Generate a solvable maze
def generate_solvable_maze(rows, cols, start, end):
    maze = [
        [1 if random.random() < WALL_PROBABILITY else 0 for _ in range(cols)]
        for _ in range(rows)
    ]
    carve_guaranteed_path(maze, start, end)
    maze[start[0]][start[1]] = 0
    maze[end[0]][end[1]] = 0
    return maze


# Draw the maze
def draw_maze(maze, path, final_path, start, end):
    screen.fill(BLACK)
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if maze[row][col] == 0 else BLACK
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for x, y in path:
        pygame.draw.rect(screen, BLUE, (y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for x, y in final_path:
        pygame.draw.rect(screen, YELLOW, (y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (start[1] * CELL_SIZE, start[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GREEN, (end[1] * CELL_SIZE, end[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Solve maze using different algorithms
def solve_maze(maze, start, end, algorithm):
    if algorithm in ["A*", "Dijkstra"]:
        frontier = [(0, start)]
        cost_so_far = {start: 0}
    elif algorithm == "BFS":
        frontier = deque([start])
    else:
        frontier = [start]

    came_from = {start: None}
    visited = set()
    path = []
    found = False

    while frontier:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

        if algorithm in ["A*", "Dijkstra"]:
            _, (x, y) = heapq.heappop(frontier)
        elif algorithm == "BFS":
            x, y = frontier.popleft()
        else:
            x, y = frontier.pop()

        if (x, y) == end:
            found = True
            break
        if (x, y) in visited:
            continue

        visited.add((x, y))
        path.append((x, y))
        draw_maze(maze, path, [], start, end)
        pygame.display.update()
        time.sleep(VISUALIZATION_DELAY)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < ROWS and 0 <= new_y < COLS and maze[new_x][new_y] == 0 and (new_x, new_y) not in visited:
                priority = 0
                if algorithm == "A*":
                    priority = cost_so_far[(x, y)] + 1 + heuristic((new_x, new_y), end)
                elif algorithm == "Dijkstra":
                    priority = cost_so_far[(x, y)] + 1
                if algorithm in ["A*", "Dijkstra"]:
                    heapq.heappush(frontier, (priority, (new_x, new_y)))
                    cost_so_far[(new_x, new_y)] = cost_so_far[(x, y)] + 1
                else:
                    frontier.append((new_x, new_y))
                came_from[(new_x, new_y)] = (x, y)

    if not found:
        return []

    final_path = []
    cur = end
    while cur is not None:
        final_path.append(cur)
        cur = came_from.get(cur)
    return final_path[::-1]


# Draw Buttons
def draw_buttons(current_algo):
    pygame.draw.rect(screen, (0, 255, 0), solve_button)
    pygame.draw.rect(screen, (255, 0, 0), stop_button)
    pygame.draw.rect(screen, (255, 255, 0), randomize_button)

    color_map = {"DFS": DFS_COLOR, "BFS": BFS_COLOR, "A*": ASTAR_COLOR, "Dijkstra": DIJKSTRA_COLOR}
    pygame.draw.rect(screen, color_map[current_algo], toggle_button)

    font = pygame.font.Font(None, 24)
    screen.blit(font.render("Solve", True, BLACK), (solve_button.x + 20, solve_button.y + 5))
    screen.blit(font.render("Clear", True, BLACK), (stop_button.x + 20, stop_button.y + 5))
    screen.blit(font.render("Randomize", True, BLACK), (randomize_button.x + 10, randomize_button.y + 5))
    screen.blit(font.render(f"Algo: {current_algo}", True, BLACK), (toggle_button.x + 10, toggle_button.y + 5))

    pygame.display.update()


def main():
    global screen, solve_button, stop_button, randomize_button, toggle_button

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))  # Extra space for buttons
    pygame.display.set_caption("Maze Solver")

    start, end = (0, 0), (ROWS - 1, COLS - 1)
    maze = generate_solvable_maze(ROWS, COLS, start, end)
    final_path = []
    current_algo = "DFS"

    solve_button = pygame.Rect(50, HEIGHT + 10, 100, 30)
    stop_button = pygame.Rect(180, HEIGHT + 10, 100, 30)
    randomize_button = pygame.Rect(310, HEIGHT + 10, 120, 30)
    toggle_button = pygame.Rect(450, HEIGHT + 10, 120, 30)

    clock = pygame.time.Clock()
    running = True
    while running:
        draw_maze(maze, [], final_path, start, end)
        draw_buttons(current_algo)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if solve_button.collidepoint(event.pos):
                    solved_path = solve_maze(maze, start, end, current_algo)
                    if solved_path is None:
                        running = False
                    else:
                        final_path = solved_path
                elif stop_button.collidepoint(event.pos):
                    final_path = []
                elif randomize_button.collidepoint(event.pos):
                    maze = generate_solvable_maze(ROWS, COLS, start, end)
                    final_path = []
                elif toggle_button.collidepoint(event.pos):
                    algorithms = ["DFS", "BFS", "A*", "Dijkstra"]
                    current_algo = algorithms[(algorithms.index(current_algo) + 1) % len(algorithms)]

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

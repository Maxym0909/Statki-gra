import pygame
import socket
import threading
import pickle
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 800
GRID_SIZE = 10
CELL_SIZE = 50
BOARD_GAP = CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gra w Statki")

# Board positions
LEFT_BOARD_X = (WIDTH - (GRID_SIZE * CELL_SIZE * 2 + BOARD_GAP)) // 2
RIGHT_BOARD_X = LEFT_BOARD_X + GRID_SIZE * CELL_SIZE + BOARD_GAP
BOARD_Y = 100

# Buttons
BUTTON_START = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 120, 50)
BUTTON_INFO = pygame.Rect(WIDTH // 2 + 30, HEIGHT - 100, 120, 50)
BUTTON_BACK = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
BUTTON_CONNECT = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

# Letters and numbers
LETTERS = "ABCDEFGHIJ"
NUMBERS = [str(i) for i in range(1, 11)]

# Screen modes
screen_mode = "connect"

# Path to ship images folder
IMAGE_FOLDER = "D:\\Statki_Gra\\Ship_Game\\ship_images"

# Load ship images
ship_images = {}
IMAGE_FOLDER = "ship_images"  # Upewniamy się, że ścieżka jest poprawna
print(f"Sprawdzanie folderu: {os.path.abspath(IMAGE_FOLDER)}")  # Debug: pokaże absolutną ścieżkę

try:
    # Próbujemy załadować obrazy
    ship_images = {
        "4_h": pygame.image.load(os.path.join(IMAGE_FOLDER, "ship_4_h.png")),
        "4_v": pygame.image.load(os.path.join(IMAGE_FOLDER, "ship_4_v.png")),
        "3_h": pygame.image.load(os.path.join(IMAGE_FOLDER, "ship_3_h.png")),
        "3_v": pygame.image.load(os.path.join(IMAGE_FOLDER, "ship_3_v.png")),
        "2_h": pygame.image.load(os.path.join(IMAGE_FOLDER, "ship_2_h.png")),
        "2_v": pygame.image.load(os.path.join(IMAGE_FOLDER, "ship_2_v.png")),
    }
    print("Obrazy załadowane pomyślnie.")
except FileNotFoundError as e:
    print(f"Błąd: Nie znaleziono plików obrazów: {e}")
except Exception as e:
    print(f"Błąd ładowania obrazów: {e}")
else:
    # Skalowanie obrazów po załadowaniu
    for key in ship_images:
        if ship_images[key] is not None:
            if "h" in key:
                size = (int(key[0]) * CELL_SIZE, CELL_SIZE)
            else:
                size = (CELL_SIZE, int(key[0]) * CELL_SIZE)
            ship_images[key] = pygame.transform.scale(ship_images[key], size)
if not ship_images or any(value is None for value in ship_images.values()):
    print("Nie udało się załadować wszystkich obrazów. Używam prostokątów jako zastępstwo.")
    ship_images = {key: None for key in ["4_h", "4_v", "3_h", "3_v", "2_h", "2_v"]}

# Scale images if needed
for key in ship_images:
    if ship_images[key] is not None:
        if "h" in key:
            size = (int(key[0]) * CELL_SIZE, CELL_SIZE)
        else:
            size = (CELL_SIZE, int(key[0]) * CELL_SIZE)
        ship_images[key] = pygame.transform.scale(ship_images[key], size)

# Game variables
placing_ships = True
game_started = False
game_over = False
winner = None
ships = []
ship_objects = [
    {"size": (4, 1), "pos": (50, 650), "placed": False, "dragging": False, "cells": [], "orientation": "h", "image": ship_images["4_h"]},
    {"size": (3, 1), "pos": (300, 650), "placed": False, "dragging": False, "cells": [], "orientation": "h", "image": ship_images["3_h"]},
    {"size": (3, 1), "pos": (550, 650), "placed": False, "dragging": False, "cells": [], "orientation": "h", "image": ship_images["3_h"]},
    {"size": (2, 1), "pos": (50, 750), "placed": False, "dragging": False, "cells": [], "orientation": "h", "image": ship_images["2_h"]},
    {"size": (2, 1), "pos": (200, 750), "placed": False, "dragging": False, "cells": [], "orientation": "h", "image": ship_images["2_h"]},
    {"size": (2, 1), "pos": (350, 750), "placed": False, "dragging": False, "cells": [], "orientation": "h", "image": ship_images["2_h"]},
]
my_shots = []
enemy_shots = []
client_socket = None
input_text = ""
my_turn = False
players_ready = 0

# Reset game state function
def reset_game_state():
    global placing_ships, game_started, game_over, winner, ships, ship_objects, my_shots, enemy_shots, input_text, my_turn, players_ready
    placing_ships = True
    game_started = False
    game_over = False
    winner = None
    ships.clear()
    my_shots.clear()
    enemy_shots.clear()
    for ship in ship_objects:
        ship["placed"] = False
        ship["cells"] = []
        if ship["size"][0] == 4 or ship["size"][1] == 4:
            ship["pos"] = (50, 650)
        elif ship["size"][0] == 3 or ship["size"][1] == 3:
            idx = ship_objects.index(ship) - 1
            ship["pos"] = (300 + idx * 250, 650)
        elif ship["size"][0] == 2 or ship["size"][1] == 2:
            idx = ship_objects.index(ship) - 3
            ship["pos"] = (50 + idx * 150, 750)
    input_text = ""
    my_turn = False
    players_ready = 0

def draw_grid(offset_x, offset_y):
    for x in range(0, GRID_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x + offset_x, offset_y), (x + offset_x, offset_y + GRID_SIZE * CELL_SIZE))
    for y in range(0, GRID_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (offset_x, y + offset_y), (offset_x + GRID_SIZE * CELL_SIZE, y + offset_y))

def draw_coordinates(offset_x, offset_y):
    font = pygame.font.Font(None, 30)
    for i in range(GRID_SIZE):
        text = font.render(NUMBERS[i], True, BLACK)
        screen.blit(text, (offset_x - 30, offset_y + i * CELL_SIZE + 15))
    for i in range(GRID_SIZE):
        text = font.render(LETTERS[i], True, BLACK)
        screen.blit(text, (offset_x + i * CELL_SIZE + 15, offset_y - 30))

def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect)
    font = pygame.font.Font(None, 30)
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (rect.x + 30, rect.y + 15))

def draw_labels():
    font = pygame.font.Font(None, 40)
    text_my = font.render("MY BOARD", True, BLACK)
    text_enemy = font.render("ENEMY BOARD", True, BLACK)
    screen.blit(text_my, (LEFT_BOARD_X + CELL_SIZE * 2, BOARD_Y + GRID_SIZE * CELL_SIZE + 10))
    screen.blit(text_enemy, (RIGHT_BOARD_X + CELL_SIZE * 1.5, BOARD_Y + GRID_SIZE * CELL_SIZE + 10))

def draw_turn_message():
    if not game_over and game_started:
        font = pygame.font.Font(None, 50)
        if my_turn:
            text = font.render("Twoja tura", True, GREEN)
        else:
            text = font.render("Tura przeciwnika", True, RED)
        screen.blit(text, (WIDTH // 2 - 100, 10))

def draw_game_over_message():
    if game_over:
        font = pygame.font.Font(None, 70)
        if winner:
            text = font.render("Wygrałeś!", True, GREEN)
        else:
            text = font.render("Przegrałeś!", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, 700))
        screen.blit(text, text_rect)

def draw_ships_to_place():
    for ship in ship_objects:
        if not ship["placed"]:
            x, y = ship["pos"]
            if ship["image"] is not None:
                screen.blit(ship["image"], (x, y))
            else:
                w, h = ship["size"]
                pygame.draw.rect(screen, GREEN, (x, y, w * CELL_SIZE, h * CELL_SIZE))

def draw_ready_status():
    font = pygame.font.Font(None, 50)
    text = font.render(f"Gracze gotowi: {players_ready}/2", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 150, 20))

def place_ship_on_board(ship, cell):
    col, row = cell
    w, h = ship["size"]
    if col + w > GRID_SIZE or row + h > GRID_SIZE:
        return False
    new_cells = [(col + i, row + j) for i in range(w) for j in range(h)]
    for existing_cell in ships:
        if existing_cell in new_cells:
            return False
    forbidden_zone = set()
    for x in range(col - 1, col + w + 1):
        for y in range(row - 1, row + h + 1):
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                forbidden_zone.add((x, y))
    for existing_cell in ships:
        if existing_cell in forbidden_zone:
            return False
    ship["cells"] = new_cells
    ship["placed"] = True
    ships.extend(new_cells)
    return True

def get_ship_at_pos(pos):
    x, y = pos
    for ship in ship_objects:
        if not ship["placed"]:
            ship_x, ship_y = ship["pos"]
            w, h = ship["size"]
            if ship_x <= x < ship_x + w * CELL_SIZE and ship_y <= y < ship_y + h * CELL_SIZE:
                return ship
    return None

def rotate_ship(ship):
    if not ship["placed"]:
        ship["size"] = (ship["size"][1], ship["size"][0])
        ship_length = max(ship["size"])
        ship["orientation"] = "v" if ship["size"][0] == 1 else "h"
        ship["image"] = ship_images[f"{ship_length}_{ship['orientation']}"]

def shoot(cell):
    global my_turn
    if not placing_ships and my_turn and cell not in [shot[0] for shot in my_shots]:
        my_shots.append((cell, False))
        client_socket.send(pickle.dumps(("shot", cell)))

def get_cell(pos):
    x, y = pos
    if LEFT_BOARD_X <= x < LEFT_BOARD_X + GRID_SIZE * CELL_SIZE and BOARD_Y <= y < BOARD_Y + GRID_SIZE * CELL_SIZE:
        col = (x - LEFT_BOARD_X) // CELL_SIZE
        row = (y - BOARD_Y) // CELL_SIZE
        return (col, row), 0
    elif RIGHT_BOARD_X <= x < RIGHT_BOARD_X + GRID_SIZE * CELL_SIZE and BOARD_Y <= y < BOARD_Y + GRID_SIZE * CELL_SIZE:
        col = (x - RIGHT_BOARD_X) // CELL_SIZE
        row = (y - BOARD_Y) // CELL_SIZE
        return (col, row), 1
    return None, None

def receive_data():
    global my_turn, game_over, winner, players_ready, game_started, screen_mode, placing_ships
    while running:
        try:
            data = pickle.loads(client_socket.recv(1024))
            print(f"Received: {data}")
            if isinstance(data, tuple) and data[0] == "shot":
                cell = (int(data[1][0]), int(data[1][1]))
                if cell not in [shot[0] for shot in enemy_shots]:
                    hit = cell in ships
                    enemy_shots.append((cell, hit))
                    client_socket.send(pickle.dumps(("hit" if hit else "miss", cell)))
                    if all(cell in [shot[0] for shot in enemy_shots if shot[1]] for cell in ships):
                        game_over = True
                        winner = False
                        client_socket.send(pickle.dumps(("game_over", False)))
                    my_turn = True
            elif isinstance(data, tuple) and data[0] in ["hit", "miss"]:
                cell = (int(data[1][0]), int(data[1][1]))
                for i, (shot_cell, _) in enumerate(my_shots):
                    if shot_cell == cell:
                        my_shots[i] = (cell, data[0] == "hit")
                hits = [shot for shot in my_shots if shot[1]]
                if len(hits) == len(ships):
                    game_over = True
                    winner = True
                    client_socket.send(pickle.dumps(("game_over", True)))
            elif data == "your_turn":
                my_turn = True
            elif data == "wait":
                my_turn = False
            elif isinstance(data, tuple) and data[0] == "game_over":
                game_over = True
                winner = data[1]
            elif isinstance(data, tuple) and data[0] == "players_ready":
                players_ready = data[1]
                if players_ready == 2:
                    game_started = True
                    placing_ships = False
            elif isinstance(data, tuple) and data[0] == "opponent_disconnected":
                screen_mode = "connect"
                reset_game_state()
                print("Opponent disconnected. Returning to connect screen.")
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Server disconnected: {e}")
            screen_mode = "connect"
            reset_game_state()
            break

def connect_to_server(ip):
    global client_socket, running
    # Reset game state before connecting to ensure a fresh start
    reset_game_state()
    PORT = 5555
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, PORT))
        threading.Thread(target=receive_data, daemon=True).start()
        return True
    except Exception as e:
        print(f"Connection error: {e}")
        return False

if __name__ == "__main__":
    running = True
    dragging_ship = None

    while running:
        screen.fill(WHITE)

        if screen_mode == "connect":
            font = pygame.font.Font(None, 36)
            text = font.render("Wpisz IP serwera:", True, BLACK)
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
            input_surf = font.render(input_text, True, BLACK)
            pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 40))
            screen.blit(input_surf, (WIDTH // 2 - 140, HEIGHT // 2 - 40))
            draw_button(BUTTON_CONNECT, "CONNECT")

        elif screen_mode == "game":
            draw_grid(LEFT_BOARD_X, BOARD_Y)
            draw_grid(RIGHT_BOARD_X, BOARD_Y)
            draw_coordinates(LEFT_BOARD_X, BOARD_Y)
            draw_coordinates(RIGHT_BOARD_X, BOARD_Y)
            draw_labels()
            if not game_started:
                draw_button(BUTTON_START, "START")
                draw_ready_status()
            draw_button(BUTTON_INFO, "INFO")
            draw_turn_message()
            draw_game_over_message()

            if placing_ships:
                draw_ships_to_place()

            for ship in ship_objects:
                if ship["placed"]:
                    col, row = ship["cells"][0]
                    x = LEFT_BOARD_X + col * CELL_SIZE
                    y = BOARD_Y + row * CELL_SIZE
                    if ship["image"] is not None:
                        screen.blit(ship["image"], (x, y))
                    else:
                        w, h = ship["size"]
                        pygame.draw.rect(screen, GREEN, (x, y, w * CELL_SIZE, h * CELL_SIZE))

            for cell, hit in enemy_shots:
                color = RED if hit else BLUE
                pygame.draw.rect(screen, color, (LEFT_BOARD_X + cell[0] * CELL_SIZE, BOARD_Y + cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            for cell, hit in my_shots:
                color = RED if hit else BLUE
                pygame.draw.rect(screen, color, (RIGHT_BOARD_X + cell[0] * CELL_SIZE, BOARD_Y + cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        elif screen_mode == "info":
            font = pygame.font.Font(None, 36)
            text_lines = [
                "Zasady gry w Statki:",
                "1. Każdy gracz rozmieszcza swoje statki na planszy (MY BOARD).",
                "2. Po rozpoczęciu gry gracze na zmianę oddają strzały.",
                "3. Trafienie statku oznaczone jest kolorem czerwonym.",
                "4. Pudło oznaczone jest kolorem niebieskim.",
                "5. Wygrywa gracz, który pierwszy zatopi wszystkie statki przeciwnika.",
                "6. Kliknij prawym przyciskiem myszy, aby obrócić statek podczas rozmieszczania."
            ]
            y_offset = 200
            for line in text_lines:
                text_surf = font.render(line, True, BLACK)
                screen.blit(text_surf, (WIDTH // 2 - 300, y_offset))
                y_offset += 40
            draw_button(BUTTON_BACK, "BACK")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if client_socket:
                    client_socket.close()
                reset_game_state()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if screen_mode == "connect":
                        if BUTTON_CONNECT.collidepoint(event.pos):
                            if connect_to_server(input_text):
                                screen_mode = "game"
                    elif screen_mode == "game":
                        if not game_started and BUTTON_START.collidepoint(event.pos):
                            if all(ship["placed"] for ship in ship_objects):
                                placing_ships = False
                                client_socket.send(pickle.dumps(("ready", None)))
                        elif BUTTON_INFO.collidepoint(event.pos):
                            screen_mode = "info"
                        else:
                            cell, board = get_cell(event.pos)
                            if cell is not None and not game_over:
                                if board == 1 and not placing_ships:
                                    shoot(cell)
                            if placing_ships:
                                dragging_ship = get_ship_at_pos(event.pos)
                                if dragging_ship:
                                    dragging_ship["dragging"] = True
                    elif screen_mode == "info":
                        if BUTTON_BACK.collidepoint(event.pos):
                            screen_mode = "game"
                elif event.button == 3 and screen_mode == "game" and placing_ships:
                    ship = get_ship_at_pos(event.pos)
                    if ship:
                        rotate_ship(ship)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_ship and dragging_ship["dragging"]:
                    dragging_ship["dragging"] = False
                    cell, board = get_cell(event.pos)
                    if cell and board == 0:
                        if place_ship_on_board(dragging_ship, cell):
                            dragging_ship["pos"] = (LEFT_BOARD_X + cell[0] * CELL_SIZE, BOARD_Y + cell[1] * CELL_SIZE)
                        else:
                            if dragging_ship["size"][0] == 4 or dragging_ship["size"][1] == 4:
                                dragging_ship["pos"] = (50, 650)
                            elif dragging_ship["size"][0] == 3 or dragging_ship["size"][1] == 3:
                                idx = ship_objects.index(dragging_ship) - 1
                                dragging_ship["pos"] = (300 + idx * 250, 650)
                            elif( dragging_ship["size"][0] == 2 or dragging_ship["size"][1] == 2):
                                idx = ship_objects.index(dragging_ship) - 3
                                dragging_ship["pos"] = (50 + idx * 150, 750)
                    dragging_ship = None
            elif event.type == pygame.MOUSEMOTION and dragging_ship and dragging_ship["dragging"]:
                dragging_ship["pos"] = event.pos
            elif event.type == pygame.KEYDOWN and screen_mode == "connect":
                if event.key == pygame.K_RETURN:
                    if connect_to_server(input_text):
                        screen_mode = "game"
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        pygame.display.flip()

    pygame.quit()

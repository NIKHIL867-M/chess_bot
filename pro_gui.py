# pro_gui.py
import pygame
import os

pygame.init()

# Responsive Board Setup
DISPLAY_SIZE = min(pygame.display.Info().current_w, pygame.display.Info().current_h) * 0.85
WIDTH = HEIGHT = int(DISPLAY_SIZE)
ROWS, COLS = 8, 8
PADDING = int(WIDTH * 0.05)  # space for coordinates

SQUARE_SIZE = (WIDTH - 2 * PADDING) // COLS

# Pro Colors
LIGHT = (240, 238, 225)
DARK = (115, 92, 72)
HIGHLIGHT = (71, 160, 207)
SELECT = (33, 199, 115)
LAST_MOVE = (255, 211, 91)
BG = (31, 34, 40)

# Set up display
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pro Chess AI")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Segoe UI", int(SQUARE_SIZE * 0.24), bold=True)

# Load Images (PNG Only, Vector-style recommended)
IMAGES = {}

def load_images():
    pieces = ['k', 'q', 'r', 'b', 'h', 'p']
    colors = ['white', 'black']
    for color in colors:
        for piece in pieces:
            name = f"{color}({piece})"
            path = os.path.join("assets", f"{name}.png")
            IMAGES[name] = pygame.transform.smoothscale(
                pygame.image.load(path), (SQUARE_SIZE, SQUARE_SIZE)
            )

load_images()

def draw_coordinates(win):
    for i in range(ROWS):
        # Ranks (left side)
        txt = FONT.render(str(8-i), True, (170, 170, 170))
        win.blit(txt, (PADDING//3, PADDING + i * SQUARE_SIZE + SQUARE_SIZE//4))
        # Files (bottom)
        txt = FONT.render(chr(ord('a')+i), True, (170, 170, 170))
        win.blit(txt, (PADDING + i * SQUARE_SIZE + SQUARE_SIZE//3, HEIGHT - PADDING//1.2))

def draw_board(win, board, selected=None, valid_moves=None, last_move=None):
    win.fill(BG)
    # Board squares
    for r in range(ROWS):
        for c in range(COLS):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(
                win,
                color,
                (PADDING + c*SQUARE_SIZE, PADDING + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                border_radius=10,
            )
            # Last move highlight
            if last_move and (r, c) in last_move:
                pygame.draw.rect(
                    win,
                    LAST_MOVE,
                    (PADDING + c*SQUARE_SIZE, PADDING + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                    border_radius=12,
                    width=6,
                )
    # Valid moves
    if valid_moves:
        surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (*HIGHLIGHT, 120), surf.get_rect().inflate(-SQUARE_SIZE//2, -SQUARE_SIZE//2))
        for r, c in valid_moves:
            win.blit(surf, (PADDING + c*SQUARE_SIZE, PADDING + r*SQUARE_SIZE))

    # Selection highlight
    if selected:
        pygame.draw.rect(
            win,
            SELECT,
            (PADDING + selected[1]*SQUARE_SIZE, PADDING + selected[0]*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            border_radius=11, width=5,
        )
    # Pieces
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece:
                win.blit(
                    IMAGES[piece],
                    (PADDING + c*SQUARE_SIZE, PADDING + r*SQUARE_SIZE)
                )
    draw_coordinates(win)
    pygame.display.update()

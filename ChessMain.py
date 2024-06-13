# This file is for handling user input and displaying the current GameState object 

import pygame as p
import ChessEngine

print(p.__version__)

# Resolution of the board
WIDTH = HEIGHT = 512 # 400 is another good display option\
DIMENSION = 8 # Dimensions of a chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # Used for animations
IMAGES = {}

# Initialize a global dictionary of images. This is done only once in main
def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]

    for piece in pieces:
        image = p.image.load("imgs/" + piece + ".png")
        IMAGES[piece] = p.transform.scale(image, (SQ_SIZE, SQ_SIZE))
    # Note: We can access an image by saying 'IMAGES["wP"]'

# Main driver for our code. Handles user input and updating the graphics
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    loadImages() # Only do this before the while loop

    running = True

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        
        drawGameState(screen, gs)

        clock.tick(MAX_FPS)
        p.display.flip()

# Responsible for all the graphics within a current game state
def drawGameState(screen, gs):
    drawBoard(screen) # Draw the squares on the board
    # Add in piece highlighting or move suggestions later
    drawPieces(screen, gs.board) # Draw pieces on top of those squares

# Draw the squares on the board
def drawBoard(screen):
    colors = [p.Color("#eeeed2"), p.Color("#769656")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# We can combine drawPieces() & drawBoard() to make our graphics more efficient as
# both currently running a nested for loop of the same ranges

# Draw the pieces on the board
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": # If the piece is not an empty square '--'
                # Currently don't know what the function blit() does???
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()
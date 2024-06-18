# This file is for handling user input and displaying the current GameState object 

import pygame as p
import ChessEngine, ChessAI

# Resolution of the board
WIDTH = HEIGHT = 512 # 400 is another good display option\
DIMENSION = 8 # Dimensions of a chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 90 # Used for animations
IMAGES = {}

# Load sound effects
p.mixer.init()
moveSound = p.mixer.Sound("sfx/move.mp3")
captureSound = p.mixer.Sound("sfx/capture.mp3")
# ---------- Todo Add check sound effect ---------
# checkSound = p.mixer.Sound("sfx/check.mp3")
castleSound = p.mixer.Sound("sfx/castle.mp3")

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

    validMoves = gs.getValidMoves() # Generate valid moves for the start of the game
    moveMade = False # Flag variable for when a move is made

    animate = False # Flag variable for when we should animate a move

    loadImages() # Only do this before the while loop

    sqSelected = () # No square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = [] # Keeps track of the player's clicks (two tuples: [(6, 4), (4, 4)])

    gameOver = False
    playerOne = True # If a Human is playing white, then this will be True. If an AI is playing, then false
    playerTwo = False # Same as above but for black

    running = True
    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTurn:
                    location = p.mouse.get_pos() # (x, y) location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col): # Player clicked the same square twice
                        sqSelected = () # Deselect or undo move
                        playerClicks = [] # Clear the players clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # Append for both first and second clicks
                    if len(playerClicks) == 2: # If the player has clicked twice make a move
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())

                        for i in range(len(validMoves)):
                            if move == validMoves[i]: # Make sure that the move being made is valid
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # Reset player clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # Key Handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True # If a player undo's we need to generate a new set of valid moves
                    animate = False
                if e.key == p.K_r: # Reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
            
        # AI move finder
        if not gameOver and not isHumanTurn:
            AIMove = ChessAI.findRandomMove(validMoves) # Give the AI the current available moves
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        # If a valid move was made we then want to generate a new set of valid moves
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

# Highlight square selected and moves for piece selected
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"): # sqSelected is a piece that can be moved
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # Transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color("blue")) # Color of the selected piece
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))

            # Highlight moves available from the selected piece
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

# Responsible for all the graphics within a current game state
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draw the squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on top of those squares

# Draw the squares on the board
def drawBoard(screen):
    global colors
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


# Animating a move
def animateMove(move, screen, board, clock):
    global colors
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    totalTime = 0.1 # total time for the animation in seconds
    frameCount = int(totalTime * MAX_FPS)
    for frame in range(frameCount + 1):
        row = move.startRow + deltaRow * (frame / frameCount)
        col = move.startCol + deltaCol * (frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)

    # TODO: Add variable to disable sound effects

    # ---------- Add some way below to add check sound effect ----------
    if move.isCastleMove:
        castleSound.play()
    elif move.pieceCaptured == "--":
        moveSound.play()
    else:
        captureSound.play()

# Fix Game Over Text as it's not too unique or good looking
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()
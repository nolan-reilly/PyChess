# This file is for handling user input and displaying the current GameState object 

import pygame as p
import ChessEngine, ChessAI
import sys
from multiprocessing import Process, Queue

# Resolution of the board
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60 # Used for animations
IMAGES = {}

# Game Settings
is_sound_disabled = False

# Load game sound effects
p.mixer.init()
move_sound = p.mixer.Sound("sfx/move.mp3")
capture_sound = p.mixer.Sound("sfx/capture.mp3")
# TODO: Add check sound effect
# check_sound = p.mixer.Sound("sfx/check.mp3")
castle_sound = p.mixer.Sound("sfx/castle.mp3")

# Initialize a global dictionary of images. This is done only once in main
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]

    for piece in pieces:
        image = p.image.load("imgs/" + piece + ".png")
        IMAGES[piece] = p.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    # Note: We can access an image by saying 'IMAGES["wP"]'

# Main driver for our code. Handles user input and updating the graphics
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    game_state = ChessEngine.GameState()

    valid_moves = game_state.getValidMoves()
    move_made = False  # Flag variable for when a move is made

    animate = False  # Flag variable for when we should animate a move

    loadImages()  # Only do this before the while loop once
    
    square_selected = ()  # No square is selected, keep track of the last click of the user (tuple: (row, col))
    player_clicks = []  # Keeps track of the player's clicks (two tuples: [(6, 4), (4, 4)])

    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    player_one = True  # If a Human is playing white, then this will be True. If an AI is playing, then false
    player_two = False  # Same as above but for black

    running = True
    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            # Mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE

                    if square_selected == (row, col) or col >= 8:  # Player clicked the same square twice
                        square_selected = ()  # Deselect or undo move
                        player_clicks = []  # Clear the players clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # Append for both first and second clicks
                    if len(player_clicks) == 2 and human_turn:  # If the player has clicked twice make a move
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:  # Make sure that the move being made is valid
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # Reset player clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

            # Key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    game_state.undoMove()
                    move_made = True # If a player undo's we need to generate a new set of valid moves
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:  # Reset the board when 'r' is pressed
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        # AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        # If a valid move was made we then want to generate a new set of valid moves
        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawGameState(screen, game_state, valid_moves, square_selected)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

# Responsible for all the graphics within current game state
def drawGameState(screen, game_state, valid_moves, square_selected):
    drawBoard(screen)  # Draw the squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)  # Draw pieces on top of those squares

# Draw the squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color("#eeeed2"), p.Color("#769656")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
# We can combine drawPieces() & drawBoard() to make our graphics more efficient as
# both currently running a nested for loop of the same ranges

# Highlight square selected and moves for piece
def highlightSquares(screen, game_state, valid_moves, square_selected):
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('yellow'))
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):  # square_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))

# Draw the pieces on the board
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--": # If the piece is not an empty square '--'
                # Currently don't know what the function blit() does???
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draws the move log
def drawMoveLog(screen, game_state, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

# TODO: Fix the end game text to make it better looking
def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))

# Animating a move
def animateMove(move, screen, board, clock):
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    total_time = 0.1 # total time for the animation in seconds
    frame_count = int(total_time * MAX_FPS)
    for frame in range(frame_count + 1):
        row = move.start_row + d_row * (frame / frame_count)
        col = move.start_col + d_col * (frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        # Draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # Draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)

    if not is_sound_disabled:
        # ---------- Add some way below to add check sound effect ----------
        if move.is_castle_move:
            castle_sound.play()
        elif move.piece_captured == "--":
            move_sound.play()
        else:
            capture_sound.play()


if __name__ == "__main__":
    main()
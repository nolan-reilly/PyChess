# This file handles the AI's moves
import random

piece_score = {"p": 100, "N": 280, "B": 320, "R": 479, "Q": 929, "K": 0}

king_scores = [[-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-20, -30, -30, -40, -40, -30, -30, -20],
               [-10, -20, -20, -20, -20, -20, -20, -10],
               [20, 20, 0, 0, 0, 0, 20, 20],
               [20, 30, 10, 0, 0, 10, 30, 20]]

king_endgame_scores = [[-50, -40, -30, -20, -20, -30, -40, -50],
                       [-30, -20, -10, 0, 0, -10, -20, -30],
                       [-30, -10, 20, 30, 30, 20, -10, -30],
                       [-30, -10, 30, 40, 40, 30, -10, -30],
                       [-30, -10, 30, 40, 40, 30, -10, -30],
                       [-30, -10, 20, 30, 30, 20, -10, -30],
                       [-30, -30, 0, 0, 0, 0, -30, -30],
                       [-50, -30, -30, -30, -30, -30, -30, -50]]

knight_scores = [[-50, -40, -30, -30, -30, -30, -40, -50],
                 [-40, -20, 0, 0, 0, 0, -20, -40],
                 [-30, 0, 10, 15, 15, 10, 0, -30],
                 [-30, 5, 15, 20, 20, 15, 5, -30],
                 [-30, 0, 15, 20, 20, 15, 5, -30],
                 [-30, 5, 10, 15, 15, 10, 5, -30],
                 [-40, -20, 0, 5, 5, 0, -20, -40],
                 [-50, -40, -30, -30, -30, -30, -40, -50]]

bishop_scores = [[-20, -10, -10, -10, -10, -10, -10, -20],
                 [-10, 0, 0, 0, 0, 0, 0, -10],
                 [-10, 0, 5, 10, 10, 5, 0, -10],
                 [-10, 5, 5, 10, 10, 5, 5, -10],
                 [-10, 0, 10, 10, 10, 10, 0, -10],
                 [-10, 10, 10, 10, 10, 10, 10, -10],
                 [-10, 5, 0, 0, 0, 0, 5, -10],
                 [-20, -10, -10, -10, -10, -10, -10, -20]]

rook_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
               [5, 10, 10, 10, 10, 10, 10, 5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [0, 0, 0, 5, 5, 0, 0, 0]]

queen_scores = [[-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]]

pawn_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
               [50, 50, 50, 50, 50, 50, 50, 50],
               [10, 10, 20, 30, 30, 20, 10, 10],
               [5, 5, 10, 25, 25, 10, 5, 5],
               [0, 0, 0, 30, 30, 0, 0, 0],
               [5, -5, -10, 10, 10, -10, -5, 5],
               [5, 10, 10, -30, -30, 10, 10, 5],
               [0, 0, 0, 0, 0, 0, 0, 0]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1],
                         "wK": king_scores,
                         "bK": king_scores[::-1]}

# TODO: Add castling bonuses
# TODO Stop AI from repeating moves
# TODO Add Killer moves

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3

def findBestMove(game_state, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if game_state.white_to_move else -1)
    return_queue.put(next_move)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    
    max_score = -CHECKMATE
    valid_moves = orderMoves(game_state, valid_moves)

    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undoMove()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

def isEndgame(game_state):
    total_material = 0
    for row in game_state.board:
        for piece in row:
            if piece != "--" and piece[1] != "K":
                total_material += piece_score[piece[1]]
    return total_material < 1600  # Threshold for endgame can be adjusted

def orderMoves(game_state, valid_moves):
    move_scores = []

    for move in valid_moves:
        move_score = scoreMove(game_state, move)
        move_scores.append((move_score, move))

    # Sort the moves based on their scored (highest score first)
    move_scores.sort(reverse=True, key=lambda x: x[0])

    # Return the sorted moves
    sorted_moves = [move for _, move in move_scores]
    return sorted_moves

def scoreMove(game_state, move):
    # Get the pieces being moved and captured
    piece_moved = game_state.board[move.start_row][move.start_col]
    piece_captured = game_state.board[move.end_row][move.end_col]

    # Score to be evaluated based on certain positional conditions, and each
    # condition met will stack onto this score so positions that meet multiple
    # conditions will be very valuable moves
    move_score = 0

    # A piece capturing a higher-value piece is extremely valuable, and this
    # hopefully also leads to the idea of less valuable pieces capturing first
    if piece_captured != "--" and piece_score[piece_captured[1]] > piece_score[piece_moved[1]]:
        move_score += 10 * piece_score[piece_captured[1]] - piece_score[piece_moved[1]]

    # If our pawn is close to being promoted we should tell it that this move
    # will raise our score by the value of a queen as we'll gain a queen's
    # worth of score for promoting
    if piece_moved[1] == "p" and (move.end_row == 0 or move.end_row == 7):
        move_score += piece_score["Q"]  # Currently our engine only allows for queen promotions

    # Developing minor pieces
    if piece_moved[1] in ["N", "B"]:
        move_score += 10 # Minor pieces to active squares

    # Evaluate pawn structure
    if piece_moved[1] == "p":
        # Check surrounding squares for other pawns
        surrounding_squares = [(move.end_row-1, move.end_col), (move.end_row+1, move.end_col),
                                (move.end_row, move.end_col-1), (move.end_row, move.end_col+1)]
        for row, col in surrounding_squares:
            if 0 <= row < 8 and 0 <= col < 8:
                # Subtract score for pawns in front or behind
                if game_state.board[row][col][1] == "p":
                    if row == move.end_row - 1 or row == move.end_row + 1:
                        move_score -= 5  # Subtract score for doubled pawns in front or behind
                    else:
                        move_score += 5  # Add score for pawns in corners

    return move_score

# Score the board. A positive score is good for white, a negative score is good for black.
def scoreBoard(game_state):
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif game_state.stalemate:
        return STALEMATE

    score = 0
    endgame = isEndgame(game_state)  # Check if it's the endgame

    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] == "K":
                    if endgame:
                        piece_position_score = king_endgame_scores[row][col]
                    else:
                        piece_position_score = king_scores[row][col]
                else:
                    piece_position_score = piece_position_scores[piece][row][col]
                piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score

    return score

# Picks and returns a random valid move
def findRandomMove(valid_moves):
    return random.choice(valid_moves)
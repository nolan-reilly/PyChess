# This file handles the AI's moves
import random

piece_score = {"K": 0, "Q": 900, "R": 500, "B": 300, "N": 300, "p": 100}

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
               [0, 0, 0, 20, 20, 0, 0, 0],
               [5, -5, -10, 0, 0, -10, -5, 5],
               [5, 10, 10, -20, -20, 10, 10, 5],
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

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3

# TODO: Reduce amount of moves searched
# TODO: There seems to be repetition in moves or cycle that can be created that should be avoided

move_times = []

def findBestMove(game_state, valid_moves, return_queue):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if game_state.white_to_move else -1)
    return_queue.put(next_move)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    max_score = -CHECKMATE
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
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score

    return score

# Picks and returns a random valid move
def findRandomMove(valid_moves):
    return random.choice(valid_moves)
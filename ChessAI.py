import random

pieceScores = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 10, "K": 0}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3 # How far we want to search

# First version of the AI is just picking a random move
def findRandomMove(validMoves):
    return random.choice(validMoves)

# Helper method to make the first recursive call for findMoveMinMax
def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    return nextMove

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1 # Can remove just counts how many positions were evaluated
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    # Move ordering - implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: # Pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

# A positive score is good for white, a negative score is good for black
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return - CHECKMATE # Black wins
        else:
            return CHECKMATE # White Wins
    elif gs.stalemate:
        return STALEMATE # Neither side wins
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScores[square[1]]
            elif square[0] == "b":
                score -= pieceScores[square[1]]

    return score

# Score the board based on material (THis area is how to improve your AI)
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScores[square[1]]
            elif square[0] == "b":
                score -= pieceScores[square[1]]

    return score
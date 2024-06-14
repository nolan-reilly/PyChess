class GameState():
    def __init__(self):
        # Possibly make these numpy arrays in the future to improve AI performance
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
    
        self.whiteToMove = True
        self.moveLog = [] # Stores all of the moves made in the game so we'll be able to undo moves

    # Takes a move as a parameter and executes it (This doesn't involve castling, pawn promotions, and en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" # When the piece moves make the square it left empty
        self.board[move.endRow][move.endCol] = move.pieceMoved # Replace the end location with the piece
        self.moveLog.append(move) # Log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # Swap players
    
    # Undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0: # Make sure there are moves to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turns

    # All moves considering checks
    def getValidMoves(self):
        return self.getAllPossibleMoves() # For now we're not going to worry about checks

    def getAllPossibleMoves(self):
        moves = []
        
        for row in range(len(self.board)): # Number of rows
            for col in range(len(self.board[row])): # Number of columns in each row
                turn = self.board[row][col][0] # Look at the first character in each cell
                if (turn == "w" and self.whiteToMove) and (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1] # Get the piece

                    # Based on the piece get all of it's current valid moves
                    if piece == "P":
                        self.getPawnMoves(row, col, moves)
                    elif piece == "N":
                        self.getKnightMoves(row, col, moves)
                    elif piece == "B":
                        self.getBishopMoves(row, col, moves)
                    elif piece == "R":
                        self.getRookMoves(row, col, moves)
                    elif piece == "Q":
                        self.getQueenMoves(row, col, moves)
                    else:
                        self.getKingMoves(row, col, moves)
    
        return moves # Return the list of current valid moves
    
    def getPawnMoves(self, row, col, moves):
        pass

    def getKnightMoves(self, row, col, moves):
        pass

    def getBishopMoves(self, row, col, moves):
        pass

    def getRookMoves(self, row, col, moves):
        pass

    def getQueenMoves(self, row, col, moves):
        pass

    def getKingMoves(self, row, col, moves):
        pass
                                

class Move():
    # The dictionaries below are used to convert chess notation to our programs
    # notation, and vice versa
    ranksToRows = { "1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0 }
    rowsToRanks = { v: k for k, v in ranksToRows.items() }
    filesToCols = { "a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7 }
    colsToFiles = { v: k for k, v in filesToCols.items() }

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Override the equals method
    def __eq__ (self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # You can add to this later if you want this to be the real chess notation (later)
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
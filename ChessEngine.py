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

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" # When the piece moves make the square it left empty
        self.board[move.endRow][move.endCol] = move.pieceMoved # Replace the end location with the piece
        self.moveLog.append(move) # Log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # Swap players

class Move():
    # The dictionaries below are used to convert chess notation to our programs
    # notation, and vice versa
    ranksToRows = { "1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0 }
    rowsToRanks = { v: k for k, v in ranksToRows.items() }
    filesToCols = { "a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 6 }
    colsToFiles = { v: k for k, v in filesToCols.items() }

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getChessNotation(self):
        # You can add to this later if you want this to be the real chess notation (later)
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
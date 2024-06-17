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
    
        self.moveFunctions = { "P": self.getPawnMoves, "N": self.getKnightMoves, "B": self.getBishopMoves,
                               "R": self.getRookMoves, "Q": self.getQueenMoves, "K": self.getKingMoves }

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
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1] # Get the piece
                    self.moveFunctions[piece](row, col, moves) # Calls specific move function based on the piece
    
        return moves # Return the list of current valid moves
    
    # Get all pawn moves located at row, col and append these moves to the moves list
    def getPawnMoves(self, row, col, moves):
        # Determine pawns movement based on color
        if self.whiteToMove:
            enemyColor = "b"
            moveDirection = -1
            startRow = 6
        else:
            enemyColor = "w"
            moveDirection = 1
            startRow = 1
    
        if self.board[row + moveDirection][col] == "--": # One square pawn advance
            moves.append(Move((row, col), (row + moveDirection, col), self.board)) # Add one square pawn advance to valid moves

            if row == startRow and self.board[row + 2 * moveDirection][col] == "--": # Two square pawn advance
                moves.append(Move((row, col), (row + 2 * moveDirection, col), self.board))

        # Captures to the left
        if col - 1 >= 0:
            if self.board[row + moveDirection][col-1][0] == enemyColor:
                moves.append(Move((row, col), (row + moveDirection, col-1), self.board))
        
        # Captures to the right
        if col + 1 <= 7:
            if self.board[row + moveDirection][col+1][0] == enemyColor:
                moves.append(Move((row, col), (row + moveDirection, col+1), self.board))
    
    # Get all knight moves located at row, col and append these moves to the moves list
    def getKnightMoves(self, row, col, moves):
        # Check current color to see which pieces are to be captured
        enemyColor = "b" if self.whiteToMove else "w"

        # Calculate all possible knight moves from the current row and col
        knightMoves = [
            (row-2, col-1), (row-1, col-2), # Top left moves
            (row-2, col+1), (row-1, col+2), # Top right moves
            (row+2, col-1), (row+1, col-2), # Bottom left moves
            (row+2, col+1), (row+1, col+2)  # Bottom right moves
        ]

        for newRow, newCol in knightMoves:
            if 0 <= newRow < 8 and 0 <= newCol < 8: # Check if the move is within the boundary
                if self.board[newRow][newCol] == "--" or self.board[newRow][newCol][0] == enemyColor:
                    moves.append(Move((row, col), (newRow, newCol), self.board))

    # Get all bishop moves located at row, col and append these moves to the moves list
    def getBishopMoves(self, row, col, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Top-left, top-right, bottom-left, bottom-right
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1, 8):  # Bishop can move at most 7 squares in one direction
                newRow = row + d[0] * i
                newCol = col + d[1] * i
                if 0 <= newRow < 8 and 0 <= newCol < 8:  # Check if new position is within the board
                    if self.board[newRow][newCol] == "--":  # Empty square
                        moves.append(Move((row, col), (newRow, newCol), self.board))
                    elif self.board[newRow][newCol][0] == enemyColor:  # Enemy piece
                        moves.append(Move((row, col), (newRow, newCol), self.board))
                        break  # Stop searching in this direction after capturing
                    else:  # Friendly piece
                        break
                else:  # Out of bounds
                    break

    # Get all rook moves located at row, col and append these moves to the moves list
    def getRookMoves(self, row, col, moves):
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)] # Up, right, down, left
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1, 8):   # Rook can move at most 7 squares in one direction
                newRow = row + d[0] * i
                newCol = col + d[1] * i
                if 0 <= newRow < 8 and 0 <= newCol < 8:  # Check if new position is within the board
                    if self.board[newRow][newCol] == "--":  # Empty square
                        moves.append(Move((row, col), (newRow, newCol), self.board))
                    elif self.board[newRow][newCol][0] == enemyColor:  # Enemy piece
                        moves.append(Move((row, col), (newRow, newCol), self.board))
                        break  # Stop searching in this direction after capturing
                    else:  # Friendly piece
                        break
                else:  # Out of bounds
                    break

    # Get all queen moves located at row, col and append these moves to the moves list
    def getQueenMoves(self, row, col, moves):
        # Queen can move in all directions
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1, 8):   # Rook can move at most 7 squares in one direction
                newRow = row + d[0] * i
                newCol = col + d[1] * i
                if 0 <= newRow < 8 and 0 <= newCol < 8:  # Check if new position is within the board
                    if self.board[newRow][newCol] == "--":  # Empty square
                        moves.append(Move((row, col), (newRow, newCol), self.board))
                    elif self.board[newRow][newCol][0] == enemyColor:  # Enemy piece
                        moves.append(Move((row, col), (newRow, newCol), self.board))
                        break  # Stop searching in this direction after capturing
                    else:  # Friendly piece
                        break
                else:  # Out of bounds
                    break

    # Get all king moves located at row, col and append these moves to the moves list
    def getKingMoves(self, row, col, moves):
        # Check current color to see which pieces are to be captured
        enemyColor = "b" if self.whiteToMove else "w"

        # Calculate all possible king moves from the current row and col
        kingMoves = [
            (row-1, col-1), (row-1, col), (row-1, col+1), (row, col-1), 
            (row, col+1), (row+1, col-1), (row+1, col), (row+1, col+1)
        ]

        for newRow, newCol in kingMoves:
            if 0 <= newRow < 8 and 0 <= newCol < 8: # Check if the move is within the boundary
                if self.board[newRow][newCol] == "--" or self.board[newRow][newCol][0] == enemyColor:
                    moves.append(Move((row, col), (newRow, newCol), self.board))

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
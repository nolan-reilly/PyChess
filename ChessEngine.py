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

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.checkMate = False
        self.staleMate = False

        self.enPassantPossible = () # Coordinates for the square where and en passant is possible

        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    # Takes a move as a parameter and executes it (This doesn't involve castling, pawn promotions, and en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" # When the piece moves make the square it left empty
        self.board[move.endRow][move.endCol] = move.pieceMoved # Replace the end location with the piece
        self.moveLog.append(move) # Log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # Swap players

        # Update the king's position whenever it's moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion (Only currently allowing pawns to be promoted to queens)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        
        # Pawn En Passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--" # Capturing the pawn en passant
        
        # Update enPassantPossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2: # Only on two square pawn advance
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # King side castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # Moves the rook
                self.board[move.endRow][move.endCol+1] = "--" # Erase old rook
            else: # Queen side castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # Moves the rook
                self.board[move.endRow][move.endCol-2] = "--" # Erase old rook
        
        # Update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    
    # Undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0: # Make sure there are moves to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turns
        
            # If a move is undone make sure to keep track of the king's movement
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            
            # Undo en passant move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--" # Leave the square the pawn took on blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured # Restore the captured pawn
                self.enPassantPossible = (move.endRow, move.endCol)
            
            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
            
            #undo castling rights
            self.castleRightsLog.pop() # Get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            # Set the current castle rights to the last one in the list
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # King side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else: # Queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] == "--"
    
    # Update the castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqa = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.bks = False
        

    # All moves considering checks
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        # Generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # For each move, make the move
        for i in range(len(moves) - 1, -1, -1): # When removing from a list go backwards through that list
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove # Switch Turns

            # Generate all opponent's moves, and see if they attack your king
            if self.inCheck():
                moves.remove(moves[i]) # If they attack your king it's not a valid move
            self.whiteToMove = not self.whiteToMove # Switch turns
            self.undoMove()
        
        if len(moves) == 0: # Either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    # Determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else: 
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
        
    # Determine if the enemy can attack the square row, col
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Switch turns back
        
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: # Square is under attack
                return True

        return False

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
            elif (row + moveDirection, col-1) == self.enPassantPossible:
                moves.append(Move((row, col), (row + moveDirection, col-1), self.board, isEnPassantMove=True))

        # Captures to the right
        if col + 1 <= 7:
            if self.board[row + moveDirection][col+1][0] == enemyColor:
                moves.append(Move((row, col), (row + moveDirection, col+1), self.board))
            elif (row + moveDirection, col+1) == self.enPassantPossible:
                moves.append(Move((row, col), (row + moveDirection, col+1), self.board, isEnPassantMove=True))
    
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

    # Generate all valid castle moves for the king at row, col and add them to the list of moves
    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return # Can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(row, col, moves)
        
    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3]:
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move(row, col), (row, col-2), self.board, isCastleMove=True)
        

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # The dictionaries below are used to convert chess notation to our programs
    # notation, and vice versa
    ranksToRows = { "1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0 }
    rowsToRanks = { v: k for k, v in ranksToRows.items() }
    filesToCols = { "a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7 }
    colsToFiles = { v: k for k, v in filesToCols.items() }

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn promotion code
        self.isPawnPromotion = False
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)

        # Pawn en passant code
        self.isEnPassantMove = False
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        
        # Castle move
        self.isCastleMove = isCastleMove


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
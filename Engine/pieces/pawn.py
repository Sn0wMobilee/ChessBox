from .base import ChessPiece

class Pawn(ChessPiece):
    def __init__(self, color):
        symbol = "♙" if color == "white" else "♟"
        super().__init__(color, symbol)
        self.piece_type = 'pawn'
    def get_attacking_squares(self, position, board):
        row, col = position
        squares = []
        direction = -1 if self.color == 'white' else 1
        for diogonal in [-1, 1]:
            new_col = col + diogonal
            if 0 <= new_col < 8 and 0 <= row + direction < 8:
                squares.append((row + direction, new_col))
        return squares
                    
    def get_possible_moves(self, position, board_obj, last_move_info = None):
        """Логика ходов пешки"""  
        row, col = position
        pawn_possible_moves = []
        
        '''ПРОСТОЕ ПЕРЕМЕЩЕНИЕ'''   
        direction = -1 if self.color == 'white' else 1
        if 0 <= row + direction < 8 and board_obj.board[row + direction][col] is None:
            pawn_possible_moves.append((row + direction, col))
            if not self.has_moved and 0 <= row + 2*direction < 8 and board_obj.board[row + 2*direction][col] is None:
                pawn_possible_moves.append((row + 2*direction, col))
                
        '''ОБЫЧНОЕ ВЗЯТИЕ'''          
        for diogonal in [-1, 1]:
            new_col = col + diogonal
            if 0 <= new_col < 8 and 0 <= row + direction < 8:
                target_piece = board_obj.board[row + direction][new_col]
                if target_piece is not None and target_piece.color != self.color:
                    pawn_possible_moves.append((row + direction, new_col))
                    
        '''ВЗЯТИЕ НА ПРОХОДЕ'''            
        if last_move_info and last_move_info.get('was_pawn_double', False):
            last_piece = last_move_info.get('piece')
            last_to = last_move_info.get('to')
            last_from = last_move_info.get('from')
            if last_to and last_piece and isinstance(last_piece, Pawn):
                target_row, target_col = last_to
                if target_row == row and abs(target_col - col) == 1:
                    if self.color == 'white':
                        if row == 3 and last_from[0] == 1 and last_to[0] == 3:
                            pawn_possible_moves.append((row - 1, target_col)) 
                    elif self.color == 'black':
                        if row == 4 and last_from[0] == 6 and last_to[0] == 4:
                            pawn_possible_moves.append((row + 1, target_col))

        return pawn_possible_moves
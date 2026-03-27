from .base import ChessPiece

class Bishop(ChessPiece):
    def __init__(self, color):
        symbol = "♗" if color == "white" else "♝"
        super().__init__(color, symbol)
        self.piece_type = 'bishop'
        
    def get_attacking_squares(self, position, board):
        return self.get_possible_moves(position, board, None) 
    
    """ХОДЫ СЛОНА"""
    def get_possible_moves(self, position, board_obj,  last_move_info = None):
        row, col = position
        bishop_possible_moves = []
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diagonals:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_obj.board[r][c] if hasattr(board_obj, 'board') else board_obj[r][c]
                if target is None:
                    bishop_possible_moves.append((r, c))
                elif target.color != self.color:
                    bishop_possible_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return bishop_possible_moves
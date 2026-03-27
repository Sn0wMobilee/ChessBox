from .base import ChessPiece

class Knight(ChessPiece):
    def __init__(self, color):
        symbol = "♘" if color == "white" else "♞"
        super().__init__(color,symbol)
        self.piece_type = 'knight'
          
        '''ХОДЫ КОНЯ'''
    def get_attacking_squares(self, position, board):
        return self.get_possible_moves(position, board, None)
      
    def get_possible_moves(self, position, board_obj, last_move_info = None):
        row, col = position
        knight_possible_moves = []
        possible_positions = [
        (row + 2, col + 1), (row + 2, col - 1),
        (row - 2, col + 1), (row - 2, col - 1),
        (row + 1, col + 2), (row + 1, col - 2),
        (row - 1, col + 2), (row - 1, col - 2)
        ]
        for r, c in possible_positions:
            if 0 <= r < 8 and 0 <= c < 8:
                target_piece = board_obj.board[r][c]
                if target_piece is None or target_piece.color != self.color:
                    knight_possible_moves.append((r, c))
        return knight_possible_moves
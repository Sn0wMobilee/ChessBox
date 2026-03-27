from .base import ChessPiece
from .rook import Rook

class King(ChessPiece):
    def __init__(self, color,):
        symbol = "♔" if color == "white" else "♚"
        super().__init__(color, symbol)
        self.piece_type = 'king'
        
    """ПРОВЕРКА НА ВОЗМОЖНОСТЬ КОРОТКОЙ РОКИРОВКИ"""
    def _can_castle_kingside(self, position, board_obj, last_move_info=None):
        row, col = position
        rook = board_obj.board[row][7]
        if self.has_moved:
            return False
        if not rook or not isinstance(rook,Rook) or rook.has_moved:
            return False
        if board_obj.board[row][5] is not None or board_obj.board[row][6] is not None:
                return False
        if board_obj.is_in_check(self.color):
                return False
        opponent_color = 'black' if self.color == 'white' else 'white'
        squares_to_check = [(row, col), (row, col + 1), (row, col + 2)]
        for square in squares_to_check:
            if board_obj.square_is_under_attack(square, opponent_color):
                return False
        return True
    
    """ПРОВЕРКА НА ВОЗМОЖНОСТЬ ДЛИННОЙ РОКИРОВКИ"""
    def _can_castle_queenside(self,position, board_obj, last_move_info=None):
        row, col = position
        rook = board_obj.board[row][0]
        if self.has_moved:
            return False
        if not rook or not isinstance(rook,Rook) or rook.has_moved:
            return False
        if board_obj.board[row][1] is not None or board_obj.board[row][2] is not None or board_obj.board[row][3] is not None:
                return False
        if board_obj.is_in_check(self.color):
                return False
        opponent_color = 'black' if self.color == 'white' else 'white'
        squares_to_check = [(row, col), (row, col - 1), (row, col - 2),]
        for square in squares_to_check:
            if board_obj.square_is_under_attack(square, opponent_color):
                return False
        return True
        
        '''ХОДЫ КОРОЛЯ'''
    def get_attacking_squares(self, position, board):
        row, col = position
        king_attacking_squares = []
        possible_positions = [
        (row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1),
        (row - 1, col + 1), (row + 1, col - 1), (row - 1, col - 1), (row + 1, col + 1),
        ]
        for r, c in possible_positions:
            if 0 <= r < 8 and 0 <= c < 8:
                king_attacking_squares.append((r, c))
        return king_attacking_squares
    
    def get_possible_moves(self, position, board_obj, last_move_info=None):
        row, col = position
        king_filtered_moves = []
        possible_positions = [
        (row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1),
        (row - 1, col + 1), (row + 1, col - 1), (row - 1, col - 1), (row + 1, col + 1),
        ]
        for r, c in possible_positions:
            if 0 <= r < 8 and 0 <= c < 8:
                target_piece = board_obj.board[r][c]
                if target_piece is None or target_piece.color != self.color:
                    king_filtered_moves.append((r, c))
        if not self.has_moved:
            if board_obj.can_castle_kingside(position, self.color):
                king_filtered_moves.append((position[0], position[1] + 2))
            if board_obj.can_castle_queenside(position, self.color):
                king_filtered_moves.append((position[0], position[1] - 2))
        return king_filtered_moves
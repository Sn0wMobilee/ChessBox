class ChessPiece:
    '''ШАХМАТНЫЕ ФИГУРЫ И ПОСЛЕДУЮЩИЕ ТИПЫ'''
    def __init__(self, color, symbol,):
        self.color = color
        self.symbol = symbol
        self.has_moved = False
        self.piece_type = None
        
    def __str__(self):
        return self.symbol
    
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

class Rook(ChessPiece):
    def __init__(self, color):
        symbol = "♖" if color == "white" else "♜"
        super().__init__(color,symbol)
        self.piece_type = 'rook'
        
    def get_attacking_squares(self, position, board):
        return self.get_possible_moves(position, board, None) 
    
    """ХОДЫ ЛАДЬИ"""   
    def get_possible_moves(self, position, board_obj, last_move_info = None):
        row, col = position
        rook_possible_moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_obj.board[r][c] if hasattr(board_obj, 'board') else board_obj[r][c]
                if target is None:
                    rook_possible_moves.append((r, c))
                elif target.color != self.color:
                    rook_possible_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return rook_possible_moves

class Queen(ChessPiece):
    def __init__(self, color,):
        symbol = "♕" if color == "white" else "♛"
        super().__init__(color, symbol)
        self.piece_type = 'queen'
        
        """ХОДЫ ФЕРЗЯ"""
    def get_attacking_squares(self, position, board):
        return self.get_possible_moves(position, board, None)
     
    def get_possible_moves(self, position, board_obj, last_move_info = None):
        row, col = position
        queen_possible_moves = []
        #ХОДЫ СЛОНА
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diagonals:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_obj.board[r][c] if hasattr(board_obj, 'board') else board_obj[r][c]
                if target is None:
                    queen_possible_moves.append((r, c))
                elif target.color != self.color:
                    queen_possible_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
                
        #ХОДЫ ЛАДЬИ 
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_obj.board[r][c] if hasattr(board_obj, 'board') else board_obj[r][c]
                if target is None:
                    queen_possible_moves.append((r, c))
                elif target.color != self.color:
                    queen_possible_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return queen_possible_moves

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

class ChessBoard:
    '''ШАХМАТНАЯ ДОСКА'''
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_player = "white"
        self.game_over = False
        self.last_move = None
        self.last_move_pawn_double = False
        self.half_moves = 0 
        
    """СОЗДАНИЕ ШАХМАТНОЙ ДОСКИ С НАЧАЛЬНОЙ РАССТАНОВКОЙ ФИГУР"""
    def create_initial_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]               
        for col in range(8):
            board[6][col] = Pawn('white')
            board[1][col] = Pawn('black') 
        pieces_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(pieces_order):
            board[7][col] = piece_class('white')
            board[0][col] = piece_class('black')
        return board
    
    """ПРОВЕРКА АТАКОВАННЫХ КЛЕТОК"""
    def square_is_under_attack(self, square, attacker_color):
        target_row, target_col = square
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == attacker_color:
                    attacking_squares = piece.get_attacking_squares((row,col), self)
                    for r, c in attacking_squares:
                        if 0 <= r < 8 and 0 <= c < 8:
                            if r == target_row and c == target_col:
                                return True
        return False
    
    """ПУБЛИЧНАЯ ПРОВЕРКА НА ВОЗМОЖНОСТЬ КОРОТКОЙ РОКИРОВКИ"""
    def can_castle_kingside(self, king_position, king_color):
        row, col = king_position
        king = self.board[row][col]
        if not king or not isinstance(king, King) or king.color != king_color:
            return False
        return king._can_castle_kingside(king_position, self)
    
    """ПУБЛИЧНАЯ ПРОВЕРКА НА ВОЗМОЖНОСТЬ ДЛИННОЙ РОКИРОВКИ"""
    def can_castle_queenside(self, king_position, king_color):
        row, col = king_position
        king = self.board[row][col]
        if not king or not isinstance(king, King) or king.color != king_color:
            return False
        return king._can_castle_queenside(king_position, self)

    
    '''НАЙТИ КОРОЛЯ'''
    def find_king_position(self,color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece and  
                   isinstance(piece, King) and
                    piece.color == color):
                    return (row,col)
        raise Exception(f"Король цвета {color} не найден!")
    
    '''НАЙТИ ВОЗМОЖНЫЕ ХОДЫ ПРОТИВНИКА'''
    def find_opponent_possible_moves(self,color):
        opponent_possible_moves = []
        opponent_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = piece.get_possible_moves((row, col), self, self.last_move)
                    opponent_possible_moves.extend(moves)
        return opponent_possible_moves
    
    def find_opponent_attacking_squares(self,color):
        opponent_attacking_squares = []
        opponent_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = piece.get_attacking_squares((row, col), self)
                    opponent_attacking_squares.extend(moves)
        return opponent_attacking_squares
    
    '''ПРОВЕРКА НА ШАХ'''
    def is_in_check(self, color):
        king_position = self.find_king_position(color)
        opponent_moves = self.find_opponent_attacking_squares(color)
        return king_position in opponent_moves
    
    '''ПРОВЕРКА НА МАТ'''
    def is_checkmate(self,color):
        if not self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = piece.get_possible_moves((row, col), self, self.last_move)
                    for move_row, move_col in moves:
                        if not (0 <= move_row < 8 and 0 <= move_col < 8):
                            continue
                        saved_piece = self.board[move_row][move_col]
                        self.board[move_row][move_col] = piece
                        self.board[row][col] = None
                        still_in_check = self.is_in_check(color)
                        self.board[row][col] = piece
                        self.board[move_row][move_col] = saved_piece
                        if not still_in_check:
                            return False
        return True

    '''ПРОВЕРКА НА ПАТ'''        
    def is_stalemate(self,color):
        if self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = piece.get_possible_moves((row, col), self, self.last_move)
                    for move_row, move_col in moves:
                        if not (0 <= move_row < 8 and 0 <= move_col < 8):
                            continue
                        target_piece = self.board[move_row][move_col]
                        self.board[move_row][move_col] = piece
                        self.board[row][col] = None
                        creates_check = self.is_in_check(color)
                        self.board[row][col] = piece
                        self.board[move_row][move_col] = target_piece
                        if not creates_check:
                            return False
    def not_enough_pieces(self):
        white_pawn_counter = 0
        black_pawn_counter = 0
        white_knight_counter = 0
        black_knight_counter = 0
        white_bishop_whitefielded_counter = 0
        white_bishop_blackfielded_counter = 0
        black_bishop_whitefielded_counter = 0
        black_bishop_blackfielded_counter = 0
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece,Queen) or isinstance(piece,Rook):
                    return False
                if isinstance(piece, Pawn) and piece.color == 'white':
                    white_pawn_counter += 1
                if isinstance(piece, Pawn) and piece.color == 'black':
                    black_pawn_counter += 1
                if isinstance(piece, Knight) and piece.color == 'white':
                    white_knight_counter += 1
                if isinstance(piece, Knight) and piece.color == 'black':
                    black_knight_counter += 1
                if isinstance(piece, Bishop) and piece.color == 'white':
                    is_dark_square =  (row + col) % 2 == 1
                    if is_dark_square:
                        white_bishop_blackfielded_counter += 1
                    else:
                        white_bishop_whitefielded_counter += 1          
                if isinstance(piece, Bishop) and piece.color == 'black':
                    is_dark_square =  (row + col) % 2 == 1
                    if is_dark_square:
                        black_bishop_blackfielded_counter += 1
                    else:
                        black_bishop_whitefielded_counter += 1
                        
        white_bishop_counter = white_bishop_whitefielded_counter + white_bishop_blackfielded_counter
        black_bishop_counter = black_bishop_whitefielded_counter + black_bishop_blackfielded_counter  
                     
        if white_knight_counter >= 1 and white_bishop_counter >= 1 or black_knight_counter >= 1 and black_bishop_counter >= 1:
            return False
        if white_bishop_counter >= 2 or black_bishop_counter >= 2:
            return False
        if white_pawn_counter >= 1 or black_pawn_counter >= 1:
            return False
        if white_bishop_blackfielded_counter >= 1 and black_bishop_whitefielded_counter >= 1:
            return False
        if white_bishop_whitefielded_counter >= 1 and black_bishop_blackfielded_counter >= 1:
            return False  
        return True
                      

    '''ПЕРЕМЕЩЕНИЕ ФИГУРЫ'''
    def move_piece(self, from_pos, to_pos):
        if self.game_over:
            print("Игра завершена!")
            return False
        # ПРЕОБРАЗУЕМ НОТАЦИЮ В ИНДЕКСЫ
        from_idx = notation_to_index(from_pos)
        to_idx = notation_to_index(to_pos)
        if not from_idx or not to_idx:
            print("Неверный формат координат!")
            return False

        row_from, col_from = from_idx
        row_to, col_to = to_idx
        
        #БАЗОВЫЕ ПРОВЕРКИ
        piece = self.board[row_from][col_from]
        if piece is None:
            print(f"На позиции {from_pos} нет фигуры!")
            return False
        
        if piece.color != self.current_player:
            print(f"Сейчас ходят {self.current_player}, а не {piece.color}")
            return False
        
        possible_moves = piece.get_possible_moves((row_from, col_from), self, self.last_move)
        if (row_to, col_to) not in possible_moves:
            print("Этот ход запрещен! Походите как-нибудь по другому")
            return False
    
        #ОБРАБОТКА ВЗЯТИЯ НА ПРОХОДЕ
        is_en_passant = False
        captured_row, captured_col = None,None
        if isinstance(piece, Pawn):
            if (self.board[row_to][col_to] is None and
                col_to != col_from and
                abs(col_to - col_from) == 1):
                
                if (self.last_move and
                self.last_move.get('was_pawn_double') and
                self.last_move.get('piece') and               
                isinstance(self.last_move['piece'], Pawn)):    
                    
                    last_to = self.last_move.get('to')
                    last_from = self.last_move.get('from')
                    if (last_to[0] == row_from and
                        last_to[1] == col_to):           
                        if piece.color == 'white' and row_from == 3 and row_to == 2:
                            is_en_passant = True       
                            captured_row, captured_col = row_from, col_to
                        elif piece.color == 'black' and row_from == 4 and row_to == 5:
                            is_en_passant = True
                            captured_row, captured_col = row_from, col_to
                            
        original_target = self.board[row_to][col_to]
        captured_piece = None
        if is_en_passant:
            captured_row = row_from
            captured_col = col_to
            captured_piece = self.board[captured_row][captured_col]
            self.board[captured_row][captured_col] = None
            
        #ОБРАБОТКА РОКИРОВКИ
        is_castling = isinstance(piece, King) and abs(col_to - col_from) == 2
        saved_state = {
        'king_from': piece,
        'king_to_cell': self.board[row_to][col_to],
        }
        if is_castling:
            if col_to > col_from:
                saved_state['rook'] = self.board[row_from][7]
                saved_state['rook_from_col'] = 7
                saved_state['rook_to_col'] = col_to - 1
            else:
                saved_state['rook'] = self.board[row_from][0]
                saved_state['rook_from_col'] = 0
                saved_state['rook_to_col'] = col_to + 1
        self.board[row_to][col_to] = piece
        self.board[row_from][col_from] = None
        if is_castling:
            rook = saved_state['rook']
            rook_to_col = saved_state['rook_to_col']
            rook_from_col = saved_state['rook_from_col']
            self.board[row_from][rook_to_col] = rook
            self.board[row_from][rook_from_col] = None

        #ОБРАБОТКА ШАХА
        self.board[row_to][col_to] = piece
        self.board[row_from][col_from] = None
        if self.is_in_check(piece.color):
              #ОТКАТЫВАЕМ ХОД
            self.board[row_from][col_from] = saved_state['king_from']
            self.board[row_to][col_to] = saved_state['king_to_cell']
            #ЕСЛИ ВЗЯТИЕ НА ПРОХОДЕ
            if is_en_passant:
                self.board[captured_row][captured_col] = captured_piece
            #ЕСЛИ РОКИРОВКА   
            if is_castling:
                self.board[row_from][saved_state['rook_from_col']] = saved_state['rook']
                self.board[row_from][saved_state['rook_to_col']] = None
            print("Оставлять короля под боем нельзя!!")
            return False
        
        #ЕСЛИ ВСЕ УСЛОВИЯ ВЕРНЫ
        piece.has_moved = True
        
        #СОХРЯНЕМ ИНФОРМАЦИЮ О ПОСЛЕДНЕМ ХОДЕ ДЛЯ ВЗЯТИЯ НА ПРОХОДЕ
        self.last_move = {
        'from': (row_from, col_from),
        'to': (row_to, col_to),
        'piece': piece,
        'was_pawn_double': False
        }
        
        #ЕСЛИ РОКИРОВКА ТО ФИКСИРУЕМ has_moved ДЛЯ ЛАДЬИ
        if is_castling:
            rook_piece = self.board[row_from][saved_state['rook_to_col']]
            rook_piece.has_moved = True
            print(f"Рокировка {'короткая' if col_to > col_from else 'длинная'} успешна!")
            
        #ВЗЯТИЕ ФИГУРЫ
        if isinstance(piece, Pawn) and abs(row_to - row_from) == 2:
            self.last_move['was_pawn_double'] = True
            print(f"Последний ход (Откуда-куда) - {from_pos} {to_pos}")
        if is_en_passant:
            print(f"Взятие на проходе! Захвачена пешка на {index_to_notation(captured_row, captured_col)}!")
        elif original_target:
            print(f"Захвачена фигура {original_target.symbol} на {to_pos}!")    

        opponent_color = "black" if piece.color == "white" else "white"
        opponent_colors = {"black": "чёрных", "white": "белых",}
        winner_colors = {"black": "чёрные", "white": "белые",}
        
        #НЕДОСТАТОЧНО МАТЕРИАЛА
        if self.not_enough_pieces():
            print(f"Недостаточно материала. На доске возникла ничья!")
            self.game_over = True
        
        #ПРАВИЛО 50 ХОДОВ
        if isinstance(piece, Pawn) or original_target is not None:
            self.half_moves = 0
            print(f"Количество полу-ходов: {self.half_moves}")
        else:
            self.half_moves += 1
            print(f"Количество полу-ходов: {self.half_moves}")
        if self.half_moves == 2:
            print(f"Правило 50 ходов. Ни одной взятой фигуры или хода пешкой. На доске возникла ничья!")
            self.game_over = True    
            
        #ОБЪЯВЛЕНИЕ ШАХА КОРОЛЮ
        if self.is_in_check(opponent_color):
            print(f"ШАХ королю {(opponent_colors.get(opponent_color))}!")
            
            #ОБЪЯВЛЕНИЕ МАТА
            if self.is_checkmate(opponent_color):
                winner_colors = {"black": "чёрные", "white": "белые"}
                print(f"МАТ королю {opponent_colors.get(opponent_color)}! Победитель - {winner_colors.get(piece.color)}!")
                self.game_over = True
            
        #ОБЪЯВЛЕНИЕ ПАТА
        elif self.is_stalemate(opponent_color):
            print(f"Пат! На доске возникла ничья!")
            self.game_over = True

            #ПРЕВРАЩЕНИЕ ПЕШКИ
        if isinstance(piece, Pawn):
            if (piece.color == "white" and row_to == 0) or (piece.color == "black" and row_to == 7):
                while True:
                    choice = input("Пешка дошла до конца! Какой фигурой вы бы хотели заменить пешку? (queen, rook, knight, bishop)")
                    if choice.lower() == "queen":
                        self.board[row_to][col_to] = Queen(piece.color)
                        print("ПЕШКА ПРЕВРАТИЛАСЬ В ФЕРЗЯ")
                        break
                    elif choice.lower() == "rook":
                        self.board[row_to][col_to] = Rook(piece.color)
                        print("ПЕШКА ПРЕВРАТИЛАСЬ В ЛАДЬЮ")
                        break
                    elif choice.lower() == "knight":
                        self.board[row_to][col_to] = Knight(piece.color)
                        print("ПЕШКА ПРЕВРАТИЛАСЬ В КОНЯ")
                        break
                    elif choice.lower() == "bishop":
                        self.board[row_to][col_to] = Bishop(piece.color)
                        print("ПЕШКА ПРЕВРАТИЛАСЬ В СЛОНА")
                        break
                    else:
                        print("Неверный выбор")
                        
            #СМЕНА ИГРОКОВ   
        self.current_player = "black" if self.current_player == "white" else "white"
        print(f"Ход: {piece.symbol} с {from_pos} на {to_pos}")
        return True
    
    '''ОТОБРАЖЕНИЕ ДОСКИ'''
    def display(self):
        print("\n   A  B  C  D  E  F  G  H")
        print("  +-------------------------")
        for row in range(8):
            print(f"{8-row} |", end="")
            for col in range(8):
                piece = self.board[row][col]
                symbol = piece.symbol if piece else '·'
                print(f" {symbol}", end=" ")
            print(f"| {8-row}")
        print("  +-------------------------")
        print("   A  B  C  D  E  F  G  H")

'''ПРЕОБРАЗОВАНИЕ ШАХМАТНОЙ НОТАЦИИ В ИНДЕКСЫ ДОСКИ'''
def notation_to_index(position):
    cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7,}
    if len(position) != 2:
        return None
    col_char, row_char = position[0].lower(), position[1]
    if col_char not in cols or not row_char.isdigit():
        return None
    col = cols[col_char]
    row = 8 - int(row_char)
    return (row, col)

'''ОБРАТНОЕ ПРЕОБРАЗОВАНИЕ'''
def index_to_notation(row,col):
    col_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    return f"{col_map[col]}{8 - row}"

'''КЛАСС ПРОЦЕССОВ ИГРЫ'''
class Game:
    def __init__(self):
        self.board = ChessBoard()
        self.game_over = False
        self.player_names = {
            "white": "БЕЛЫЕ",
            "black": "ЧЕРНЫЕ"
        }
        
    '''ПОКАЗЫВАЕТ ЧЕЙ ХОД НА ДАННЫЙ МОМЕНТ'''
    def show_current_player_turn(self):
        player = self.player_names[self.board.current_player]
        print(f"[{player}],Сейчас ваш ход!")
    
    '''НАЧАЛО ИГРЫ'''    
    def play(self):
        print("   Добро пожаловать в игру!")
        #ПОТОМ ТУТ БУДУТ РАЗНЫЕ РЕЖИМЫ
        while True:
            if self.board.game_over:
                self.board.display()
                print("Игра завершена!")
                choice = input("Хотите сыграть еще раз? (да/нет): ")
                if choice.lower() == "да":
                    self.board = ChessBoard()
                    continue
                else:
                    break
                
            #ОТОБРАЖЕНИЕ ДОСКИ    
            self.board.display()    
            self.show_current_player_turn()
            move = input("Введите ход (например, e2 e4) или выход для завершения:")
            if move.lower() == 'выход':
                print("Игра завершена")
                break
            
            #ПРОВЕРЯЕТ ЧТОБЫ ДЛИНА ШАХМАТНЫХ НОТАЦИЙ БЫЛА ОБЯЗАТЕЛЬНО = 2
            parts = move.split()
            if len(parts) != 2:
                print("Формат: 'откуда куда', например: 'e2 e4'")
                continue
            
            #ВЫПОЛНЕНИЕ ХОДА
            if self.board.move_piece(parts[0], parts[1]):
                print("Ход выполнен!")
            else:
                print("Не удалось выполнить ход. Попробуйте снова.")
                
if __name__ == "__main__":
    game = Game()
    game.play()
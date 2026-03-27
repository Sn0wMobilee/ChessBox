class ChessPiece:
    '''ШАХМАТНЫЕ ФИГУРЫ И ПОСЛЕДУЮЩИЕ ТИПЫ'''
    def __init__(self, color, symbol,):
        self.color = color
        self.symbol = symbol
        self.has_moved = False
        self.piece_type = None
        
    def __str__(self):
        return self.symbol
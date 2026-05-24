import os
import sys
'''ПРЕОБРАЗОВАНИЕ ШАХМАТНОЙ НОТАЦИИ В ИНДЕКСЫ ДОСКИ'''
def notation_to_index(position):
    col_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7,} #0 - самый левый, 7 - самый правый
    if len(position) != 2: #важно чтобы позиция была в стиле буква-цифвра, тоесть длина 2
        return None
    col_char, row_char = position[0].lower(), position[1] 
    if col_char not in col_map or not row_char.isdigit():
        return None
    col = col_map[col_char]
    row = 8 - int(row_char)
    return (row, col)

'''ОБРАТНОЕ ПРЕОБРАЗОВАНИЕ'''
def index_to_notation(row,col):
    col_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    return f"{col_map[col]}{8 - row}"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
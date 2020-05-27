# implement make_numbers_triangulo_p7 here
def make_numbers_triangulo_p7(self, line, col, numLines, numColumns, p2Block: int):
    index = numColumns*line + numColumns-col
    return p2Block, index

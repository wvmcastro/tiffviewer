def make_numbers_sede_p1(line, col, numLines, numColumns, p1Block: int):
        if col % 2 == 0:
            oy = numLines - 1
        else:
            oy = 0

        if p1Block == 1:
            start_number = 1
        elif p1Block == 2:
            start_number = 111
        else:
            start_number = 221
        
        index = col * numLines + abs(line - oy)
        index += start_number
        return p1Block, index
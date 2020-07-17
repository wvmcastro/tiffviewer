# implement make_numbers_sede_b1 here
def make_numbers_sede_b1(self, line, col, numLines, numColumns, p2Block: int):
if(col % 2 == 0):
    startnumber = 51
else:
    startnumber = 1
index = startnumber + line
return p2Block, index

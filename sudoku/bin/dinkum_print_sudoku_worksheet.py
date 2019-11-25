#!/usr/bin/env python3
# dinkum/sudoku/bin/dinkum_print_sudoku_worksheet.py
''' Prints (to stdout) a sudoku board with rows/columns/blocks/cells
labeled with number.  An example is shown below:

<todo> replace this with actual example
<todo> replace ALL examples with real examples
Ignore next two lines, just ruler used to write the code

    0  1  2 |  3  4  5 |  6  7  8 
 /--------------------------------\
0|  0  1  2 |  3  4  5 |  6  7  8 |0
1|  9 10 11 | 12 13 14 | 15 16 17 |1
            ...
7| 63 64 65 | 66 67 68 | 69 70 71 |7
8| 72 73 74 | 75 76 77 | 78 79 80 |8
 \ --------------------------------/
    0  1  2 |  3  4  5 |  6  7  8 

'''
# 2019-11-13 tc Initial development
# 2019-11-19 tc refactored replace_substr_at() into dinkum.utils.str_utils.py
# 2019-11-22 tc debugging and putting in block separaters 
# 2019-11-23 tc labeling cell# and blk#
#               refactored in sudoku.labeled_printer.labeled_print()

from dinkum.sudoku.labeled_printer import print_labeled_board

if __name__ == "__main__" :

    # [] of lines making up output
    # each is NOT terminated by \n
    # With no board supplied, it prints empty board
    # which is what we want for a worksheet
    print_labeled_board()






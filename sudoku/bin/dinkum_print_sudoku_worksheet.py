#!/usr/bin/env python3
# dinkum/sudoku/bin/dinkum_print_sudoku_worksheet.py
''' Prints (to stdout) a sudoku board with rows/columns/blocks/cells
labeled with number.  An example is shown below:

<todo> replace this with actual example
Ignore next two lines, just ruler used to write the code
0         1         2         3
-123456789-123456789-123456789-123456789


    0  1  2 |  3  4  5 |  6  7  8 
 /--------------------------------\
0|  0  1  2 |  3  4  5 |  6  7  8 |0
1|  9 10 11 | 12 13 14 | 15 16 17 |1
            ...
7| 63 64 65 | 66 67 68 | 69 70 71 |7
8| 72 73 74 | 75 76 77 | 78 79 80 |8
 \ --------------------------------/
    0  1  2 |  3  4  5 |  6  7  8 

-123456789-123456789-123456789-123456789
0         1         2         3
Ignore the lines above, they are just a
ruler used to write the code

'''

# <todo> remove this when package is sorted out
# We are in directory: .../dinkum/sudoku/bin 
# We need to import:   .../dinkum/sudoku/sudoku.py
import sys
import os
# Put dinkum directory on sys.path
dinkum_parent_dirname  = os.path.abspath(sys.argv[0])        # ".../whatever/dinkum/sudoku/bin/ourname.py"
for i in range(4) :
    dinkum_parent_dirname = os.path.dirname( dinkum_parent_dirname) # ".../whatever
sys.path = [dinkum_parent_dirname] + sys.path               # put at head of path


from dinkum.sudoku.sudoku import Board

# What we make lines with
horz_line_char = '-'
vert_line_char = '|'

cell_width   = 4  # width of printed cell.  Includes rightmost | but not leftmost |
left_width_to_first_cell = 2
right_width_after_last_cell = 1
output_width = left_width_to_first_cell + right_width_after_last_cell + \
               cell_width * Board.rcb_size          # line length excluding \n


def top_or_bottom_lines(is_top) :
    ''' returns [] of [column label line, horz separator line. e.g.
    <todo> example here
    is_top controls whether top or bottom lines
    '''
    hsl = horz_separator_lines(is_top) # ------
    cll = col_label_lines()            # 0 1 2 ...

    # The order in the list depends on whether to or bottom
    return cll+hsl if is_top else hsl+cll

def horz_separator_lines(is_top) :
    ''' Returns [] of lines making up top or bottom
    lines, e.g.
        <todo> put example here
    is_top controls whether top or bottom lines
    are returned.
    les are NOT new line terminated.
    '''

    # Assume it's the top line
    first_char = '/'
    last_char  = '\\'  # \\ ==> \ i.e. Only one char
    if not is_top :
        # Swap them
        (last_char, first_char) = (first_char, last_char)

    # -----------
    # Start with full line of lines
    # and overwrite what we need to
    sep_line = horz_line_char * output_width

    # ' /------------------'
    sep_line = ' ' + first_char + sep_line[2:]

    # ' /------------------\\'
    sep_line = sep_line[:-1] + last_char

    # All done
    return [sep_line]

def col_label_lines() :
    ''' returns [] of lines that label the columns.
    Each line is NOT \n terminated.
    '''

    # Start with full line of spaces
    col_label_line = ' ' * output_width

    for col_num in range(Board.rcb_size) :
        # Replace the space at left_width_to_first_cell + cell_width + cell_width * col_num
        # with the column number.
        # Extra cell_width above right justifies the column_label in cell

        offset = left_width_to_first_cell + cell_width + col_num * cell_width
        col_label_line = col_label_line[:offset] + str(col_num) + col_label_line[offset:]

    return [col_label_line]
    
        
def row_line(row_num) :
    ''' returns [] of lines that make up a row.
    lines are NOT \n terminated.  e.g.
      1|  9 10 11 | 12 13 14 | 15 16 17 |1
    '''

    # 1|
    row_line = str(row_num) + vert_line_char

    # Do the cells (without vertical separator
    # 0  1  2 |  3  4  5 |  6  7  8 |
    cell_num = row_num * Board.rcb_size # cell_num of leftmost cell
    for cell_in_line in range(Board.rcb_size) :
        cell_line = "%3s " % str(cell_num)
        cell_num += 1

        row_line += cell_line

    # Label row on right
    row_line += str(row_num)

    return [row_line]

def worksheet() :
    ''' creates a blank sudoku worksheet, i.e.
        print this to get a labeled sudoku board
        to futz with.  No cell values are printed,
        but is labeled with cell#/row/col/blk of each
        cell.

        Returns a [] of lines (NOT terminated by new line) that
        make up the worksheet
        '''

    ws = [] # What we return

    #    0  1  2 ...
    # /--------------------------------\  #
    ws += top_or_bottom_lines(is_top=True)

    # Stuff in the middle, e.g.
    # 1|  9 10 11 | 12 13 14 | 15 16 17 |1
    for row_num in range(Board.rcb_size) :
        ws += row_line(row_num)

    # \ --------------------------------/ #
    #    0  1  2 ...
    ws += top_or_bottom_lines(is_top=False)
        
    return ws

if __name__ == "__main__" :

    # [] of lines making up output
    # each is NOT terminated by \n
    lines = worksheet()

    for l in lines :
        print (l) 





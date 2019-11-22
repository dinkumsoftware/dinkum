#!/usr/bin/env python3
# dinkum/sudoku/bin/dinkum_print_sudoku_worksheet.py
''' Prints (to stdout) a sudoku board with rows/columns/blocks/cells
labeled with number.  An example is shown below:

<todo> replace this with actual example
<todo> replace ALL examples with real examples
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
# 2019-11-13 tc Initial development
# 2019-11-19 tc refactored replace_substr_at() into dinkum.utils.str_utils.py
# 2019-11-22 tc debugging and putting in block separaters 

from dinkum.sudoku.sudoku   import Board
from dinkum.utils.str_utils import *

# What we make lines with
horz_line_char = '-'
vert_line_char = '|'

# size of printed cell
# includes rightmost | and topmost -
# does NOT include leftmost | and bottom -
# does NOT include any block separators
cell_width   = 6
cell_height  = 4

# Width of whole printed board
left_offset_to_first_cell = 2           # Accounts for row label and one |
right_pad_after_last_cell = 3           # || + row_label
width_of_internal_block_separators = 2  # Two internal |'s

output_width = left_offset_to_first_cell + cell_width * Board.rcb_size +     \
               width_of_internal_block_separators + right_pad_after_last_cell

# Height of whole printed board
top_offset_to_first_cell = 2 # column label + '-'
bot_pad_after_last_cell  = 2 # bottom cell '-' + '-' + column_label

def top_or_bottom_lines(is_top) :
    ''' returns [] of [column label line, horz separator line. e.g.
    <todo> example here
    is_top controls whether top or bottom lines
    '''

    if is_top :
        # column label and separator line
        ret_list  = col_label_lines()               # 0 1 2 ...
        ret_list += horz_separator_lines('/', '\\') # /----------\
        assert len(ret_list) == top_offset_to_first_cell
        return ret_list

    else :
        # bottom
        ret_list =  horz_separator_lines('\\', '/')                       # \---------------/ 
        ret_list += col_label_lines()                                     #     0     1   2 ...

        assert len(ret_list) == bot_pad_after_last_cell
        return ret_list

    assert False, "Impossible Place"

def row_line(row_num) :
    ''' returns [] of lines that make up a row of cells
    lines are NOT \n terminated.  e.g.
    <todo> replace
      1|  9 10 11 | 12 13 14 | 15 16 17 |1

    The top line, left, and right cell outlines are include
    in returned lines.  A horizontal block separator may
    be included in the output.

    The bottom cell lines are NOT in the returned lines.

    The cell number is written in the upper left corner of
    the cell area
    '''

    # An empty sudoku board. Each cell in that board
    # knows it's cell number, row number, etc
    # We make use of that so we don't have to compute it.
    board = Board()

    # What we return.  Gets filled in below                     
    ret_lines= [None] * cell_height

    # A cell consists of the left and top border, spaces inside,
    # but NOT the bottom and right border

    # Start with a separator line. This is top line of all cells in
    # the row
    # <todo> example here
    ret_lines = horz_separator_lines()

    # Each individual row is made of multiple output lines.
    # Iterate over them
    first_line_of_cell_content = 1 # skips horz_separator_lines
    for line_num_in_row in range(first_line_of_cell_content, cell_height) :
        # <todo> examples
        line = '' # start with an empty line and append to it
                  # moving left to right

        # Time to place row label on outside ?
        line += str(row_num) if line_num_in_row == cell_height//2 else ' '

        line += vert_line_char 

        # We iterate over a row of Cells in a Board so
        # we don't have to do the arithmetic for cell#, block#, etc
        # Output the left edge and appropriate number of spaces
        for cell in board.rows[row_num] :

            # cell's left edge
            line += vert_line_char

            # spaces of the cell
            cell_content = ' ' * (cell_width-1) # The -1 is for vert_line_char we just printed

            # on top line only, label the cell number
            if line_num_in_row == first_line_of_cell_content:
                replace_substr_at(cell_content, "%2d" % cell.cell_num, 0)

            line += cell_content # Tack it on

            # Time to place an internal (not on edges) vertical block separator ?
            if cell_is_rightmost_in_block_and_internal(cell.col_num) :
                line += vert_line_char

        # Right cell's right border
        line += vert_line_char 

        # Outside line
        line += vert_line_char 

        # Time to place row label on outside ?
        line += str(row_num) if line_num_in_row == cell_height//2 else ' '

        # All done composing line
        assert len(line) == output_width, "is: %d, should be:%d" %(len(line), output_width)

        # Set our result in the [] we return
        ret_lines.append(line)

    assert len(ret_lines) == cell_height

    # If this is the bottom row of an internal block, we need
    # to separate it by adding another line of ----------'s
    if cell_is_bottom_most_in_block_and_internal(row_num) :
        ret_lines += horz_separator_lines()

    return ret_lines

def horz_separator_lines(first_char=vert_line_char, last_char=vert_line_char) :
    ''' Returns [] of lines making up top or bottom
    lines, e.g.
        <todo> put example here
    The first and last chars of each line are set to
    first_char and last_char
    lines are NOT new line terminated.
    '''

    # -----------
    # Start with full line of lines
    # and overwrite what we need to
    sep_line = horz_line_char * output_width

    # Overwrite first and last chars with spaces
    # to account for row label's

    sep_line = replace_substr_at(sep_line, ' ',  0)
    sep_line = replace_substr_at(sep_line, ' ' , -1)

    # overwrite first and last chars that were passed in                    
    sep_line = replace_substr_at(sep_line, first_char,  1)
    sep_line = replace_substr_at(sep_line, last_char , -2)

    # All done
    return [sep_line]

def col_label_lines() :
    ''' returns [] of lines that label the columns.
    Each line is NOT \n terminated.
    '''
    
    # Start with stuff on left before first Cell
    # "   "
    col_label_line = left_pad()

    # Do the stuff above a row of cells
    # We don't care which row
    row = Board().rows[0]

    for cell in row :
        # A cell_width blank string
        cell_line = ' ' * cell_width

        # Write column label in the middle
        cell_line = replace_substr_at(cell_line, str(cell.col_num),
                                      len(cell_line)//2 )

        # We have to account for vertical block separators
        # to keep the center alignment of column numbers
        if cell_is_rightmost_in_block_and_internal(cell.col_num) :
            cell_line += ' '

        # Tack it on
        col_label_line += cell_line
    
    # Fill out the rest of the line
    # "   "
    col_label_line += right_pad()

    # Give them back list of our one generated line
    return [col_label_line]
    
def cell_is_rightmost_in_block_and_internal(col_num) :
    ''' Returns true if cell in col_num needs a block
    separator to it's right AND it isn't the last cell
    on the line.  Hence the internal word
    '''
    return col_num==2  or col_num==5

def cell_is_bottom_most_in_block_and_internal(row_num) :
    ''' Returns True if the row at row_num is the
    bottommost row of the block AND and not on the
    bottom row of the board, hence the use of internal.
    '''
    return row_num==2 or row_num==5

def cell_is_in_middle_of_block(cell) :
    ''' returns TRUE if cell is the center cell
    of it's block.
    '''
    return cell.row_num in [1,4,7] and cell.col_num in [1,4,7]


def left_pad() :
    ''' Returns a string that makes up the left edge of the output board.
    <todo> support row label
    <todo> provide example
    '''
    ret_str = '  '
    assert len(ret_str) == left_offset_to_first_cell
    return ret_str

    return ""


def right_pad() :
    ''' Returns a string that makes up the right edge of the output board.
        It's all spaces.
    '''
    ret_str = '   '
    assert len(ret_str) == right_pad_after_last_cell

    return ret_str


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





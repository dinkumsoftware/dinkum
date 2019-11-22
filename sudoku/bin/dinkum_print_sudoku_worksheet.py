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


from dinkum.sudoku.sudoku import Board

# What we make lines with
horz_line_char = '-'
vert_line_char = '|'

# size of printed cell
# includes rightmost | and topmost -
# does NOT include leftmost | and bottom -
cell_width   = 6
cell_height  = 4

# Width of whole printed board
left_offset_to_first_cell = 2     # Accounts for row label and one |
right_pad_after_last_cell = 3     # || + row_label
output_width = left_offset_to_first_cell + cell_width * Board.rcb_size + right_pad_after_last_cell

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


def horz_separator_lines(first_char, last_char) :
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
        cell_line = '' * cell_width

        # Write column label in the middle
        cell_line = replace_substr_at(cell_line, str(cell.col_num),
                                      len(cell_line)//2 )
        
        # Tack it on
        col_label_line += cell_line
    
    # Fill out the rest of the line
    # "   "
    col_label_line += right_pad()

    # Give them back list of our one generated line
    return [col_label_line]
    
        
def row_line(row_num) :
    ''' returns [] of lines that make up a row of cells
    lines are NOT \n terminated.  e.g.
    <todo> replace
      1|  9 10 11 | 12 13 14 | 15 16 17 |1

    The top line, left, and right cell outlines are include
    in returned lines.  The bottom cell lines are NOT in 
    the returned lines.
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
    ret_lines = horz_separator_lines(vert_line_char, vert_line_char)

    # Each individual row is made of multiple output lines.
    # Iterate over them
    for line_num_in_row in range(1, cell_height) :
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
            line += ' ' * (cell_width-1) # The -1 is for vert_line_char we just printed

        # Left cell's left border
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
    return ret_lines

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
    <todo> support row label
    <todo> provide example
    '''
    ret_str = vert_line_char + '  '
    assert len(ret_str) == right_pad_after_last_cell

    return ret_str




def cell_output_line(cell) :
    ''' returns a string representing cell's output.
    It includes the vertical separator on left side, but
    NOT the right side.
    It includes the top line but NOT the bottom line
    '''

    return "     "


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





#!/usr/bin/env python3
# dinkum/sudoku/cell.py
'''Defines the Cell class which is part of a Sudoku Board.
also a member of an RCB (row/col/blk).

A Cell knows what board it belongs to.  It's value and
possible_values if unsolved.  It knows which row/col/blk
it belongs to.
'''

# 2019-11-25 tc Moved fom sudoku.py
# 2019-12-01 tc changes row/col/blk from () to class variable
# 2019-12-08 tc Added rcb_num_and_idx()


from dinkum.sudoku import *  # Get package wide constants from __init__.py


class Cell :
    ''' Represents a single cell on the sudoku board. Has
    value           can be unsolved_cell_value or 1-9
    possible_values set of potential values, empty if value has been set
    board           The Board we belong to

    row/col/blk     The RCB we belong to
    rcbs            [] of row,col, and blk

    cell_num   0 to Board.num_cells-1

    All of these run 0 to Board.rcb_size-1 
    They are all in raster order
    row_num    which row we are  (Index into Board.rows)
    row_idx    which Cell in row (Index into Board.rows[row_num].cells)

    col_num    which col we are  (Index into Board.cols)
    col_idx    which Cell in col (Index into Board.cols[col_num].cells)

    blk_num    which blk we are  (Index into Board.blks)
    blk_idx    which Cell in blk (Index into Board.blks[blk_num].cells)

    row/col/blk The RCBs we belong to, e.g. board.rows[row_idx]

    '''
    unsolved_cell_value = 0 # Used to signal cell hasn't been set()
    num_values = RCB_SIZE
    all_cell_values = set(range(1,num_values+1))

    def __init__(self, board, cell_num) :
        ''' Creates a Cell.  cell_num runs 0 to Board.num_cells.
        cell_num increases in raster order, i.e. cell 0 is upper left
        and Board.num_cells-1 is lower right

        The cell will have an unsolved value.
        row/col/blk are non-None if board is provided
        '''
        self.board = board # The board we belong to

        # Assume board is None. If not, these are overwritten in a bit
        self.row = None
        self.col = None
        self.blk = None
        self.rcbs = [None] * 3

        # Sanity checks
        assert 0 <= cell_num < NUM_CELLS
        self.cell_num = cell_num

        # Remember which row/col/blk we belong to
        # e.g Each cell has a row_num and row_idx (likewise for cols[], and blks[]
        # where rows[row_num].cells[row_idx] (or rows[row_num][row_idx]) retrieves a cell
        # Likewise for cols and blks

        # We figure our (row,col) in the board and have someone else compute the indexes
        row_num = self.cell_num // RCB_SIZE
        col_num = self.cell_num  % RCB_SIZE

        (self.row_num, self.row_idx) = self.map_row_col_to_indexes(RCB_TYPE_ROW, row_num, col_num)
        (self.col_num, self.col_idx) = self.map_row_col_to_indexes(RCB_TYPE_COL, row_num, col_num)
        (self.blk_num, self.blk_idx) = self.map_row_col_to_indexes(RCB_TYPE_BLK, row_num, col_num)

        # Mark us unsolved with all possibles
        self.value = Cell.unsolved_cell_value
        self.possible_values = Cell.all_cell_values.copy()

        # Remember our RCBs
        if board :
            self.row = self.board.rows[self.row_num]
            self.col = self.board.cols[self.col_num]
            self.blk = self.board.blks[self.blk_num]

            self.rcbs = (self.row, self.col, self.blk)
            

    def set(self, value) :
        '''Sets value into cell
             value, possible_values
             Board.unsolved_cells

        We adjust our neighbors, (all cells in our
        row,col, and blk) by removing value from their possible_values
        
        '''
        # Error check value
        assert value in Cell.all_cell_values

        # Make sure data structs are consistent
        assert value in self.possible_values
        assert self in self.board.unsolved_cells

        # Our data structs
        self.value = value
        self.possible_values = set() # empty possible_values

        # Our Board's data structs
        self.board.unsolved_cells.remove(self)

        # Adjust our neighbors
        # Fix up the row/col/blk's we are in
        for rcb in self.rcbs :
            rcb.cell_was_set(self)


    def rcb_num_and_idx(self, rcb_type) :
        ''' Returns tuple of ( row/col/blk_num, row/col/blk_indx)
        as specified by rcb_type.

        e.g. with rcb_type of RCB_TYPE_ROW, returns:
            (self.row_num of the cell's row and
             self.row_idx of our position in that row
            )
        '''

        if rcb_type   == RCB_TYPE_ROW :
            return ( self.row_num, self.row_idx)
        elif rcb_type == RCB_TYPE_COL :
            return ( self.col_num, self.col_idx)
        elif rcb_type == RCB_TYPE_BLK :            
            return ( self.blk_num, self.blk_idx)
        else :
            assert False, "Bad arg: rcb_type: %d" % rcb_type

        assert False, "Impossible Place"


    def all_neighbors(self) :
        ''' Returns set of cells which are in same row, col, and blk
        as us.  self is NOT in the list.  No cell is duplicated, hence
        the set
        '''

        # iterate thru self.rcbs() when RCB iterator works
        # put all our neighbors together
        ans = set()  # What we return

        # Put unique cells into ans
        for rcb in self.rcbs :
            ans = ans.union( set(list(rcb)) )

        # and take thyself out
        ans.remove(self) 

        return ans


    def map_row_col_to_indexes(self, rcb_type, row_num, col_num) :
        ''' Given row_num, col_num of a cell in the board,
        returns touple of array_index of the RCB, e.g. into self.rows/cols/blks[]
                      cell_index in RCB.rcb[]
        '''

        if rcb_type == RCB_TYPE_ROW :
            return (row_num, col_num)

        elif rcb_type == RCB_TYPE_COL :
            return (col_num, row_num)

        elif rcb_type == RCB_TYPE_BLK :
            blks_per_row = RCB_SIZE // BLK_SIZE

            # We First compute (x,y) of block in board
            # and convert that to block number

            # Get (x,y) of what block we are in
            blk_x = col_num // BLK_SIZE
            blk_y = row_num // BLK_SIZE

            # convert to blk_num
            blk_num = blk_y * blks_per_row + blk_x

            # get (x,y) of cell in blk
            cell_x_in_blk = col_num % BLK_SIZE
            cell_y_in_blk = row_num % BLK_SIZE

            # Compute index of cell in block
            blk_idx = cell_y_in_blk * BLK_SIZE + cell_x_in_blk

            return (blk_num, blk_idx)

        else :
            assert False, "Unknown rcb_type:" + str(rcb_type) + " Should be one of:" + str(ALL_RCB_TYPES)

        assert False, "Impossible place"


    def __str__(self) :
        ''' Return human readable multi-line string that
        describes all our data
        '''
        ret_str  = "Cell#: %d" % self.cell_num                            + '\n'

        # value
        value_str = str(self.value) if self.value != Cell.unsolved_cell_value else 'Unknown'
        ret_str += "  value: %s" % ( value_str)                           + '\n'
        
        # possible_values
        sorted_possible_values = list(self.possible_values)
        sorted_possible_values.sort()
        ret_str += "  possible_values: %s" % (str(sorted_possible_values))+ '\n'

        # row/col/blk numbers and offset
        ret_str += "  row#: %d offset:%d" % (self.row_num, self.row_idx)  + '\n'
        ret_str += "  col#: %d offset:%d" % (self.col_num, self.col_idx)  + '\n'
        ret_str += "  blk#: %d offset:%d" % (self.blk_num, self.blk_idx)  + '\n'

        # All done                                            
        return ret_str

    def str_value(self, desired_length=1, unsolved_char = ' ') :
        ''' Returns cell.value as string of desired_length
        with the numeric value right justified.
        unsolved cells return unsolved_char.
        '''
        return "%*s" %(desired_length,
                       self.value if self.value != Cell.unsolved_cell_value else unsolved_char )



# Test code
import unittest

class Test_cell(unittest.TestCase):

    def test_cell_constructor(self):

        # Make a boards worth of independent cells, i.e. no board associated with them
        for cell_num in range(NUM_CELLS) :
            cell = Cell(None, cell_num)

            # Confirm it knows where it is on the board
            self.assertEqual (cell.cell_num, cell_num, "Cell number doesn't match")

            # Each cell has a row_num and row_idx (likewise for cols[], and blks[]
            # where rows[row_num].cells[row_idx] (or rows[row_num][row_idx] retrieves a cell
            # Likewise for cols and blks
            # The Cell constructor computes these from cell_num
            # We check by going backwards from row/col/blk_num, row/col/blk_idx to cell_num
            # and verify that they are equal

            # a common error message str
            def err_msg(cell_num, rgb_name, arr_idx, cell_idx, cell_num_from_rcb) :
                return "cell:%d cell_num of %s[%d].cells[%d] is %d. Should be %d" %     \
                (cell_num, rgb_name, arr_idx, cell_idx, cell_num_from_rcb, cell_num)


            # rows
            cell_num_should_be = cell.row_num * RCB_SIZE + cell.row_idx
            self.assertEqual( cell.cell_num, cell_num_should_be,
                              err_msg(cell.cell_num, "rows", cell.row_num, cell.row_idx, cell_num_should_be))

            # cols
            cell_num_should_be = cell.col_idx * RCB_SIZE + cell.col_num
            self.assertEqual( cell.cell_num, cell_num_should_be,
                              err_msg(cell.cell_num, "cols", cell.col_num, cell.col_idx, cell_num_should_be))

            # blks
            row_num_should_be = (cell.blk_num // BLK_SIZE) * BLK_SIZE + \
                                 cell.blk_idx // BLK_SIZE
            col_num_should_be = (cell.blk_num  % BLK_SIZE) * BLK_SIZE + \
                                 cell.blk_idx  % BLK_SIZE
            cell_num_should_be = row_num_should_be * RCB_SIZE + col_num_should_be

            self.assertEqual( cell.cell_num, cell_num_should_be,
                              err_msg(cell.cell_num, "blks", cell.blk_num, cell.blk_idx, cell_num_should_be))

    def test_bad_cell_num(self) :
        # Cell(None, 93) Should get an assertion error
        self.assertRaises( AssertionError, Cell, None, 93 )


    def test_sample_nums_and_idxs(self) :
        cell = Cell(None, 22)
        self.assertEqual( cell.row_num, 2)
        self.assertEqual( cell.row_idx, 4)
        self.assertEqual( cell.col_num, 4)
        self.assertEqual( cell.col_idx, 2)
        self.assertEqual( cell.blk_num, 1)
        self.assertEqual( cell.blk_idx, 7)
                          
        cell = Cell(None, 52)
        self.assertEqual( cell.row_num, 5)
        self.assertEqual( cell.row_idx, 7)
        self.assertEqual( cell.col_num, 7)
        self.assertEqual( cell.col_idx, 5)
        self.assertEqual( cell.blk_num, 5)
        self.assertEqual( cell.blk_idx, 7)
                          
        cell = Cell(None, 55)
        self.assertEqual( cell.row_num, 6)
        self.assertEqual( cell.row_idx, 1)
        self.assertEqual( cell.col_num, 1)
        self.assertEqual( cell.col_idx, 6)
        self.assertEqual( cell.blk_num, 6)
        self.assertEqual( cell.blk_idx, 1)
                          
    def test_values(self) :
        cell = Cell(None, 18) # Random cell

        # Should remember the board
        self.assertEqual( cell.board, None )

        # Should be unset
        self.assertEqual( cell.value, Cell.unsolved_cell_value )

        # All should be possible
        self.assertSetEqual ( cell.possible_values, Cell.all_cell_values)

    def test_rcb_num_and_idx(self) :
        # Test back RCB_TYPE as an argument
        cell = Cell(None, 18)
        bad_rcb_type = 42
        self.assertRaises(AssertionError, cell.rcb_num_and_idx, bad_rcb_type)

        # Try a random cell
        cell = Cell(None, 66)

        (rcb_num, rcb_idx) = cell.rcb_num_and_idx(RCB_TYPE_ROW)
        self.assertEqual (rcb_num, 7)
        self.assertEqual (rcb_idx, 3)

        (rcb_num, rcb_idx) = cell.rcb_num_and_idx(RCB_TYPE_COL)
        self.assertEqual (rcb_num, 3)
        self.assertEqual (rcb_idx, 7)

        (rcb_num, rcb_idx) = cell.rcb_num_and_idx(RCB_TYPE_BLK)
        self.assertEqual (rcb_num, 7)
        self.assertEqual (rcb_idx, 3)

        # And another                          
        cell = Cell(None, 23)

        (rcb_num, rcb_idx) = cell.rcb_num_and_idx(RCB_TYPE_ROW)
        self.assertEqual (rcb_num, 2)
        self.assertEqual (rcb_idx, 5)

        (rcb_num, rcb_idx) = cell.rcb_num_and_idx(RCB_TYPE_COL)
        self.assertEqual (rcb_num, 5)
        self.assertEqual (rcb_idx, 2)

        (rcb_num, rcb_idx) = cell.rcb_num_and_idx(RCB_TYPE_BLK)
        self.assertEqual (rcb_num, 1)
        self.assertEqual (rcb_idx, 8)


    def test_str_value(self) :
        cell = Cell(None, 33)

        # default replacement char is a space
        # Cell is unsolved, should get back all spaces
        self.assertEqual ( cell.str_value(1 ), ' '   ) 
        self.assertEqual ( cell.str_value(  ), ' '   ) # default desired_length is one
        self.assertEqual ( cell.str_value(20), ' '*20) 

        # Solve it
        cell.value = 8
        self.assertEqual ( cell.str_value( ),          '8' )
        self.assertEqual ( cell.str_value(6 ), ' '*5 + '8' )

        # Do it again with X as replacement char
        cell = Cell(None, 18)

        # Cell is unsolved, should get back all spaces + replacement char
        self.assertEqual ( cell.str_value(1,  'X'              ), 'X'         ) 
        self.assertEqual ( cell.str_value(    unsolved_char='X'), 'X'         ) # default desired_length is one
        self.assertEqual ( cell.str_value(14, 'X'              ), ' '*13 + 'X') 

        # Solve it
        cell.value = 6
        self.assertEqual ( cell.str_value(unsolved_char='Z' ),  '6' )
        self.assertEqual ( cell.str_value(6, 'Y' ),             ' '*5 + '6' )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    

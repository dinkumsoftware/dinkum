#!/usr/bin/env python3
# dinkum/sudoku/board.py
''' Defines sudoku Board class which represents a
sudoku board full of Cells with values.
'''

# 2019-11-25 tc Initial
# 2019-11-26 tc Gave names to boards
# 2019-11-30 tc Added board description
# 2019-12-02 tc Added some spaces in __str__() output

from dinkum.sudoku.rcb   import *
from dinkum.sudoku.cell  import *

import time

class Board :
    ''' Holds the representation of of a sudoku board.
    Has a solve() which will solve the Board by altering
    it in place.

    Various data:
      name            Name of the board, set in constructor
      description     Description of the board, set in constructor
    

      cells           List of all Cells in raster order,
                      i.e. left to right, top to bottom
      unsolved_cells  Set of Cells that need to be filled in with a value

      rows,cols,blks  [] of Cells in that entity.  Indexed by {row/col/blk}_num
                      Can be retrieved by rcb()

    Board()[row][col] can be used to get Cell at (row,col)

    '''

    def __init__(self, arr=None, name=None, desc="") :
        ''' constructor of a Board
        arr is list of row-lists
        If arr is None, an empty board will be created.

        name is used as the name of the board.
        If None, a unique name will be chosen, something on
        the order of:
            board-<lots of numbers which represent the curr time> 

        desc is description of the board, i.e. it's source or
        characteristics.  It defaults to empty string.

        raise ExcBadPuzzleInput if "arr" is bad
        various assertion failures if things aren't right.
        '''

        # Deal with the name/description
        self.name = name if name else self.unique_board_name()
        self.description = desc
        
        # We are generating new board from a list of row-lists
        # We create empty data structs and have set() adjust them

        # Create all rows/cols/blocks.  Make them empty
        self.rows = [ RCB(RCB_TYPE_ROW, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 
        self.cols = [ RCB(RCB_TYPE_ROW, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 
        self.blks = [ RCB(RCB_TYPE_ROW, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 

        # List of all Cells indexed by cell#
        # Is inited to unsolved and all values possible
        # We pass our self in so Cell knows what board it belongs to
        # Cell() initializes the rows/cols/blks it belongs to
        # These are created in raster order
        self.cells = [ Cell(self, cell_num) for cell_num in range(NUM_CELLS)]

        # A separate Set of Cells that are unsolved.
        # Currently all cells are unsolved
        # Note: We use Set rather than list because set is faster than []
        self.unsolved_cells = set(self.cells)
        assert len( self.unsolved_cells) == NUM_CELLS

        # Populate all rows/cols/blocks
        for cell in self.cells :
            # Populate all the rows/cols/blks that this cell belongs to
            self.rows[cell.row_num][cell.row_idx] = cell
            self.cols[cell.col_num][cell.col_idx] = cell
            self.blks[cell.blk_num][cell.blk_idx] = cell

        # Is there any input to set cells with?
        if not arr :
            return # nope, all done


        # We have a valid empty board at this point
        # We need to populate it with values as spec'ed by the caller

        # Go thru and set each cell value from our input,
        # set() adjusts all the data structures
        if len(arr) != RCB_SIZE :    # Sanity check input
            raise ExcBadPuzzleInput( "Wrong number of rows: %d" % len(arr) )

        cell_num=0
        row_num =0
        for row in arr :
            # Sanity check
            if len(row) != RCB_SIZE :
                raise ExcBadPuzzleInput( "Row %d: Wrong size: %d" % (row_num, len(row)))

            col_num = 0
            for value in row :
                # who we are testing
                cell=self.cells[cell_num]
                
                # Skip unknown values, all data bases init'ed for all unknown
                if value != Cell.unsolved_cell_value:
                    # Sanity check the value
                    if value not in Cell.all_cell_values :
                        raise ExcBadPuzzleInput( "Bad value: %d at (row,col) (%d,%d)" % (value, row_num, col_num))

                    # Common error msg for duplicate entries, which Should be formated with
                    # (cell_num, row_num, col_num, value, "row/col/blk"
                    err_fmt_str = "cell#%d at (%d,%d) value:%d is duplicated in cell's %s"

                    # We know that cell is currently unset
                    assert cell.value == Cell.unsolved_cell_value

                    # Can't have duplicate values in a row/col/blk
                    if value in [ cell.value for cell in cell.row] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "row"))
                    if value in [ cell.value for cell in cell.col] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "col"))
                    if value in [ cell.value for cell in cell.blk] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "blk"))

                    # All looks good, set it
                    cell.set(value)

                cell_num += 1
                col_num += 1
            row_num += 1

        # Sanity check(s) A whole bunch of asserts
        # Could move this into unittest code....
        # but we aren't time sensitive at construction time
        self.sanity_check()


    def solve(self) :
        ''' Returns a Board that solve us.
            Return None if unsolvable
           raise Exception on multiple solutions 
            We change our values in the process '''

        # We try all the solution techniques we know about
        # Each is required to return True if they set a cell
        # We give up when no cell is set in a pass
        a_cell_was_set = False
        while (not self.is_solved()) :
            # Set cells with only 1 possible value
            a_cell_was_set |= self.solve_cells_with_single_possible_value()
            
            # How did we do?
            if not a_cell_was_set :
                return None  # Not well, sigh

        # If we fall out of the loop... we solved the puzzle!
        return self

    
    def solve_cells_with_single_possible_value(self) :
        '''Sets all unsolved cells on the board that have a single possible value.
        Returns True if any cell was set.
        '''

        # We are going to iterate thru this
        # We have to make a copy because self.unsolved_cells
        # will change during the iteration
        unsolved_cells = self.unsolved_cells.copy()

        we_set_a_cell = False
        for cell in unsolved_cells :
            if len(cell.possible_values) == 1 :
                # Extract the only element in the set.  Leave num_possible_values intact
                # See https://stackoverflow.com/questions/20625579/access-the-sole-element-of-a-set
                [value] = cell.possible_values

                # and set that value into the cell
                # This also adjusts all the row/col/blk of cell
                # by removing value from their possible_values
                cell.set(value) 

                # Remember we set a cell
                we_set_a_cell = True

        return we_set_a_cell

    
    def __getitem__(self, row) :
        ''' Returns our RCB at row
            Allows Board()[row][col] to return a cell
        '''
        return self.rows[row]

    def rcb(self, rcb_type) :
        ''' Return [] of RCBs, rows[], cols[], or blks[]
        depending on rcb_type
        '''

        if   rcb_type == RCB_TYPE_ROW :
            return self.rows
        elif rcb_type == RCB_TYPE_COL :
            return self.cols
        elif rcb_type == RCB_TYPE_BLK :
            return self.blks
        else :
            assert False, "Unknown rcb_type:" + str(rcb_type) + " Should be one of:" + str(ALL_RCB_TYPES)
        assert False, "Impossible place"





    def is_solved(self) :
        ''' returns true if board is solved '''
        return len(self.unsolved_cells) == 0


    def output(self) :
        ''' returns list of rows of the Board.
        Same format as __init__ argument '''

        # Build [] of rows where every row is [] of cells in it
        arr = [[ cell.value for cell in self.rows[row_indx]] for row_indx in range(RCB_SIZE) ]

        return arr

    def __str__(self) :
        ''' returns human readable terse picture of a sudoku.
        The last line is terminated by a new line.

        Example:
         3 4 6  1 2 7  9 5 8
         7 8 5  6 9 4  1 3 2
         2 1 9  3 8 5  4 6 7

         4 6 2  5 3 1  8 7 9
         9 3 1  2 7 8  6 4 5
         8 5 7  9 4 6  2 1 3

         5 9 8  4 1 3  7 2 6
         6 2 4  7 5 9  3 8 1
         1 7 3  8 6 2  5 9 4

        '''
        ret_str = ""
        for row in self.rows :
            # row separator?
            if row.rcb_num and not row.rcb_num % BLK_SIZE :
                ret_str += '\n'
                
            # Print the cell values
            for cell in row :
                # Vertial block separator?
                if cell.col_num and not cell.col_num % BLK_SIZE :
                    ret_str += ' '

                # Cell's value
                ret_str += "%2d" % cell.value

            ret_str += '\n'

        return ret_str

    def unique_board_name(self) :
        ''' Picks a unique name for the board comprised of:
        board-<current_time as bunch of numbers>
        '''
        nanosecs_from_1970 = time.time() * 10**9

        return "board-" + str(int(nanosecs_from_1970))

    def is_subset_of(self, their_board) :
        ''' returns True if every cell in our Board has
        the same value "their_board"
        '''
        # Iterate over both our cells
        for (our_cell, their_cell) in zip(self.cells, their_board.cells) :
            # Is our cell set?
            if our_cell.value != Cell.unsolved_cell_value :
                # Yes, is it the same?
                if our_cell.value != their_cell.value :
                    return False # nope, they differ

        # If we fall out of the loop.. it's a subset
        return True
                


    # Operators
    def __eq__(self, their) :
        ''' == tester.  We just require all cells to have the same value
        '''
        # If they aren't a Board, we aren't equal
        if not isinstance (their, Board)  :
            return False

        # Iterate cells together
        for (our_cell, their_cell) in zip(self.cells, their.cells) :
            if our_cell.value != their_cell.value :
                return False  # we are NOT equal

        # If we fall out, all cells matched.
        return True

    def sanity_check(self) :
        ''' Runs a variety of checks on the data structures.
        assert's on first failure.
        '''

        # Make sure all rows/cols/blks got populated
        for rcb_num in range(RCB_SIZE) :
            for indx in range(RCB_SIZE) :
                if not self.rows[rcb_num][indx] : assert "Unpopulated row:% entry:%d" % (rcb_num, indx)
                if not self.cols[rcb_num][indx] : assert "Unpopulated col:% entry:%d" % (rcb_num, indx)
                if not self.blks[rcb_num][indx] : assert "Unpopulated blk:% entry:%d" % (rcb_num, indx)

        # Make sure cells/rows/cols/blks all refer to the same cell
        # Raster scan cells/rows/cols/blks
        cell_num = 0
        for row_num in range(RCB_SIZE) :
            for col_num in range(RCB_SIZE) :

                # cells[] are in raster order
                cell = self.cells[cell_num]

                # Confirm cell number matches
                assert cell.cell_num == cell_num, "Cell.num %d should be %d" % (cell.cell_num, cell_num)

                # Confirm raster order
                assert cell.row_num == row_num, "cell%d has row#%d, should be %d" % (cell.cell_num,
                                                                                     cell.row_num, row_num)
                assert cell.col_num == col_num, "cell%d has col#%d, should be %d"  % (cell.cell_num,
                                                                                      cell.col_num, col_num)
                # We don't check blk because too hard to compute block number here.

                # The cells notion of row/col/blk should match ours
                assert cell.row is self.rows[cell.row_num], "Cell.row is wrong"
                assert cell.col is self.cols[cell.col_num], "Cell.col is wrong"
                assert cell.blk is self.blks[cell.blk_num], "Cell.blk is wrong"

                # We compare each row/col/blk to this cell
                cell_by_rows  = cell.row[cell.row_idx]
                cell_by_cols  = cell.col[cell.col_idx]
                cell_by_blks  = cell.blk[cell.blk_idx]

                # They should all be the same
                assert cell_by_rows is cell, "Cell#%d is not same as cell in rows[%d][%d]" % (cell_num,
                                                                                              cell.row_num,
                                                                                              cell.row_idx)
                assert cell_by_cols is cell, "Cell#%d is not same as cell in cols[%d][%d]" % (cell_num,
                                                                                              cell.col_num,
                                                                                              cell.col_idx)
                assert cell_by_blks is cell, "Cell#%d is not same as cell in blks[%d][%d]" % (cell_num,
                                                                                              cell.blk_num,
                                                                                              cell.blk_idx)
                # Advance to next cell
                cell_num += 1

        # If all out of loop... all went well
        return (True, None )

# Test code
import unittest
import copy

class Test_board(unittest.TestCase):


    def test_empty_board(self) :
        board = Board() # No cells should be set

        # Confirm none set
        for cell in board.cells :
            self.assertEqual (cell.value, Cell.unsolved_cell_value,
                         "Cell# %d should be unset, it is: %d" % (cell.cell_num, cell.value))
            # All values should be possible
            self.assertSetEqual (cell.possible_values, Cell.all_cell_values,
                                 "Cell# %d: num_possibles should have all possible values" %cell.cell_num)
                       
    def test_board_name(self) :
        name = "I never know what to call you"
        board = Board(None, name)
        self.assertEqual(name, board.name)
        self.assertEqual(board.description, "")  # No description supplied, default ""

        name = "The world is a tough place"
        desc = "Isn't that cynical?"
        board = Board(None, name, desc)
        self.assertEqual(name, board.name)
        self.assertEqual(board.description, desc)

    def test_unique_board_names(self) :

        # Generate a bunch of boards and make sure names are all different
        names_so_far = set()
        for cnt in range(100) :
            board = Board()

            assert board.name not in names_so_far

            names_so_far.add(board.name)
        

    def test_subset(self) :
        # What we test with
        some_board_spec = [ \
                    [3, 4, 6, 1, 2, 7, 9, 5, 8], 
                    [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                    [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                    [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                    [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                    [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                    [5, 9, 8, 4, 1, 3, 7, 2, 6],
                    [6, 2, 4, 7, 5, 9, 3, 8, 1],
                    [1, 7, 3, 8, 6, 2, 5, 9, 4]]
        some_board = Board(some_board_spec, "some_board" )

        # An empty board is a subset of everything
        empty_board=Board()
        self.assertTrue ( empty_board.is_subset_of(some_board))

        # Everyboard is a subset of itself
        self.assertTrue (some_board.is_subset_of(some_board))

        # Create a legal subset by zeroing some elements
        subset_spec = some_board_spec.copy()
        subset_spec[0][3] = 0
        subset_spec[5][0] = 0
        subset_spec[2][3] = 0
        subset_spec[8][1] = 0
        subset_spec[4][0] = 0
        subset_board=Board(subset_spec, "subset_board", "For unit testing")
        self.assertTrue (subset_board.is_subset_of(some_board))        

        # Create a non-subset 
        non_subset_spec = [ [0]*9, [0]*9, [0]*9,
                            [0]*9, [0]*9, [0]*9,
                            [0]*9, [0]*9,
                            [0]*8 + [9]      # was a 4 in some_board
        ]

        non_subset_board=Board(non_subset_spec, "non subset board")
        self.assertFalse ( non_subset_board.is_subset_of(some_board) )

    def test_cell_all_neighbors(self) :
        # By rights it should be in the unittest for cell.py
        # but it can't because it would mean cyclical imports
        # so... we test it here

        board = Board()

        # Test a few at random
        cell = board[3][7]
        cell_neighbors_are = cell.all_neighbors()

        cell_neighbors_should_be  = [board.cells[idx] for idx in range(27, 36   ) if idx != cell.cell_num] # row
        cell_neighbors_should_be += [board.cells[idx] for idx in range( 7, 80, 9) if idx != cell.cell_num] # col
        cell_neighbors_should_be += [board.cells[idx] for idx in [42, 44, 51, 53]] # blk: that aren't in row/col
        cell_neighbors_should_be = set( cell_neighbors_should_be)

        self.assertEqual( cell_neighbors_are, cell_neighbors_should_be)
                                     

        cell = board[2][4]
        cell_neighbors_are = cell.all_neighbors()

        cell_neighbors_should_be  = [board.cells[idx] for idx in range(18, 27   ) if idx != cell.cell_num] # row
        cell_neighbors_should_be += [board.cells[idx] for idx in range( 4, 81, 9) if idx != cell.cell_num] # col
        cell_neighbors_should_be += [board.cells[idx] for idx in [3,5,12,14]] # blk: that aren't in row/col
        cell_neighbors_should_be = set( cell_neighbors_should_be)

        self.assertEqual( cell_neighbors_are, cell_neighbors_should_be)

        



    def test_input_bad_input_wrong_row_cnt(self) :
        # Only 7 rows, values don't matter
        puzzle = [ [0] * 9 for i in range(7) ]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Wrong number of rows: 7')


    def test_input_bad_value(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]
        
        # Make a single bad value
        puzzle[3][6] = 18

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message,
                             'Bad value: 18 at (row,col) (3,6)')

    def test_input_bad_input_wrong_row_size(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]

        # remove an cell from a row
        puzzle[4] = puzzle[4][1:]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Row 4: Wrong size: 8')

    def test_input_duplicate_values(self) :
        some_board_spec = [ \
                            [0, 4, 6, 1, 2, 7, 9, 5, 8], # 0 row
                            [7, 0, 0, 6, 9, 4, 1, 3, 2], # 1 row
                            [2, 1, 9, 0, 0, 0, 4, 6, 7], # 2 row
                            [4, 6, 2, 5, 3, 1, 0, 0, 0], # 3 row
                            [0, 3, 0, 2, 0, 8, 0, 0, 0], # 4 row
                            [8, 5, 7, 9, 4, 6, 2, 0, 3], # 5 row
                            [0, 9, 8, 4, 1, 3, 7, 2, 6], # 6 row
                            [6, 2, 4, 7, 5, 9, 3, 8, 1], # 7 row
                            [1, 7, 3, 8, 6, 2, 5, 9, 4]  # 8 row
                #       col  0  1  2  3  4  5  6  7  8
        ]

        # Make some illegal input
        # duplicate value in a row
        dup_in_row = copy.deepcopy(some_board_spec)
        dup_in_row[3][7] = 1
        expected_err_msg = "cell#34 at (3,7) value:1 is duplicated in cell's row"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_row) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_row)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # duplicate value in a col
        dup_in_col = copy.deepcopy(some_board_spec)
        dup_in_col[4][7] = 5
        dup_in_col[3][3] = 0 # avoid duplicate in the block
        expected_err_msg = "cell#43 at (4,7) value:5 is duplicated in cell's col"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_col) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_col)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message
            
        # duplicate value in a blk
        dup_in_blk = copy.deepcopy(some_board_spec)
        dup_in_blk[6][7] = 4
        expected_err_msg = "cell#61 at (6,7) value:4 is duplicated in cell's row"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_blk) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_blk)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


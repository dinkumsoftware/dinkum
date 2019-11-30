#!/usr/bin/env python3
# dinkum/sudoku/board.py
''' Defines sudoku Board class which represents a
sudoku board full of Cells with values.
'''

# 2019-11-25 tc Initial
# 2019-11-26 tc Gave names to boards
# 2019-11-30 tc Added board description

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
        
        # We are generating new board from list of row-lists
        # We create empty data structs and have set() adjust them

        # Create all rows/cols/blocks.  Make them empty
        self.rows = [ None ] * RCB_SIZE
        self.cols = [ None ] * RCB_SIZE
        self.blks = [ None ] * RCB_SIZE

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
            # If need be, create the RCB itself
            # Initial RCB has all Cells set to None
            if not self.rows[cell.row_num] : self.rows[cell.row_num] = RCB(self, cell.row_num)
            if not self.cols[cell.col_num] : self.cols[cell.col_num] = RCB(self, cell.col_num)
            if not self.blks[cell.blk_num] : self.blks[cell.blk_num] = RCB(self, cell.blk_num)

            # Populate all the rows/cols/blks that this cell belongs to
            self.rows[cell.row_num][cell.row_idx] = cell
            self.cols[cell.col_num][cell.col_idx] = cell
            self.blks[cell.blk_num][cell.blk_idx] = cell

        # Sanity check.  Make sure all rows/cols/blks got populated
        for rcb_num in range(RCB_SIZE) :
            for indx in range(RCB_SIZE) :
                if not self.rows[rcb_num][indx] : assert "Unpopulated row:% entry:%d" % (rcb_num, indx)
                if not self.cols[rcb_num][indx] : assert "Unpopulated col:% entry:%d" % (rcb_num, indx)
                if not self.blks[rcb_num][indx] : assert "Unpopulated blk:% entry:%d" % (rcb_num, indx)

        # Is there any input to set cells with?
        if not arr :
            return # nope


        # Go thru and set each cell value from our input,
        # set() adjusts all the data structures
        if len(arr) != RCB_SIZE :    # Sanity check input
            raise ExcBadPuzzleInput( "Wrong number of rows: %d" % len(arr) )

        # <todo> ######################### don't need cell/row num here.... retrieve from cell
        cell_num=0
        row_num =0
        for row in arr :
            # Sanity check
            if len(row) != RCB_SIZE :
                raise ExcBadPuzzleInput( "Row %d: Wrong size: %d" % (row_num, len(row)))

            col_num = 0
            for value in row :
                # Skip unknown values, all data bases init'ed for all unknown
                if value != Cell.unsolved_cell_value:
                    # Sanity check the value
                    if value not in Cell.all_cell_values :
                        raise ExcBadPuzzleInput( "Bad value: %d at (row,col) (%d,%d)" % (value, row_num, col_num))

                    cell=self.cells[cell_num]
                    cell.set(value)

                cell_num += 1
                col_num += 1
            row_num += 1

        # ##################################################
        # <todo> check for duplicate numbers in rows/cols/blks

        # Sanity check(s)
        (sanity_check_passed, err_msg) = self.sanity_check()
        assert sanity_check_passed, "sanity_check() failed:"+err_msg
        


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
        returns a touple: (passed, err_msg_if_failed)
        It stops testing and returns on the first failure
        err_msg_if_failed will be None if passed
        '''

        # ##################################
        return (True, None)
    # ##################################



        # Make sure cells/rows/cols/blks all refer to the same cell
        # Raster scan cells/rows/cols/blks
        cell_num = 0
        for row_num in range(RCB_SIZE) :
            for col_num in range(RCB_SIZE) :

                # We compare each row/col/blk to this cell
                cell_by_cells = self.cells[cell_num] # cells[] are in raster order

                # Do all rows/cols/blks for this cell
                # <todo> fix this NOT to use Cell.map_row_col_to_indexes
                for rcb_type in self.all_rcb_types :
                    # Translate row and column into indexes in row/col/blks and correspond cells[]
                    (arr_indx,cell_indx) = Board.map_row_col_to_indexes(rcb_type, row_num, col_num)

                    # Fetch and compare the cells
                    cell_by_rcb  = self.rcb(rcb_type)[arr_indx][cell_indx]

                    # Compare them and complain if un-equal
                    if cell_by_cells != cell_by_rcb :
                        return ( False,
                                 "%s[%d].cell[%d] != cells[%d] @ row/col (%d,%d)" %
                                 (Board.rcb_names[rcb_type],
                                  arr_indx, cell_indx,
                                  cell_num,
                                  row_num, col_num))
                    
                # Advance to next cell
                cell_num += 1

        # If all out of loop... all went well
        return (True, None )

# Test code
import unittest

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



if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


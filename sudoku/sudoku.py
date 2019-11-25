#!/usr/bin/env python3
# dinkum/sudoku/sudoku.py
''' sudoku_solver() solves a sudoku puzzle
Various classes defined Board, Cell, etc

Solution technique does NOT involve guessing.
It only fills in cells that have no alternative.
'''

# 2019-11-01 tc Initial
# 2019-11-07 tc Made Board(None) return empty board
# 2019-11-23 tc Bug fix in sanity_check()
# 2019-11-25 tc various bug fixes

###################
#<todo>
# Change RCB.rcb to RCB.cells
# Add rcb_type as RCB member and constructor
# Test pre-solved
# print out nonsolvabe puzzles
# print out timings
# Have some set indicate there are cells with single possible values
###################

import math
import copy
import re
                      
# Exceptions we can toss
# The general approach is to raise an exception if the error is a result of user input.
# Otherwise, we assert things to perform sanity checks
class ExcUnsolvable(Exception) :
    def __init__(self) :
        self.message="Puzzle is NOT solvable"


class ExcBadPuzzleInput(Exception) :
    ''' Something wrong with puzzle given to be solved.
    Raiser should pass in error msg to contructor
    '''
    def __init__(self, message) :
        self.message=message



def sudoku_solver(puzzle):
    ''' return solution to puzzle as a Board
    raise Exception on no solutions
    puzzle should be [] of row-lists
    '''

    board = Board(puzzle)

    # Return a board that solves board
    solution=board.solve()

    # Toss Exception if can't solve
    if solution :
        return solution.output() # Uniquely solved!
    else :
        raise ExcUnsolvable()
        

class Board :
    ''' Holds the representation of of a sudoku board.
    Has a solve() which will solve the Board by altering
    it in place.

    Various data:
      cells           List of all Cells in raster order,
                      i.e. left to right, top to bottom
      unsolved_cells  Set of Cells that need to be filled in with a value

      rows,cols,blks  [] of Cells in that entity.  Indexed by {row/col/blk}_num
                      Can be retrieved by rcb()
    '''

    # class variables
    rcb_size = 9 # num items in row/col/blk
    num_cells = rcb_size * rcb_size
    blk_size = int(math.sqrt(rcb_size)) # Size of blocks e.g. 3x3 in 9x9 grid

    # enums which label row/cols/blks
    rcb_type_row = 0
    rcb_type_col = 1
    rcb_type_blk = 2
    all_rcb_types = [rcb_type_row, rcb_type_col, rcb_type_blk]
    rcb_names =     ["rows",       "cols",       "blks"      ] # indexed by rcb_type_X

    # End of class variables

    def __init__(self, arr=None) :
        ''' constructor of a Board
        arr is list of row-lists
        If arr is None, an empty board will be created.

        raise ExcBadPuzzleInput if "arr" is bad
        various assertion failures if things aren't right.
        '''
        
        # We are generating new board from list of row-lists
        # We create empty data structs and have set() adjust them

        # Create all rows/cols/blocks.  Make them empty
        self.rows = [ None ] * Board.rcb_size
        self.cols = [ None ] * Board.rcb_size
        self.blks = [ None ] * Board.rcb_size

        # List of all Cells indexed by cell#
        # Is inited to unsolved and all values possible
        # We pass our self in so Cell knows what board it belongs to
        # Cell() initializes the rows/cols/blks it belongs to
        # These are created in raster order
        self.cells = [ Cell(self, cell_num) for cell_num in range(Board.num_cells)]

        # A separate Set of Cells that are unsolved.
        # Currently all cells are unsolved
        # Note: We use Set rather than list because set is faster than []
        self.unsolved_cells = set(self.cells)
        assert len( self.unsolved_cells) == Board.num_cells

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
        for rcb_num in range(Board.rcb_size) :
            for indx in range(Board.rcb_size) :
                if not self.rows[rcb_num][indx] : assert "Unpopulated row:% entry:%d" % (rcb_num, indx)
                if not self.cols[rcb_num][indx] : assert "Unpopulated col:% entry:%d" % (rcb_num, indx)
                if not self.blks[rcb_num][indx] : assert "Unpopulated blk:% entry:%d" % (rcb_num, indx)

        # Is there any input to set cells with?
        if not arr :
            return # nope


        # Go thru and set each cell value from our input,
        # set() adjusts all the data structures
        if len(arr) != Board.rcb_size :    # Sanity check input
            raise ExcBadPuzzleInput( "Wrong number of rows: %d" % len(arr) )

        # <todo> ######################### don't need cell/row num here.... retrieve from cell
        cell_num=0
        row_num =0
        for row in arr :
            # Sanity check
            if len(row) != Board.rcb_size :
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

        # Sanity check(s)
        assert cell_num == self.num_cells, "Software Error: cell_num mismatch"
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

        if   rcb_type == Board.rcb_type_row :
            return self.rows
        elif rcb_type == Board.rcb_type_col :
            return self.cols
        elif rcb_type == Board.rcb_type_blk :
            return self.blks
        else :
            assert False, "Unknown rcb_type:" + str(rcb_type) + " Should be one of:" + str(Board.all_rcb_types)
        assert False, "Impossible place"



    @staticmethod # Needs to be called in test code without a Board instance
    def map_row_col_to_indexes(rcb_type, row_num, col_num) :
        ''' Given row_num, col_num of a cell in the board,
        returns touple of array_index of the RCB, e.g. into self.rows/cols/blks[]
                      cell_index in RCB.rcb[]
        '''

        if rcb_type == Board.rcb_type_row :
            return (row_num, col_num)

        elif rcb_type == Board.rcb_type_col :
            return (col_num, row_num)

        elif rcb_type == Board.rcb_type_blk :
            blks_per_row = Board.rcb_size // Board.blk_size

            # We First compute (x,y) of block in board
            # and convert that to block number

            # Get (x,y) of what block we are in
            blk_x = col_num // Board.blk_size
            blk_y = row_num // Board.blk_size

            # convert to blk_num
            blk_num = blk_y * blks_per_row + blk_x

            # get (x,y) of cell in blk
            cell_x_in_blk = col_num % Board.blk_size
            cell_y_in_blk = row_num % Board.blk_size

            # Compute index of cell in block
            blk_idx = cell_y_in_blk * Board.blk_size + cell_x_in_blk

            return (blk_num, blk_idx)

        else :
            assert False, "Unknown rcb_type:" + str(rcb_type) + " Should be one of:" + str(Board.all_rcb_types)

        assert False, "Impossible place"


    def is_solved(self) :
        ''' returns true if board is solved '''
        return len(self.unsolved_cells) == 0


    def output(self) :
        ''' returns list of rows of the Board.
        Same format as __init__ argument '''

        # Build [] of rows where every row is [] of cells in it
        arr = [[ cell.value for cell in self.rows[row_indx]] for row_indx in range(Board.rcb_size) ]

        return arr

    def sanity_check(self) :
        ''' Runs a variety of checks on the data structures.
        returns a touple: (passed, err_msg_if_failed)
        It stops testing and returns on the first failure
        err_msg_if_failed will be None if passed
        '''

        # Make sure cells/rows/cols/blks all refer to the same cell
        # Raster scan cells/rows/cols/blks
        cell_num = 0
        for row_num in range(Board.rcb_size) :
            for col_num in range(Board.rcb_size) :

                # We compare each row/col/blk to this cell
                cell_by_cells = self.cells[cell_num] # cells[] are in raster order

                # Do all rows/cols/blks for this cell
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

class RCB :
    ''' Represents a row, column, or block.
    data:
      board    The Board we belong to
      rcb_num  The raster order row/column/block number (0 to Board.rcb_size-1)
      cells    a [] of cells in the row/column/block

    some funcs:
      [x] gets/sets cells[x]
    '''

    def __init__(self, board, rcb_num) :
        '''Creates an empty RCB.
        board   The board we belong to
        rcb_num Our index into board.row/col/blk

        cells[] is our [] of Cells that belong to us.
        It will be created with proper length and all values None.
        Counting on someone else to fill in cells[]
        '''
        self.board = board
        self.rcb_num = rcb_num
        self.cells = [None] * Board.rcb_size

    def __getitem__(self, idx) :
        ''' Returns our idx'th Cell
        '''
        return self.cells[idx]

    def __setitem__(self, idx, cell) :
        ''' Sets our idx'th entry to cell
        '''
        self.cells[idx] = cell



class Cell :
    ''' Represents a single cell on the sudoku board. Has
    value           can be unsolved_cell_value or 1-9
    possible_values set of potential values, empty if value has been set
    board           The Board we belong to

    cell_num   0 to Board.num_cells-1

    All of these run 0 to Board.rcb_size-1 
    They are all in raster order
    row_num    which row we are  (Index into Board.rows)
    row_idx    which Cell in row (Index into Board.rows[row_num].cells)

    col_num    which col we are  (Index into Board.cols)
    col_idx    which Cell in col (Index into Board.cols[col_num].cells)

    blk_num    which blk we are  (Index into Board.blks)
    blk_idx    which Cell in blk (Index into Board.blks[blk_num].cells)

    '''
    unsolved_cell_value = 0 # Used to signal cell hasn't been set()
    num_values = Board.rcb_size
    all_cell_values = set(range(1,num_values+1))

    def __init__(self, board, cell_num) :
        ''' Creates a Cell.  cell_num runs 0 to Board.num_cells.
        cell_num increases in raster order, i.e. cell 0 is upper left
        and Board.num_cells-1 is lower right

        The cell will have an unsolved value.
        '''
        self.board = board # The board we belong to

        # Sanity checks
        assert 0 <= cell_num < Board.num_cells
        self.cell_num = cell_num

        # Remember which row/col/blk we belong to
        # e.g Each cell has a row_num and row_idx (likewise for cols[], and blks[]
        # where rows[row_num].cells[row_idx] (or rows[row_num][row_idx]) retrieves a cell
        # Likewise for cols and blks

        # We figure our (row,col) in the board and have someone else compute the indexes
        row_num = self.cell_num // Board.rcb_size
        col_num = self.cell_num  % Board.rcb_size

        (self.row_num, self.row_idx) = Board.map_row_col_to_indexes(Board.rcb_type_row, row_num, col_num)
        (self.col_num, self.col_idx) = Board.map_row_col_to_indexes(Board.rcb_type_col, row_num, col_num)
        (self.blk_num, self.blk_idx) = Board.map_row_col_to_indexes(Board.rcb_type_blk, row_num, col_num)

        # Mark us unsolved with all possibles
        self.value = Cell.unsolved_cell_value
        self.possible_values = Cell.all_cell_values.copy()

    def set(self, value) :
        '''Sets value into cell
             value, possible_values
             Board.unsolved_cells

        We adjust our neighbors, (all cells in our
        row,col, and blk) by removing value from thier possible_values
        
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
        # Remove value from their possible_values
        for cell in self.all_neighbors() :
            cell.possible_values.discard(value) # does not complain if value not a member


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


    def all_neighbors(self) :
        ''' Returns set of cells which are in same row, col, and blk
        as us.  self is NOT in the list.  No cell is duplicated, hence
        the set
        '''

        row_neighbors = set([cell for cell in self.board.rows[self.row_num] if cell != self])
        col_neighbors = set([cell for cell in self.board.cols[self.col_num] if cell != self])
        blk_neighbors = set([cell for cell in self.board.blks[self.blk_num] if cell != self])

        return row_neighbors.union(col_neighbors,blk_neighbors)


# Test code
import unittest

class Test_sudoku(unittest.TestCase):

    def test_cell_constructor(self):

        # Make a boards worth of independent cells, i.e. no board associated with them
        for cell_num in range(Board.num_cells) :
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
            cell_num_should_be = cell.row_num * Board.rcb_size + cell.row_idx
            self.assertEqual( cell.cell_num, cell_num_should_be,
                              err_msg(cell.cell_num, "rows", cell.row_num, cell.row_idx, cell_num_should_be))

            # cols
            cell_num_should_be = cell.col_idx * Board.rcb_size + cell.col_num
            self.assertEqual( cell.cell_num, cell_num_should_be,
                              err_msg(cell.cell_num, "cols", cell.col_num, cell.col_idx, cell_num_should_be))

            # blks
            row_num_should_be = (cell.blk_num // Board.blk_size) * Board.blk_size + \
                                 cell.blk_idx // Board.blk_size
            col_num_should_be = (cell.blk_num  % Board.blk_size) * Board.blk_size + \
                                 cell.blk_idx  % Board.blk_size
            cell_num_should_be = row_num_should_be * Board.rcb_size + col_num_should_be

            self.assertEqual( cell.cell_num, cell_num_should_be,
                              err_msg(cell.cell_num, "blks", cell.blk_num, cell.blk_idx, cell_num_should_be))


    def test_empty_board(self) :
        board = Board() # No cells should be set

        # Confirm none set
        for cell in board.cells :
            self.assertEqual (cell.value, Cell.unsolved_cell_value,
                         "Cell# %d should be unset, it is: %d" % (cell.cell_num, cell.value))
            # All values should be possible
            self.assertSetEqual (cell.possible_values, Cell.all_cell_values,
                                 "Cell# %d: num_possibles should have all possible values" %cell.cell_num)
        

    def test_bad_input_wrong_row_cnt(self) :
        # Only 7 rows, values don't matter
        puzzle = [ [0] * 9 for i in range(7) ]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, sudoku_solver, puzzle)

        # Verify the error message
        try :
            sudoku_solver(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Wrong number of rows: 7')


    def test_bad_input_wrong_row_size(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]

        # remove an cell from a row
        puzzle[4] = puzzle[4][1:]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, sudoku_solver, puzzle)

        # Verify the error message
        try :
            sudoku_solver(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Row 4: Wrong size: 8')


    def test_bad_value(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]
        
        # Make a single bad value
        puzzle[3][6] = 18

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, sudoku_solver, puzzle)

        # Verify the error message
        try :
            sudoku_solver(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message,
                             'Bad value: 18 at (row,col) (3,6)')
                       

    def test_unsolvable(self) :
        # Try to solve a puzzle with all unknowns... Can't be done
        puzzle = [ [0] * 9 for i in range(9) ]

        self.assertRaises(ExcUnsolvable, sudoku_solver, puzzle)

    def test_presolved(self) :
        presolved = [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
                     [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                     [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                     [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                     [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                     [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                     [5, 9, 8, 4, 1, 3, 7, 2, 6],
                     [6, 2, 4, 7, 5, 9, 3, 8, 1],
                     [1, 7, 3, 8, 6, 2, 5, 9, 4]]

        self.assertEqual( sudoku_solver(presolved), presolved )

    def test_mindless(self) :
        '''All cells filled in but 1'''

        mindless =    [[0, 4, 6, 1, 2, 7, 9, 5, 8], 
                       [7, 0, 5, 6, 9, 4, 1, 3, 2], 
                       [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                       [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                       [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                       [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                       [5, 9, 8, 4, 1, 3, 7, 2, 6],
                       [6, 2, 4, 7, 5, 9, 3, 8, 1],
                       [1, 7, 3, 8, 6, 2, 5, 9, 4]]

        mindless_ans= [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
                       [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                       [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                       [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                       [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                       [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                       [5, 9, 8, 4, 1, 3, 7, 2, 6],
                       [6, 2, 4, 7, 5, 9, 3, 8, 1],
                       [1, 7, 3, 8, 6, 2, 5, 9, 4]]

        self.assertEqual( sudoku_solver(mindless), mindless_ans)

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()


#!/usr/bin/env python3
# dinkum/sudoku/sudoku.py
''' sudoku_solver() solves a sudoku puzzle
Various classes defined Board, Cell, etc

Solution technique does NOT involve guessing.
It only fills in cells that have no alternative.
'''


###################
#<todo>
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
      cells           List of all Cells
      unsolved_cells  Set of Cells that need to be filled in with a value
    '''

    # class variables
    rcb_size = 9 # num items in row/col/blk
    num_cells = rcb_size * rcb_size
    blk_size = int(math.sqrt(rcb_size)) # Size of blocks e.g. 3x3 in 9x9 grid


    def __init__(self, arr) :
        ''' constructor of a Board
        arr is list of row-lists
        raise ExcBadPuzzleInput if "arr" is bad
        various assertion failures if things aren't right.
        '''
        
        # We are generating new board from list of row-lists
        # We create empty data structs and have set() adjust them

        # List of all Cells indexed by cell#
        # Is inited to unsolved and all values possible
        # We pass our self in so Cell knows what board it belongs to
        self.cells = [ Cell(self, cell_num) for cell_num in range(Board.num_cells)]

        # A separate Set of Cells that are unsolved.
        # Currently all cells are unsolved
        # Note: We use Set rather than list because deletion is faster
        self.unsolved_cells = set(self.cells)
        assert len( self.unsolved_cells) == Board.num_cells

        # Go thru and set each value from our input,
        # set() adjusts all the data structures
        if len(arr) != Board.rcb_size :    # Sanity check input
            raise ExcBadPuzzleInput( "Wrong number of rows: %d" % len(arr) )

        cell_num=0
        row_num =0
        for row in arr :
            # Sanity check
            if len(row) != Board.rcb_size :
                raise ExcBadPuzzleInput( "Row %d; Wrong size: %d" % (row_num, len(row)))

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

        # Sanity check
        assert cell_num == self.num_cells, "Software Error: cell_num mismatch"


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
        we_set_a_cell = False
        for cell in self.unsolved_cells :
            if len(cell.possible_values) == 1 :
                # Extract the only element in the set.  Leave num_possible_values intact
                # See https://stackoverflow.com/questions/20625579/access-the-sole-element-of-a-set
                [value] = self.possible_value

                # and set that value into the cell
                cell.set(value) 

                # Remember we set a cell
                we_set_a_cell = True

        return we_set_a_cell

    def is_solved(self) :
        ''' returns true if board is solved '''
        return len(self.unsolved_cells) == 0


    def output(self) :
        ''' returns list of rows of the Board.
        Same format as __init__ argument '''
        arr = []
        # <todo> ############## write this
        return arr


class Cell :
    ''' Represents a single cell on the sudoku board. Has
    value           can be unsolved_cell_value or 1-9
    possible_values set of potential values, empty if value has been set
    board           The Board we belong to
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

        # Mark in unsolved with all possibles
        self.value = Cell.unsolved_cell_value
        self.possible_values = Cell.all_cell_values


    def set(self, value) :
        '''Sets value into cell and adjusts all the data structures:
             value, possible_values
             Board.unsolved_cells
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



# Test code
import unittest

class TestSudoku(unittest.TestCase):


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
            self.assertEqual(exc.message, 'Row 4; Wrong size: 8')


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


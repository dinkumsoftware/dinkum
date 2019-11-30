#!/usr/bin/env python3
# dinkum/sudoku/sudoku.py
''' sudoku_solver() solves a sudoku puzzle

Solution technique does NOT involve guessing.
It only fills in cells that have no alternative.
'''

# 2019-11-01 tc Initial
# 2019-11-07 tc Made Board(None) return empty board
# 2019-11-23 tc Bug fix in sanity_check()
# 2019-11-25 tc various bug fixes
# 2019-11-25 tc move Board/RCB/Cell into own files

from dinkum.sudoku       import *  # Package wide defines
from dinkum.sudoku.board import *

def sudoku_solver(puzzle):
    ''' return solution to puzzle as a Board
    raise Exception on no solutions
    puzzle should be [] of row-lists
    '''

    board = Board("created by sudoku_solver()", puzzle)

    # Return a board that solves board
    solution=board.solve()

    # Toss Exception if can't solve
    if solution :
        return solution.output() # Uniquely solved!
    else :
        raise ExcUnsolvable()
        





# Test code
import unittest

class Test_sudoku(unittest.TestCase):

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


#!/usr/bin/env python3
# dinkum/sudoku/solved_puzzles.py
''' Provides a test suite of sudoku puzzles.
The class SolvedPuzzle will contain:
    name of the input board
    input string for the input board
    constructed input Board
    answer Board
    string output of answer Board

    all_known_puzzles is a [] of all puzzles in this module.
    Some may not have a solution recorded and/or aren't currently
    solvable.

    all_known_solved_puzzles is a [] of all known puzzles and solutions
    which are known to be solvable and have a solution recorded.

    all_known_unsolved_puzzles is a [] of puzzles which can't be solved and/or
    do not solution recorded

    Performs a couple of sanity checks which trigger a
    failed assertion on any errors.
'''

# 2019-11-26 tc Initial
# 2019-11-30 tc bug fix for cyclic import of Board
#               added all_known_[un]solved_puzzles

from dinkum.sudoku.board import Board

class SolvedPuzzle :
    ''' Constructor receives spec for input_board,
    spec for solution_board, and the name to use
    for input board.  The name for the solution_board is
    <input_name>-solution.

    Constructs and remembers input_board and solution_board.
    '''

    def __init__(self, name, desc, input_spec, solution_spec) :
        ''' Constructor. Inputs
        name            Optional Name of input board
        desc            Optional Description of it

        input_spec      [[1,3,...][2,9,0,...]....]
        solution_spec       ditto

        Keeps a copy of it's arguments, plus
        input_board     Board(input_spec)
        solution_name   Name of solution board
        solution_description Same description as input_board
        solution_board  Board(solution_spec)
        '''

        self.name          = name
        self.desc          = desc
        self.solution_name = name + "-solution"

        self.input_spec = input_spec
        self.input_board = Board(input_spec, name, desc)

        self.solution_spec  = solution_spec
        self.solution_board = Board(solution_spec,
                                    self.solution_name, self.input_board.description )


# all_known_[un]solved_puzzles are lists of all puzzles that
# are solved or unsolved.  They will be combined later to
# form all_known_puzzles
all_known_solved_puzzles = []
all_known_unsolved_puzzles = []

# Each puzzle definition below must add the puzzle to
# one of these lists

# Define some puzzles        


# *** pre_solved
desc= "All cells filled in initially"
input_spec =   [[0, 4, 6, 1, 2, 7, 9, 5, 8], 
                [7, 0, 5, 6, 9, 4, 1, 3, 2], 
                [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                [5, 9, 8, 4, 1, 3, 7, 2, 6],
                [6, 2, 4, 7, 5, 9, 3, 8, 1],
                [1, 7, 3, 8, 6, 2, 5, 9, 4]]

solution_spec= [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
                [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                [5, 9, 8, 4, 1, 3, 7, 2, 6],
                [6, 2, 4, 7, 5, 9, 3, 8, 1],
                [1, 7, 3, 8, 6, 2, 5, 9, 4]]
pre_solved = SolvedPuzzle("pre_solved", desc, input_spec, solution_spec)
all_known_solved_puzzles.append(pre_solved)




# *** real_easy
desc="only one cell to solve"
real_easy  =      [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
                   [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                   [2, 1, 9, 3, 0, 5, 4, 6, 7], 
                   [4, 6, 2, 0, 3, 1, 8, 7, 9], 
                   [9, 3, 0, 2, 7, 8, 6, 4, 5], 
                   [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                   [5, 9, 8, 4, 0, 3, 7, 2, 6],
                   [6, 2, 4, 7, 5, 9, 3, 8, 1],
                   [1, 7, 3, 8, 6, 2, 5, 9, 4]]

real_easy_ans = [[3, 4, 6, 1, 2, 7, 9, 5, 8],
                 [7, 8, 5, 6, 9, 4, 1, 3, 2],
                 [2, 1, 9, 3, 8, 5, 4, 6, 7],
                 [4, 6, 2, 5, 3, 1, 8, 7, 9],
                 [9, 3, 1, 2, 7, 8, 6, 4, 5],
                 [8, 5, 7, 9, 4, 6, 2, 1, 3],
                 [5, 9, 8, 4, 1, 3, 7, 2, 6],
                 [6, 2, 4, 7, 5, 9, 3, 8, 1],
                 [1, 7, 3, 8, 6, 2, 5, 9, 4]]
real_easy = SolvedPuzzle("real_easy", desc, real_easy, real_easy_ans)
all_known_solved_puzzles.append(real_easy)



# *** puzzle
desc="Unsure lineage, maybe kato"
puzzle_in = [[0, 0, 6, 1, 0, 0, 0, 0, 8], 
             [0, 8, 0, 0, 9, 0, 0, 3, 0], 
             [2, 0, 0, 0, 0, 5, 4, 0, 0], 
             [4, 0, 0, 0, 0, 1, 8, 0, 0], 
             [0, 3, 0, 0, 7, 0, 0, 4, 0], 
             [0, 0, 7, 9, 0, 0, 0, 0, 3], 
             [0, 0, 8, 4, 0, 0, 0, 0, 6], 
             [0, 2, 0, 0, 5, 0, 0, 8, 0], 
             [1, 0, 0, 0, 0, 2, 5, 0, 0]]

puzzle_ans = [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
              [7, 8, 5, 6, 9, 4, 1, 3, 2], 
              [2, 1, 9, 3, 8, 5, 4, 6, 7], 
              [4, 6, 2, 5, 3, 1, 8, 7, 9], 
              [9, 3, 1, 2, 7, 8, 6, 4, 5], 
              [8, 5, 7, 9, 4, 6, 2, 1, 3], 
              [5, 9, 8, 4, 1, 3, 7, 2, 6],
              [6, 2, 4, 7, 5, 9, 3, 8, 1],
              [1, 7, 3, 8, 6, 2, 5, 9, 4]]
puzzle = SolvedPuzzle("puzzle", desc, puzzle_in, puzzle_ans)
all_known_unsolved_puzzles.append(puzzle) # Can't solve it yet

# All the puzzles we know about
all_known_puzzles = all_known_solved_puzzles + all_known_unsolved_puzzles

# Sanity checks here
for sp in all_known_solved_puzzles :
    # All solved puzzles must have solution
    assert sp.solution_board, "Board %s in all_known_solved_puzzles, but has no solution"

    # Make sure input cells which are set have
    # the same value in the solution
    assert sp.input_board.is_subset_of( sp.solution_board)

    # Verify we can solve all the solvable puzzles
    for sp in all_known_solved_puzzles :
        # Verify an answer is supplied
        assert sp.solution_spec,  "%s:No solution_spec" % sp.solution_spec
        assert sp.solution_board, "%s:No solution_board" % sp.solution_board

        our_solution = sp.input_board.solve() 
        assert our_solution, "%s: Cannot solve a solvable puzzle" % sp.name
        assert our_solution == sp.solution_board, "%s: solutions differ" % sp.name

    # Verify we can't solvable the unsolvable
    for sp in all_known_unsolved_puzzles :
        our_solution = sp.input_board.solve()
        assert not our_solution, "%s: we can solve and unsolvable puzzle"

# Test code
import unittest

class Test_solved_puzzles(unittest.TestCase) :
    # Much of the test code is run in sanity check
    # above at import time with an assertion failure

    def test_simple_construction(self) :
        name = "whatever"
        desc = "who knows?"
        sp = SolvedPuzzle(name, desc, input_spec, solution_spec) 
    
        self.assertEqual (name,             sp.name         )
        self.assertEqual (name+"-solution", sp.solution_name)

        self.assertEqual (desc, sp.input_board.description)
        self.assertEqual (desc, sp.solution_board.description)

        self.assertEqual (input_spec,     sp.input_spec     )
        self.assertEqual (solution_spec,  sp.solution_spec  )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



        
#!/usr/bin/env python3
# dinkum/sudoku/test_puzzles.py
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

    all_known_names is a {} of all_known_puzzles.  Key:name Value:SolvedPuzzle

    Performs a couple of sanity checks which trigger a
    failed assertion on any errors.

read/write_prior_stats() return (or write) a {} to/from a file
which is keyed by puzzle_name and the value is last written sudoku.Stats
of that puzzle, regardless of whether the puzzle is solved or not

'''

# 2019-11-26 tc Initial
# 2019-11-30 tc bug fix for cyclic import of Board
#               added all_known_[un]solved_puzzles
# 2019-12-02 tc Added empty_board
# 2019-12-03 tc Added a couple of globe puzzles
# 2019-12-04 tc Added read/write_prior_solve_times_secs()
# 2019-12-09 tc read/write_prior_solve_times_secs() ==>
#               read/write_prior_solve_stats()
from copy                import deepcopy
import pickle
import os

from dinkum.sudoku       import *
from dinkum.sudoku.board import Board
from dinkum.sudoku.stats import *


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
# *** empty
empty_row  = [0]*RCB_SIZE
input_spec = [ deepcopy(empty_row) for i in range(RCB_SIZE)]
desc="No initial values, unsolvable"

empty = SolvedPuzzle("empty", desc, input_spec, None)
all_known_unsolved_puzzles.append(empty)



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

# ***
name="globe_mon_2019_12_02"
desc="Boston Globe mon, 2019-12-02, www.sudoku.com"
puzzle_in  = '''
001 605 400
028 000 760
000 080 000

600 804 005
072 000 940
100 209 008

000 050 000
057 000 310
009 106 200
'''

puzzle_ans = '''
731 695 482
528 413 769
964 782 531

693 874 125
872 561 943
145 239 678

216 357 894
457 928 316
389 146 257
'''
puzzle = SolvedPuzzle(name, desc, puzzle_in, puzzle_ans)
all_known_solved_puzzles.append(puzzle)


# ***
name="globe_sat_2019_11_02"
desc="Boston Globe sat, 2019-11-02, www.sudoku.com"
puzzle_in  = '''
001 603 000
900 047 010
000 000 700

390 025 600
000 000 000
004 360 059

003 000 000
040 170 006
000 206 500
'''

puzzle_ans = '''
781 653 942
962 847 315
435 912 768

398 425 671
156 789 423
274 361 859

623 594 187
549 178 236
817 236 594
'''
puzzle = SolvedPuzzle(name, desc, puzzle_in, puzzle_ans)
all_known_unsolved_puzzles.append(puzzle)


# ***
name="kato_puzzle"
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
puzzle = SolvedPuzzle(name, desc, puzzle_in, puzzle_ans)
all_known_unsolved_puzzles.append(puzzle) # Can't solve it yet

# All the puzzles we know about
all_known_puzzles = all_known_solved_puzzles + all_known_unsolved_puzzles

# Make a dictionary of names
all_known_puzzle_names = {}
for sp in all_known_puzzles :
    all_known_puzzle_names[sp.name] = sp

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
        assert not our_solution, "%s: we can solv and unsolvable puzzle"



def prior_stats_filename() :
    ''' returns the filename where statistics are
    stored on disk.
    '''
    # We write the file in the same directory we live in
    # at the time of this writing it was
    # ..../dinkum/sudoku/test_data
    dir = os.path.dirname(__file__) # .../dinkum/sudoku/test_data
    file = os.path.join(dir, "prior_solve_stats.pickled")

    return file

def read_prior_stats() :
    ''' Read and return {} of board.solved_stats from file
    and return it.  Keyed by puzzle_name, value is
    sudoku.Stats.

    These are the stats last written by write_prior_solve_stats()
    '''
    stats = {} # in case of file not found
    try:
        with open(prior_stats_filename(), "rb") as pickle_file :
            stats = pickle.load(pickle_file)
    except FileNotFoundError:
        pass # We'll just return the initial empty dictionary

    return stats
    

def write_prior_stats(stats) :
    ''' Writes stats to a disk file.
    It can be read via read_prior_stats()
    Current implementation pickles it.
    '''
    
    pickle.dump(stats, open(prior_stats_filename(), "wb"))


# Test code
import unittest

class Test_test_puzzles(unittest.TestCase) :
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

    def test_all_known_puzzle_names(self) :
        # Make sure every puzzle is in the dictionary
        for sp in all_known_puzzles :
            self.assertIn (sp.name, all_known_puzzle_names)
            self.assertIs (sp, all_known_puzzle_names[sp.name])


# Some standalone functions

# Where we pickle/unpickle the {}




if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



        

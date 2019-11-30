#!/usr/bin/env python3
# dinkum/sudoku/solved_puzzles.py
''' Provides a test suite of sudoku puzzles.
The class SolvedPuzzle will contain:
    name of the input board
    input string for the input board
    constructed input Board
    answer Board
    string output of answer Board

    all_solved_puzzles is a [] of all known puzzles and solutions

    Performs a couple of sanity checks which trigger a
    failed assertion on any errors.
'''

# 2019-11-26 tc Initial

from dinkum.sudoku.board import Board

class SolvedPuzzle :
    ''' Constructor receives spec for input_board,
    spec for solution_board, and the name to use
    for input board.  The name for the solution_board is
    <input_name>-solution.

    Constructs and remembers input_board and solution_board.
    '''

    def __init__(self, name, input_spec, solution_spec) :
        ''' Constructor. Inputs
        name            Name of input board

        input_spec      [[1,3,...][2,9,0,...]....]
        solution_spec       ditto

        Keeps a copy of it's arguments, plus
        solution_name   Name of solution board
        input_board     Board(input_spec)
        solution_board  Board(solution_spec)
        '''
        self.name          = name
        self.solution_name = name + "-solution"

        self.input_spec = input_spec
        self.input_board = Board(name, input_spec)

        self.solution_spec  = solution_spec
        self.solution_board = Board(self.solution_name, solution_spec)


# all_solved_puzzles is a [] of all known SolvedPuzzles
all_solved_puzzles = []

# Define some puzzles        


# mindless
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
mindless = SolvedPuzzle("mindless", input_spec, solution_spec)
all_solved_puzzles.append(mindless)




# *** real_easy
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
real_easy = SolvedPuzzle("real_easy", real_easy, real_easy_ans)
all_solved_puzzles.append(real_easy)



# *** puzzle
name="puzzle"
puzzle = [[0, 0, 6, 1, 0, 0, 0, 0, 8], 
          [0, 8, 0, 0, 9, 0, 0, 3, 0], 
          [2, 0, 0, 0, 0, 5, 4, 0, 0], 
          [4, 0, 0, 0, 0, 1, 8, 0, 0], 
          [0, 3, 0, 0, 7, 0, 0, 4, 0], 
          [0, 0, 7, 9, 0, 0, 0, 0, 3], 
          [0, 0, 8, 4, 0, 0, 0, 0, 6], 
          [0, 2, 0, 0, 5, 0, 0, 8, 0], 
          [1, 0, 0, 0, 0, 2, 5, 0, 0]]

puzzle_ans      = [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
                   [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                   [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                   [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                   [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                   [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                   [5, 9, 8, 4, 1, 3, 7, 2, 6],
                   [6, 2, 4, 7, 5, 9, 3, 8, 1],
                   [1, 7, 3, 8, 6, 2, 5, 9, 4]]
puzzle = SolvedPuzzle("puzzle", puzzle, puzzle_ans)
all_solved_puzzles.append(puzzle)


# An after the fact table of contents
# 0 mindless
# 1 real_easy
# 2 puzzle




# ##################################
# Some editting....
# During development, couldn't solve these boards yet
all_solved_puzzles = all_solved_puzzles[:-1] # remove puzzle

# Sanity check here
for sp in all_solved_puzzles :
    # Make sure input cells which are set have
    # the same value in the solution
    assert sp.input_board.is_subset_of( sp.solution_board)


# Test code
import unittest

class Test_solved_puzzles(unittest.TestCase) :

    def test_simple_construction(self) :
        name = "whatever"
        sp = SolvedPuzzle(name, input_spec, solution_spec) 
    
        self.assertEqual (name,             sp.name         )
        self.assertEqual (name+"-solution", sp.solution_name)

        self.assertEqual (input_spec,     sp.input_spec     )
        self.assertEqual (solution_spec,  sp.solution_spec  )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



        

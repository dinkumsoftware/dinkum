#!/usr/bin/env python3
#filename: dinkum_sudoku_solve_known.py
#path: sudoku/test-bin/
#repo: http://github.com/dinkumsoftware/dinkum.git
'''
Times copy constructor for Board.
Prints results

EXIT STATUS
    0  Normal
'''

import sys
import time
from   dinkum.sudoku.board import *
import dinkum.sudoku.test_data.test_puzzles

# 2020-02-01 tc Initial

def main() :
    # How many to time
    num_constructions_to_time = 1000

    # Pick a board to copy from test_puzzles
    # We pick a hard one that can't be solved by deduction
    # as this is where we start recursing with lots of
    # Board copy construcitons
    sp = dinkum.sudoku.test_data.test_puzzles.all_known_puzzle_names["kato_puzzle"]
    bd_to_copy = sp.input_board

    # Get the execution time of Board(board) in seconds
    start_time = time.process_time()

    num_constructions = 0
    while num_constructions < num_constructions_to_time :
        num_constructions += 1
        Board(bd_to_copy)
    end_time = time.process_time()

    # Compute the number of microsecondssecs per construction
    execution_time_in_usecs = ((end_time-start_time) / num_constructions_to_time) * 1.0e6

    # Report it in microseconds
    #       123456789.123456789.1234567
    print ("Board(bd_to_copy):         %0.0f microseconds" % execution_time_in_usecs)

    # Get the execution time of copy.deepcopy(board)
    num_constructions = 0
    while num_constructions < num_constructions_to_time :
        num_constructions += 1
        copy.deepcopy(bd_to_copy)
    end_time = time.process_time()

    # Compute the number of microsecondssecs per construction
    execution_time_in_usecs = ((end_time-start_time) / num_constructions_to_time) * 1.0e6

    # Report it in microseconds
    #       123456789.123456789.1234567
    print ("copy.deepcopy(bd_to_copy): %0.0f microseconds" % execution_time_in_usecs)

    return 0



if __name__ == '__main__':
    try:
        # Invoke the actual program
        # We pass back to OS whatever it returns
        main_return = main()

        # Pass back to the OS the proper exit code. 0 is good
        sys.exit( main_return)

    except KeyboardInterrupt as e: # Ctrl-C
        raise e
    except SystemExit as e: # sys.exit()
        raise e
    except Exception as e:         
        print ('ERROR: uncaught EXCEPTION. Msg after traceback.')
        traceback.print_exc()    # stack dump (which prints err msg)
        os._exit(ret_val_exception_raised)

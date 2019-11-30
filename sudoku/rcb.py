#!/usr/bin/env python3
# dinkum/sudoku/rcb.py
''' Part of a sudoku Board.  An RCB represents a row/col/ or blk.
Each RGB is a [] of Cells in that row/col/block.
'''

# 2019-11-25 tc Moved fom sudoku.py

from dinkum.sudoku import * # All package wide def's

class RCB :
    ''' Represents a row, column, or block.
    data:
      board    The Board we belong to
      rcb_num  The raster order row/column/block number (0 to Board.rcb_size-1)
      cells    a [] of Cells in the row/column/block

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
        self.cells = [None] * RCB_SIZE

    def __getitem__(self, idx) :
        ''' Returns our idx'th Cell
        makes rcb[n] return the nth cell
        '''
        return self.cells[idx]

    def __setitem__(self, idx, cell) :
        ''' Sets our idx'th entry to cell
        rcb[n] =3  set's the nth cell value to 3
        '''
        self.cells[idx] = cell


# Test code
import unittest

class Test_rcb(unittest.TestCase):

    def test_construction(self) :
        rcb = RCB(None, 2) 

        # All should be empty
        # and tests __getitem__()
        for idx in range(RCB_SIZE) :
            self.assertEqual( rcb.cells[idx], None )

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

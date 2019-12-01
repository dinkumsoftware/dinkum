#!/usr/bin/env python3
# dinkum/sudoku/rcb.py
''' Part of a sudoku Board.  An RCB represents a row/col/ or blk.
Each RCB is a [] of cells.
'''

# 2019-11-25 tc Moved fom sudoku.py

from dinkum.sudoku import * # All package wide def's

class RCB(list) :
    ''' Represents a row, column, or block.
    data:
      board    The Board we belong to
      rcb_type RCB_TYPE_ROW/COL/BLK
      rcb_num  The raster order row/column/block number (0 to Board.rcb_size-1)

      self    a [] of Cells in the row/column/block

    some funcs:
      [x] gets/sets cells[x]
      iterators iterator over cells[]
    '''

    def __init__(self, rcb_type, board, rcb_num) :
        '''Creates an empty RCB
        rcb_type RCB_TYPE_ROW/COL/BLK
        board    The board we belong to
        rcb_num  Our index into board.row/col/blk

        cells[] is our [] of Cells that belong to us.
        It will be created with proper length and all values None.
        Counting on someone else to fill in cells[]
        '''
        self.rcb_type = rcb_type
        assert self.rcb_type in ALL_RCB_TYPES, "Illegal rcb_type: %d" % self.rcb_type

        self.board = board

        self.rcb_num = rcb_num
        assert self.rcb_num in range(RCB_SIZE)

        # make the cells themselves
        super().__init__( [None] * RCB_SIZE )


# Test code
import unittest

class Test_rcb(unittest.TestCase):

    def test_construction(self) :
        rcb = RCB(RCB_TYPE_BLK, None, 2) 

        # All should be empty
        # and tests __getitem__()
        for idx in range(RCB_SIZE) :
            self.assertEqual( rcb[idx], None )

    def test_bad_rcb_type(self) :
        bad_rcb_value = 82
        
        try:
            self.assertRaises( RCB(bad_rcb_value, None, 2))
        except AssertionError as exc :
            self.assertEqual(str(exc), "Illegal rcb_type: 82")

        def test_iteration(self) :
            rcb = RCB(RCB_TYPE_COL, None, 4)

            self.assertEqual( len(rcb), RCB_SIZE )

            # All cells should be uninitialized
            cell_cnt = 0
            for c in rcb :
                self.assertNone, c.value
                cell_cnt += 1

            self.assertEqual( cell_cnt, len(rcb) )

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

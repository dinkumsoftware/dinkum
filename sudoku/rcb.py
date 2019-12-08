#!/usr/bin/env python3
# dinkum/sudoku/rcb.py
''' Part of a sudoku Board.  An RCB represents a row/col/ or blk.
Each RCB is a [] of cells.
'''

# 2019-11-25 tc Moved fom sudoku.py
# 2019-12-07 tc Added unsolved_cells

from dinkum.sudoku      import * # All package wide def's
from dinkum.sudoku.cell import Cell

class RCB(list) :
    ''' Represents a row, column, or block.
    data:
      board    The Board we belong to
      rcb_type RCB_TYPE_ROW/COL/BLK
      rcb_num  The raster order row/column/block number (0 to Board.rcb_size-1)

      self            a [] of Cells in the row/column/block
      unsolved_cells  a set of cells in self that are not solved

    some funcs:
      initial_cell_placement  Should be called to initially populate the rcb
      cell_was_set            Should be called when a cell in the rcb was set
                              either in initial board or during solution

      [x] gets/sets cells[x]
      iterators iterator over cells[]
    '''

    def __init__(self, rcb_type, board, rcb_num) :
        '''Creates an empty RCB
        rcb_type RCB_TYPE_ROW/COL/BLK
        board    The board we belong to
        rcb_num  Our index into board.row/col/blk

        self is our [] of Cells that belong to us.
        It will be created with proper length and all values None.
        Counting on someone else to fill in cells[]

        unsolved_cells           a set of cells in self that are not solved

        '''
        self.rcb_type = rcb_type
        assert self.rcb_type in ALL_RCB_TYPES, "Illegal rcb_type: %d" % self.rcb_type

        self.board = board

        self.rcb_num = rcb_num
        assert self.rcb_num in range(RCB_SIZE)

        # make a place for the cells themselves
        super().__init__( [None] * RCB_SIZE )

        # We currently don't have any cells, merely a place
        # to put them.  When populated via initial_cell_placement(),
        # unsolved_cells() will be populated as well.
        self.unsolved_cells = set()

    def initial_cell_placement(self, cell, indx) :
        ''' Called to place cell in position indx in the RCB.
        The cell isn't touched, it is merely recorded as belonging
        to this RCB

        All other data structs are maintained.
        '''
        assert cell.value == Cell.unsolved_cell_value
        assert self[indx] is None  # We don't allow overwrites
        
        # Put the cell in
        self[indx] = cell

        # and add it to unsolved
        self.unsolved_cells.add(cell)



    def cell_was_set(self, set_cell) :
        ''' Should be called when a cell in this rcb has been set.
        set_cell is the cell that was set.

        It adjusts all the data structs:
         set_cell is removed from unsolved_cells
         set_cell.value is removed from unset cells in the rcb
        '''

        # Sanity check
        assert set_cell in self

        # Remove set_cell from unsolved_cells
        # Note: This is like
        #    assert set_cell in unsolved_cells
        # as remove() complains if set_cell not a member
        self.unsolved_cells.remove(set_cell)

        # Remove cell.value from all unset cells
        for cell in self.unsolved_cells :
            # does not complain if value not a member
            cell.possible_values.discard(set_cell.value)

        

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

#!/usr/bin/env python3
# dinkum/sudoku/rcb.py
''' Part of a sudoku Board.  An RCB represents a row/col/ or blk.
Each RCB is a [] of cells.
'''

# 2019-11-25 tc Moved fom sudoku.py
# 2019-12-07 tc Added unsolved_cells and unsolved_value_possibles

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
      unsolved_value_possibles {} of sets of cells
                               key: cell value
                               value: set of cells in rgb that have key as a possibility

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

        We created all of these with no content.
        They are populated by calls to initial_cell_placement()

        self                     [] of our Cells
        unsolved_cells           set of cells in self that are not solved
        unsolved_value_possibles {} of sets of our cells 
                                 key: cell value
                                 value: set of our cells wit key(cell value)
                                        as a possibility
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
        # the following will be populated with Cell values
        self.unsolved_cells = set()

        self.unsolved_value_possibles = {}
        for value in Cell.all_cell_values :
            self.unsolved_value_possibles[value] = set()

    def initial_cell_placement(self, cell) :
        ''' Called to place cell in the RCB.
        The cell's indx into cell is retrieved from the cell
        The cell isn't touched, it is merely recorded as belonging
        to this RCB

        All other data structs are maintained.
        '''
        assert cell.value == Cell.unsolved_cell_value

        # For error messages
        id_str = "%s[%d] : cell#%d" % (RCB_NAME[self.rcb_type],
                                       self.rcb_num, cell.cell_num)
    
        # Figure out the index for cell into self[]
        (cell_rcb_num, indx) = cell.rcb_num_and_idx( self.rcb_type )

        assert self.rcb_num == cell_rcb_num, \
               "%s: rcb_num disagreement: rcb:%d, cell:%d" % (id_str,
                                                              self.rcb_num,
                                                              cell_rcb_num)
        # We don't allow overwrites
        assert self[indx] is None, "%s: Trying to overwrite cell#%d" % (id_str,
                                                                        self[indx].cell_num)
        
        # Put the cell in
        self[indx] = cell

        # and add it to unsolved
        self.unsolved_cells.add(cell)

        # and remember it as a possible solution
        # for all values
        for value in cell.possible_values :
            self.unsolved_value_possibles[value].add(cell)

    def sanity_check(self) :
        ''' an RCB sanity check.
        Should be called after all the initial_cell_placement()
        but before any cell is set().

        Checks multiple conditions and asserts if they aren't met.
        '''

        # Used for error messages
        id_str = "%s[%d]" % (RCB_NAME[self.rcb_type], self.rcb_num)
        
        assert len(self) == RCB_SIZE,                                           \
            "%s: Wrong number of cells." % id_str
        assert len(self.unsolved_cells) == RCB_SIZE,                            \
            "%s: Wrong number of unsolved cells" % id_str
        assert len(self.unsolved_value_possibles) == len(Cell.all_cell_values), \
            "%s: Wrong number of unsolved_value_possibles" % id_str

        # Look at each cell
        for idx in range(RCB_SIZE) :
            cell = self[idx] 

            # Make sure it exists and is unsolved
            assert cell,                                  \
                "%s[%d]: Not populated." %(id_str, idx)
            assert cell.value == Cell.unsolved_cell_value,\
                "%s[%d]: should not be solved." %(id_str, idx)
        
            # Make sure it's in unsolved_value_possibles at all value positions
            for value in Cell.all_cell_values :
                possible_cells = self.unsolved_value_possibles[value]
                assert cell in possible_cells, "%s[%d]: not in unsolved_value_possibles[%d]" % (id_str, idx, value)

    def cell_was_set_initial_call(self, set_cell) :
        ''' Should be called when a cell in this rcb has been set.
        set_cell is the cell that was set.

        It adjusts all the data structs:
         set_cell is removed from unsolved_cells
         set_cell.value is removed from unset cells in the rcb

        We expect that after we have been called for all of a
        a set cell's RCB's... then cell_was_set_all_rcbs_notified()
        will be called
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


    def cell_was_set_all_rcbs_notified(self, set_cell) :
        ''' Should be called when a cell in this rcb has
        been set AND cell_was_set_initial_call() has been
        made to all of the cell's RCB's (including us)

        We rebuild unsolved_value_possibles from all our
        unsolved_cells.  This can't be done in
        cell_was_set_initial_call() because other
        rcb's may not have adjusted their possible_values yet.
        '''

        # Wipe out the old
        for value in self.unsolved_value_possibles :
            self.unsolved_value_possibles[value] = set()

        # Put any unsolved cell whose possible value
        # could be value in unsolved_value_possible[value]
        for cell in self.unsolved_cells :
            for value in cell.possible_values :
                self.unsolved_value_possibles[value].add(cell)


    def is_solved(self) :
        ''' Returns True if all cells have solved, i.e. have values '''
        return not self.unsolved_cells

    def __str__(self) :
        ''' String representation.  Example:
            row[3]:
               Values: 6 _ _ 8 _ 4 _ _ 5
               Cell index possibles for unsolved values:
                  1:  1  2  4  6  7 
                  2:  1  2  4  6  7 
                  3:  1  2  4  6  7 
                  4:  1  2  4  6  7 
                  5:  1  2  4  6  7 
                  6:  1  2  4  6  7 
                  7:  1  2  4  6  7 
                  8:  1  2  4  6  7 
                  9:  1  2  4  6  7 
        '''

        ret_str = ''

        # Our type and such
        # e.g.             row[3]:
        ret_str += "%s[%d]:\n" % ( RCB_NAME[self.rcb_type], self.rcb_num)

        # How much to indent the following lines
        indent_str = " " * 3
        secondary_indent_str = indent_str * 2

        # Cell values on one line
        # e.g.               Values: 6 _ _ 8 _ 4 _ _ 5

        ret_str += indent_str + "Values:" # space over and label
        col_width = 2 # how many spaces per cell
        for cell in self :
            # position been populated ?
            if cell :
                # yes
                token = cell.str_value(col_width, '_')
            else :
                # Nope
                token = "%*s" % (col_width, "X")
            ret_str += token # this cell's representation
        ret_str += '\n' # terminate the line


        # Give them possible cells that satisfy unsolved values
        # Sort the indexes before we print them
        # e.g.               Cell index possibles for unsolved values:
        #                       1:  1  2  4  6  7 
        ret_str += "%sCell index possibles for unsolved values:\n" % (indent_str)

        for val in self.unsolved_value_possibles :

            ret_str += "%s%d: " % (secondary_indent_str, val)

            # Collect all the indexes of possible cells that
            # could supply value (whew!) in indexs
            indexs=[]
            for cell in self.unsolved_value_possibles[val] :
                (rcb_num, rcb_idx) = cell.rcb_num_and_idx(self.rcb_type)
                indexs.append(rcb_idx)

            # Now sort and "print" it
            indexs.sort()
            for rcb_idx in indexs :
                ret_str += "%2s " % (rcb_idx)

            ret_str += '\n' # terminate the line

        # Give 'um the answer
        return ret_str

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

    def populated_rcb_for_test(self, rcb_type) :
        ''' For test purposes, constructs and returns
        an RCB populated with cells.  This is simulating what the Board
        constructor does, but we can't do that here because
        we end up with circular imports.
        '''

        # Get the cell numbers we are going to assign
        # We'll do row 4 --or-- col 6 --or blk 2
        if rcb_type == RCB_TYPE_ROW :
            rcb_num = 4
            our_cell_nums = range (36, 45)
        if rcb_type == RCB_TYPE_COL :
            rcb_num = 6
            our_cell_nums = range ( 6, 87, 9)
        if rcb_type == RCB_TYPE_BLK :
            rcb_num = 2
            our_cell_nums = (list(range( 6,  9)) +
                             list(range(15, 18)) +
                             list(range(24, 27)) )
        
        # Make an unpopulated rcb
        rcb = RCB(rcb_type, None, rcb_num)

        # Populate it
        for cell_num in our_cell_nums :
            rcb.initial_cell_placement ( Cell(None, cell_num))

        return rcb


    def test_sanity_check(self) :
        # We want trigger all the bad conditions it checks for

        # wrong # of cells
        rcb = self.populated_rcb_for_test(RCB_TYPE_ROW)
        rcb.pop()
        self.assertRaises(AssertionError, rcb.sanity_check )

        # wrong number of unsolved cells
        rcb = self.populated_rcb_for_test(RCB_TYPE_COL)
        rcb.unsolved_cells.pop()
        self.assertRaises(AssertionError, rcb.sanity_check )

        # wrong length of unsolved_value_possibles
        rcb = self.populated_rcb_for_test(RCB_TYPE_COL)
        cell_to_discard = rcb[2]
        rcb.unsolved_value_possibles[3].discard( cell_to_discard )
        self.assertRaises(AssertionError, rcb.sanity_check )

        # unpopulated cell
        rcb = self.populated_rcb_for_test(RCB_TYPE_COL)
        rcb[8] = None
        self.assertRaises(AssertionError, rcb.sanity_check )

        # a populated cell is solved
        rcb = self.populated_rcb_for_test(RCB_TYPE_BLK)
        rcb[4].value = 3 # solve it
        self.assertRaises(AssertionError, rcb.sanity_check )

        # cell not in unsolved_value_possibles[cell.value]
        rcb = self.populated_rcb_for_test(RCB_TYPE_BLK)
        rcb.unsolved_value_possibles[9].discard( rcb[4] )
        self.assertRaises(AssertionError, rcb.sanity_check )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

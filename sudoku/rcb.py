#!/usr/bin/env python3
# dinkum/sudoku/rcb.py
''' Part of a sudoku Board.  An RCB represents a row/col/ or blk.
Each RCB is a [] of cells.
'''

# 2019-11-25 tc Moved fom sudoku.py
# 2019-12-07 tc Added unsolved_cells and unsolved_value_possibles
# 2019-12-12 tc Added a_cell_was_set() and remove_from_possibles()


from dinkum.sudoku      import * # All package wide def's
from dinkum.sudoku.cell import Cell, CellToSet

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
      a_cell_was_set          Should be called when a cell in the rcb was set
                              either in initial board or during solution
      remove_from_possibles   Removes a value as a possible solution

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
                                 value: set of our cells with key(cell value)
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
            if value in self.unsolved_value_possibles :
                self.unsolved_value_possibles[value].add(cell)
            else:
                # First time we have seen this value
                # Start it off with this cell
                self.unsolved_value_possibles[value] = set([cell])

    def a_cell_was_set(self, set_cell) :
        ''' Should be called when set_cell (one of our cells,
        has been set.

        Returns a set() of CellToSet which should be set
        as a result of the setting of set_cell.

        Specifically:
            removes set_cell from unsolved_cells
            removes set_cell from other unsolved_value_possibles
                if removal would result in only one possible
                cell for that value... cell is added to returned set
            remove_from_possibles(set_cell.value) for other cells in our RCB
        '''
        # Enforce our assumptions
        assert set_cell.is_solved()
        assert set_cell in self.unsolved_cells
        assert set_cell in self.unsolved_value_possibles[set_cell.value]

        set_value = set_cell.value  # What the set_cell was set to
        assert set_cell in self.unsolved_value_possibles[set_value]

        returned_set = set() # what we return

        # remove set_cell from unsolved_cells
        self.unsolved_cells.remove(set_cell)

        # No other cell can provide the value that was just set
        # Note: assert beginning function ensures this won't
        #       raise KeyError if set_cell.value not present
        del self.unsolved_value_possibles[set_cell.value]

        # removes set_cell from other unsolved_value_possibles
        # Take note if removal only leaves one cell left for
        # that value... means that the supplying cell is
        # uniquely determined
        for (value, possible_cells) in self.unsolved_value_possibles.items() :
            if set_cell in possible_cells :

                # remove from unsolved_value_possibles
                possible_cells.remove(set_cell)

                # Only one remaining cell there?
                if len(possible_cells) == 1 :
                    # Yes, The single remaining cell can be set
                    # This syntax gets, but doesn't remove the
                    # single entry in the set
                    [cell_to_set]   = list(possible_cells)

                    # Add to the returned set
                    returned_set.add ( CellToSet(cell_to_set, value) )

        # remove_from_possibles(set_cell.value) for other cells in our RCB
        # accumulate any additional cells to set
        for cell in self.unsolved_cells :
            returned_set |= cell.remove_from_possibles(set_cell.value)


        # All done
        return returned_set


    def remove_from_possibles(self, value) :
        ''' Removes value as a possible solution for us.

        returns a (possibly empty) set of CellToSet's that
        consists of any other Cell that becomes solvable
        by removing value as a possibility.

        if value isn't one of our possible_values, we
        silently return an empty set.

        The details:

        iterates thru unsolved_cells
             Cell.remove_from_possibles(value)
             accumulates set(CellsToSet)

        Rebuilds unsolved_value_possibles

        If there remains only a single Cell that can provide
        a value, that Cell and the value to set it to is
        added to the returned set of CellToSet's

        return set of CellsToSet's
        '''
        assert value in Cell.all_cell_values

        # What we return
        cells_to_set = set()

        # Anything to remove?
        if value not in self.unsolved_value_possibles :
            return cells_to_set # nope, set is empty

        # iterates thru unsolved_cells
        #    Cell.remove_from_possibles(value)
        #    accumulates set(CellsToSet)
        for cell in self.unsolved_cells :
            cells_to_set |= cell.remove_from_possibles(value)

        # rebuild unsolved_value_possibles from scratch
        # This scan all unsolved_cells and return
        # a dict keyed by value having a set of Cells which
        # can supply that value.
        self.unsolved_value_possibles = self.build_unsolved_value_possibles()
        
        # Any unsolved value have only one Cell that solve it?
        for (value, cells) in self.unsolved_value_possibles.items() :
            # Only one cell can supply this?
            if len(cells) == 1 :
                # Yes, cell can be solved with value.  Tell caller
                cell = cells.pop() # only one cell in set
                cells_to_set += CellToSet(cell, value)

        # Tell them solvable cells based on removing value
        return cells_to_set

    def unsolved_values(self) :
        ''' returns a set of values to be solved
        '''
        return Cell.all_cell_values - self.solved_values()


    def solved_values(self) :
        ''' returns set of values already solved
        '''
        return set ([ cell.value for cell in self.solved_cells() ])

    def solved_cells(self) :
        ''' set of cells that are solved
        '''
        return set([ cell for cell in self if cell.is_solved() ])


    def sanity_check(self) :
        ''' an RCB sanity check.

        Checks multiple conditions and asserts if they aren't met.
        '''

        # Used for error messages
        id_str = "%s[%d]" % (RCB_NAME[self.rcb_type], self.rcb_num)
        
        assert len(self) == RCB_SIZE,                                           \
            "%s: Wrong number of cells." % id_str

        # Look at each cell
        for idx in range(RCB_SIZE) :
            cell = self[idx] 

            # Make sure it exists
            assert isinstance( cell, Cell), "%s[%d]: Not populated." %(id_str, idx)
        

        # Verify the number of unsolved cells
        our_unsolved_cells = set()
        for cell in self :
            if not cell.is_solved() :
                our_unsolved_cells.add(cell)
        assert our_unsolved_cells == self.unsolved_cells

        # Verify unsolved_value_possibles
        our_unsolved_value_possibles = self.build_unsolved_value_possibles()
        assert our_unsolved_value_possibles == self.unsolved_value_possibles
        
        # solved_cells + unsolved_cells = all cells in rcb with no overlap
        self.solved_cells() | self.unsolved_cells == set(self)
        self.solved_cells() & self.unsolved_cells == set()

        # solved_values + unsolved_values = all possible values with no overlap
        self.solved_values() | self.unsolved_values() == Cell.all_cell_values
        self.solved_values() & self.unsolved_values() == set()


    def build_unsolved_value_possibles(self) :
        ''' Builds and returns a {} keyed by cell_value and whose value is
        a set() of cells in the rcb that can provide that cell_value.
        '''
        
        # what we return
        ret_unsolved_value_possibles = {}

        # Put any unsolved cell whose possible value
        # could be value in unsolved_value_possible[value]
        for cell in self.unsolved_cells :
            for value in cell.possible_values :
                if value in ret_unsolved_value_possibles :
                    ret_unsolved_value_possibles[value].add(cell)
                else :
                    # First time we have seen this value
                    # Create the set itself with cell as only member
                    ret_unsolved_value_possibles[value] = set ([cell])

        return ret_unsolved_value_possibles

    def unsolved_cells_with_common_unique_values(self, match_size) :
        ''''
        Searches every rcb for pairs(match_size=2) and triples
        (match_size=3) of unsolved cells that all have the same
        possible value unique to those pairs/triples in this
        rcb i.e. no other cell in the rcb has that value as a possible.

        It works for match sizes other than 2 or 3, but probably
        not a lot of usefulness in the real world.

        returns [] of tuples:
            (common_unique_value, [] of cells)
        '''
        ret_list = []

        # unsolved_value_possibles is a {} keyed by "cell value"
        # containing a set() of cells that have "cell value" in
        # their cell.possible_values

        # We iterate thru that looking for values where only
        # "match_size" cells have that value as a possible
        for (value, cells) in self.unsolved_value_possibles.items() :

            if len(cells) == match_size :
                # We've got a winner
                ret_list.append( (value, cells) )

        return ret_list

    def is_solved(self) :
        ''' Returns True if all cells have solved, i.e. have values '''
        return not self.unsolved_cells

    def name(self) :
        ''' Returns something like:
                row#4
        '''
        return "%s#%d" % (RCB_NAME[self.rcb_type], self.rcb_num)

    def __str__(self) :
        ''' Returns terse human-readable description. e.g.
                row#3: [3 ? 2 ... ]  
        ? ==> unsolved    Cell
        X ==> unpopulated Cell
        unsolved values are: ?
        unpolu
        '''
        # Describe outselves
        ret_str = "%s: [ " % self.name()

        # And each of our cells
        for cell in self :
            ret_str += cell.str_value(unsolved_char='?') if cell else 'X'
            ret_str += ' '

        # Close the list
        ret_str += ']'
        
        return ret_str
        
    def detailed_str(self) :
        ''' String representation.  Example:
            row[3]:
               Cell#s: 27 28 29 30 31 32 33 34 35 
               Indexs:  0  1  2  3  4  5  6  7  8
               Values:  6  _  _  8  _  4  _  _  5
               Cell index possibles for unsolved values:
                  1:  0 2 4 6 7 
                  2:  0 2
                  3:  4 6 7 
                  4:  0 2 4 6 7 
                  9:  4 6 7

        Unpopulated Cells are printed as X
        '''

        ret_str = ''

        # Our type and such
        # e.g.             row[3]:
        ret_str += "%s:\n" %  self.name()

        # How much to indent the following lines
        indent_str = " " * 3

        # What to output if there isn't a Cell, i.e. None
        non_cell_str = "XX"

        # Cell numbers on one line
        # non-Cells as 'XX'
        # e.g.   Cell#s: 27 28 29 30 31 32 33 34 35 
        ret_str += indent_str + "Cell#s:"
        for cell in self :
            ret_str += "%3d" % cell.cell_num if cell else ' ' + non_cell_str
        ret_str += '\n'

        # Cell indexes one line
        ret_str += indent_str                           + \
                   "Indexs:  0  1  2  3  4  5  6  7  8" + \
                   '\n'

        # Cell values on one line
        # e.g. Values:  6  _  _  8  _  4  _  _  5
        # non-Cell values as 'XX'
        ret_str += indent_str + "Values:" # space over and label
        col_width = 3 # how many spaces per cell
        for cell in self :
            # position been populated ?
            if cell :
                # yes
                token = cell.str_value(col_width, '_')
            else :
                # Nope
                token = "%*s" % (col_width, non_cell_str)


            ret_str += token  # this cell's representation
        ret_str += '\n' # terminate the line


        # This converts self.unsolved_value_possibles to human readable string
        ret_str += self.str_unsolved_value_possibles(indent_str)

        # Give 'um the answer
        return ret_str


    def str_unsolved_value_possibles(self,
                                     indent_str = "",
                                     uvp = None) :
        '''
        # returns uvp as a human readable string.  
        # If it's None (which is probably typical) it
        # uses self.unsolved_value_possibles
        # 
        # uvp is expected to be the output of build_unsolved_value_possibles(),
        # i.e. a {} keyed by value whose {}value is set() of cells.
        #
        # Each line is prepended by indent_str.
        #
        # Example for 3 unsolved cells at index 2,4,6
        #      Cell index possibles for unsolved values:
        #         1:  2  4  6
        #         3:  4  6
        #         9:  2  4
        '''

        # If they didn't specify, use our unsolved_values_possibles
        if not uvp :
            uvp=self.unsolved_value_possibles

        # How much to index the 1: to 9: lines
        secondary_indent_str = indent_str + ' ' * 3

        ret_str = '' # what we return

        # Give them possible cells that satisfy unsolved values
        # Sort the indexes before we print them
        # e.g.               Cell index possibles for unsolved values:
        #                       1:  1  2  4  6  7 
        ret_str += "%sCell index possibles for unsolved values:\n" % (indent_str)

        # Build a [] of values in unsolved_value_possibles so we
        # can sort it an output values in numerical order
        our_unsolved_values = list ( self.unsolved_value_possibles.keys() )
        our_unsolved_values.sort()

        for value in our_unsolved_values :
            # Get the possible cells that provide this value
            cells = self.unsolved_value_possibles[value]

            ret_str += "%s%d: " % (secondary_indent_str, value)

            # Collect all the indexes of possible cells that
            # could supply value (whew!) in indexs
            indexs=[]
            for cell in cells:
                (rcb_num, rcb_idx) = cell.rcb_num_and_idx(self.rcb_type)
                indexs.append(rcb_idx)

            # Now sort and "print" it
            indexs.sort()
            for rcb_idx in indexs :
                ret_str += "%2s" % (rcb_idx)

            ret_str += '\n' # terminate the line

        # Give 'um the answer
        return ret_str

# Test code
import unittest

class Test_rcb(unittest.TestCase):

    # un-test functions, i.e. support code
    def all_unsolved_rcb_for_test(self, rcb_type) :
        ''' For test purposes, constructs and returns
        an RCB populated with cells.  This is simulating what the Board
        constructor does, but we can't do that here because
        we end up with circular imports.

        All the cells in the returned rcb are unset.
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

        # Make sure life is good
        rcb.sanity_check()

        return rcb

    def all_solved_rcb_for_test(self, rcb_type) :
        ''' returns an rcb with every cell having a value.
        '''
        # Start with one with nothing set
        rcb = self.all_unsolved_rcb_for_test(rcb_type)

        for (indx, value) in zip( range(RCB_SIZE),             # index
                                  [5, 2, 9, 6, 1, 3, 8, 4, 7] # value
                                  ) :
            # Adust the cell
            cell = rcb[indx]
            cell.value = value
            cell.possible_values=set()

        # Adjust our self
        rcb.unsolved_cells = set()
        rcb.unsolved_value_possibles = rcb.build_unsolved_value_possibles()

        # Make sure life is good
        rcb.sanity_check()

        return rcb


    def partially_solved_rcb_for_test(self, rcb_type, not_set_indexes) :
        ''' returns a board with some cells set and others unknown.
        not_set_indexes is an iterable of cell indexes (0-8) that are NOT set
        '''
        # Get a full one
        rcb = self.all_solved_rcb_for_test(rcb_type)
        assert len(rcb.unsolved_cells) == 0  # All should have a value

        # Go thru and "unset" what the caller specifies
        # Two passes

        # On first pass go thru and accumulate the values
        # of all the cells we are going to unset
        unset_cell_values = set()
        for indx in not_set_indexes :
            cell = rcb[indx]

            # build our possibles
            unset_cell_values.add ( cell.value )

        # Pass two. Set what we need to.
        # Diddle the cells. We assume all unset cells could have any of those values
        # mark the cell unsolved in the rcb
        for indx in not_set_indexes :
            cell = rcb[indx]

            # adjust the cell
            cell.value = Cell.unsolved_cell_value
            cell.possible_values |= unset_cell_values

            # adjust rcb
            rcb.unsolved_cells.add ( cell )
        

        # Rebuild unsolved_value_possibles
        rcb.unsolved_value_possibles = rcb.build_unsolved_value_possibles()

        # Make sure life is good
        rcb.sanity_check()
        return rcb

    # Actual test functions
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

    def test_solved_cells(self) :
        # an empty rcb should have none solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_cells(), set() )
        
        # a full rcb should have all cell solved
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_cells(), set(rcb) )

        # a partial rcb should have some
        solution_rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)

        # rcb is subset of solution_rcb with [8,4,3] not solved
        cells_unsolved = [8,4,3]
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_ROW,
                                                 cells_unsolved)
        solved_should_be = set(rcb) - set ([ rcb[indx] for indx in cells_unsolved ])

        self.assertEqual ( rcb.solved_cells(), solved_should_be )

        

    def test_solved_values(self) :
        # an empty rcb should have no values in solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_values(), set() )

        # a full rcb should have all values in solved
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.solved_values(), Cell.all_cell_values )


        # a partial rcb should have some
        solution_rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)

        # rcb is subset of solution_rcb with [1,2,4,6] not solved
        cells_unsolved = set([  1,2,  4,   6       ])
        cells_solved   = set([0,    3,  5,   7, 8, ])
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_ROW,
                                                 cells_unsolved)

        solved_should_be = set([ rcb[indx].value for indx in cells_solved])
        self.assertEqual ( rcb.solved_values(), solved_should_be )


    def test_unsolved_values(self) :

        # an empty rcb should have every value in unsolved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.unsolved_values(), Cell.all_cell_values )

        # a full rcb should have no values in unsolved
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_BLK)
        self.assertEqual ( rcb.unsolved_values(), set() )


        # a partial rcb should have some
        solution_rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)

        # rcb is subset of solution_rcb with [4,5,7,8] not solved
        cells_unsolved = [4,5,7,8]
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_ROW,
                                                 cells_unsolved)
        unsolved_should_be = set([ solution_rcb[indx].value for indx in cells_unsolved])
        self.assertEqual ( rcb.unsolved_values(), unsolved_should_be )


    def test_sanity_check(self) :
        # We want trigger all the bad conditions it checks for

        # wrong # of cells
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_ROW)
        rcb.pop()
        self.assertRaises(AssertionError, rcb.sanity_check )

        # wrong number of unsolved cells
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_COL)
        rcb.unsolved_cells.pop()
        self.assertRaises(AssertionError, rcb.sanity_check )

        # wrong length of unsolved_value_possibles
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_COL)
        cell_to_discard = rcb[2]
        rcb.unsolved_value_possibles[3].discard( cell_to_discard )
        self.assertRaises(AssertionError, rcb.sanity_check )

        # unpopulated cell
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_COL)
        rcb[8] = None
        self.assertRaises(AssertionError, rcb.sanity_check )

        # a populated cell is solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        rcb[4].value = 3 # solve it
        self.assertRaises(AssertionError, rcb.sanity_check )

        # cell not in unsolved_value_possibles[cell.value]
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        rcb.unsolved_value_possibles[9].discard( rcb[4] )
        self.assertRaises(AssertionError, rcb.sanity_check )


    def test_name(self) :
        rcb = RCB(RCB_TYPE_ROW, None, 2)
        self.assertEqual ( rcb.name(), "row#2")

        rcb = RCB(RCB_TYPE_COL, None, 4)
        self.assertEqual ( rcb.name(), "col#4")

        rcb = RCB(RCB_TYPE_BLK, None, 8)
        self.assertEqual ( rcb.name(), "blk#8")

    
    def test_str(self) :
        # An unpopulated row
        rcb = RCB(RCB_TYPE_ROW, None, 5)
        self.assertEqual( str(rcb),
                          "row#5: [ X X X X X X X X X ]")

        # A partially populated column
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL, [1,6,8])
        self.assertEqual( str(rcb),
                          "col#6: [ 5 ? 9 6 1 3 ? 4 ? ]")



    def test_detailed_str(self) :
        # An unpopulated RCB
        rcb = RCB(RCB_TYPE_BLK, None, 8)
        should_be = '\n'.join([
            "blk#8:",
            "   Cell#s: XX XX XX XX XX XX XX XX XX",
            "   Indexs:  0  1  2  3  4  5  6  7  8",
            "   Values: XX XX XX XX XX XX XX XX XX",
            "   Cell index possibles for unsolved values:",
        ]) + '\n'
        self.assertEqual( rcb.detailed_str(), should_be)


        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL, [2, 7])        

        should_be = '\n'.join( [
            "col#6:",
            "   Cell#s:  6 15 24 33 42 51 60 69 78",
            "   Indexs:  0  1  2  3  4  5  6  7  8",
            "   Values:  5  2  _  6  1  3  8  _  7",
            "   Cell index possibles for unsolved values:",
            "      4:  2 7",
            "      9:  2 7"
        ]) + '\n'
        self.assertEqual( rcb.detailed_str(), should_be)



    def test_a_cell_was_set(self) :
        # Get a partially populated rcb with index 3,4,5 unset
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL, [3,4,5])

        # Initial:
        # col[6]:
        # Cell#s:  6 15 24 33 42 51 60 69 78
        # Indexs:  0  1  2  3  4  5  6  7  8
        # Values:  5  2  9  _  _  _  8  4  7
        # Cell index possibles for unsolved values:
        # 1:  3  4  5 
        # 3:  3  4  5 
        # 6:  3  4  5 

        # Can't set a previously set Cell
        already_set_cell = rcb[0]
        self.assertRaises (AssertionError, rcb.a_cell_was_set, already_set_cell )
        
        # Can't do this will a cell not in the RCB
        non_rcb_cell = Cell(None, 80)
        self.assertRaises (AssertionError, rcb.a_cell_was_set, non_rcb_cell )

        # Can't do this with unset cell
        unset_cell = rcb[3]
        self.assertRaises( AssertionError, rcb.a_cell_was_set, unset_cell )

        # Test if it actually works
        # Set one of our unsolved cells to an unsolved value
        set_cell  = rcb[3]
        set_value = 1
        set_cell.set(set_value)

        # After rcb[3] set to 1
        # col[6]:
        # Cell#s:  6 15 24 33 42 51 60 69 78
        # Indexs:  0  1  2  3  4  5  6  7  8
        # Values:  5  2  9  1  _  _  8  4  7
        # Cell index possibles for unsolved values:
        # 3:  4  5 
        # 6:  4  5 

        ret_set = rcb.a_cell_was_set(set_cell)
        self.assertEqual (ret_set, set() ) # No other cells can be set
                                           # as a result of this
        # cell is no longer unsolved
        self.assertEqual (rcb.unsolved_cells, set([ rcb[4], rcb[5] ]))

        # No one can provide it's value
        self.assertTrue (set_cell.value not in rcb.unsolved_value_possibles)

        # Cell can't provide any other value
        for cells in rcb.unsolved_value_possibles.values() :
            self.assertTrue( set_cell not in cells )

        rcb.sanity_check()

        # Set another our unsolved cells to an unsolved value
        set_cell  = rcb[4]
        set_value = 3
        set_cell.set(set_value)

        # After rcb[4] set to 4
        # col[6]:
        # Cell#s:  6 15 24 33 42 51 60 69 78
        # Indexs:  0  1  2  3  4  5  6  7  8
        # Values:  5  2  9  1  3  _  8  4  7
        # Cell index possibles for unsolved values:
        # 6:  5 
        # Note that cell rcb[5] can be set to 6

        ret_set = rcb.a_cell_was_set(set_cell)

        # We know that cell at rcb[5] can be set to 6
        should_be = set([ CellToSet(rcb[5], 6) ])
        self.assertEqual (ret_set, should_be )

        # cell is no longer unsolved
        self.assertEqual (rcb.unsolved_cells, set([ rcb[5] ]))

        # No one can provide it's value
        self.assertTrue (set_cell.value not in rcb.unsolved_value_possibles)

        # Cell can't provide any other value
        for cells in rcb.unsolved_value_possibles.values() :
            self.assertTrue( set_cell not in cells )

        rcb.sanity_check()


    def test_remove_from_possibles(self) :
        # Error conditions
        # Bad value
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)
        self.assertRaises (AssertionError, rcb.remove_from_possibles,18)

        # Silently don't remove non-existent values
        # just returns empty set
        rcb = self.all_solved_rcb_for_test(RCB_TYPE_ROW)
        ret = rcb.remove_from_possibles( 5 )
        self.assertEqual ( ret,                          set() )
        self.assertEqual ( rcb.unsolved_value_possibles, {}    )
        rcb.sanity_check()

        # Remove a possiblity that doesn't cause any other cells to be solved
        rcb = self.all_unsolved_rcb_for_test(RCB_TYPE_BLK)  # empty
        removed_value = 4
        ret = rcb.remove_from_possibles( removed_value )

        self.assertEqual ( ret,                          set() )
        self.assertTrue ( removed_value not in rcb.unsolved_value_possibles )
        rcb.sanity_check()
        

        # Remove a possibility that forces another cell to be solvable
        # Get which cells we are going to use from full rcb
        # as partial rcb is a subset of that
        rcb_type = RCB_TYPE_COL
        full_rcb = self.all_solved_rcb_for_test(rcb_type)

        removed_index   = 0
        solvable_index  = 1
        unsolved_index  = 2

        removed_value = full_rcb[removed_index].value

        solvable_cell_num   = full_rcb[solvable_index].cell_num
        solvable_cell_value = full_rcb[solvable_index].value

        # Now create an rcb without those cells set
        rcb = self.partially_solved_rcb_for_test(RCB_TYPE_COL,
                                                 [removed_index,
                                                  solvable_index,
                                                  unsolved_index] )
        # Here's the current situation
        #    col#6:
        #    Cell#s:  6 15 24 33 42 51 60 69 78
        #    Indexs:  0  1  2  3  4  5  6  7  8
        #    Values:  _  _  _  6  1  3  8  4  7
        #    Cell index possibles for unsolved values:
        #    2:  0 1 2
        #    5:  0 1 2
        #    9:  0 1 2
        #
        #Cell#:6  index:0 possible_values: [2, 5, 9]
        #Cell#:15 index:1 possible_values: [2, 5, 9]
        #Cell#:24 index:2 possible_values: [2, 5, 9]
        
        # removed_value: 5
        ret = rcb.remove_from_possibles(removed_value)

        # Returns: []

        # Leaves:
        #   col#6:
        #   Cell#s:  6 15 24 33 42 51 60 69 78
        #   Indexs:  0  1  2  3  4  5  6  7  8
        #   Values:  _  _  _  6  1  3  8  4  7
        #   Cell index possibles for unsolved values:
        #      2:  0 1 2
        #      9:  0 1 2
        # Cell#:  6 index:0 possible_values: [2, 9]
        # Cell#: 15 index:1 possible_values: [2, 9]
        # Cell#: 24 index:2 possible_values: [2, 9]

        ###################################################
        # Busted
        return
        ###################################################

        self.assertEqual( len(ret), 1) # only one cell set
        (cell_to_set, value_to_set) = ret.pop()
        self.assertEqual(cell_to_set.cell_num, solvable_cell_cell_num)
        self.assertEqual(value_to_set        , solvable_cell_value   )
        



if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

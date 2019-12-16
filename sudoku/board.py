#!/usr/bin/env python3
# dinkum/sudoku/board.py
''' Defines sudoku Board class which represents a
sudoku board full of Cells with values.
'''

# 2019-11-25 tc Initial
# 2019-11-26 tc Gave names to boards
# 2019-11-30 tc Added board description
# 2019-12-02 tc Added some spaces in __str__() output
#               Let Board() take a string as well as list of rows
# 2019-12-04 tc Added solve_time_secs
# 2019-12-08 tc Added str_unsolved_rcbs()
# 2019-12-09 tc use class sudoku.Stats
#               Added copy constructor
# 2019-12-10 tc copy_construtor.  Use name of copied board
#               Added reduce_possibles_from_matching_cells()
# 2019-12-14 tc Added a_cell_was_set() and
#               solve_cells()

from dinkum.sudoku.rcb   import *
from dinkum.sudoku.cell  import *
from dinkum.sudoku.stats import *

import time

def str_to_list_of_rows(s) :
    ''' translate s to list of row-lists suitable for input to Board()
    and return it.

    s should contain a boards worth (81) of digits in range 0-9 inclusive.
    Whitespace is ignored as well as any non-digits.  The values are in
    raster order.

    Not much error checking is done. Presumably someone else is
    error checking the returned list of row-lists.

    Raises ExcBadStrToConvert if there aren't exactly a boards worth of
    digits in s.
    '''

    # Disappear the white space
    digits = [ int(c) for c in s if c.isdigit() ]

    # Verify the count
    if len(digits) != (RCB_SIZE)*(RCB_SIZE) :
        raise ExcBadStrToConvert  # Oops

    # Put them in their place
    list_of_rows=[]
    for row_num in range(RCB_SIZE) :
        offset = row_num * RCB_SIZE # which digit starts this row
        list_of_rows.append ( digits[offset:offset+RCB_SIZE] )

    return list_of_rows


class Board :
    ''' Holds the representation of of a sudoku board.
    Has a solve() which will solve the Board by altering
    it in place.

    Various data:
      name            Name of the board, set in constructor
      description     Description of the board, set in constructor
    

      cells           List of all Cells in raster order,
                      i.e. left to right, top to bottom
      unsolved_cells  Set of Cells that need to be filled in with a value

      rows,cols,blks  [] of Cells in that entity.  Indexed by {row/col/blk}_num
                      Can be retrieved by rcb()

      rcbs            [] of all rows,cols,blks

      solve_stats     class Stats that holds various
                      statistics about solve(), e.g.
                      how long to solve, etc

    Board()[row][col] can be used to get Cell at (row,col)

    Some seful functions (there are others)
      solve()           Trys to solve the board
      solve_cells       solves(sets) a bunch of cells
      a_cell_was_set()  Should be called when any cell is solved

    A Board can be specified to Board() as a list of row, e.g
        [ [1,2,3,4,5,6,7,8,9],
          [0,0,1,0,0,2,5,0,0],
               ...
        ]
    It can also be specified as a string of digits 0-9 separated by as
    much or little whitespace as you desire. e.g.
        1 2 3 4 5 6 7 8 9
        0 0 1 0 0 2 5 0 0
            ...
    --or--
        123456789001002500
            ...

    It can also be passed another Board, i.e. copy constructor
    '''

    # Class variables
    board_copy_cnts = {} # How many times a board was copied in
                         # in copy constructor.
                         # key: base board name value: # times copied
                         # see _pick_name_and_desc()


    def __init__(self, board_spec=None, name=None, desc="") :
        ''' constructor of a Board
        board_spec is list of row-lists --or--
        a string of values              --or--
        a Board
        If board_spec is None, an empty board will be created.

        name is used as the name of the board.
        If name is None, a unique name will be chosen, something on
        the order of:
            board-<lots of numbers which represent the curr time> 

        desc is description of the board, i.e. it's source or
        characteristics.  It defaults to empty string.

        raise ExcBadPuzzleInput if "arr" is bad
        various assertion failures if things aren't right.
        '''

        # Deal with the name/description and statistics
        (self.name, self.description) = self._pick_name_and_desc(name, desc, board_spec)
        self.solve_stats  = Stats()
        
        # Convert board_spec into list of rows
        # Need to translate string into list of rows?
        if isinstance(board_spec, str) :
            try:
                list_of_rows = str_to_list_of_rows(board_spec)
            except ExcBadStrToConvert :
                raise ExcBadPuzzleInput( "Not an exact boards worth of digits in arr as string" )

        # Need to translate Board into list of rows?
        elif isinstance(board_spec, Board) :
            list_of_rows = board_spec.output()
        else :
            list_of_rows = board_spec

        # We are generating new board from a list of row-lists
        # We create empty data structs and have set() adjust them

        # Create all rows/cols/blocks.  Make them empty
        self.rows = [ RCB(RCB_TYPE_ROW, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 
        self.cols = [ RCB(RCB_TYPE_COL, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 
        self.blks = [ RCB(RCB_TYPE_BLK, self, rcb_num) for rcb_num in range(RCB_SIZE) ] 

        # Gather them all in one place
        self.rcbs = self.rows + self.cols + self.blks

        # List of all Cells indexed by cell#
        # Is inited to unsolved and all values possible
        # We pass our self in so Cell knows what board it belongs to
        # Cell() initializes the rows/cols/blks it belongs to
        # These are created in raster order
        self.cells = [ Cell(self, cell_num) for cell_num in range(NUM_CELLS)]

        # A separate Set of Cells that are unsolved.
        # Currently all cells are unsolved
        # Note: We use Set rather than list because set is faster than []
        self.unsolved_cells = set(self.cells)
        assert len( self.unsolved_cells) == NUM_CELLS

        # Populate all rows/cols/blocks
        for cell in self.cells :
            # Populate all the rows/cols/blks that this cell belongs to
            self.rows[cell.row_num].initial_cell_placement(cell)
            self.cols[cell.col_num].initial_cell_placement(cell)
            self.blks[cell.blk_num].initial_cell_placement(cell)

        # We have a valid empty board at this point
        # Sanity check all the RCBs
        for rcb in self.rcbs :
            rcb.sanity_check() 

        # Is there any input to set cells with?
        if not list_of_rows :
            return # nope, all done

        # We need to populate it with values as spec'ed by the caller

        # Go thru and set each cell value from our input,
        # set() adjusts all the data structures
        if len(list_of_rows) != RCB_SIZE :    # Sanity check input
            raise ExcBadPuzzleInput( "Wrong number of rows: %d" % len(list_of_rows) )

        cell_num=0
        row_num =0
        for row in list_of_rows :
            # Sanity check
            if len(row) != RCB_SIZE :
                raise ExcBadPuzzleInput( "Row %d: Wrong size: %d" % (row_num, len(row)))

            col_num = 0
            for value in row :
                # who we are testing
                cell=self.cells[cell_num]
                
                # Skip unknown values, all data bases init'ed for all unknown
                if value != Cell.unsolved_cell_value:
                    # Sanity check the value
                    if value not in Cell.all_cell_values :
                        raise ExcBadPuzzleInput( "Bad value: %d at (row,col) (%d,%d)" % (value, row_num, col_num))

                    # Common error msg for duplicate entries, which Should be formated with
                    # (cell_num, row_num, col_num, value, "row/col/blk"
                    err_fmt_str = "cell#%d at (%d,%d) value:%d is duplicated in cell's %s"

                    # We know that cell is currently unset
                    assert cell.value == Cell.unsolved_cell_value

                    # Can't have duplicate values in a row/col/blk
                    if value in [ cell.value for cell in cell.row] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "row"))
                    if value in [ cell.value for cell in cell.col] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "col"))
                    if value in [ cell.value for cell in cell.blk] :
                        raise ExcBadPuzzleInput( err_fmt_str % (cell_num, row_num, col_num,
                                                                value, "blk"))

                    # All looks good, set it
                    cell.set(value)

                cell_num += 1
                col_num += 1
            row_num += 1


        # Sanity check(s) A whole bunch of asserts
        # Could move this into unittest code....
        # but we aren't time sensitive at construction time
        self.sanity_check()

    def _pick_name_and_desc(self, name, desc, board_spec) :
        ''' returns tuple: (board_name, board_description)
        name, desc, board_spec should be the arguments passed
        into the constructor.

           board_name        name                   if name not None
                             board_spec.name-cp.<N> if board_spec is Board
                             board-<N>              otherwise.

           board_description desc                   if not None
                             board_spec.description if board_spec is Board
                             ""                     otherwise
        '''

        # What we return
        board_name = None
        board_desc = None

        # Pick the name
        if name :
            board_name = name
        elif isinstance(board_spec, Board) :
            # We keep track of the number of times a board
            # is copied in class variable: board_copy_cnts
            # a {} key:base board name value:# of times it is copied
            bn   = board_spec.name        # Just make the code read easier
            cp_dict = Board.board_copy_cnts
            if bn in  cp_dict :
                cp_dict[bn] += 1
            else:
                cp_dict[bn] = 1    # First copy

            # How many times this board has been copied
            copy_cnt = cp_dict[bn]

            # Pick the name
            board_name = board_spec.name + "-cp." + str(copy_cnt)

        else :
            board_name = self._unique_board_name()

        # Pick the description
        if desc :
            board_desc = desc
        elif isinstance(board_spec, Board) :        
            board_desc = board_spec.description
        else :
            board_desc = ""

        # All done
        return (board_name, board_desc)


    def solve(self) :
        '''
        Returns a Board that solve us.
        Return None if unsolvable
        raise Exception on multiple solutions 
        We change our values in the process
        Sets various statistics in solve_stats
        '''

        # fractional seconds
        self.solve_stats.solve_start_time_secs = time.perf_counter()

        # What we return, assume the best
        ret_value = self # overwritten if can't solve

        # We try all the solution techniques we know about
        # Each is required to return True if they set a cell
        # We give up when no cell is set in a pass
        self.solve_stats.num_solve_passes = 0
        while (not self.is_solved()) :
            # count the # of times thru the loop
            self.solve_stats.num_solve_passes += 1

            board_was_modified = False

            # Set cells with only 1 possible value
            num_solved = self.solve_cells_with_single_possible_value()
            board_was_modified |= (num_solved != 0)

            # Set row/col/blks where an unsolved value can only be
            # satisfied by a single cell
            num_solved = self.solve_rcbs_with_single_possible_value_solution()
            board_was_modified |= (num_solved != 0)

            # Remove some possibles by looking for matching cells with same possibles
            # and projecting that into other rcb's.  This doesn't actually set any
            # cells, but may modifify the board
            board_was_modified |= self.reduce_possibles_from_matching_cells()

            # How did we do?
            if not board_was_modified :
                # Not well, sigh
                ret_value = None
                break


        # All done, Remember how long we ran
        self.solve_stats.solve_time_secs = (time.perf_counter() -
                                            self.solve_stats.solve_start_time_secs)

        # Arrive here with ret_value set to either
        # self or None depending on whether we successfully solved the puzzle
        return ret_value

    
    def solve_cells_with_single_possible_value(self) :
        '''Sets all unsolved cells on the board that have a single possible value.
        Returns number of cells solved.
        '''

        # Examine all the unsolved cells, looking for ones
        # that have only 1 possible solutions
        cells_to_solve = set() # Put those cells in this set
        for cell in self.unsolved_cells :
            if len(cell.possible_values) == 1 :
                # Extract the only element in the set.  Leave num_possible_values intact
                # See https://stackoverflow.com/questions/20625579/access-the-sole-element-of-a-set
                [value] = list(cell.possible_values)

                # and set that value into the set of CellToSet
                cells_to_solve.add( CellToSet(cell, value) )


        # solve all those Cells (and any other Cells that solution causes)
        # return the total number solved
        return self.solve_cells( cells_to_solve )

    def solve_rcbs_with_single_possible_value_solution(self) :
        ''' sets all cells in all unsolved RCBs that 
        where an unsolved value can only be satisfied by a single cell (that cell)

        Returns number of cells that were solved
        '''
        num_solved = 0 # what we return

        # Iterate over unsolved rcbs
        for rcb in [rcb for rcb in self.rcbs if not rcb.is_solved()] :

            # Build a set() of CellToSet's that could provide "value"
            # We build the list and then Cell.set() in a separate pass
            # to prevent "dictionary changed size during iteration" as
            # Cell.set may modify rcb.unsolved_value_possibles
            cells_to_solve = set()
            for (value, possible_cells) in rcb.unsolved_value_possibles.items() :
                # If there is only one such cell ....
                if len(possible_cells) == 1 :
                    # We have a winner
                    # This is the only cell in the RCB what can provide "value"
                    # Extract the only element in the set, which is the providing cell
                    # See https://stackoverflow.com/questions/20625579/access-the-sole-element-of-a-set
                    [cell] = possible_cells

                    # Put it in set() to be solved
                    cells_to_solve.add( CellToSet(cell, value))

                    
            # Now solve those cells
            num_solved += self.solve_cells( cells_to_solve )
                    
        # Tell um how we did
        return num_solved


    def reduce_possibles_from_matching_cells(self) :
        '''
        Searches every rcb for pairs and triples
        of unsolved cells that all have the same possible value
        that is unique to that rcb, i.e. no other cell in the rcb
        has that value as a possible.

        It then removes their values from any common rcb in
        the pair.

        returns True if any possibles were eliminated.
        '''

        # What we return
        removed_some_possibles = False # assume the worst

        for rcb in self.rcbs :
            # this looks for pairs and triples
            # Note: quads could happen, but they can't
            #       be in the same rcb, except us
            #       and there are no other unsolved
            #       cells with their value
            for match_size in [2,3] :
                # returns [] of (common_unique_value, set() of cells)
                value_and_cells = rcb.unsolved_cells_with_common_unique_values(match_size)

                # Go thru those and remove value as a possibility
                # in all common rcbs
                for (value, cells) in value_and_cells :
                    assert len(cells) == match_size

                    # Iterate thru a list of rcbs that the matching cells have in common
                    first_cell = cells.pop() # pull a cell out of cells

                    for common_rcb in first_cell.common_rcbs( cells ) :
                        removed_some_possibles |= common_rcb.remove_value_from_possibles(value)

        return removed_some_possibles

    def a_cell_was_set(self, solved_cell) :
        ''' Should be called whenever a Cell is solved.
        solved_cell is the Cell that was solved.

        Returns a set of CellToSolve which can
        be uniquely solved as a result of cell
        being solved.

        Currently called from Cell.set()

        Maintains Board internal data:
            removes cell from unsolved_cells

        iterates thru rcbs:
            RCB.a_cell_was_set(cell)
            accumulates CellToSet for return
        '''

        # What we return
        cells_to_solve = set()

        # remove cell from unsolved_cells
        assert solved_cell in self.unsolved_cells
        self.unsolved_cells.remove(solved_cell)

        # Iterates thru rcbs:        
        for rcb in solved_cell.rcbs :
            cells_to_solve |= rcb.a_cell_was_set(solved_cell)

        # Tell them more cells to solve (if any)
        return cells_to_solve

    def __getitem__(self, row) :
        ''' Returns our RCB at row
            Allows Board()[row][col] to return a cell
        '''
        return self.rows[row]

    def rcb(self, rcb_type) :
        ''' Return [] of RCBs, rows[], cols[], or blks[]
        depending on rcb_type
        '''

        if   rcb_type == RCB_TYPE_ROW :
            return self.rows
        elif rcb_type == RCB_TYPE_COL :
            return self.cols
        elif rcb_type == RCB_TYPE_BLK :
            return self.blks
        else :
            assert False, "Unknown rcb_type:" + str(rcb_type) + " Should be one of:" + str(ALL_RCB_TYPES)
        assert False, "Impossible place"


    def solve_cells( self, cells_to_solve ) :
        ''' All Cells in cells_to_solve will
        be solved, along with any Cells that
        become solvable as a result of
        solving one of the cells in cells_to_solve.

        cells_to_solve should be iterable containing
        CellToSet's (class holds a Cell and a value
        to solve it with)

        Returns the total number of cell's solved.

        Cells in cells_to_solve which have already
        been solved are silently ignored as long
        as they have been solved with passed in
        value in CellToSet
        '''

        # What we return
        num_solved = 0

        # What we learn from setting a cell.
        additional_cells_to_solve = set()

        for (cell,value) in cells_to_solve :
            if cell.is_solved() :
                # Already solved, make sure values match
                assert cell.value == value
            else :
                # cell not solve, solve it
                additional_cells_to_solve |= cell.set(value)
                num_solved += 1

        # Any more to set?
        if additional_cells_to_solve :
            # Yes, Recurse
            num_solved += self.solve_cells( additional_cells_to_solve )

        # All done
        return num_solved
        

    def is_solved(self) :
        ''' returns true if board is solved '''
        return self.num_unsolved() == 0

    def num_unsolved(self) :
        ''' returns the number of unsolved cells.
        '''
        return len(self.unsolved_cells)


    def output(self) :
        ''' returns list of rows of the Board.
        Same format as __init__ argument '''

        # Build [] of rows where every row is [] of cells in it
        list_of_rows = [[ cell.value for cell in self.rows[row_indx]] for row_indx in range(RCB_SIZE) ]

        return list_of_rows

    def __str__(self) :
        ''' returns human readable terse picture of a sudoku.
        The last line is terminated by a new line.

        Example:
         3 4 6  1 2 7  9 5 8
         7 8 5  6 9 4  1 3 2
         2 1 9  3 8 5  4 6 7

         4 6 2  5 3 1  8 7 9
         9 3 1  2 7 8  6 4 5
         8 5 7  9 4 6  2 1 3

         5 9 8  4 1 3  7 2 6
         6 2 4  7 5 9  3 8 1
         1 7 3  8 6 2  5 9 4

        '''
        ret_str = ""
        for row in self.rows :
            # row separator?
            if row.rcb_num and not row.rcb_num % BLK_SIZE :
                ret_str += '\n'
                
            # Print the cell values
            for cell in row :
                # Vertial block separator?
                if cell.col_num and not cell.col_num % BLK_SIZE :
                    ret_str += ' '

                # Cell's value
                ret_str += "%2d" % cell.value

            ret_str += '\n'

        return ret_str

    def str_unsolved_rcbs(self) :
        ''' returns printable information about
        all RCBs that aren't completely solved.
        '''
        ret_str = "" # What we return

        # Iterate over all unsolved rcbs
        for rcb in self.rcbs :
            if len(rcb.unsolved_cells) :
                # It's unsolved
                ret_str += str(rcb)
        return ret_str

    def _unique_board_name(self) :
        ''' Picks a unique name for the board comprised of:
        board-<current_time as bunch of numbers>
        '''
        nanosecs_from_1970 = time.time() * 10**9

        return "board-" + str(int(nanosecs_from_1970))

    def is_subset_of(self, their_board) :
        ''' returns True if every cell in our Board has
        the same value "their_board"
        '''
        # Iterate over both our cells
        for (our_cell, their_cell) in zip(self.cells, their_board.cells) :
            # Is our cell set?
            if our_cell.value != Cell.unsolved_cell_value :
                # Yes, is it the same?
                if our_cell.value != their_cell.value :
                    return False # nope, they differ

        # If we fall out of the loop.. it's a subset
        return True
                

    # Operators
    def __eq__(self, their) :
        ''' == tester.  We just require all cells to have the same value
        '''
        # If they aren't a Board, we aren't equal
        if not isinstance (their, Board)  :
            return False

        # Iterate cells together
        for (our_cell, their_cell) in zip(self.cells, their.cells) :
            if our_cell.value != their_cell.value :
                return False  # we are NOT equal

        # If we fall out, all cells matched.
        return True

    def sanity_check(self) :
        ''' Runs a variety of checks on the data structures.
        assert's on first failure.
        '''

        # Make sure all rows/cols/blks got populated
        for rcb_num in range(RCB_SIZE) :
            for indx in range(RCB_SIZE) :
                if not self.rows[rcb_num][indx] : assert "Unpopulated row:% entry:%d" % (rcb_num, indx)
                if not self.cols[rcb_num][indx] : assert "Unpopulated col:% entry:%d" % (rcb_num, indx)
                if not self.blks[rcb_num][indx] : assert "Unpopulated blk:% entry:%d" % (rcb_num, indx)

        # Make sure cells/rows/cols/blks all refer to the same cell
        # Raster scan cells/rows/cols/blks
        cell_num = 0
        for row_num in range(RCB_SIZE) :
            for col_num in range(RCB_SIZE) :

                # cells[] are in raster order
                cell = self.cells[cell_num]

                # Confirm cell number matches
                assert cell.cell_num == cell_num, "Cell.num %d should be %d" % (cell.cell_num, cell_num)

                # Confirm raster order
                assert cell.row_num == row_num, "cell%d has row#%d, should be %d" % (cell.cell_num,
                                                                                     cell.row_num, row_num)
                assert cell.col_num == col_num, "cell%d has col#%d, should be %d"  % (cell.cell_num,
                                                                                      cell.col_num, col_num)
                # We don't check blk because too hard to compute block number here.

                # The cells notion of row/col/blk should match ours
                assert cell.row is self.rows[cell.row_num], "Cell.row is wrong"
                assert cell.col is self.cols[cell.col_num], "Cell.col is wrong"
                assert cell.blk is self.blks[cell.blk_num], "Cell.blk is wrong"

                # We compare each row/col/blk to this cell
                cell_by_rows  = cell.row[cell.row_idx]
                cell_by_cols  = cell.col[cell.col_idx]
                cell_by_blks  = cell.blk[cell.blk_idx]

                # They should all be the same
                assert cell_by_rows is cell, "Cell#%d is not same as cell in rows[%d][%d]" % (cell_num,
                                                                                              cell.row_num,
                                                                                              cell.row_idx)
                assert cell_by_cols is cell, "Cell#%d is not same as cell in cols[%d][%d]" % (cell_num,
                                                                                              cell.col_num,
                                                                                              cell.col_idx)
                assert cell_by_blks is cell, "Cell#%d is not same as cell in blks[%d][%d]" % (cell_num,
                                                                                              cell.blk_num,
                                                                                              cell.blk_idx)
                # Advance to next cell
                cell_num += 1

        # If all out of loop... all went well
        return (True, None )

# Test code
import unittest
import copy

class Test_board(unittest.TestCase):


    def test_empty_board(self) :
        board = Board() # No cells should be set

        # Confirm none set
        for cell in board.cells :
            self.assertEqual (cell.value, Cell.unsolved_cell_value,
                         "Cell# %d should be unset, it is: %d" % (cell.cell_num, cell.value))
            # All values should be possible
            self.assertSetEqual (cell.possible_values, Cell.all_cell_values,
                                 "Cell# %d: num_possibles should have all possible values" %cell.cell_num)
                       
    def test_board_name(self) :
        name = "I never know what to call you"
        board = Board(None, name)
        self.assertEqual(name, board.name)
        self.assertEqual(board.description, "")  # No description supplied, default ""

        name = "The world is a tough place"
        desc = "Isn't that cynical?"
        board = Board(None, name, desc)
        self.assertEqual(name, board.name)
        self.assertEqual(board.description, desc)

    def test_unique_board_names(self) :

        # Generate a bunch of boards and make sure names are all different
        names_so_far = set()
        for cnt in range(100) :
            board = Board()

            assert board.name not in names_so_far

            names_so_far.add(board.name)
        

    def test_str_constructor(self) :
        ''' Make sure string and list of row-list generate same board '''
        lrl_spec =   [[0, 4, 6, 1, 2, 7, 9, 5, 8], 
                      [7, 0, 5, 6, 9, 4, 1, 3, 2], 
                      [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                      [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                      [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                      [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                      [5, 9, 8, 4, 1, 3, 7, 2, 6],
                      [6, 2, 4, 7, 5, 9, 3, 8, 1],
                      [1, 7, 3, 8, 6, 2, 5, 9, 4]]


        str_board_spec = '''
                      0 4 6 1 2 7 9 5 8 
                      7 0 5 6 9 4 1 3 2 
                      2 1 9 3 8 5 4 6 7 
                      4 6 2 5 3 1 8 7 9 
                      9 3 1 2 7 8 6 4 5 
                      8 5 7 9 4 6 2 1 3 
                      5 9 8 4 1 3 7 2 6
                      6 2 4 7 5 9 3 8 1
                      1 7 3 8 6 2 5 9 4
        '''
        self.assertEqual( Board(lrl_spec), Board(str_board_spec),
                          "string and list of row-lists generate different Boards")

    def test_copy_constructor(self) :

        # Make a couple of copies and insure they copy properly
        # and empty board
        in_board = Board() # empty
        out_board = Board(in_board)
        self.assertEqual(in_board, out_board)

        # random filled in board
        str_board_spec = '''
                      0 4 6 1 2 7 9 5 8 
                      7 0 5 6 9 4 1 3 2 
                      2 1 9 3 8 5 4 6 7 
                      4 6 2 5 3 1 8 7 9 
                      9 3 1 2 7 8 6 4 5 
                      8 5 7 9 4 6 2 1 3 
                      5 9 8 4 1 3 7 2 6
                      6 2 4 7 5 9 3 8 1
                      1 7 3 8 6 2 5 9 4
        '''
        in_board = Board(str_board_spec)
        out_board = Board(in_board)

        self.assertEqual(in_board, out_board) # produces same board
        self.assertEqual(out_board.name, in_board.name + "-cp.1")
        self.assertEqual(in_board.description, out_board.description)

        # copy # is correct
        # We have already made 1 copy
        for copy_cnt in range(2, 10) :
            out_board = Board(in_board)
            self.assertEqual (out_board.name, in_board.name + "-cp." + str(copy_cnt))

        # Make sure a specified name overrides picking from copied board
        speced_name = "We picked it"
        out_board = Board(in_board, speced_name)
        self.assertEqual( out_board.name, speced_name )
        self.assertEqual( out_board.description,
                          in_board.description)
        
        # Make sure a specified description overrides picking from copied board
        speced_desc = "Just for unittesting!"
        out_board = Board(in_board, None, speced_desc)
        self.assertEqual( out_board.description, speced_desc )


    def test_subset(self) :
        # What we test with
        some_board_spec = [ \
                    [3, 4, 6, 1, 2, 7, 9, 5, 8], 
                    [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                    [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                    [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                    [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                    [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                    [5, 9, 8, 4, 1, 3, 7, 2, 6],
                    [6, 2, 4, 7, 5, 9, 3, 8, 1],
                    [1, 7, 3, 8, 6, 2, 5, 9, 4]]
        some_board = Board(some_board_spec, "some_board" )

        # An empty board is a subset of everything
        empty_board=Board()
        self.assertTrue ( empty_board.is_subset_of(some_board))

        # Everyboard is a subset of itself
        self.assertTrue (some_board.is_subset_of(some_board))

        # Create a legal subset by zeroing some elements
        subset_spec = some_board_spec.copy()
        subset_spec[0][3] = 0
        subset_spec[5][0] = 0
        subset_spec[2][3] = 0
        subset_spec[8][1] = 0
        subset_spec[4][0] = 0
        subset_board=Board(subset_spec, "subset_board", "For unit testing")
        self.assertTrue (subset_board.is_subset_of(some_board))        

        # Create a non-subset 
        non_subset_spec = [ [0]*9, [0]*9, [0]*9,
                            [0]*9, [0]*9, [0]*9,
                            [0]*9, [0]*9,
                            [0]*8 + [9]      # was a 4 in some_board
        ]

        non_subset_board=Board(non_subset_spec, "non subset board")
        self.assertFalse ( non_subset_board.is_subset_of(some_board) )

    def test_str_to_row_lists_errors(self) :

        # Number of values expected
        board_size = RCB_SIZE * RCB_SIZE
        board = Board() # empty board

        too_few_spec = '0' * (board_size-1)
        self.assertRaises(ExcBadStrToConvert, str_to_list_of_rows,too_few_spec)

        # Test too many digits in str
        too_many_spec = '0' * (board_size+1)
        self.assertRaises(ExcBadStrToConvert, str_to_list_of_rows, too_many_spec)

    def test_solve_stats(self) :

        # Can't really validate the solve stats
        # Just make sure it exists

        # unsolvable (empty board)
        board = Board() 
        self.assertIsNone   ( board.solve_stats.solve_time_secs )
        board.solve()
        self.assertIsNotNone( board.solve_stats.solve_time_secs )        

        # solvable
        board_spec = '''
         3 4 6  1 2 7  9 5 8
         7 8 5  6 9 4  1 3 2
         2 1 9  3 8 5  4 6 7

         4 6 2  5 3 1  8 7 9
         9 3 1  2 7 8  6 4 5
         8 5 7  9 4 6  2 1 3

         5 9 8  4 1 3  7 2 6
         6 2 4  7 5 9  3 8 1
         1 7 3  8 6 2  5 9 4
        '''
        board = Board(board_spec) 
        self.assertIsNone   ( board.solve_stats.solve_time_secs )
        board.solve()
        self.assertIsNotNone( board.solve_stats.solve_time_secs )        

        

    def test_cell_all_neighbors(self) :
        # By rights it should be in the unittest for cell.py
        # but it can't because it would mean cyclical imports
        # so... we test it here

        board = Board()

        # Test a few at random
        cell = board[3][7]
        cell_neighbors_are = cell.all_neighbors()

        cell_neighbors_should_be  = [board.cells[idx] for idx in range(27, 36   ) if idx != cell.cell_num] # row
        cell_neighbors_should_be += [board.cells[idx] for idx in range( 7, 80, 9) if idx != cell.cell_num] # col
        cell_neighbors_should_be += [board.cells[idx] for idx in [42, 44, 51, 53]] # blk: that aren't in row/col
        cell_neighbors_should_be = set( cell_neighbors_should_be)

        self.assertEqual( cell_neighbors_are, cell_neighbors_should_be)
                                     

        cell = board[2][4]
        cell_neighbors_are = cell.all_neighbors()

        cell_neighbors_should_be  = [board.cells[idx] for idx in range(18, 27   ) if idx != cell.cell_num] # row
        cell_neighbors_should_be += [board.cells[idx] for idx in range( 4, 81, 9) if idx != cell.cell_num] # col
        cell_neighbors_should_be += [board.cells[idx] for idx in [3,5,12,14]] # blk: that aren't in row/col
        cell_neighbors_should_be = set( cell_neighbors_should_be)

        self.assertEqual( cell_neighbors_are, cell_neighbors_should_be)

        
    def test_is_solved_and_cnt(self) :
        # empty board
        board = Board()
        self.assertFalse ( board.is_solved() )
        self.assertEqual ( board.num_unsolved(), RCB_SIZE * RCB_SIZE )

        # Full populated board
        input_spec ='''
         3 4 6 1 2 7 9 5 8 
         7 8 5 6 9 4 1 3 2 
         2 1 9 3 8 5 4 6 7 
         4 6 2 5 3 1 8 7 9 
         9 3 1 2 7 8 6 4 5 
         8 5 7 9 4 6 2 1 3 
         5 9 8 4 1 3 7 2 6
         6 2 4 7 5 9 3 8 1
         1 7 3 8 6 2 5 9 4
        '''
        board = Board(input_spec)
        self.assertTrue ( board.is_solved() )
        self.assertEqual ( board.num_unsolved(), 0 )
        

        # Partially populated board
        input_spec ='''
         3 0 6 1 2 7 9 5 8 
         7 0 0 6 9 4 1 3 2 
         2 1 9 3 8 5 4 6 7 
         4 6 2 5 3 1 8 7 9 
         9 3 1 2 7 8 6 4 5 
         0 0 0 9 0 6 2 1 3 
         5 9 8 4 1 3 7 2 6
         6 2 4 7 5 9 3 8 1
         1 7 3 8 6 2 5 9 0
        '''
        board = Board(input_spec)
        self.assertFalse ( board.is_solved() )
        self.assertEqual ( board.num_unsolved(), 8 )


    def test_common_cell_rcbs(self) :

        # we are testing Cell.common_rcbs() which can't
        # be testing in cell.py because it doesn't know
        # about Boards to avoid a circular import loop

        board=Board()

        base_cell         = board[4][5]
        cell_same_row     = board[4][6]
        cell_same_col     = board[2][5]
        cell_same_blk     = board[3][3]
        cell_with_none    = board[8][8]
        cell_same_row_blk = board[4][4]
        cell_same_col_blk = board[3][5]

        all_test_cells = [cell_same_row,
                          cell_same_col,
                          cell_same_blk,
                          cell_with_none
                          ]

        row_rcb = base_cell.row
        col_rcb = base_cell.col
        blk_rcb = base_cell.blk

        self.assertEqual( base_cell.common_rcbs( []               ), [] )
        self.assertEqual( base_cell.common_rcbs( [cell_with_none] ), [] )

        self.assertEqual( base_cell.common_rcbs( [cell_same_row]     ), [row_rcb] )
        self.assertEqual( base_cell.common_rcbs( [cell_same_col]     ), [col_rcb] )
        self.assertEqual( base_cell.common_rcbs( [cell_same_blk]     ), [blk_rcb] )

        self.assertEqual( base_cell.common_rcbs( [cell_same_row_blk] ), [row_rcb, blk_rcb] )
        self.assertEqual( base_cell.common_rcbs( [cell_same_col_blk] ), [col_rcb, blk_rcb] )

        self.assertEqual( base_cell.common_rcbs( all_test_cells ), [] )

    def test_input_bad_input_wrong_row_cnt(self) :
        # Only 7 rows, values don't matter
        puzzle = [ [0] * 9 for i in range(7) ]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Wrong number of rows: 7')

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(puzzle))


    def test_input_bad_value(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]
        
        # Make a single bad value
        puzzle[3][6] = 18

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message,
                             'Bad value: 18 at (row,col) (3,6)')

    def test_input_bad_input_wrong_row_size(self) :
        # 9 rows, , values don't matter
        puzzle = [ [0] * 9 for i in range(9) ]

        # remove an cell from a row
        puzzle[4] = puzzle[4][1:]

        # Make sure it raise the exception
        self.assertRaises(ExcBadPuzzleInput, Board, puzzle)

        # Verify the error message
        try :
            Board(puzzle)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, 'Row 4: Wrong size: 8')

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(puzzle))


    def test_input_duplicate_values(self) :
        some_board_spec = [ \
                            [0, 4, 6, 1, 2, 7, 9, 5, 8], # 0 row
                            [7, 0, 0, 6, 9, 4, 1, 3, 2], # 1 row
                            [2, 1, 9, 0, 0, 0, 4, 6, 7], # 2 row
                            [4, 6, 2, 5, 3, 1, 0, 0, 0], # 3 row
                            [0, 3, 0, 2, 0, 8, 0, 0, 0], # 4 row
                            [8, 5, 7, 9, 4, 6, 2, 0, 3], # 5 row
                            [0, 9, 8, 4, 1, 3, 7, 2, 6], # 6 row
                            [6, 2, 4, 7, 5, 9, 3, 8, 1], # 7 row
                            [1, 7, 3, 8, 6, 2, 5, 9, 4]  # 8 row
                #       col  0  1  2  3  4  5  6  7  8
        ]

        # Make some illegal input
        # duplicate value in a row
        dup_in_row = copy.deepcopy(some_board_spec)
        dup_in_row[3][7] = 1
        expected_err_msg = "cell#34 at (3,7) value:1 is duplicated in cell's row"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_row) # Make sure it raise the exception
        try:
            board = Board(dup_in_row)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(dup_in_row))



        # duplicate value in a col
        dup_in_col = copy.deepcopy(some_board_spec)
        dup_in_col[4][7] = 5
        dup_in_col[3][3] = 0 # avoid duplicate in the block
        expected_err_msg = "cell#43 at (4,7) value:5 is duplicated in cell's col"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_col) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_col)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(dup_in_col))


        # duplicate value in a blk
        dup_in_blk = copy.deepcopy(some_board_spec)
        dup_in_blk[6][7] = 4
        expected_err_msg = "cell#61 at (6,7) value:4 is duplicated in cell's row"
        self.assertRaises(ExcBadPuzzleInput, Board, dup_in_blk) # Make sure it raise the exception
        try:                        
            board = Board(dup_in_blk)
        except ExcBadPuzzleInput as exc :
            self.assertEqual(exc.message, expected_err_msg)  # with right error message

        # Make sure string spec'ed board generates a error
        # The error message may differ
        self.assertRaises(ExcBadPuzzleInput, Board, str(dup_in_blk))

    def test_solve_cells(self) :
        # Empty Board
        board = Board()

        # Solve 1 cell only
        # Shouldn't set any others
        cells_to_solve = set( [CellToSet( board[4][6], 3)])
        num_solved = board.solve_cells( cells_to_solve)
        self.assertEqual( num_solved, 1)
        self.assertEqual( len( board.unsolved_cells), NUM_CELLS-1)


        # Board with 4 unsolved that don't influence each other
        input_spec ='''
         0 4 6 1 2 7 9 5 8 
         7 8 5 6 9 4 1 3 0 
         2 1 9 3 8 5 4 6 7 
         4 0 2 5 3 1 8 7 9 
         9 3 1 2 7 8 6 0 5 
         8 5 7 9 4 6 2 1 3 
         5 9 8 4 1 3 7 2 6
         6 2 4 7 5 9 3 8 1
         1 7 3 8 6 2 5 9 4
        '''
        board = Board(input_spec)
        solutions = [ CellToSet( board[0][0] , 3 ),
                      CellToSet( board[1][8] , 2 ),
                      CellToSet( board[3][1] , 6 ),
                      CellToSet( board[4][7] , 4 )
                      ]
        # Make sure we got that right
        self.assertEqual (len(solutions), len(board.unsolved_cells))
        for (cell,value) in solutions :
            self.assertTrue (cell in board.unsolved_cells)


        # Solve each cell in turn and make sure they solve the right amt of others
        for cell_to_solve in solutions :
            num_solved = board.solve_cells( set([ cell_to_solve ]))
            self.assertEqual( num_solved, 1)
        self.assertTrue ( board.is_solved() )

            
            

        # Partially populated board
        input_spec ='''
         3 0 6 1 2 7 9 5 8 
         7 0 0 6 9 4 1 3 2 
         2 1 9 3 8 5 4 6 7 
         4 6 2 5 3 1 8 7 9 
         9 3 1 2 7 8 6 4 5 
         0 0 0 9 0 6 2 1 3 
         5 9 8 4 1 3 7 2 6
         6 2 4 7 5 9 3 8 1
         1 7 3 8 6 2 5 9 0
        '''

        board = Board(input_spec)

        # All the cells that will solve this
        solutions = [ CellToSet( board[0][1] , 4 ),
                      CellToSet( board[1][1] , 8 ),
                      CellToSet( board[1][2] , 5 ),
                      CellToSet( board[5][0] , 8 ),
                      CellToSet( board[5][1] , 5 ),
                      CellToSet( board[5][2] , 7 ),
                      CellToSet( board[5][4] , 4 ),
                      CellToSet( board[8][8] , 4 )
                      ]
        # Make sure we got that right
        self.assertEqual (len(solutions), len(board.unsolved_cells))
        for (cell,value) in solutions :
            self.assertTrue (cell in board.unsolved_cells)

            
        # Now solve it
        num_solved = board.solve_cells ( solutions )
        self.assertEqual ( num_solved, len( solutions) )
        self.assertTrue  ( board.is_solved() )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


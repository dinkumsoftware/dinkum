#!/usr/bin/env python3
###################################################################
import math
import copy
import re
                      
def sudoku_solver(puzzle):
    # return solution to puzzle
    # raise Exception on no or multiple solutions
    board = Board(arr=puzzle)

    solution=board.solve() # Return a board that solves board

    if solution :
        return solution.output() # Uniquely solved!
    else :
        raise Exception("Unsolvable")
        

class Board :
    ''' Holds the representation of of a sudoku board '''

    # class variables
    # A cell is represented by index into [] of all cells
    rcb_size = 9 # num items in row/col/blk
    num_cells = rcb_size * rcb_size
    blk_size = int(math.sqrt(rcb_size)) # Size of blocks e.g. 3x3 in 9x9 grid

    no_such_cell = -1  # Used to flag illegal cell

    unsolved_cell_value = 0 # Used to signal cell hasn't been set()
    num_values = rcb_size
    def all_cell_values(self) :
        ''' return [] of all legal cell values '''
        return list(range(1,self.rcb_size+1))

    # Symbolic definitions for x in _cells[cell#][x]
    _cell_indx_value = 0       # symbolic definition of _cells[x]
    _cell_indx_possibles = 1

    # Primarily for debugging and performance tuning

    # running count of boards made via a copy constructor
    board_construct_cnt = 0
    # How deeply recursed functions are
    solve_depth_cnt = 0
    set_depth_cnt   = 1

    # A speedup for solve()
    # It's recursively called many times with same input
    # So it stores all of it's results here, and checks it before recomputing
    # Keyed by board and value is None or Board
    solve_cache={}

    # Set this true to get print's during a solve()
    debugging = False

    def __init__(self, board=None, arr=None, cloning_board=False ) :
        ''' constructor.  Either a copy constructor (board) or initialized
        from [] of rows (arr).... but not both
        cloning_board only meaningful for copy constructor.  If True,
          the board_number is copied from board.  Normally it is
          incremented.
        On "arr" constructor, raises Exception if not a legal board
        '''

        if board and arr :
            raise Exception("Board() called with both board and arr set")
        if not board and not arr :
            # Neither is set.  Make an empty board
            # <todo> test this
            arr = [ [unsolved_cell_value] * self.rcb_size for i in range(self.rcb_size) ]

        # Bump the number construction count
        Board.board_construct_cnt += 1

        # Copy constructor ?
        if board :
            # Yes, make a copy of all of boards/our data structures
            self._unsolved_cells = copy.deepcopy(board._unsolved_cells)
            self._cells          = copy.deepcopy(board._cells         )

            self.board_num = board.board_num if cloning_board else Board.board_construct_cnt

        else:
            # We are generating new board from list of row-lists
            # Reset all class level stats
            Board.board_construct_cnt = 1 
            Board.solve_depth_cnt = 0
            Board.set_depth_cnt = 0
            Board.solve_cache={}

            # Set our board number (should be 1 as we init'ed it above)
            self.board_num  = Board.board_construct_cnt

            # We create empty data structs and have set() adjust them
            # List indexed by cell# containing (value, [] possible solution values for cell)
            # We init to unsolved and all possibles
            self._cells = [ [self.unsolved_cell_value, self.all_cell_values()]  for i in range(self.num_cells)]

            # We keep dictionary key:num_possiblites value: [] of cell indexes with that many possibilities
            # We init to single entry (num_legal_values) and set of all cellindexes in it
            self._unsolved_cells = { self.num_values:list(range(self.num_cells)) }

            # We do NOT want debugging output during this construction
            # It is specified by Board.debugging(class level).  If it's
            # set, well create instance level debugging=False and delete
            # it at the end
            if Board.debugging :
                self.debugging = False

            # Go thru and set each value, adjusting all data structures
            cell=0
            for row in arr :
                for value in row :
                    # Skip unknown values, all data bases init'ed for all unknown
                    if value != self.unsolved_cell_value:
                        # Confirm it is legal <todo> test this
                        if value not in self._cells[cell][self._cell_indx_possibles] :
                            raise Exception("Illegal initial cell value (%d) in cell $d" %(value, cell) )
                        # It's legal, set it
                        self.set(cell,value)
                    cell += 1

            # Clean up from debugging suppression
            if not self.debugging is Board.debugging :
                # We make a self.debugging.... remove it
                del self.debugging

            # Sanity check
            if cell != self.num_cells :
                raise Exception ("Too many cells in the arr:%d" % cell )


    def solve(self) :
        ''' Returns a board that solve us.
            Return None if unsolvable
           raise Exception on multiple solutions 
            We change our values in the process '''

        # Instrument
        Board.solve_depth_cnt += 1

        if self.debugging :
            print (self.debug_solve_label("Entered"), end="\n\n")
            print (self)
            print (self.debug_str(), end='\n\n')

        # We get called multiple times with the same board
        # Whatever we return, we store in class wise dictionary: self.solve_cache
        # keyed by board, value is what we return
        if self in self.solve_cache :
            # Return a copy of prior results
            # Have to make a copy so data in the cache isn't changed
            answer = self.solve_cache[self]
            if self.debugging :
                print (self.debug_solve_label("Cache Hit. Returning: "), "A solution" if answer else None, end="\n")

            Board.solve_depth_cnt -= 1
            return Board(answer, cloning_board=True) if answer else None

        solution = None # what we return

        # Try to fill in all the blanks in board
        for cell in self.next_unsolved_cell() :

            # This list of all possible legal values for cell
            possibles = self._cells[cell][self._cell_indx_possibles]

            if self.debugging :
                print ( self.debug_solve_label( "Trying cell:%d with %s" %(cell, str(possibles)) ))

            # Try all of those values for this cell
            for value in possibles :

                # Copy Constructor
                test_board = Board(self)

                if self.debugging :
                    print ( self.debug_solve_label("Constructed BdNum:%d to try cell:%d value:%d" %(test_board.board_num,
                                                                                                    cell,value) ) )

                # Set the cell and see how we do                                            
                (solved, no_solution) = test_board.set(cell, value, True)

                if solved :
                    if self.debugging :
                        print ( test_board.debug_solve_label("Returning SOLVED"))
                        print (test_board)

                    # record and make sure unique
                    solution = self.check_solution_for_uniqueness(solution, test_board)

                elif no_solution :
                    # Remove this cell/value as a possibility from board we are
                    # trying to solve, not test.board
                    num_possibilites_left = self.remove_a_possibility(cell, value) 
                    if num_possibilites_left == 0 :
                        # That made the whole board unsolvable
                        # <todo> move set_cache() into a function
                        self.solve_cache[self] = Board(solution, cloning_board=True) if solution else None  # Keep track of what we return
                        if self.debugging :
                            print ( self.debug_solve_label("UNsolvable Board. Returning:"), "A solution" if solution else None)
                        Board.solve_depth_cnt -= 1
                        return solution   # Look no further
                    # Try next value for this cell

                else :
                    # not solved, but solvable.... recurse
                    recursed_solution = test_board.solve()

                    if recursed_solution :
                        # record and/or make sure unique
                        if self.debugging :
                            print (test_board.debug_solve_label( "Received Recursed Solution"))
                        solution = self.check_solution_for_uniqueness(solution, recursed_solution)


        # Give them the answer
        # Keep track of what we return
        self.solve_cache[self] = Board(solution,cloning_board=True) if solution else None

        if self.debugging :
            print ( self.debug_solve_label("Returning:"), "A solution" if solution else None)
        Board.solve_depth_cnt -= 1
        return solution

    
    def check_solution_for_uniqueness(self, curr_solution, new_solution) :
        ''' Returns the new curr_solution or raises Exception on error.
        
            Return curr_solution if same as new_solution
            Returns new_solution if curr_solution is None
            Raises exception of new_solution and a non-None curr_solution  differ
        '''
        # First solution so far?
        if not curr_solution :
            return new_solution # No, new_solution is the first
        else:
            # We have Prior solution
            # Same as this new_solution ?
            if curr_solution != new_solution :
                # Multiple solutions, this is an error
                raise Exception( "Multiple Solutions")

            # they are both the same
            return curr_solution

        # Both if and else return.....
        raise Exception("SOFTWARE Error: Impossible Place")

    def next_unsolved_cell(self) :
        ''' Iterator that returns next cell to try to solve
        cell will be picked as one with fewest possibles.
        # <todo> speed enhancement order possible values list by most used value to least used value
        # <todo> have to do it else where
        '''

        # We are searching dict _unsolved_cells, keyed by num_possibilities whose
        # value is list of all cells with that many possible values
        for num_possibles in range (1, self.num_values+1) :
            if num_possibles in self._unsolved_cells :
                # give them the cells in list of possibilites
                for cell in self._unsolved_cells[num_possibles] :
                    yield cell

        # No unsolved cells
        return


    def set(self, cell, value, set_neighbors=False) :
        ''' Sets the contents of cell to value.
        Adjusts all the internal data bases.
        Returns (solved, not_solvable)
        if set_neighbors, Any neigbors of cell whose possibility cnt is
            reduced to 1 based on this cell being set are also set
        Exception if cell already set
        Exception if value out of bounds
        '''
        # Sanity checks
        if value not in self.all_cell_values() :
            raise Exception( "Illegal cell value: %d" % value)
        if self._cells[cell] in self.all_cell_values() :
            raise Exception( "Cell already set" )

        Board.set_depth_cnt += 1 # We keep track of call depth

        if self.debugging :
            print ( self.debug_set_label(cell, value, "Entered"))

        # Remember how many possibles cell originally had
        orig_num_possibles = len(self._cells[cell][self._cell_indx_possibles])

        # Set the cell itself
        self._cells[cell][self._cell_indx_value]     = value
        self._cells[cell][self._cell_indx_possibles] = []

        # Remove us from unsolved list
        self.remove_from_unsolved(cell, orig_num_possibles)

        # Adjust possibles on all the unset cells in our row/col/blk
        # Keep track of cells with only one possibility left
        cells_with_1_possible = []
        for neigh_cell in self.unsolved_neighbors(cell) :
            num_possibilities = self.remove_a_possibility (neigh_cell, value )
            if num_possibilities == 0 :
                # No possibilities left for neigh_cell
                # Not solvable
                if self.debugging :
                    print ( self.debug_set_label(cell, value, "Returning UNSOLVABLE"))
                Board.set_depth_cnt -= 1
                return (False, True)

            # Keep track of ones with only 1 choice left
            if num_possibilities == 1 :
                cells_with_1_possible.append(neigh_cell)

        if set_neighbors :
            # Go thru and set cells with only 1 choice left
            for c in cells_with_1_possible :
                # note: We have to recheck that they still only have 1 choice left
                # The set() we call recurses and may have "solved" on of these cells
                possibles = self._cells[c][self._cell_indx_possibles]
                if len(possibles) != 1 :
                    continue    # Someone else filled it in
                value = possibles[0] # then only one left

                # Set it
                (solved, unsolvable) = self.set(c, value, set_neighbors)
                if solved or unsolvable :
                    if self.debugging :
                        print ( self.debug_set_label(cell, value,"Returning "),
                                "UNSOLVABLE" if unsolvable else "",
                                "SOLVED" if solved else "")
                    Board.set_depth_cnt -= 1
                    return (solved, unsolvable)

        # Tell them if puzzle is solved
        if self.debugging and self.is_solved():
            print ( self.debug_set_label(cell, value, "Returning SOLVED"))

        Board.set_depth_cnt -= 1
        return (self.is_solved(), False )

    def is_solved(self) :
        ''' returns true if board is solved '''
        # any() returns True if has any key which is True
        return not any(self._unsolved_cells)


    def num_unsolved(self) :
        ''' Returns the number of unsolved cells '''
        # Go thru all the cells and pick those that are unsolved
        return len ([ True for cell in self._cells if cell[self._cell_indx_value] == self.unsolved_cell_value ])

    def remove_from_unsolved(self, cell, num_possibles) :
        ''' Takes cell out of _unsolved_cells at key:num_possibles
        and prunes any empty list resulting from removing cell.
        It is an error to try to remove a cell not in _unsolved[num_possibles]
        '''

        # Remove it
        if num_possibles :
            possible_list = self._unsolved_cells[num_possibles]
            possible_list.remove(cell)

            if not possible_list :
                # We just took out the last possibility
                # prune _unsolved_cells
                del self._unsolved_cells[num_possibles]


    def add_to_unsolved(self, cell, num_possibles) :
        ''' puts cell in _unsolved, a dict keyed by possibility num_possibles
        and value is list of cells with that number of possibles '''
        num_possibilities = len(self._cells[cell][self._cell_indx_possibles])

        # Sanity check
        if not num_possibles :
            raise Exception("Trying to add a cell with no possibles to _unsolved")
    
        # Seed with empty list if this first with this num_possibilities
        if not num_possibles in self._unsolved_cells :
            self._unsolved_cells[num_possibles] = []

        # Tack us on the end
        self._unsolved_cells[num_possibles].append(cell)


    def unsolved_neighbors(self, cell) :
        ''' Iterator of all cell numbers that are unsolved and in the
        row column or block as cell
        <todo> speedup... Don't return the same cell twice. '''


        # Get the position of cell
        row_num = cell // self.rcb_size
        col_num = cell % self.rcb_size

        # Get what block it's in
        blk_x = col_num // self.blk_size
        blk_y = row_num // self.blk_size

        # On same Row (not including ourself)
        row_start = row_num   * self.rcb_size
        row_end   = row_start + self.rcb_size
        # To left of us
        for c in range(row_start, cell) :
            if self._cells[c][self._cell_indx_value] == self.unsolved_cell_value :
                yield c
        # to the right of us
        for c in range(cell, row_end) :
            if self._cells[c][self._cell_indx_value] == self.unsolved_cell_value :
                yield c

        # On same column (not including ourself)
        col_start = col_num
        col_delta = self.rcb_size
        col_end   = self.num_cells
        # below us
        for c in range(col_start, cell, col_delta) :
            if self._cells[c][self._cell_indx_value] == self.unsolved_cell_value :
                yield c
        # Above us
        for c in range(cell, col_end, col_delta) :
            if self._cells[c][self._cell_indx_value] == self.unsolved_cell_value :
                yield c

        # In the block
        # Get index of upper-left cell and one past lower-right in the block
        blk_start = blk_x * self.blk_size +  blk_y * self.blk_size * self.rcb_size
        blk_end   = blk_start + self.blk_size * self.rcb_size

        # Scan each row in the block
        for row_start_c in range(blk_start, blk_end, self.rcb_size) :
            # and every cell in that row
            for bc in range(self.blk_size) :
                c = row_start_c + bc  # Cell in question

                # If isn't us and unsolved.....
                if c != cell and self._cells[c][self._cell_indx_value] == self.unsolved_cell_value :
                    yield c


    def remove_a_possibility(self, cell, value ) :
        ''' Removes value as a possible for cell.
        Returns the number of possibilities left after the removal
        Adjusts all data bases
        '''

        possibilities = self._cells[cell][self._cell_indx_possibles]
        orig_num_possibles = len(possibilities)
        curr_num_possibles = orig_num_possibles - 1 # len() after we remove one


        # Can we remove it?
        if value not in possibilities :
            # Nope, Tell them if it is insolvable because no choices left for this cell
            return orig_num_possibles
            
        # Remove value from _cells
        possibilities.remove(value)

        # move it's place in _unsolved_cells
        self.remove_from_unsolved(cell, orig_num_possibles  )   # out from it's current place
        if curr_num_possibles :
            self.add_to_unsolved( cell, curr_num_possibles)   # and into it's new place

        # Tell them # of choices left
        return curr_num_possibles


    def sanity_check(self):
        ''' Prints internal data and raises Exception
        if any internal data is "out of whack" '''

        try :
            unsolved = [] # list of unsolved cells
            solved   = [] # list of solved cells
            if len(self._cells) != self.num_cells :
                raise Exception("Length of _cells[] wrong")

            for (cell, (value, possibles)) in enumerate(self._cells) :
                if value == self.unsolved_cell_value :
                     unsolved.append(cell)
                     num_possibles = len(possibles)
                     # Unsolved, should be in the _unsolved dict
                     if cell not in self._unsolved_cells[num_possibles] :
                         raise Exception("unsolved cell %d: not in _unsolved_cells[%d]" % (cell, num_possibles))

                else :
                    # It is solved
                    solved.append(cell)
                    if possibles :
                        raise Exception("solved cell %d has possibles: %s" %(cell, str(possibles)))
                     
            if (len(solved) + len(unsolved)) != self.num_cells :
                raise Exception( "solved_cnt:%d  unsolved_cnt: %d, doesn't sum to %d" % (len(solved), len(unsolved), self.num_cells))

            # total unsolves in _unsolves
            num_in_unsolved = 0
            for num_possibles in self._unsolved_cells :
                num_in_unsolved += len( self._unsolved_cells[num_possibles])
            if num_in_unsolved != len(unsolved) :
                raise Exception( "Bad count (%d) in _unsolved.  Should be %d" % (num_in_unsolved, len(unsolved)))
        except:
            print ("Board.sanity_check()Board.sanity_check()Board.sanity_check()Board.sanity_check()Board.sanity_check()Board.sanity_check()")
            print (self._unsolved_cells)
            print (self.debug_str())
            raise

    def output(self) :
        ''' returns list of rows of the Board.
        Same format as __init__ argument '''
        arr = []
        for row in range(0, self.num_cells, self.rcb_size) :
            row = [ self._cells[row+col][self._cell_indx_value] for col in range(self.rcb_size) ]
            arr.append(row)
        return arr
                    

    def __str__(self) :
        ''' prints contents of the board. 
        <space> for unsolved cells
        '''

        str = "" # What we return
        for (cell, (value, possibles) ) in enumerate(self._cells) :
            if value != self.unsolved_cell_value :
                str += "%1d " % value
            else :
                # It is unsolved, just spaces
                str += "  "

            # End of row?
            if (cell % self.rcb_size) == self.rcb_size-1 :
                str += "\n"

        return str

    def debug_str(self) :
        ''' returns hash and contents of the board. 
        [possibles]  for unsolved cells
        each cell labeled with cell number
        '''
        ret_str = self.hash_str() # hash of the board
        ret_str += '\n\n'

        # 
        # Board Format
        # | 0:2                    |
        # |10: [1,2,3,4,5,6,7,8,9] |
        # |19: []
        after_cell_length = 20


        for (cell, (value, possibles) ) in enumerate(self._cells) :
            # Put on cell number
            ret_str += "%2d:" % cell

            if value != self.unsolved_cell_value :
                # Put in the solved value
                ret_str += "%1d" % value
                ret_str += " "*(after_cell_length-1)  # Space over, -1 for solved value 
            else :
                # It is unsolved, print list possibles
                possibles =  self._cells[cell][self._cell_indx_possibles].__str__()
                possibles = re.sub('[ ]', "", possibles) # Take out all space to use less width
                ret_str += " %s" % possibles    # [1,2,...]
                ret_str +=  " " * (after_cell_length-1-len(possibles)) # space over, -1 is for space before []

            # End of row?
            if (cell % self.rcb_size) == self.rcb_size-1 :
                ret_str += "\n"

        return ret_str

    def hash_str(self) :
        ''' Returns one line string (sans\n) with all the values in
        the board.  Unset cells printed as _'''

        ret_str = ''    # What we return

        # The has is all the digits strung together
        # With unknowns printed as '_'
        for (value, possibles) in self._cells :
            ret_str += str ( value)
        ret_str = re.sub('[0]', '_', ret_str)

        return ret_str

    def __hash__(self) :
        ''' returns a qausi unique integer representing the board.
        Primarily exists so can put Boards in sets.
        This is not very efficient, so if it gets used a long should
        make it faster.
        '''
        
        # hash_str is a string of concatanated values
        return hash( self.hash_str() )


    def __eq__(self, other_board) :
        ''' The == operator.
        We compare the the hash_str's which represent the contents of _cell[n].value for equality
        '''
        return self.hash_str() == other_board.hash_str()

    def __ne__(self, other_board) :
        ''' The != operator.
        We let __eq__() do the work
        '''
        return not self.__eq__(other_board)


    # These are functions returning strings to label debug print out
    def debug_solve_label(self, trailing_label = "") :
        ''' Used to label debug output from inside solve().
        Returns
            SOLVE(DepthCnt:<M>, BdNum:<n>) <trailing_label>
        where <m> is solve_depth_cnt and <n> is board_num. 
        It is intented to match solve_depth_cnt. '''

        return self.debug_solve_indent() + "SOLVE(DepthCnt:%d, BdNum:%d) %s" %(Board.solve_depth_cnt,
                                                   self.board_num,
                                                   trailing_label)
    def debug_solve_indent(self) :
        ''' return spaces proportional solve_depth_cnt '''
        spaces_per_depth = 3
        return " " * (spaces_per_depth * self.solve_depth_cnt)
        

    def debug_set_label(self, cell, value, trailing_label = "") :
        ''' Used to label debug output from inside set().
        Returns
            SET(DepthCnt:<M>, BdNum:<n>) cell:<cell> <-- <value> <trailing_label>
        where <m> is set_depth_cnt and <n> is board_num
        Indented debug_solve_indent() plust more proportional to set_depth_cnt '''

        return self.debug_set_indent() + "SET(DepthCnt:%d, BdNum:%d) cell:%d <--%d %s" %(Board.set_depth_cnt,
                                                                                         self.board_num,
                                                                                         cell, value,
                                                                                         trailing_label)

    def debug_set_indent(self) :
        '''Returns number of spaces to indent a debug_set_label().
        It is the indent for current set(), plus fixed amount,
        plus some proportional to set() depth '''
        always_indent = '     '
        spaces_per_set_call = 2

        return self.debug_solve_indent() +                      \
            always_indent +                                     \
            ' ' * (spaces_per_set_call * Board.set_depth_cnt) 


###################################################################
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

easy =[[0,5,0,3,0,0,4,1,0],
       [1,0,4,0,0,0,0,0,7],
       [0,2,0,4,7,0,0,6,0],
       [0,7,3,0,0,0,0,0,1],
       [2,0,1,0,0,0,5,0,3],
       [6,0,0,0,0,0,8,2,0],
       [0,1,0,0,5,9,0,8,0],
       [9,0,0,0,0,0,7,0,2],
       [0,8,2,0,0,3,0,4,0]]
easy_ans = None  # Don't have an answer


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

mindless        = [[0, 4, 6, 1, 2, 7, 9, 5, 8], 
                   [7, 0, 5, 6, 9, 4, 1, 3, 2], 
                   [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                   [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                   [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                   [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                   [5, 9, 8, 4, 1, 3, 7, 2, 6],
                   [6, 2, 4, 7, 5, 9, 3, 8, 1],
                   [1, 7, 3, 8, 6, 2, 5, 9, 4]]

mindless_ans    = [[3, 4, 6, 1, 2, 7, 9, 5, 8], 
                   [7, 8, 5, 6, 9, 4, 1, 3, 2], 
                   [2, 1, 9, 3, 8, 5, 4, 6, 7], 
                   [4, 6, 2, 5, 3, 1, 8, 7, 9], 
                   [9, 3, 1, 2, 7, 8, 6, 4, 5], 
                   [8, 5, 7, 9, 4, 6, 2, 1, 3], 
                   [5, 9, 8, 4, 1, 3, 7, 2, 6],
                   [6, 2, 4, 7, 5, 9, 3, 8, 1],
                   [1, 7, 3, 8, 6, 2, 5, 9, 4]]




def pretty_print(ans) :
    print ("[", ans[0])
    for row in ans[1:-1] :
        print (" ", row)
    print (" ", str(row)+ "]")


if __name__ == "__main__" :

    # Board.debugging = True

    todo      = [ mindless,     real_easy,     easy,     puzzle     ]
    solutions = [ mindless_ans, real_easy_ans, easy_ans, puzzle_ans ]

    for (arr,solution) in zip(todo[:3],solutions) :
        ans = sudoku_solver(arr)
        print ("##### Solved! ",end="")
        if solution :
            print ("Correctly" if ans==solution else "INCORRECTLY", end="")
        print ()


#!/usr/bin/env python3
#filename: dinkum_sudoku_solve_known.py
#path: sudoku/bin/
#repo: http://github.com/dinkumsoftware/dinkum.git
"""
This program attempts to solve one or more of the sudoku boards
in module dinkum.sudoku.test_data.test_puzzles whose puzzle names
are taken from the command line.  If no puzzles are listed on
the command line, all known puzzles are attempted.

It prints the solution(or insolution time) for the puzzles with
comparisons to prior solution times stored in:

    ~/.dinkum/sudoku/test_data/solved_times.pickled

Use --update to write the current solve times to that file

EXIT STATUS
    0  All puzzles solved
    1  Some kind of error on command line
    2  Some puzzle wasn't solved
    3  Some kind of exception thrown

"""

# 2019-12-?? tc Initial
# 2019-12-03 tc changed cmd line usage, added -v and -l
# 2019-12-04 tc Added timing printout
# 2019-12-07 tc Added --update and print delta times.
# 2019-12-09 tc support for sudoku.Stats
# 2019-12-10 tc added -n, --num_to_average
# 2019-12-19 tc check for negative --num_to_average

import sys, os, traceback, argparse
import textwrap    # dedent
import time

from dinkum.sudoku.test_data.test_puzzles import *
from dinkum.sudoku.labeled_printer        import labeled_board
from dinkum.sudoku.stats                  import *
from dinkum.utils.str_utils               import fixed_width_columns


# What main() can return
ret_val_good             = 0
ret_val_some_not_solved  = 1
ret_val_cmd_line_err     = 2
ret_val_exception_raised = 3



def main ():
    ''' See module docstring ...
    Attempts to solve all puzzle_names on the cmd line.
    If none listed, tries to solve them all.
    puzzles are found in test_data/test_puzzles
    
    --verbose Print solutions on solved and lots of info
              on unsolved.

    --list    list all the known puzzles

    --update  Write the solution statistics to disk

    --num_to_average How many times to try solve each puzzle
                     Currently Defaults to 100 to reduce
                     jitter in timing measurements

    Returns: 0  All puzzles solved
             1  Something wrong on cmd line
             2  Some puzzle was NOT solved.
    '''

    # Specify and parse the command line arguments
    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__)
    )
    
    parser.add_argument("-l", "--list",
                        help="List all the known puzzles and exit",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="Always print solutions.  Print debug info on unsolved",
                        action="store_true")

    parser.add_argument("-u", "--update",
                        help="Write solution times to disk file",
                        action="store_true")

    parser.add_argument("-n", "--num_to_average", type=int,
                        help="Number of times solve each puzzle for stat averages",
                        default=100 )

    # puzzles names, every non-option on the command line
    parser.add_argument('puzzle_names', metavar="puzzle_name",  # singular in -h, plural for [] generated
                        help="name(s) of puzzle in dinkum/sudoku/test_data/known_puzzles.py",
                        nargs='*')

    parser.parse_args()
    args = parser.parse_args()

    # A little sanity checking
    if args.num_to_average < 1 :
        # Alert them and set it to 1
        print ("NUM_TO_AVERAGE (%d) is less than 1.  Setting it to 1" % args.num_to_average,
               file=sys.stderr)
        args.num_to_average = 1

    # They just want a listing?
    if args.list :

        for sp in all_known_puzzles :
            # Example:empty        UNSOLVED No initial values, unsolvable
            print ("%-20s %-8s %s" % ( sp.name,
                                       "UNSOLVED" if sp not in all_known_solved_puzzles else "",
                                      sp.desc))
        # Life is good
        return ret_val_good
        

    # Set puzzle_names_to_solve
    # They specify any specific puzzles to solve?
    if not args.puzzle_names :
        # No, try them all
        puzzle_names_to_solve = all_known_puzzle_names
    else :
        # Yes, just try to solve the ones they specified
        puzzle_names_to_solve = args.puzzle_names

    # We have one or more puzzles to solve
    # Iterate thru them
    we_solved_all_puzzles = True # Forever the optimist
                                 # Set False on unsolved in loop

    # This is where text to print to user is stored.
    # One entry per puzzle.
    tokens_to_print = []          # value: list of strings to be printed in fixed width column
    verbose_lines_to_print = []   # value: string to print (maybe multi-line)

    # For comparing solve times to prior runs
    # A {} key:   puzzle_name
    #      value: sudoku.Stats
    prior_solve_stats_dict = read_prior_stats()

    # Attempt to solve
    for puzzle_name in puzzle_names_to_solve :

        # Grab the SolvedPuzzle from the dictionary
        try:
            sp = all_known_puzzle_names[puzzle_name]
        except KeyError :
            # No such name
            print ("%s: Unknown puzzle name: %s" % (sys.argv[0], puzzle_name),
                   file=sys.stderr)
            return ret_val_cmd_line_err

        # Try to solve it
        # Note: solve() may be attempted multiple times in order
        #       to average some timing results
        (is_solved, solve_results_board) = solve(sp.input_board, args.num_to_average)

        # keep track of whether any board wasn't solved
        we_solved_all_puzzles &= is_solved

        # build up line(s) to print for the user
        


        # we build the lines to be printed for the user
        #    tokens        [] of what is always printed to user about this puzzle
        #                  suitable for input to fixed_width_columns()
        #    verbose_lines string only printed to user with --verbose on cmd line
        # we pass in any prior statistics to allow change in any statistics to
        # be computed
        (tokens, verbose_lines) = build_printed_output( solve_results_board,
                                                        prior_solve_stats_dict.get(puzzle_name))

        # record lines for later printing
        tokens_to_print.append(tokens)
        verbose_lines_to_print.append(verbose_lines)

        if args.update :
            # we are writing solution statistics.  update ours
            # whole dict written before return
            prior_solve_stats_dict[puzzle_name] = solve_results_board.solve_stats

    # end of per puzzle solution loop

    # print all the info previously recorded
    # we print in fixed width columns.
    # fixed_width_columns(tokens_to_print) is a generator which puts the tokens
    # together and returns them as one line
    for (always, only_verbose) in zip(fixed_width_columns(tokens_to_print),
                                      verbose_lines_to_print) :
        print (always)

        if args.verbose :
            print (only_verbose)

    # if we had no statistics to compare
    # tell them how to create statistics file
    if len(prior_solve_stats_dict) == 0 :
        print ()
        print ("no prior statistics available from file:")
        print ("   %s" % prior_stats_filename() )
        print ("consider --update to write current statistics to that file."     )

    # write solution stats if reqd
    if args.update :
        write_prior_stats(prior_solve_stats_dict)
        print ()
        print ("solve statistics written to:"   )
        print ("   %s" % prior_stats_filename() )        

    # tell um how it went
    return ret_val_good if we_solved_all_puzzles else ret_val_some_not_solved



def solve(input_board, num_to_average) :
    ''' attempts to solve input_board.
    returns (is_solved, solve_results_board)

    solve_results_board will be either the solution if is_solved,
    otherwise it is the partial results

     some of the puzzles solve so fast there is tremendous jitter in the solution time
     in solve_results_board.solve_stats.  so we will solve it "num_to_average" times, compute the average,
     and adjust the appropriate statistics(s) in solve_results_board.solve_stats

    '''

    solution_total_time = 0.0
    for try_num in range(num_to_average) :
        # make a copy with same name
        # this is prevent returned board name of whatever.cp-100 instead of
        # just whatever
        board_to_solve      =  Board( input_board, name=input_board.name )

        solve_results_board =  board_to_solve.solve()
        solution_total_time += board_to_solve.solve_stats.solve_time_secs 

    # average 
    solve_time_secs = solution_total_time / num_to_average

    # insert it in appropriate stats
    # if it was solved, solve_results_board will be solved puzzle
    # if unsolved, solve_results_board will be None, and board_to_solve
    # will be partial results.
    # we set is_solved and solve_results_board appropriately
    if solve_results_board :
        is_solved = True  # solved!
    else :
        is_solved = False # sigh... not solved
        solve_results_board = board_to_solve # partial results

    # now update the solution to the average we computed above
    solve_results_board.solve_stats.solve_time_secs = solve_time_secs

    # is_solved indicates whether board was solved or not
    # The solution results (solved or not) are in solve_results_board
    return (is_solved, solve_results_board)


def build_printed_output( board, prior_stats=None) :
    '''We build the lines to be printed for the user, returning:
    (tokens, verbose_lines)
            tokens        [] of what is always printed to user about this puzzle
                          Each entry should be column of text to print,
                          suitable for input to fixed_width_columns()
            verbose_lines string (possible multi-line) which is only printed
                          with --verbose on cmd line

    verbose_lines content will change depending on whether the puzzle is solved
    or not.

    prior_stats is used to allow change in any statistic to be computed.
    '''
    # what we return
    tokens = []
    verbose_lines = ""

    # Make the code read a little easier
    stats     = board.solve_stats
    is_solved = board.is_solved()

    # If we can, compute the change in statistics from prior runs
    delta_stats = None
    if prior_stats :
        delta_stats = stats - prior_stats

    # tokens is a single line that is always printed, whether unsolved or not

    # Name and solution state
    tokens.append ( board.name )
    tokens.append ("solved" if is_solved else "UNSOLVED!" )

    # Solution Time
    secs_to_usec_multiplier = 1000.0 * 1000.0
    tokens.append ( str_stat_value(board, "solve_time_secs", secs_to_usec_multiplier, "usecs",
                                   prior_stats, want_percent_delta=True, value_format="%6.1f"))

    # Number of passes
    tokens.append ( str_stat_value(board, "num_solve_passes", None, "passes",
                                   prior_stats))

    # verbose_lines may or may not be printed
    # content varies depending on whether puzzle is solved or not

    # Always print a solution
    solution_label = "solution" if is_solved else "partial solution"
    verbose_lines += "%s:\n" % solution_label + str(board)
    verbose_lines += '\n' # Space it nicely
    
    if not board.is_solved() :
        verbose_lines += "Num unsolved: %d\n" % board.num_unsolved() 

        # Print all the stats
        stats = board.solve_stats
        for stat_name in vars(stats) :
            stat_value = getattr(stats, stat_name)
            stat_line = "%s: %s\n" % (stat_name, str(stat_value))
            verbose_lines += stat_line

        verbose_lines += '\n' # Space it nicely

        # print partial solution in a variety of formats
        # These fit on a page
        for l in labeled_board( board, want_cell_nums=False, want_num_possibles=False ) :
            verbose_lines += l + '\n'

        # This needs it's own page
        verbose_lines += '\f'
        for l in labeled_board( board, want_cell_nums=True, want_num_possibles=True ) :
            verbose_lines += l + '\n'

    return (tokens, verbose_lines)

               
def str_stat_value(board, stat_name, stat_multiplier=None, stat_units=None,
                   prior_stats=None, want_percent_delta=False,
                   value_format=None) :
    ''' Returns str representing a board.solve_stats.<stat_name> value
    and how much it changed since prior_stats. e.g.
        <stat_value> <stat_units>(<stat_delta>)                

    no prior_stats:
        <stat_value> <stat_units>(?)                           

    want_percent_delta
        <stat_value> <stat_units>(<delta_value>/<prior_value>%) 

    stat_value and delta_value are multiplied by stat_multiplier
    format_str is used to format stat_value and delta_value (if not percentage)
    '''
    assert isinstance(board, Board)

    stat_value = getattr(board.solve_stats, stat_name)

    delta_value = None # assume no prior stats
    if prior_stats is not None:
        prior_value = getattr(prior_stats, stat_name)
        delta_value = stat_value - prior_value

    # scale all
    if stat_multiplier :
        stat_value *= stat_multiplier
        
        if prior_value is not None:
            prior_value *= stat_multiplier
        if delta_value is not None:
            delta_value *= stat_multiplier

    # Produce the stat_value output
    stat_value_str = value_format % stat_value if value_format else str(stat_value)

    # produce delta_value output along with a label
    # convert to % if req'd
    if delta_value is None:
        delta_value_str = '?'
        delta_label     = ""
    else :
        # delta_value exists
        if want_percent_delta :
            # delta_value exists and they want it as a percent
            delta_value  = delta_value / prior_value
            delta_value *= 100.0

            delta_value_str = "%5.1f" % delta_value
            delta_label = '%'
        else :
            # want raw change
            delta_value_str = value_format % delta_value if value_format else str(delta_value)
            delta_label = ""


    # <stat_value> <stat_units>(<delta_value><delta_label>)
    ret_str = ""
    ret_str += stat_value_str + ' '                                 
    ret_str += stat_units  if stat_units  else ''  
    ret_str += '(' + delta_value_str + delta_label + ')'

    return ret_str

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

# full-license:
'''
Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {yyyy} {name of copyright owner}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.        
'''

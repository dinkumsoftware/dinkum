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
# 2019-12-04 tc Added timing printout

import sys, os, traceback, argparse
import textwrap    # dedent

from dinkum.sudoku.test_data.test_puzzles import *
from dinkum.sudoku.labeled_printer        import print_labeled_board

# history:
# 2019-12-01 tc Initial
# 2019-12-03 tc changed cmd line usage, added -v and -l
# 2019-12-07 tc Added --update and print delta times.

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

    --update  Write the solution times to disk

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

    # puzzles names, every non-option on the command line
    parser.add_argument('puzzle_names', metavar="puzzle_name",  # singular in -h, plural for [] generated
                        help="name(s) of puzzle in dinkum/sudoku/test_data/known_puzzles.py",
                        nargs='*')

    parser.parse_args()
    args = parser.parse_args()

    # They just want a listing?
    if args.list :

        for sp in all_known_puzzles :
            # Example:empty        UNSOLVED No initial values, unsolvable
            print ("%-20s %-8s %s" % ( sp.name,
                                       "UNSOLVED" if sp not in all_known_solved_puzzles else "",
                                      sp.desc))
        # Life is good
        return ret_val_good
        

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

    # For comparing solve times to prior runs
    # A {} key:   puzzle_name
    #      value: last solve time
    prior_solve_times_secs = read_prior_solve_times_secs()

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
        solved_board = sp.input_board.solve()

        # did we?
        if not solved_board :
            # nope, board is unsolved
            we_solved_all_puzzles = False # oh well
            solve_time_usec = sp.input_board.solve_time_secs * 1000.0 * 1000.0
            print ("%-20s: UNSOLVED! after %6.3f usecs" % (puzzle_name, solve_time_usec) )

            if args.verbose :
                # sp.input_board was  changed in-place
                partial_solution = sp.input_board

                # print partial soltion in a variety of formats
                # These fit on a page
                print (partial_solution)
                print_labeled_board( partial_solution, want_cell_nums=False, want_num_possibles=False )

                # This needs it's own
                print('\f')
                print_labeled_board( partial_solution, want_cell_nums=True, want_num_possibles=True )

        else:
            # Puzzle is solved
            # Some of the puzzles solve so fast there is tremendous jitter in the solution time
            # So we will solve it a bunch of times and compute the average
            num_solutions_to_average = 10000 # turns 1us into 10ms
            solution_total_time = 0.0
            for try_num in range(num_solutions_to_average) :
                sp.input_board.solve()
                solution_total_time += sp.input_board.solve_time_secs 
            solve_time_secs = solution_total_time / num_solutions_to_average


            # Compute speed improvement (hopefully)
            if puzzle_name in prior_solve_times_secs :
                # We have a recorded prior time
                prior_solve_time_secs = prior_solve_times_secs[puzzle_name]
                percent_better = (  (prior_solve_time_secs - solve_time_secs ) / prior_solve_time_secs ) * 100.0

                improvement = "Improvement: %0.1f%%" % percent_better
            else :
                # Nothing to compare it to.
                improvement = "Unknown improvement.  Consider --update"
            

            # Show them the solution info
            solve_time_usec = solve_time_secs * 1000.0 * 1000.0
            print ("%-20s:   Solved! after %6.3f usecs. %s" % (puzzle_name,
                                                               solve_time_usec,
                                                               improvement))
            if args.verbose :
                print (solved_board)

            if args.update :
                # We are writing solution times.  Update ours
                # Whole dict written before return
                prior_solve_times_secs[puzzle_name] = solve_time_secs ;
                

    # Write solution times if reqd
    if args.update :
        write_prior_solve_times_secs(prior_solve_times_secs)

    # Tell um how it went
    return ret_val_good if we_solved_all_puzzles else ret_val_some_not_solved

    # All went OK                   
    print ("%s:All puzzles solved!" % sys.argv[0])
    return ret_val_good


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

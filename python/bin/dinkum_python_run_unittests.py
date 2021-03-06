#!/usr/bin/env python3
#filename: dinkum_python_run_unittests.py
#path: dinkum/python/bin
#repo: http://github.com/dinkumsoftware/dinkum.git
"""
Locates and runs all python unittests in all python
modules in a specified filetree which defaults to the
current directory, but can be specified by --start_dir
switch.

**** How unittests are discovered....
Normally all unittests in or below the --start_dir are run.

Any directory which has a file named "NO_PYTHON_UNITTESTS"
causes that directory and all of it's subdirectories to
be skipped.  This can be disabled with the --ignore_NO_PYTHON_UNITTESTS
switch.

The unittests to run can be filtered by additional cmd line
arguments which may be a:
    python filename     *.py
    dir_path            Has a / in it or is . or is ..
                        dir_path must be somewhere in the
                        full pathname of .py file
    Test_Case           Test_*  
    test_function       test_*
    module_name         [p0.p1.p2.]module_name

Only unittests which match one or more of the above will be run.

**** PYTHONPATH/sys.path ......

Normally PYTHONPATH/sys.path should be set that all of the
discovered unittests import properly.  If this is NOT the case,
an --import_dir <directory>...<directory) will insert all the directories
into sys.path starting at index 1.

**** Per unittest vocabulary....

A Failure is something broken in trying to run the unittest.
This is probably some kind of import error.

An Error is the unittest being run did not pass, i.e
it had some kind of self.assert..() that wasn't True.

A Warning is python code that does NOT comply with
dinkumsoftware coding standards.
See dinkum.mas_unittest.coding_standards.
All Warnings can be suppressed with the --nowarnings switch.

EXIT STATUS
    0  No failures, errors or warnings
    1  Some unknown exception raised
    2  Some kind of command line problem
    3  Errors occurred 
    4  Failures occurred (but no Errors)
    5  Warnings occurred (but no Errors/Failures and NOT ignoring_warnings)

"""

# 2020-02-02 tc Initial
# 2020-02-04 tc moved from dinkum/bin to dinkum/python/bin
# 2020-02-06 tc Generally works.  Added --verbose, --failfast
#               --nowarnings
# 2020-02-08 tc move code into ./support.py
#               Added class EFW
# 2020-02-18 tc Added --start_dir and cmd line filters
# 2020-02-20 tc Added cmd line test selection
#               Fixed bug not reporting longest module path
#               moved python/bin/support.py ==> python/rut_support

import sys, os, traceback, argparse
import textwrap    # dedent
import unittest

import dinkum.project.dirs
from   dinkum.mas_unittest.utils            import * 
from   dinkum.mas_unittest.coding_standards import * 

from   dinkum.python.rut_support import *  # Our support code


def main ():
    ''' See module docstring ...
    '''

    # Specify and parse the command line arguments
    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__)
    )
    
    parser.add_argument("-l", "--list",
                        help="list (but don't run) all tests",
                        action="store_true")


    # Where to start looking for unittests
    # Func to insure argument is a directory
    def is_a_directory(dirname) :
        if os.path.isdir(dirname) :
            return dirname
        raise argparse.ArgumentTypeError(f"Not a directory: {dirname}")
            
    parser.add_argument( "-sd", "--start_dir",
                         type=is_a_directory,
                         help="Directory to start looking for unittests in. Default: current directory",
                         default=os.getcwd() )

    # Set verbosity of test run
    parser.add_argument("-v", "--verbose",
                        help="TestRunner verbosity. Bigger=>More Verbose",
                        type=int, choices=[0,1,2], default=1 )


    parser.add_argument("-ff", "--failfast",
                        help="Stop running unittests on first failure",
                        action="store_true")


    # Don't print WARNING! lines
    parser.add_argument("-nw", "--nowarnings",
                        help="suppress all warnings",
                        action="store_true")

    parser.add_argument("-ign", "--ignore_NO_PYTHON_UNITTESTS",
                        help="Process directories even though they have a file named NO_PYTHON_UNITTESTS in them",
                        action="store_true")

    parser.add_argument("-id", "--import_dir",
                        help="Path(s) to add to sys.path(PYTHONPATH)",
                        nargs='+',
                        type=is_a_directory )

    # Anything else on command is used to filter tests
    # file, dir, Test_*, test_*, mod
    # function to make sure argument is one of the above
    def fdTtm(arg) :
        if FilterTests.is_legal_filter_spec(arg) :
            return arg
        raise argparse.ArgumentTypeError(f"Not a legal specifier for FilterTest: {arg}")

    parser.add_argument("file_dir_Test_test_mod",
                        nargs="*",
                        help="tests to run: file -or- dir -or- Test_* -or- test_* -or- module",
                        type = fdTtm
                        )

    parser.parse_args()
    args = parser.parse_args()

    # The default directory where we start looking for test code
    top_level_dir = args.start_dir

    # Do we need to diddle sys.path ?
    if args.import_dir :
        # Yes, insert all the supplied directories
        # after sys.path[0] (script dir)
        # [::-1] We scan back to front to get them in

        # same order they were entered
        for import_path in args.import_dir[::-1] :
            sys.path.insert(1,import_path)
             
    # Build the unittests filter from cmd line arguments
    filter = FilterTests( args.file_dir_Test_test_mod )

    # Accumulate test_XXX() cases
    # Note: I don't use unittest.discover() because I want to filter which tests
    #       are included.
    # Here is general algorithm
    # os.walk all the files from --start_directory
    #    skip dirs with file: NO_PYTHON_UNITTESTS
    #    iterate over files
    #        skip non *.py files
    #        skip filenames filter by cmd line arguments
    #        test for importability, possibly skipping
    #        collect test_functions defined in the file
    #        skip tests based on cmd line arguments
    #        check tests for Warnings and print them (honors --nowarnings)
    #    remove duplicate tests (probably not needed, but doesn't hurt)
    #    print test names if --list
    #    otherwise, run the tests


    loader = unittest.TestLoader()  # What we use to accumulate unittests
    test_suite = unittest.TestSuite() # Where we build tests to run
    efw = EFW(args.failfast, args.nowarnings, args.list) # What we handle Failures/Errors/Warnings with

    # Walk the filetree at --start_directory looking for *.py files
    for dirpath, dirnames, filenames in os.walk(top_level_dir) :
        # skip dirs with file: NO_PYTHON_UNITTESTS
        # Is this directory excluded from having unittests?
        if "NO_PYTHON_UNITTESTS" in filenames and not args.ignore_NO_PYTHON_UNITTESTS :
            # Stop looking at this directory and any of it's subdirectories
            dirnames.clear()
            continue ;


        # Extract all unittests from *.py files in this directory
        for filename in filenames :

            # Get "dinkum.what.ever.modulename"
            # skip non *.py files
            pathname = os.path.join(dirpath, filename)       # /a/b/c/foo.py
            dotted_module_name = dotted_module_name_from_filename( pathname ) # a.b.c.foo
            if not dotted_module_name :
                # Not a python file (doesn't end in *.py)
                continue

            # skip filenames filter by cmd line arguments
            if filter.is_filtered_by_pathname( pathname ) :
                continue  # Yes, look at it no further
            
            # Make sure the module is findable for import --and--
            # the module will import sucessfully
            # Note: this may issue a variety of errors/warnings
            (should_skip, should_exit) = should_skip_module_for_importability_problems(dotted_module_name,
                                                                                       pathname, efw)
            if should_exit :
                # A Failure/Error/Warning, failfast, and Not list
                return should_exit 
            if should_skip :
                continue    # don't process this module
            
            # Look for warnings
            if not args.nowarnings :
                # Returns a list of tuples for each warning
                warnings = check_file_for_ut_coding_standard_violations(pathname)
                for (filename, msg) in warnings :
                    module_name = dotted_module_name_from_filename(filename)
                    efw.issue_warning(msg, module_name, filename)

                
            # Find the unittest code defined in this FILE
            # Normal unittest.loader.loadTestsFromXXX() load test_cases/functions from
            # the module AND any modules it imports.  This why the code as
            # originally written/and or unittest.discover() have duplicate tests in them.
            module_test_suite = loadTestsFromFile( pathname, limit_to_tests_in_file=True )

            # skip tests based on cmd line arguments
            # We previouly just checked based on pathname (as there were no unittests yet)
            # We do it again and filter based on pathname and TestCase/test_function name

            # Copy all the approved (non-filtered) tests into final test_suite
            test_suite = filter.filter_TestSuite(module_test_suite, test_suite)

    # os.walk is complete
    # We have iterated thru all the directories and files

    # Print all errors/failures/warning we have accumulated to date
    # unless we are just listing
    if not args.list :
        efw.print()

    # Remove duplicate tests
    # Note: this probably isn't necessary any more, but it doesn't hurt
    #       It used to be necessary where each file looked at generated
    #       tests defined in that file PLUS tests in any files it
    #       imported.  loadTestFromFile() fixed that.
    test_suite = prune_dups_from_TestSuite(test_suite)

    # They just want a listing?
    if args.list :
        for test in test_suite :
            print (test.id())
            
        # Give them a count
        print ("%d tests would be run." % test_suite.countTestCases() )

        # tell um how it went
        return os_ret_val_good


    # They want to run the tests, do so
    runner = unittest.TextTestRunner(verbosity=args.verbose,
                                     failfast=args.failfast)
    test_result = runner.run(test_suite)

    # From test_result, combine the Failures/Errors
    # (no Warnings as run() doesn't any) into
    # few (our Failures/Errors/Warning class
    efw.update_from_TestResult( test_result )

    # tell um how it went
    efw.announce_results()
    return efw.os_return_code()


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
        os._exit(os_ret_val_exception_raised)

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

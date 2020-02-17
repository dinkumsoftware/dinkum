#!/usr/bin/env python3
#filename: dinkum_python_run_unittests.py
#path: dinkum/python/bin
#repo: http://github.com/dinkumsoftware/dinkum.git
"""
Locates and runs all python unittests in all python
modules in a specified filetree.  Defaults to running
all dinkum python unittests.

All *.py files in the filetree are REQUIRED to have unittest except:
    Those in a *bin directory --or--
    Their enclosing directory has a file named "NO_PYTHON_UNITTESTS"


Per unittest vocabulary....

A Failure is something broken in trying to run the unittest.
This is probably some kind of import error.

An Error is the unittest being run did not pass, i.e
it had some kind of self.assert..() that wasn't True.

EXIT STATUS
    0  No failures, errors or warnings
    1  Some unknown exception raised
    2  Some kind of command line problem (handled by argparse)
    3  Failures occurred
    4  Errors occurred (but no Failures)
    5  Warnings occurred (but no Failures/Errors and NOT ignoring_warnings)
"""

# 2020-02-02 tc Initial
# 2020-02-04 tc moved from dinkum/bin to dinkum/python/bin
# 2020-02-06 tc Generally works.  Added --verbose, --failfast
#               --nowarnings
# 2020-02-08 tc move code into ./support.py
#               Added class EFW

import sys, os, traceback, argparse
import textwrap    # dedent
import unittest

import dinkum.project.dirs
from   dinkum.mas_unittest.utils import * 

from   support                   import * # From same dir as this script


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


    # Don't print WARNING! lines
    parser.add_argument("-n", "--no_warnings",
                        help="suppress all warnings",
                        action="store_true")

    # Set verbosity of test run
    parser.add_argument("-v", "--verbose",
                        help="TestRunner verbosity. Bigger=>More Verbose",
                        type=int, choices=[0,1,2], default=1 )

    parser.add_argument("-ign", "--ignore_NO_PYTHON_UNITTESTS",
                        help="Process directories even though they have a file named NO_PYTHON_UNITTESTS in them",
                        action="store_true")

    parser.add_argument("-ff", "--failfast",
                        help="Stop running unittests on first failure",
                        action="store_true")

    parser.parse_args()
    args = parser.parse_args()

    # The default directory where we start looking for test code
    top_level_dir = dinkum.project.dirs.top_level_dir()  # /what/ever/dinkum i.e. where "import dinkum" starts

    # Accumulate test_XXX() cases
    #    Note:I tried to use unittest.TestLoader.discover() but
    #         it was inserting duplicate copies of tests.
    #         Not sure why. So... I wrote my own. It had duplicate copies as well.... sigh
    #         I left my code in so could filter and check stuff.
    loader = unittest.TestLoader()  # What we use to accumulate unittests
    test_suite = unittest.TestSuite() # Where we build tests to run
    efw = EFW(args.failfast, args.no_warnings, args.list) # What we handle Failures/Errors/Warnings with

    # Walk the filetree at top_level_dir looking for *.py files
    for dirpath, dirnames, filenames in os.walk(top_level_dir) :
        # Is this directory excluded from having unittests?
        # i.e. is there a file named "NO_PYTHON_UNITTESTS" in it
        if "NO_PYTHON_UNITTESTS" in filenames and not args.ignore_NO_PYTHON_UNITTESTS :
            # Stop looking at this directory and any of it's subdirectories
            dirnames.clear()
            continue ;

        # Extract all unittests from *.py files in this directory
        for filename in filenames :

            # Get "dinkum.what.ever.modulename"
            pathname = os.path.join(dirpath, filename)       # /a/b/c/foo.py
            dotted_module_name = dotted_module_name_from_filename( pathname ) # a.b.c.foo
            if not dotted_module_name :
                # Not a python file (doesn't end in *.py)
                continue


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
            
            # Find the unittest code in the module
            # Note the returned TestSuite has tests listed multiple times
            module_test_suite = loader.loadTestsFromName( dotted_module_name )

            # Check for no unit tests for warning
            # <todo>

            # Add any surviving module tests to the final test_suite
            test_suite.addTest(module_test_suite)


    # Remove duplicate tests
    test_suite = prune_dups_from_TestSuite(test_suite)

    # They just want a listing?
    if args.list :
        for test in test_suite :
            print (test.id())
            
        # tell um how it went
        return os_ret_val_good


    # They want to run the tests
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

#!/usr/bin/env python3
# dinkum/mas_unittest/coding_standards
'''
Has standalone functions to examine *.py files
and unittest.TestCases derived from the *.py
file for violations of dinkum coding standard.

In particular:
    All *.py files:
       1) must have unittest code.
       2) must be executable
       Exceptions are: See dirs/files_with_unittest[]
          it's in *bin directory (it could be a script)
          __init__.py

       3) Must run unittests if invoked as a script

       4) TestCase name must match Test_<module name>
          e.g class Test_xxx(unittest.TestCase) must be in module xxx
          Exception: There are multiple TestCases in the file
'''

# These are error messages associated with each violation
# The are what's returned in the tuple from
# check_TestSuite/filename_for_ut_coding_standard_violations()

utcs_emsg_doesnt_exist            = "Does not exist (or unreadable)"
utcs_emsg_not_executable          = "Not executable"
utcs_emsg_not_a_python_file       = "Not a python file"
utcs_emsg_no_unittest_code        = "No unittest code"
utcs_emsg_testcase_misnamed       = "Bad TestCase name: %s"  # Requires % "Test_XXX"
utcs_emsg_unittest_code_not_run   = "Unittest code not executed"


# These are directories and files which do NOT have to have unittest code.
dirs_without_unittest  = [  "bin"         ]    # Must end with bin
files_without_unittest = [  "__init__.py" ]
def isnt_excepted(pathname, dirs, files) :
    ''' Returns True if pathname is NOT in dirs or files.
    i.e. pathname is NOT and exception

    filenames must match on one of files[]
    dirs must match the END of one of dirs[]
    '''
    if files and  os.path.basename(pathname) in files :
        return False  # Match, It's exempt. Return Not exempt

    if dirs :
        dirname = os.path.dirname(pathname)
        for exempt_dir in dirs :
            if dirname.endswith(exempt_dir) :
                return False  # Match, It's exempt. Return Not exempt

    # pathname is NOT exempt
    return True    # isnt_except

# 2020-02-20 tc Initial

from dinkum.mas_unittest.utils import *
from dinkum.python.modnames    import *
import subprocess

def check_TestSuite_for_ut_coding_standard_violations(test_suite) :
    ''' Checks all test_functions in test_suite (and their
    associated file) for unittest coding standard violations.
    (See module doc for a list).

    Returns a list of tuples, one for each violation.
    The tuple is:
        (filename, error_msg )
    '''

    # Iterate over each test and build an iterable
    # of all the files referenced, preserving the
    # test order
    iterable_of_filenames = OrderedDict() # key:filename, value:None

    for test in tests_from_TestSuite(test_suite) :
        # Extract the pathname
        (dotted_module_name, ignored, ignored) = parse_test_name(test)
        pathname = filename_from_dotted_module_name(dotted_module_name)

        # Stick it in the dictionary
        iterable_of_filenames[pathname] = None
        
    # Iterate over all those files and check each one
    violations = [] # Where we accumulate whoops
    for filename in iterable_of_filenames.keys() :
        violations += check_file_for_ut_coding_standard_violations(filename)
        
    # Tell um how they did
    return violations
        
def check_file_for_ut_coding_standard_violations(filename,
                                                 exception_dirs=dirs_without_unittest, 
                                                 exception_files=files_without_unittest) :
    ''' Checks all unittests filename for unittest coding
    standard violations.  (See module doc for a list).

    Returns a list of tuples, one for each violation.
    The tuple is:
        (filename, error_msg )

    The exceptions (files that it is permissable to NOT have unittests)
    are contained in following []s :
        exception_dirs     path(sans filename) that dirname(filename) ends with.
                           e.g  bin matches both bin/a.py and foo_bin/a.py
        exception_files    filenames (sans a path)
    Set to None to disallow exceptions.

    If no error, returns []
    '''

    filename = os.path.abspath(filename)
    violations = [] # What we normally return

    # Remember if file is exemption from a bunch of errors
    # based on it's name and/or location
    filename_not_exception =  isnt_excepted(filename,
                                            exception_dirs,
                                            exception_files)

    # Make sure it exists
    if not os.path.isfile(filename) :
        return [(filename, utcs_emsg_doesnt_exist) ]  # it doesn't
    # and is readable
    if not os.access(filename, os.R_OK) :
        return [(filename, utcs_emsg_doesnt_exist)] # it isn't

    # make sure it's a python file
    module_name = module_name_from_filename(filename)
    if module_name is None :
        return [(filename, utcs_emsg_not_a_python_file)]

    # and executable
    if not os.access(filename, os.X_OK) and filename_not_exception :
        # It's not, report and keep checking
        violations.append( (filename, utcs_emsg_not_executable) )

    # Get all the unit tests defined in filename
    # the 2nd arg does NOT include unittests from files that
    # are imported by filename (as opposed to being define
    # in filename)
    ts = loadTestsFromFile( filename, limit_to_tests_in_file=True)

    # Any test code?
    if ts.countTestCases() == 0 :
        if filename_not_exception :
            # Nope, add it to violations
            violations.append ((filename, utcs_emsg_no_unittest_code))

        # In either case, nothing more to test
        return violations # Nothing more to check
    

    # If there is only one TestCase, it must
    # be named Test_<module_name>.
    # It is not a violation to have multiple
    # TestCases defined, not named after the module
    # build set of TestCases
    set_of_testcases = set()
    for test in tests_from_TestSuite(ts) :
        (ignored, test_case, ignored) = parse_test_name(test)
        set_of_testcases.add(test_case)

    # If only one TestCase, check it's name
    if len(set_of_testcases) == 1 :
        expected_test_case = "Test_" + module_name
        (our_test_case,) = set_of_testcases  # Get the only member
        if  our_test_case != expected_test_case :
            # Wrong Name
            violations.append ((filename, utcs_emsg_testcase_misnamed % our_test_case))

    # Verify that the test code actually runs
    if not does_unittest_execute(filename) and filename_not_exception :
        violations.append( (filename, utcs_emsg_unittest_code_not_run) )


    # Tell um how we did
    return violations

def does_unittest_execute(filename) :
    ''' Returns True if executing filename results in the
    unitests in that file being run.

    i.e tests for presence of
        if __name__ == "__main__" :
        # Run the unittests
        unittest.main()
    '''

    # We run filename as a script, which should run unittest.main()
    # We pass a hopeful non-existance Test_Case:
    #      No_Such_Test_Case
    # If unit tests are running, we expect:
    #     return code of 1
    #     no stdout output
    #     stderr looks something like:

    #    E
    #    ======================================================================
    #    ERROR: No_Such_Test_Case (unittest.loader._FailedTest)
    #    ----------------------------------------------------------------------
    #    AttributeError: module '__main__' has no attribute 'No_Such_Test_Case'
    #    
    #    ----------------------------------------------------------------------
    #    Ran 1 test in 0.000s
    #    
    #    FAILED (errors=1)
    
    # If unittests aren't running, we expect
    #    return code of 0
    #    nothing on stderr and stdout

    
    # Cmd to execute
    bogus_test_case = "Test_No_Such_TestCase"
    cmd = ["python3", filename, bogus_test_case ]
    try :
        sp =subprocess.run ( cmd,
                             stdin=None,
                             stdout=subprocess.PIPE,   # capture
                             stderr=subprocess.PIPE,   # capture
                             universal_newlines=True,  # capture in text mode
                             timeout=10 )              # raise exeception if doesn't complete (infinite loop protection)
    except:

        # Any kind of error means unittests didn't run
        return False

    # Check return code
    if sp.returncode != 1 :
        return False # wrong return code
        
    # Shouldn't be any stdout
    if len(sp.stdout) :
        return False

    # Make sure the stderr output looks appropriate
    #    ERROR: No_Such_Test_Case (unittest.loader._FailedTest)
    exp_str = "ERROR: %s (unittest.loader._FailedTest)" % bogus_test_case
    if not exp_str in sp.stderr :
        return False
    exp_str = "unittest"
    if not exp_str in sp.stderr :
        return False

    #    AttributeError: module '__main__' has no attribute 'No_Such_Test_Case'
    exp_str = "has no attribute '%s'" % bogus_test_case
    if not exp_str in sp.stderr :
        return False

    #    Ran 1 test in 0.000s
    exp_str = "Ran 1 test"
    if not exp_str in sp.stderr :
        return False

    #    FAILED (errors=1)
    exp_str = "FAILED (errors=1)"
    if not exp_str in sp.stderr :
        return False

    # Unit tests ran
    return True

# Test code
import unittest
class Test_coding_standards(unittest.TestCase) :

    # This is dictionary of ./test_data/ *.py files and the error tuple they return
    # None ==> no error
    test_files = { "no_violations.py"     : None,
                   "no_such_file.py"      : utcs_emsg_doesnt_exist,
                   "non_python_file"      : utcs_emsg_not_a_python_file,
                   "not_executable.py"    : utcs_emsg_not_executable,
                   "no_unittest_code.py"  : utcs_emsg_no_unittest_code,
                   "testcase_misnamed.py" : utcs_emsg_testcase_misnamed % "Test_not_correctly_named",
                   "multiple_testcases.py": None,
                   "unittest_not_run.py"  : utcs_emsg_unittest_code_not_run,
    }

    # This is a dictionary of ./test_data/*.py files
    # that should normally be exempt (i.e lack of unittests isn't treated
    # as warnings).  The error message is what should be reported if
    # normal exeception_dir/files processing is bypassed.
    exception_test_files = { \
                       "__init__.py"          : utcs_emsg_no_unittest_code,
        "exceptions_bin/no_unittest_code.py"  : utcs_emsg_no_unittest_code,
        "exceptions_bin/not_executable.py"    : utcs_emsg_not_executable,
        "exceptions_bin/unittest_not_run.py"  : utcs_emsg_unittest_code_not_run,
    }
    



    @staticmethod
    def abspath_of_test_file(basename) :
        ''' basename into it's absolute path
        see test_files{} just above
        '''

        # Form the full pathname.  filename exists in ./test_data
        filename = os.path.join( os.path.dirname(__file__),
                                 "test_data",
                                 basename)
        filename = os.path.abspath (filename)

        return filename

    

    def test_check_file_for_ut_coding_standard_violations(self) :

        # We iterate thru test_files, running
        # check_file_for_ut_coding_standard_violations(test_file.key) and verify
        # results match test_file.value
        for (filename, expected_err_msg) in self.test_files.items() :

            # Form the full pathname.  filename exists in ./test_data
            filename = self.abspath_of_test_file(filename)

            # We get back a [] of tuples (filename, error_msg)
            results_list = check_file_for_ut_coding_standard_violations(filename)

            # Compare to expected_results

            # Any violations expected?
            if expected_err_msg is None :
                # no violations => empty list
                self.assertListEqual (results_list, [], msg=filename)
                continue # Done with this filename

            # Should only be a single violation
            self.assertEqual ( len(results_list), 1, msg=filename )

            # Make detected the right violation
            results_tuple = results_list[0]
            expected_result_tuple = (filename, expected_err_msg)
            self.assertTupleEqual( results_tuple, expected_result_tuple)


    def test_exceptions_check_file_for_ut_coding_standard_violations(self) :
        # We iterate thru exception_test_files.  None of the files
        # should produce a warning as they are in excepted dir or are
        # an excepted file.
        for filename in self.exception_test_files.keys() :

            # Form the full pathname.  filename exists in ./test_data
            filename = self.abspath_of_test_file(filename)

            # We get back a [] of tuples (filename, error_msg)
            results_list = check_file_for_ut_coding_standard_violations(filename)

            self.assertListEqual(results_list, [] )  # Should be no warnings

        # Do the same again, but bypass exception checking
        # All files should produce the error message in exception_test_files{}
        for (filename, expected_err_msg) in self.exception_test_files.items() :

            # Form the full pathname.  filename exists in ./test_data
            filename = self.abspath_of_test_file(filename)

            # We get back a [] of tuples (filename, error_msg)
            results_list = check_file_for_ut_coding_standard_violations(filename, None, [])

            if len(results_list) != 1 : print ("####") ; print (results_list)


            # Should only be a single violation
            self.assertEqual ( len(results_list), 1, msg=filename )

            # Make sure detected the right violation
            results_tuple = results_list[0]
            expected_result_tuple = (filename, expected_err_msg)
            self.assertTupleEqual( results_tuple, expected_result_tuple)



    def test_check_TestSuite_for_ut_coding_standard_violations(self) :
        # We build a TestSuite of all the files in class variable test_files
        loader = unittest.TestLoader()
        ts = unittest.TestSuite()
        for filename in self.test_files.keys() :
            file_ts = loadTestsFromFile( self.abspath_of_test_file(filename))
            if not file_ts is None :
                ts.addTest ( file_ts )
                                            
        # Process that TestSuite
        violations = check_TestSuite_for_ut_coding_standard_violations(ts)
    
        # Verify that every violation is listed in test_files
        # violations is list of tuples: (full_pathname, error_msg)
        for (pathname, emsg) in violations :
            # test_files only have basename, not full pathname
            basename = os.path.basename(pathname)
                       
            # Make sure returned diddle tuple is in test_files
            self.assertTrue ( basename in self.test_files, msg=basename)
            self.assertEqual ( emsg, self.test_files[basename] )
    


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

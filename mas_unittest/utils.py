#!/usr/bin/env python3
# dinkum/mas_unittest/utils.py
''' A number of support functions for python unittest
'''

# 2020-02-03 tc Initial
# 2020-02-16 tc bug fix in prune_dups_from_TestSuite
# 2020-02-21 tc Added loadTestsFromFile()


import unittest
from collections import OrderedDict

from dinkum.python.modnames import *


def tests_from_TestSuite(test_suite) :
    """ returns a [] of TestCases contained in test_suite
    """

    # All of the tests in test_suite
    returned_list = []

    # The iterator of TestSuite returns either a TestCase --or-- another TestSuite
    # Build a list of all the tests in test_suite
    # Note: There will be duplicates which we may toss later
    for test in test_suite:
        if unittest.suite._isnotsuite(test):
            # It's a TestCase
            returned_list.append(test)
        else:
            # It's a TestSuite, recurse
            returned_list += tests_from_TestSuite(test)

    # All done
    return returned_list

def loadTestsFromFile( filename, limit_to_tests_in_file=False) :
    ''' Retrieves unittests from filename and all other modules
    it imports.  Builds and returns a TestSuite.

    if limit_to_tests_in_file is True, only unittest tests defined
    in filename are returned. I.e. not any unittests from imported
    modules.

    Bad filenames (like non-existent) result in a return of None
    '''

    # Convert the filename to a dotted_module_name
    dotted_module_name = dotted_module_name_from_filename(filename)

    # Protect against bad filenames
    if not dotted_module_name :
        # Bad filename
        return None

    # Gather all the unittests
    loader = unittest.TestLoader()
    ts = loader.loadTestsFromName(dotted_module_name)

    # Need to prune it?
    if not limit_to_tests_in_file :
        return ts # nope, give um what we got

    # Limit returns TestSuite to ones from filename
    ret_ts = unittest.TestSuite()
    for test in tests_from_TestSuite(ts) :
        # Figure out the file associated with test
        (dotted_module_name, ignored, ignored) = parse_test_name(test)
        test_filename = filename_from_dotted_module_name(dotted_module_name)
        
        # Come from filename?
        if test_filename == filename :
            # Yes add the test in
            ret_ts.addTest(test)

    # Give them back the pruned TestSuite
    return ret_ts



def prune_dups_from_TestSuite(test_suite) :
    ''' Removes duplicate tests from test_suite
    and returns it as new TestSuite

    Preserves the order of the tests.
    '''

    # We build a dictionary with
    #    key:   (abs_filename, test_case, test_name)
    #    value: TestCase
    # We make it an OrderedDictionary to preserve the test order
    # We use this tuple as key in order to do this remove duplicate with a different import path.
    # i.e a.b.c.module and module could refer to same or different module
    ordered_dict = OrderedDict()
    for test in tests_from_TestSuite(test_suite) :
        
        # dig out names of the test
        (dotted_module_name, test_case, test_name) = parse_test_name(test)

        # Form the filename
        abs_filename=filename_from_dotted_module_name( dotted_module_name )

        # Remember it
        # If there are dups, remember one with longest dotted_module_name
        key = (abs_filename,test_case,test_name)
        if key not in ordered_dict :
            # First time we've seen it
            ordered_dict[key] = test
        else:
            # This is a duplicate, Use the one with longest dotted_module_name
            our_dmn_length = len(dotted_module_name)

            # Get length of current entry in the dictionary
            dict_test = ordered_dict[key]
            (dict_dotted_module_name, ignored, ignored) = parse_test_name(test)
            dict_dmn_length = len(dict_dotted_module_name)

            # Are we longer?
            if our_dmn_length > dict_dmn_length :
                # Yes, overwrite what's there
                ordered_dict[key] = test
            

    # Now reinsert the unique tests
    ret_ts = unittest.TestSuite()
    for test in ordered_dict.values() :
        ret_ts.addTest(test)

    return ret_ts


def is_TestLoader_error(test) :
    ''' Returns True if test is the special special class
    that indicates an error when loading unit tests.

    This is typically generated from a TestLoader.loadTestsFrom***()
    call.

    See TestLoader_error_msg().
    '''

    return type(test) is unittest.loader._FailedTest

def TestLoader_error_msg(loader, n=-1) :
    ''' Returns errors detected at load time by a
    TestLoader.loadTestsFrom***().

    Returns None if no nth error.  See is_TestLoader_error()

    The errors are stored in loader.errors[].
    n is used as an index.  There is one entry
    for every error detected in the life of loader.

    A typical full TestLoader.errors[n] is shown here:

        Failed to import test module: dinkum-install-from-git
        Traceback (most recent call last):
          File "/usr/lib/python3.6/unittest/loader.py", line 153, in loadTestsFromName
            module = __import__(module_name)
        ModuleNotFoundError: No module named 'dinkum-install-from-git'

    We pick off the first line up to the : and return that. i.e.
        Failed to import test module
    '''
    try:
        full_err_msg = loader.errors[n]

    except IndexError :
        # No errors len(errors_== 0  ... or wrong n
        # Either way:
        return None

    # Parse full_err_msg
    # Return everything up to but NOT including the first colon
    colon_indx = full_err_msg.find(":")

    # Note: colon_indx will be -1 of there is no colon.
    # This will result in returning the full error message.
    # I guess that is reasonable.  Other choices might be
    # returning None or "" 

    # Give them start of the error msg
    return full_err_msg[:colon_indx]
                  
    
def parse_test_name(test) :
    ''' Returns a tuple from test:
        (dotted_module_name, test_case, test_name)

    e.g. if the test is:
        a.b.c.mod.Test_mod.test_name
    Returns
        ("a.b.c.mod", "Test_mod", "test_name")

    All of this is retrieved from test.id()
    '''

    # The typical output of test.id() is:
    #     dinkum.sudoku.rcb.Test_rcb.test_bad_rcb_type
    #                    ^     ^          ^
    #                    |     |          |
    #                    |     |          |
    #                    |     |          L test_name
    #                    |     L TestCase 
    #                    L mod

    # Turn id() output into a []
    tokens= test.id().split(".")

    test_name          = tokens[ -1]
    test_case          = tokens[ -2]
    dotted_module_name = '.'.join( tokens[:-2])

    # Give um the answer
    return (dotted_module_name, test_case, test_name)


# Test code
class Test_utils(unittest.TestCase):
    # In all these tests, we use ourselves as input

    # Class variables
    our_module_name="dinkum.mas_unittest.utils"

    # List of tests in THIS file
    expected_tests_as_str= ["test_empty_testsuite (%s.Test_utils)"           % our_module_name,
                            "test_prune_dups_from_TestSuite (%s.Test_utils)" % our_module_name,
                            "test_is_TestLoader_error (%s.Test_utils)"       % our_module_name,
                            "test_TestLoader_err_msg (%s.Test_utils)"        % our_module_name,
                            "test_parse_test_name (%s.Test_utils)"           % our_module_name,
                            "test_loadTestsFromFile (%s.Test_utils)"         % our_module_name,
    ]
    expected_tests_as_str.sort()



    def test_empty_testsuite(self) :
        ts = unittest.TestSuite()
        self.assertEqual( [], tests_from_TestSuite(ts))

    def test_prune_dups_from_TestSuite(self) :
        # Load ourselves twice
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromName( Test_utils.our_module_name)
        dup_ts = unittest.TestSuite([ts,ts])

        # Confirm duplicated entries
        self.assertEqual( 2 * len( tests_from_TestSuite(ts    ) ),
                              len( tests_from_TestSuite(dup_ts) ),
                          )

        # Remove dups and verify length
        pruned_ts = prune_dups_from_TestSuite(dup_ts)
        self.assertEqual( len( tests_from_TestSuite(ts       ) ),
                          len( tests_from_TestSuite(pruned_ts) ),
                          )
        

    def test_is_TestLoader_error(self) :
        # Random class should fail
        self.assertFalse( is_TestLoader_error( [1,2,3,4] ) )

        # Proper class should detected
        self.assertTrue(  is_TestLoader_error( unittest.loader._FailedTest("methodname", None) ) )


    def test_TestLoader_err_msg(self) :
        loader = unittest.TestLoader()

        # Error Free
        self.assertIsNone ( TestLoader_error_msg(loader       ) )
        self.assertIsNone ( TestLoader_error_msg(loader, n=  0) )
        self.assertIsNone ( TestLoader_error_msg(loader, n= 12) )
        self.assertIsNone ( TestLoader_error_msg(loader, n=-12) )

        expected_error_msg = 'Failed to import test module'

        # Generate one error
        loader.loadTestsFromName( "no.such.module" )
        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader, n= 0 ) )
        self.assertIsNone (                     TestLoader_error_msg(loader, n= 1 ) )

        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader       ) )
        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader, n=-1 ) )
        self.assertIsNone (                     TestLoader_error_msg(loader, n=-2 ) )


        # Generate an additional error
        loader.loadTestsFromName( "no.such.module.really!" )
        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader, n= 0 ) )
        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader, n= 1 ) )
        self.assertIsNone (                     TestLoader_error_msg(loader, n= 2 ) )

        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader       ) )
        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader, n=-1 ) )
        self.assertEqual  ( expected_error_msg, TestLoader_error_msg(loader, n=-2 ) )
        self.assertIsNone (                     TestLoader_error_msg(loader, n=-3 ) )

        

    def test_parse_test_name(self) :

        # What we are looking for
        expected_dotted_module_name = "dinkum.mas_unittest.utils"
        expected_testcase    = "Test_utils"

        # The expected tests are the first token in
        # class variable Test_utils.expected_tests_as_str

        # Load ourself
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromModule(expected_dotted_module_name)

        # Examine all the tests
        for test in tests_from_TestSuite(ts) :
            (dotted_module_name, testcase, testname) = parse_test_name(test)

            # These are same for all tests
            self.assertEqual( dotted_module_name, expected_dotted_modulename)
            self.assertEqual( testcase,           expected_testcase   )

            # Make sure testname is at the beginning of some line in
            # Test_utils.expected_tests_as_str[]
            for l in Test_utils.expected_tests_as_str :
                if l.startswith( testname ) :
                    # we got a winner
                    break
            else :
                # testname didn't match anything
                self.assertTrue ( False, "testname doesn't match anything")


    def test_loadTestsFromFile(self) :
        ### Bogus filename should return None
        self.assertIsNone ( loadTestsFromFile("aint/no/such/file/my/friend"))

        ### Accumulate unittests from just this file
        our_ts = loadTestsFromFile(__file__, limit_to_tests_in_file=True)

        # Build a list of their names for comparision with expected results
        our_test_strs = [ test.__str__() for test in tests_from_TestSuite(our_ts) ]
        our_test_strs.sort()

        # Verify they are correct
        self.assertListEqual(our_test_strs, Test_utils.expected_tests_as_str)

        ### Verify pruning
        # We'll build the TestSuite again, not limiting it to just this file
        # We should get more tests
        all_ts=loadTestsFromFile(__file__, limit_to_tests_in_file=False)
        self.assertGreater( all_ts.countTestCases(),
                            our_ts.countTestCases())
        

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    

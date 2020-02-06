#!/usr/bin/env python3
# dinkum/mas_unittest/utils.py
''' A number of support functions for python unittest
'''

# 2020-02-03 tc Initial

import unittest
from collections import OrderedDict


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

def prune_dups_from_TestSuite(test_suite) :
    ''' Removes duplicate tests from test_suite
    and returns it as new TestSuite

    Preserves the order of the tests.
    '''

    # See https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
    test_list = tests_from_TestSuite(test_suite)
    ordered_dict = OrderedDict.fromkeys(test_list)

    # Insert them in new TestSuite and return it
    return unittest.TestSuite( ordered_dict )


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
        (dotted_pkg_names, module_name, test_case, test_name)

    e.g. if the test is:
        a.b.c.mod.Test_mod.test_name
    Returns
        ("a.b.c", "mod", "Test_mod", "test_name")

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

    test_name        = tokens[ -1]
    test_case        = tokens[ -2]
    module_name      = tokens[ -3]
    dotted_pkg_names = '.'.join( tokens[:-3])

    # Give um the answer
    return (dotted_pkg_names, module_name, test_case, test_name)


# Test code
class Test_utils(unittest.TestCase):
    # In all these tests, we use ourselves as input

    # Class variables
    our_module_name="dinkum.mas_unittest.utils"

    # List of tests in THIS file
    expected_tests_as_str= ["test_empty_testsuite (%s.Test_utils)"           % our_module_name,
                            "test_our_testsuite (%s.Test_utils)"             % our_module_name,
                            "test_prune_dups_from_TestSuite (%s.Test_utils)" % our_module_name,
                            "test_is_TestLoader_error (%s.Test_utils)"       % our_module_name,
                            "test_TestLoader_err_msg (%s.Test_utils)"        % our_module_name,
                            "test_parse_test_name (%s.Test_utils)"           % our_module_name,
    ]
    expected_tests_as_str.sort()



    def test_empty_testsuite(self) :
        ts = unittest.TestSuite()
        self.assertEqual( [], tests_from_TestSuite(ts))

    def test_our_testsuite(self) :
        # Put our tests in a TestSuite
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromName( Test_utils.our_module_name)

        # Build a list of tests id()'s
        test_strs = [ test.__str__() for test in tests_from_TestSuite(ts) ]

        test_strs.sort()
        self.assertEqual(test_strs, Test_utils.expected_tests_as_str)

    def test_prune_dups_from_TestSuite(self) :
        # Load ourselves twice
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromName( Test_utils.our_module_name)
        dup_ts = unittest.TestSuite([ts,ts])

        # Confirm duplicated entries
        self.assertEqual( 2 * len( Test_utils.expected_tests_as_str),
                              len( tests_from_TestSuite(dup_ts)    )
                          )

        # Remove dups and build list of id() strings
        pruned_ts = prune_dups_from_TestSuite(dup_ts)
        test_strs = [ test.__str__() for test in tests_from_TestSuite(pruned_ts) ]

        # Verify they are correct
        test_strs.sort()
        self.assertEqual(test_strs, Test_utils.expected_tests_as_str)
        

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
        expected_dotted_path = "dinkum.mas_unittest"
        expected_module      = "utils"
        expected_testcase    = "Test_utils"

        # The expected tests are the first token in
        # class variable Test_utils.expected_tests_as_str

        # Load ourself
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromModule(expected_dotted_path + "." + expected_module)

        # Examine all the tests
        for test in tests_from_TestSuite(ts) :
            (dotted_path, module, testcase, testname) = parse_test_name(test)

            # These are same for all tests
            self.assertEqual( dotted_path, expected_dotted_path)
            self.assertEqual( module     , expected_module     )
            self.assertEqual( testcase   , expected_testcase   )

            # Make sure testname is at the beginning of some line in
            # Test_utils.expected_tests_as_str[]
            for l in Test_utils.expected_tests_as_str :
                if l.startswith( testname ) :
                    # we got a winner
                    break
            else :
                # testname didn't match anything
                self.assertTrue ( False, "testname doesn't match anything")


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    

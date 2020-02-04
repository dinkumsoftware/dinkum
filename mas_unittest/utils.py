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
            # But remove duplicates as only the top invocation
            # in the recursion stack.
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


# Test code
class Test_utils(unittest.TestCase):
    # In all these tests, we use ourselves as input

    # Class variables
    our_module_name="dinkum.mas_unittest.utils"

    # List of tests in THIS file
    expected_tests_as_str= ["test_empty_testsuite (%s.Test_utils)"           % our_module_name,
                            "test_our_testsuite (%s.Test_utils)"             % our_module_name,
                            "test_prune_dups_from_TestSuite (%s.Test_utils)" % our_module_name,
    ]



    def test_empty_testsuite(self) :
        ts = unittest.TestSuite()
        self.assertEqual( [], tests_from_TestSuite(ts))

    def test_our_testsuite(self) :
        # Put our tests in a TestSuite
        loader = unittest.TestLoader()
        ts = loader.loadTestsFromName( Test_utils.our_module_name)

        # Build a list of tests id()'s
        test_strs = [ test.__str__() for test in tests_from_TestSuite(ts) ]

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
        self.assertEqual(test_strs, Test_utils.expected_tests_as_str)
        


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    

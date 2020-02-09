#!/usr/bin/env python3
# modules_with_test_failures.py
# python/test_data
#
# See README.txt in this directory
#
# Used ONLY to test ../bin/dinkum_python_run_unittest.py

# Has 5 unittests.  2 of them fail

# 2020-02-06 tc Initial

import unittest
class Test_module_with_test_failures(unittest.TestCase) :
    def test_1(self) :
        self.assertTrue(True)

    def test_2(self) :
        self.assertTrue(False)    # Fail

    def test_3(self) :
        self.assertTrue(True)

    def test_4(self) :
        self.assertTrue(False)    # Fail

    def test_5(self) :
        self.assertTrue(True)

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

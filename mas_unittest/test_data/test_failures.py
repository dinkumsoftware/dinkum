#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/test_failures.py
'''
This is test program input to unittests.

It has test code that fails, i.e. self.asserts.xxx() fails
'''

def foo() :
    pass

import unittest
class Test_test_failures(unittest.TestCase) :
    def test_first_thing(self) :
        pass

    def test_second_thing(self) :
        self.assertTrue(True)

    def test_third_thing(self) :
        self.assertTrue(False)    # Will fail


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/testcase_misnamed.py
'''
This is test program input to unittests for coding_standards.py.

The unittest:TestCase has wrong name
'''

def foo() :
    pass

import unittest
class Test_not_correctly_named(unittest.TestCase) :
    def test_first_thing(self) :
        pass


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


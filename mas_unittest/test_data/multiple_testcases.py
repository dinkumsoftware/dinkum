#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/multiple_testcases.py
'''
This is test program input to unittests for coding_standards.py.
It has several TestCase's defined.

It has NO violations of the coding standard.
'''

def foo() :
    pass

import unittest

class Test_1 (unittest.TestCase) :
    def test_1_first_thing(self) :
        pass

class Test_2 (unittest.TestCase) :
    def test_2_first_thing(self) :
        pass
    


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


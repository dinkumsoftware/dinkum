#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/no_violations.py
'''
This is test program input to unittests for coding_standards.py.

It has NO violations of the coding standard.
'''

def foo() :
    pass

import unittest
class Test_no_violations(unittest.TestCase) :
    def test_first_thing(self) :
        pass


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


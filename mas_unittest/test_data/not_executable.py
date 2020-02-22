#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/not_executable.py
'''
This is test program input to unittests for coding_standards.py.

The file is NOT executable
'''

def foo() :
    pass

import unittest
class Test_not_executable(unittest.TestCase) :
    def test_first_thing(self) :
        pass


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


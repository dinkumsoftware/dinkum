#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/unittest_not_run.py
'''
This is test program input to unittests for coding_standards.py.

It should produce "Unittest code not executed"
'''

def foo() :
    pass

import unittest
class Test_unittest_not_run(unittest.TestCase) :
    def test_first_thing(self) :
        pass


# Omit the following for force unittest to NOT be run
# if __name__ == "__main__" :
#    # Run the unittests
#    unittest.main()
    


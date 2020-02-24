#!/usr/bin/env python3
# dinkum_mas_unittest/test_data/import_errors.py
'''
This is test program input to unittests.

It is NOT importable
'''

import no.such.module.my.friend


def foo() :
    pass

import unittest
class Test_import_errors(unittest.TestCase) :
    def test_first_thing(self) :
        pass


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
    


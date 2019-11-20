#!/usr/bin/env python3
# dinkum/utils/str_utils.py
''' A collection of stand-alone functions to manipulate
strings
'''
# 2019-11-20 tc refactored from dinkum_print_sudoku_worksheet.py
#               changed default num_substr_chars to len(substr)
#               changed out of range behavior
#               fixed bugs

def replace_substr_at(s, substr, offset_into_s, num_substr_chars=None) :
    ''' Replaces num_substr_chars at s[offset_into_s] with
    first num_substr_chars in substr and returns the new s

    if offset_into_s is negative, counts from end of s, a la 
    slice (:).  i.e. -1 refers to last char of s

    If num_substr_chars is NOT supplied, all of substr will be
    used as the replacement.

    Any combination of arguments that reference chars out of
    s or substr are silently clipped to only reference chars in s
    and substr

    The length of s will never change.  The number of
    chars extracted from substr always equal the number
    of chars in s that are returned
    '''
    original_s_length = len(s) 

    # Handle num_substr_chars unspecified
    if not num_substr_chars :
        num_substr_chars = len(substr)

    # Handle offsets from end of string
    if offset_into_s < 0 :
        offset_into_s = len(s) + offset_into_s
        # offset_into_s could still be <0
        # this is handled below

    # clip to make sure offset_in_s and num_substr_chars
    # refer to chars in both s and substr, i.e. not off the end
    # See test code at end of file for examples
    
    # Bless offset_into_s
    if offset_into_s >= len(s) :
        # It's off the end of s
        return s # nothing to substitute

    if offset_into_s < 0 :
        # Can't insert before start of s
        # Throw away the chars inserted before start of s
        num_substr_chars_to_toss = -offset_into_s
        substr = substr[ num_substr_chars_to_toss : ]
        offset_into_s = 0
        num_substr_chars -= num_substr_chars_to_toss
        
                         
    # can't replace what isn't there
    if num_substr_chars > len(substr) :
        num_substr_chars = len(substr)
    if num_substr_chars <= 0 :
        return s # we aren't doing any replacements

    # discard replacements past the end of s
    if offset_into_s + num_substr_chars > len(s):
        num_substr_chars = len(s) - offset_into_s

    # do the replacement
    # example: s:abcdefg substr:123 offset_into_s:3 num_substr_chars:1
    leading_s   = s[:offset_into_s]                   # abc
    replacement = substr[:num_substr_chars]           # 1
    trailing_s  = s[offset_into_s+num_substr_chars:]  # efg

    s = leading_s + replacement + trailing_s          #abc1efg

    assert len(s) == original_s_length
    return s 


# test code
import unittest

class TestStrUtils(unittest.TestCase):
    def test_replace_substr_at(self) :
        # vanilla change
        self.assertEqual( replace_substr_at( '12345', 'x', 2, 1 ),
                          '12x45')

        # confirm num_substr_chars reverts to len(substr)
        self.assertEqual( replace_substr_at( '1234', 'x', 1 ),
                          '1x34')

        # muliple chars
        self.assertEqual( replace_substr_at( '1234567', 'abcdefg', 1, 5),
                          '1abcde7')

        # from the end
        self.assertEqual( replace_substr_at( '1234567', 'ab', -3 ),
                          '1234ab7')

        # pathalogical cases
        # empty s
        self.assertEqual( replace_substr_at( '', 'ab', 0 ),
                          '')
        
        self.assertEqual( replace_substr_at( '', 'ab', -18 ),
                          '')

        # empty substr
        self.assertEqual( replace_substr_at( '1234567', '', 3, 4 ),
                          '1234567')

        # range out of s
        self.assertEqual( replace_substr_at( '1234567', 'xyz', 20, 3 ),
                          '1234567')
        self.assertEqual( replace_substr_at( '1234567', 'xyz', -17, 1 ),
                          '1234567')
        
        # range out of substr
        self.assertEqual( replace_substr_at( '1234567', 'abc', 0, 15 ),
                          'abc4567')
        self.assertEqual( replace_substr_at( '1234567', 'abc', 0, -1 ),
                          '1234567')
        
        # partial ranges
        self.assertEqual( replace_substr_at( '1234567', 'abc',  2, 8 ),
                          '12abc67')
        self.assertEqual( replace_substr_at( '1234567', 'abc', -2, 4 ),
                          '12345ab')
        self.assertEqual( replace_substr_at( '1234567', 'abc', -8, 2 ),
                          'b234567')
        


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

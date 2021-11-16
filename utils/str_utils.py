#!/usr/bin/env python3
# dinkum/utils/str_utils.py
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/
''' A collection of stand-alone functions to manipulate
strings
'''
# 2019-11-20 tc refactored from dinkum_print_sudoku_worksheet.py
#               changed default num_substr_chars to len(substr)
#               changed out of range behavior
#               fixed bugs
# 2019-12-09 tc Added fixed_width_columns()
# 2020-02-24 tc Bug fix, fixed_width_columns()
#                 Protect against None tokens, treat as ""
#               Made comply with dinkum_python_run_unittests
# 2021-10-19 tc Added FixedColWidths

import sys
import io

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

def fixed_width_columns(lines, column_padding=' ',
                        right_justified=False ) :
    '''
    Typically used to print fixed width columns of
    text.

    It is a generator which returns a string for
    each lines[x] with fixed width columns.  Each
    column is separated by column_padding.

    right_justified controls whether the output
    is left or right justified in the column.

    Each lines[x] should be a list of strings,
    with one entry for each column desired.

    By examining all the lines[] it determines the
    smallest column width that will accomodate all
    the data.

    An example might be clearer:
        lines[0] = [ 'a'   , 'xxxx', 'what ever' ]
        lines[1] = [ 'abbb', 'y',    'what'      ]

        fixed_width_columns(lines, "    ") will return
        (on successive iterations)
           a       xxxx    what ever
           abbb    y       what

    '''
    # Don't consider any word that is all whitespace, empty, or None
    for indx, words in enumerate(lines) :
        if words :
            words = [word.rstrip().lstrip() for word in words         ]
            words = [word                   for word in words if word ]
            lines[indx] = words

    # compute the longest word in each column
    # In order to size column_widths, we need
    # to know the maximum number of words in
    # in all lines
    max_num_columns = 0
    for list_of_words in lines :
        max_num_columns = max(max_num_columns,
                              len(list_of_words))
    column_widths = [0] * max_num_columns
    
    for list_of_words in lines :
        for (indx,word) in enumerate(list_of_words) :
            # Protect against None strings
            if word is None :
                word = ""
            column_widths[indx] = max(column_widths[indx],
                                      len(word))

    # Now go thru and build up each line and yield it to them

    # Which way to shove the text in the column
    sign_of_format_width = 1 if right_justified else -1

    for line in lines :
        returned_line = ""
        for (indx,word) in enumerate(line) :
            if word is None :    # Protect against entries of None 
                word = ''
            returned_line += "%*s" %                                               \
                             ( sign_of_format_width * column_widths[indx], word) 
            returned_line += column_padding

        # Give them the line, sans the last column_padding we just added
        yield returned_line.rstrip()

class FixedColWidths() :
    ''' Used to print lines of text in fixed width columns.

    Typical usage:
        fwc=FixedColWidths(file=sys.stdout, column_padding=' ', right_justified=False )
            fwc.print("a b c e" , x, y, z, sep='3')
                     .....
            fwc.print("dd ee ff gg", w, end='' )

            fwc.really_print(file=sys.stdout)

    works just like print() excepts prints all in fixed column
    widths.  It can't know all the column widths until it's seen all
    the lines.

    In the initial calls, fwc.print() prints to an internal buffer.
    when fwc.really_print() is called, the buffer is printed to
    the last file= it print saw, in either the constructor or in
    an fwc.print().

    '''
    def __init__(self, **kwargs) :
        self.file            = kwargs.pop("file"           , sys.stdout)
        self.column_padding  = kwargs.pop("column_padding" , ' '       )
        self.right_justified = kwargs.pop("right_justified", False     )

        if kwargs:
            raise TypeError('Unknown keyword arguments: ' + str(list(kwargs.keys())))
        
        self.buffer = None  # Where we buffer printed strings

    def print(self, *args, **kwargs) :
        ''' passes all it's arguments along to the real print(),
        but captures the real print's output to an internal buffer.
        call really_print() to actually print the internal buffer.
        '''
        # We have a place to print to?
        if self.buffer is None :
            # nope, make one
            self.buffer = io.StringIO()

        # Remove any file= arg and Remember where they
        # really want to print it
        their_file_arg = kwargs.pop("file", None)
        if their_file_arg is not None :
            self.file = their_file_arg

        # print to it
        print (*args, file=self.buffer, **kwargs)

    def really_print(self) :
        ''' converts self.buffer to fixed width columns
        and prints() it to self.file
        '''

        # Convert buffer to [] of [] of words
        list_of_list_of_words = []
        for l in self.buffer.getvalue().split('\n') :
            if l :
                list_of_list_of_words.append( l.split() )

        for l_to_print in fixed_width_columns(list_of_list_of_words,
                                              column_padding=self.column_padding,
                                              right_justified=self.right_justified) :
            print(l_to_print, file=self.file)

        # Start afresh on next self.print()
        self.file=None
        self.buffer=None

# test code
import unittest

class Test_str_utils(unittest.TestCase):
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
        
    def test_fixed_width_columns(self) :
        # Do the example in it's _doc first
        lines=[None] * 2
        lines[0] = [ 'a'   , 'xxxx', 'what ever' ]
        lines[1] = [ 'abbb', 'y',    'what'      ]

        expect=[None] * 2
        expect[0] = "a       xxxx    what ever"
        expect[1] = "abbb    y       what"

        for (i,l) in enumerate(fixed_width_columns(lines, "    ")) :
            self.assertEqual(l, expect[i] )


        # no padding
        lines=[None] * 2
        lines[0] = [ 'a', 'b', 'c' ]
        lines[1] = [ '1', '2', '3' ]

        expect=[None] * 2
        expect[0] = "abc"
        expect[1] = "123"
        
        for (i,l) in enumerate(fixed_width_columns(lines, column_padding='')) :
            self.assertEqual(l, expect[i] )


        # Right justify
        lines=[None] * 2
        lines[0] = [ 'a'   , 'xxxx', 'what ever' ]
        lines[1] = [ 'abbb', 'y',    'what'      ]

        expect=[None] * 2
        #                12345678    12345678         12345678
        expect[0] = "   a        xxxx        what ever"
        expect[1] = "abbb           y             what"

        for (i,l) in enumerate(fixed_width_columns(lines, " "*8, True)) :
            self.assertEqual(l, expect[i] )

        # line[] has a non-list element
        lines=[None] * 3  
        lines[0] = [ 'a', 'b', 'c' ]
        lines[1] = [ '1', '2', '3' ]
        lines[2] = None

        with self.assertRaises(TypeError) :
            for (i,l) in enumerate(fixed_width_columns(lines)) :
                pass

    # Mismatched number of columns
        lines=[None] * 3  
        lines[0] = [ 'a', 'b', 'c' ]
        lines[1] = [ '1', '2', '3' ]
        lines[2] = [ 'x', 'y'      ]

        expect=[None] * 3
        expect[0] = "a b c"
        expect[1] = "1 2 3"
        expect[2] = "x y"

        for (i,l) in enumerate(fixed_width_columns(lines)) :
            self.assertEqual(l, expect[i] )

        
    def test_fcw_constructs(self) :
        ''' FixedColWidths constructs ok '''

        FixedColWidths()    # Should work

        fcw=FixedColWidths(column_padding=12*' ',
                           file="foo",
                           right_justified=False)
        self.assertEqual( 12*' ',fcw.column_padding )
        self.assertEqual( "foo", fcw.file           )
        self.assertEqual( False, fcw.right_justified) 

        # Make sure it picks up bad arguments
        self.assertRaises(TypeError, fcw, [], {"unknown":69})

    def test_fcw_prints_a_line(self) :
        ''' check that can print() a line '''

        # Default col = 1 space
        tst_in =  'abcd       efg'
        desired='abcd efg\n'
        fcw=FixedColWidths(right_justified=True)
        output_file=io.StringIO()

        fcw.print(tst_in, file=output_file)
        fcw.really_print()

        output=output_file.getvalue()
        self.assertEqual(output, desired)


        # col = 3 space
        desired='abcd   efg\n'
        fcw=FixedColWidths(column_padding=3*' ')
        output_file=io.StringIO()

        fcw.print(tst_in, file=output_file)
        fcw.really_print()

        output=output_file.getvalue()
        self.assertEqual(output, desired)


    def test_fcw_prints_a_line(self) :
        ''' prints multiple lines '''


        tst_in=[ 'abcd       efg    h    ijk    lmnop',
                 '12 45        3      18    250000000',
                 '3333 22 4       7 2',
        ]

        desired= 'abcd efg h ijk lmnop\n' + \
                 '12   45  3 18  250000000\n'   + \
                 '3333 22  4 7   2\n'

        fcw=FixedColWidths()
        output_file=io.StringIO()

        for l in tst_in :
            fcw.print(l, file=output_file)
        fcw.really_print()

        output=output_file.getvalue()
        self.assertEqual(output, desired)


        desired= 'abcd efg h ijk     lmnop\n' + \
                 '  12  45 3  18 250000000\n' + \
                 '3333  22 4   7         2\n'

        fcw=FixedColWidths(right_justified=True)
        output_file=io.StringIO()

        for l in tst_in :
            fcw.print(l, file=output_file)
        fcw.really_print()

        output=output_file.getvalue()
        self.assertEqual(output, desired)


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()

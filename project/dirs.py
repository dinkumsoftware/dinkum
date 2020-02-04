#!/usr/bin/env python3
# dinkum/project/dirs.py
''' Has functions related to directory locations in a dinkum project
'''

def top_level_dirname() :
    ''' Returns the directory name where all imports start
    in projects.
    '''
    return 'dinkum'

def top_level_dir() :
    ''' Returns the absolute pathname of the python top level
    directory of dinkum projects.

    i.e. returns the directory associated with dinkum package
    in an "import dinkum.what.ever"

    The directory is determined by scanning PYTHONPATH and returning
    the first entry that has a dinkum subdirectory.

    Returns None if it can't find one
    '''

    # Iterate thru PYTHONPATH (i.e. part of sys.path)
    # Skip first entry as it is the directory of the script(us)
    for dir in sys.path[1:] :
        # If it has a subdirectory named "dinkum" we are done
        top_level_dir = os.path.abspath( os.path.join(dir,
                                                      top_level_dirname()))

        # Is it an existing directory?
        if os.path.isdir( top_level_dir) :
            return top_level_dir # yep, we are all done

    # Couldn't find a top level dir
    return None

# Test code
import unittest
import os.path
import sys

class Test_dirs(unittest.TestCase):

    def test_top_level_dir(self) :

        # This counts on following directory structure
        # dinkum/        # top level dir
        #   project/
        #     dirs.py    # our file
        # Compute the top_level_dir relative to our location
        our_dir = os.path.abspath(__file__)   # .../dinkum/project/dirs.py
        our_dir = os.path.dirname(our_dir)    # .../dinkum/project

        top_dir = os.path.abspath( os.path.join( our_dir, ".."))

        self.assertEqual( top_dir, top_level_dir() )


if __name__ == "__main__" :
    # Run the unittests
    unittest.main()
        



    

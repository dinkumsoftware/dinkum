#!/usr/bin/env python3
# dinkum/python/modnames.py
''' A number of standalone functions which deal with
python module and package names.  In particular, they
deal with translating filenames/directory_names back
and forth to dotted python module/package paths

'''

# 2020-02-04 tc Initial

import os.path

def full_dotted_modulename(filename) :
    ''' returns the module path of filename. e.g.
           filename= a/b/c/dinkum/what/ever/foo.py
           return  = dinkum.what.ever.foo
    
    Returns None if filename isn't a python file, ie
    doesn't end in *.py
    '''

    # Get the absolute pathname of filename
    filename = os.path.expanduser(filename) # ~ expansion
    filename = os.path.abspath(filename)

    # Get the modulename (by stripping *.py) from last component
    module_name = modulename(filename)
    if not module_name :
        return None # Not a python file
    # strip off the module/filename
    path = os.path.dirname( filename )
    
    # Make sure file is in the filetree of our
    # top level directory, i.e. /a/b/c/dinkum/what/ever/module
    from dinkum.project.dirs import top_level_dir ####################
    proj_root = top_level_dir()
    if os.path.commonprefix([proj_root, path]) != proj_root :
        return None # path of filename doesn't fall in dinkum subtree

    # Ok, ready to generate the dotted pathname
    # Make a list of directories, this does not include module name
    packages = path.split(os.sep)

    # Remove everything to left of  dinkum/...
    # i.e proj_root    = "/a/b/c/dinkum"
    #     packages     = ["a","b","c","dinkum", "what", "ever",  "module"]
    # we want packages = [            "dinkum", "what", "ever" , "module"]
    packages = packages[len(proj_root.split(os.sep))-1 : ]

    # Tack on the module
    packages.append( module_name )

    # give them a single dotted string
    return ".".join(packages)

def modulename(filename) :
    ''' turns filename (with or without a path) into
    the python module name. e.g.
        a/b/c/foo.py ==> foo

    returns None if it isn't a python file, i.e.
                 doesn't end in *.py
    '''

    # Sanity check
    if not os.path.isfile(filename) :
        return None

    # Peel off the extension
    (root, ext) = os.path.splitext(filename)
    if ext != ".py" :
        return None # Not a python file

    # The last component is the module name
    return os.path.basename(root)


# Test code
import unittest
import tempfile

class Test_modnames(unittest.TestCase) :

    def test_full_dotted_modulename(self) :
        # Test ourself
        self.assertEqual ("dinkum.python.modnames", full_dotted_modulename( __file__ ) )

        # Test non-python file
        self.assertIsNone (full_dotted_modulename( "not/a/python/file"))

        # A python file not in dinkum subtree
        f = tempfile.NamedTemporaryFile(suffix=".py")
        self.assertIsNone ( full_dotted_modulename(f.name) )



    def test_modulename(self) :
        # filename doesn't exist
        self.assertIsNone ( modulename("a/b/c/no-such_file"))

        # not a python file
        f = tempfile.NamedTemporaryFile()
        self.assertIsNone ( modulename(f.name))

        # Test ourself
        self.assertEqual( "modnames", modulename(__file__))

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



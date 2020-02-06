#!/usr/bin/env python3
# dinkum/python/modnames.py
''' A number of standalone functions which deal with
python module and package names.  In particular, they
deal with translating filenames/directory_names back
and forth to dotted python module/package paths

'''

# 2020-02-04 tc Initial
# 2020-02-06 tc Added is_importable and is_findable_for_import

import os.path
import importlib.util
import traceback

def is_findable_for_import(module_name) :
    ''' Returns True if module_name can be located for import.
    It doesn't necessary imply that module_name imports without
    error.
    '''
    try :
        return importlib.util.find_spec(module_name) != None
    except :
        # Some kind of error
        # likely to be "module_name" isn't a string
        return False

    assert False, "Impossible Place"


def has_import_errors(module_name) :
    ''' Normally returns None.

    If there is any kind of problem importing module_name,
    a human-readable error message will be returned.
    It is typically a stack trace with associated error message.
    '''
    try:
        # Do the import
        importlib.__import__(module_name)

        # It must have worked
        return None

    except Exception as e :
        # Got some kind of error doing the import

        # Retrieve the error message
        returned_err_msg = traceback.format_exc(limit=0)

        return returned_err_msg
        

def full_dotted_modulename(filename) :
    ''' returns the module path of filename. e.g.
           filename= "a/b/c/dinkum/what/ever/foo.py"
           return  = "dinkum.what.ever.foo"
        where dinkum is top level directory in project
    
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
    
    # What we return
    # Always has the module name.  We'll insert req'd package names below
    returned_dotted_modulename = module_name

    # Walk up the directory path until we find a non-package
    # directory (i.e. has no __init__.py in it)
    while is_package_dir (path) :
        # Put the end path component at head of what we return
        # and strip it off of path
        (path, pkg) = os.path.split(path)   
        returned_dotted_modulename = pkg + "." + returned_dotted_modulename

    # give them a single dotted string
    return returned_dotted_modulename

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


def is_package_dir (directory) :
    ''' Returns true if directory is a python package directory,
    i.e. it has a __init__.py in it
    '''

    # It must exist
    if not os.path.isdir(directory) :
        return False

    # It must have an __init__.py in it
    reqd_pkg_file = os.path.join(directory, "__init__.py" )
    return os.path.isfile  ( reqd_pkg_file )


# Test code
import unittest
import tempfile

class Test_modnames(unittest.TestCase) :
    def test_is_importable(self) :
        self.assertFalse( is_findable_for_import(None))
        self.assertFalse( is_findable_for_import(""))
        self.assertFalse( is_findable_for_import("no.such.damn.package.or.module") )
        self.assertFalse( is_findable_for_import("no_such_damn____________module") )

        # Library stuff is importable
        self.assertTrue( is_findable_for_import("os.path"       ))
        self.assertTrue( is_findable_for_import("importlib.util"))

        # This file should be importable
        my_modulename = full_dotted_modulename(__file__)
        self.assertTrue( is_findable_for_import( my_modulename ))


    def test_full_dotted_modulename(self) :
        # Test ourself
        self.assertEqual ("dinkum.python.modnames", full_dotted_modulename( __file__ ) )

        # Test non-python file
        self.assertIsNone (full_dotted_modulename( "not/a/python/file"))

        # A python file not in package
        # Should just return the modulename
        f = tempfile.NamedTemporaryFile(suffix=".py") # /tmp/foo.py
        (path,ext)        = os.path.splitext(f.name)  # /tmp/foo
        should_be_modname = os.path.basename(path)    # foo

        self.assertEqual ( should_be_modname, full_dotted_modulename(f.name) )



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



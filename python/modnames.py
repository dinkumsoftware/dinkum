#!/usr/bin/env python3
# dinkum/python/modnames.py
''' A number of standalone functions which deal with
python module and package names.  In particular, they
deal with translating filenames/directory_names back
and forth to dotted python module/package paths

Vocabulary:
    dotted_module_name    "a.b.c.mod" -or- "mod"
    module_name           "mod" i.e. no a.b.c
'''

# 2020-02-04 tc Initial
# 2020-02-06 tc Added is_importable and is_findable_for_import
# 2020-02-16 tc Added filename_from_modulename
#               Discovered that since python 3.3, __init__.py NOT
#               required to make importable

import os.path
import importlib.util
import traceback

def is_findable_for_import(dotted_module_name) :
    ''' Returns True if module_name can be located for import.
    It doesn't necessary imply that module_name imports without
    error.
    '''
    try :
        return importlib.util.find_spec(dotted_module_name) != None
    except :
        # Some kind of error
        # likely to be "dotted_module_name" isn't a string
        return False

    assert False, "Impossible Place"


def has_import_errors(dotted_module_name) :
    ''' Normally returns None.

    If there is any kind of problem importing dotted_module_name,
    a human-readable error message will be returned.
    It is typically a stack trace with associated error message.
    '''
    try:
        # Do the import
        importlib.__import__(dotted_module_name)

        # It must have worked
        return None

    except Exception as e :
        # Got some kind of error doing the import

        # Retrieve the error message
        returned_err_msg = traceback.format_exc(limit=0)

        return returned_err_msg
        

def dotted_module_name_from_filename(filename) :
    ''' returns the module path of filename. e.g.
           filename= "a/b/c/dinkum/what/ever/foo.py"
           return  = "dinkum.what.ever.foo"
    where dinkum is top level directory in project and
    is a child of something in PYTHONPATH/sys.path
    
    It attempts to return the longest package path that is importable
    with current settings of PYTHONPATH (sys.path).

    Returns None if
        filename isn't a python file, ie doesn't end in *.py -or-
        isn't findable for import with current PYTHONPATH(sys.path) settings
    '''

    # Get the absolute pathname of filename
    filename = os.path.abspath(filename)

    # Get the modulename (by stripping *.py) from last component
    module_name = module_name_from_filename(filename)
    if not module_name :
        return None # Not a python file

    # strip off the module/filename
    path = os.path.dirname( filename )
    
    # Construct the longest possible package path
    # We iterate thru PYTHONPATH (sys.path) and find one
    # that is on path.  If there are multiple ones,
    # pick the one with the greatest number of intermediate
    # package dirs
    final_pkg_dirs = []     # List of package dirs, e.g.
                            # ["a", "b", "c"] from "a.b.c"

    for pkg_root in sys.path :
        # Convert empty strings to current directory
        if not pkg_root :
            pkg_root = os.getcwd()

        # path intersect this sys.arg[x] ?
        if pkg_root == os.path.commonprefix( [pkg_root, path] ) :
            # yes, remove PYTHONPATH leadin and extract dirs
            path_tail = path[ len(pkg_root) + 1: ] # +1 removes leading /
            pkg_dirs = path_tail.split(os.sep)
        
            # Longer than current?
            if len(pkg_dirs) > len(final_pkg_dirs) :
                # Yes, use it
                final_pkg_dirs = pkg_dirs

    # We have the longest package path
    # Put it together with module name
    final_pkg_dirs.append( module_name)
    dotted_module_name = '.'.join(final_pkg_dirs)

    # Last sanity check
    # It should be importable
    return dotted_module_name if is_findable_for_import(dotted_module_name) else None


def module_name_from_filename(filename) :
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


def filename_from_dotted_module_name(dotted_module_name) :
    '''
    Returns absolute pathname of the file that defines dotted_module_name.
    dotted_module_name can be "module" or "a.b.c.module"

    It must be findable for import so that the appropriate
    sys.path entry can be prepended.

    Silently returns None on any kind of error.
    '''

    # Sanity check the argument
    if not is_findable_for_import(dotted_module_name) :
        return None

    # Convert .'s to /'s
    tokens = dotted_module_name.split('.')   # a.b.mod
    relative_filename = os.sep.join(tokens)  # a/b/mod

    # Tack on python extension
    relative_filename += '.py'               # a/b/mod.py

    # Now search thru PYTHONPATH, appending relative_filename
    # until we find a file
    for head_filename in sys.path :
        # Account for empty strings
        if not head_filename :
            head_filename = os.getcwd()

        full_filename = os.path.join(head_filename, relative_filename)
        if os.path.isfile (full_filename) :
            return full_filename

    # As we know the module can be found for import
    # We MUST have returned somewhere in prior loop
    assert False, "Impossible Place"


def join_dotted_pkg_path_and_module_name(pkg_path, module_name) :
    '''
    pkg_path      package path to module, i.e. a.b.c
    module_name   what it says, e.g. mod

    Puts those together and returns it, e.g. a.b.c.mod

    '''

    # any package path?
    if not pkg_path :
        # No, nothing but the module
        return module_name

    # What we return
    ret_str = pkg_path

    # Avoid double dots
    dot = '.'
    while ret_str.endswith(dot) :
        # Strip trailing dot(s)
        ret_str = ret_str[:-1]

    # Tack on a dot separated module
    ret_str += dot + module_name
        
    return ret_str
    

# Test code
import unittest
import tempfile
import pathlib
import sys

class Test_modnames(unittest.TestCase) :
    def test_is_findable_for_importable(self) :
        self.assertFalse( is_findable_for_import(None))
        self.assertFalse( is_findable_for_import(""))
        self.assertFalse( is_findable_for_import("no.such.damn.package.or.module") )
        self.assertFalse( is_findable_for_import("no_such_damn____________module") )

        # Library stuff is importable
        self.assertTrue( is_findable_for_import("os.path"       ))
        self.assertTrue( is_findable_for_import("importlib.util"))

        # This file should be importable
        my_modulename = dotted_module_name_from_filename(__file__)
        self.assertTrue( is_findable_for_import( my_modulename ))

        # A module not in a package should not be importable
        self.assertFalse( is_findable_for_import("test_data/not_a_package/module.py"))

    def test_has_import_errors(self) :
        # We should be importable
        self.assertIsNone (has_import_errors(__name__))

        module_name = dotted_module_name_from_filename(__file__)
        self.assertIsNone( has_import_errors(module_name))

        # This shouldn't import
        module_name = "test_data.import_syntax_errors.py"
        self.assertIsNotNone( has_import_errors(module_name))        
        
        # Library stuff is importable
        self.assertIsNone( has_import_errors("os.path"       ))
        self.assertIsNone( has_import_errors("importlib.util"))


    def test_dotted_module_name_from_filename(self) :
        # Test ourself
        self.assertEqual ("dinkum.python.modnames", dotted_module_name_from_filename( __file__ ) )

        # Test non-python file
        self.assertIsNone (dotted_module_name_from_filename( "not/a/python/file"))
        
        # We are gonna diddle sys.path and restore it at the end
        sys_path_orig = sys.path

        # Create the following directory struct
        # /tmp/txyzzy/a/b/whatever.py
        with tempfile.TemporaryDirectory()  as td : # /tmp/txyzzy

            wrk_dir= os.path.join( td, "a")
            os.mkdir( wrk_dir )                                         # /tmp/txyzzy/a

            wrk_dir= os.path.join( wrk_dir, "b")
            os.mkdir( wrk_dir )                                         # /tmp/txyzzy/a/b

            # A python file
            pfilename = os.path.join(wrk_dir, "foo.py") # /tmp/txyzzy/a/b/foo.py
            pathlib.Path(pfilename).touch()             # create it

            # Shouldn't be importable as txyzzy, a, b, aren't on PYTHONPATH(sys.path)
            self.assertIsNone ( dotted_module_name_from_filename(pfilename) )

            # Now put /tmp/txyzzy/a at end of sys.path
            sys.path.append( os.path.join(td, "a" ))
            self.assertEqual ( "b.foo" , dotted_module_name_from_filename(pfilename) )

            # Now put /tmp/txyzzy at end of sys.path
            # Should pick the longer dotted package path
            sys.path.append( td )
            self.assertEqual ( "a.b.foo" , dotted_module_name_from_filename(pfilename) )

        # Restore sys.path
        sys.path = sys_path_orig


    def test_module_name_from_filename(self) :
        # filename doesn't exist
        self.assertIsNone ( module_name_from_filename("a/b/c/no-such_file"))

        # not a python file
        f = tempfile.NamedTemporaryFile()
        self.assertIsNone ( module_name_from_filename(f.name))

        # Test ourself
        self.assertEqual( "modnames", module_name_from_filename(__file__))

    def test_filename_from_dotted_module_name(self) :

        # a non-importable module
        self.assertIsNone( filename_from_dotted_module_name ("no.such.path.or.module"))

        # Ourselves
        our_dotted_module_name = dotted_module_name_from_filename(__file__)
        our_filename           = os.path.abspath (__file__)

        self.assertEqual( our_filename, filename_from_dotted_module_name(our_dotted_module_name) )

    def test_join_dotted_pkg_path_and_module_name(self) :
        pkg_path    = "a.b.c.e.f.g"
        module_name = "mod"
        should_be   = "a.b.c.e.f.g.mod"

        self.assertEqual( join_dotted_pkg_path_and_module_name(pkg_path, module_name),
                          should_be)

        # Trailing dots
        pkg_path    = "a.b.c.e.f.g."
        module_name = "mod"
        self.assertEqual( join_dotted_pkg_path_and_module_name(pkg_path, module_name),
                          should_be)
        
        # No path
        pkg_path    = ""
        module_name = "mod"
        self.assertEqual( join_dotted_pkg_path_and_module_name(pkg_path, module_name),
                          module_name)

        pkg_path    = None
        module_name = "mod"
        self.assertEqual( join_dotted_pkg_path_and_module_name(pkg_path, module_name),
                          module_name)



if __name__ == "__main__" :
    # Run the unittests
    unittest.main()



#!/usr/bin/env python3
# dinkum/utils/state_space.py
'''
Functions dealing with "state" space.  This is a subdirectory
typically under ~/.dinkum  where an application can read/write
state information that needs to be available from invocation to invocation.

Convention is that state_root() is ~/.dinkum/state_space/
It can be changed.

Convention is that a function in package.module a.b.c.mod
reads/writes from/to:
     ~/.dinkum/state_space/a/b/c/mod/<filename>
     via state_space_filename(__name__, <filename>,
                                     create_reqd_subdirs)

Convention is that a function in package.module a.b.c.mod
that has info that is needed package wide reads/writes from/to:
     ~/.dinkum/state_space/a/b/c/<filename>
     via state_space_filename(__name__, <filename>,
                              create_reqd_subdirs,
                              num_name_components_to_trim=1)

Function summary,
    assuming name=__name__ 
             called from a function in dinkum.foo.bar.mod
             filename = "foo"

    state_filename(name, filename,
                   create_reqd_subdirs=False,
                   num_name_components_to_trim=0)

    # tacks filename on the end of state_subdir() returns it
    # example return: /home/user/.dinkum/a/b/c/mod/foo


    state_subdir(name,
                 create_reqd_subdirs=False,
                 num_name_components_to_trim=0)
    # Changes dots in name to / and removes num_name_components_to_trim from
    # right side.  Prepends with state_space_root() and returns it.
    # example return: /home/user/.dinkum/state_space/a/b/c/mod

    state_root(create_if_nonexistant)
    # returns ~/.dinkum/state_space as absolute pathname


    if create_reqd_subdirs is True, All of these create any required directories
    Note: the file for filename is NOT created if it doesn't exist.
          the directories in the path may be created.
    They all return a tuple of (path-or-filename, exists, dirs_created) where the last
        are bools that indicate:
            exists: returned path-or-filename exists AFTER the call
            dirs_created: some directories in returned path-or-filename were created

    Use set_state_root(pathname) to change the "root" directory.  This is
    typically only done for test code and/or by installers.
'''

# 2019-12-04 tc  Initial
# 2019-12-06 tc  Changed all func names from dinkum_XX() to XX()

import os.path


# Exceptions we can raise:
class ExcAttemptToChangeStateRootToNonExistantDir(Exception) :
    ''' Someone [probably set_state_root()] attempted
    to change the state root to a non-existant directory
    '''
    def __init__(self, message) :
        self.message = message

class ExcAttemptToChangeStateRootToFile(Exception) :
    ''' raised when set_dinkum_root_state() is told
    to change the root to a file instead of a directory
    '''
    def __init__(self, filename) :
        super().__init__("%s is a file, should a directory" % filename)

class ExcOSError(Exception) :
    ''' Got some kind of error for the OS in trying to
    do something to the filesystem.  We catch them
    and rethrow so avoid the stacktrace deep into
    the Python library

    Raiser should pass in the original exception to the
    constructor.
    '''
    def __init__(self, exc) :
        # Pass along the error message
        self.message = str(exc) 



# The default root directory where state_space stuff is written
# Can be altered by set_state_root() or reset_state_root()
_default_state_root = "~/.dinkum/state_space"
_state_root         = _default_state_root

def reset_state_root() :
    ''' Restore the state root (as returned by state_root() to
    the default.  Typically this is ~/.dinkum.
    '''
    global _default_state_root, _state_root

    _state_root = _default_state_root


def set_state_root(pathname, create_if_nonexistant=False) :
    ''' Set the root of all state space to "pathname".
    create_if_nonexistant controls whether pathname is created
    if it doesn't exist.

    Does expands pathname for ~ and environment variables. Makes
    it an absolute pathname.

    returns tuple (pathname (as modified),
                   pathname_exists_after_call,
                   subdirs_were_created)
    
    '''
    global _state_root

    new_root_pathname = expand_abs_vars_user(pathname)

    # Does it exist?
    # If not, make it if caller wants
    new_root_pathname, exists, dirs_created = create_path_if_needed(
                                                   new_root_pathname,
                                                   create_if_nonexistant)
    
    if not exists :
            raise ExcAttemptToChangeStateRootToNonExistantDir(
                "set_state_root(%s): pathname does not exist" % (new_root_pathname)
            )

    # Check that it is a directory
    if not os.path.isdir (new_root_pathname) :
        raise ExcAttemptToChangeStateRootToFile(new_root_pathname)

    # Change it for all the world
    _state_root = new_root_pathname
    return (_state_root, exists, dirs_created)

def state_root() :
    ''' Returns the root of the state system.
    '''
    return expand_abs_vars_user(_state_root)

def state_subdir(subdir, create_reqd_subdirs=False,
                        num_name_components_to_trim=0) :
    ''' Determines the subdirectories between state_root()
    and the directory to write state files.

    Typically called as:
        state_subdir(subdir=__name__, create_reqd_subdirs=True)

    A subdirectory is created in the returned pathname for every .
    separated token in name.

    If create_reqd_subdirs is True, the directories will be created.

    num_name_components_to_trim controls how many are tossed before
    constructing the pathname. num_name_components_to_trim is typically
    set to 1 to remove the module name for a space that is needed
    package wide.
    
    returns tuple (pathname (as modified),
                   pathname_exists_after_call,
                   subdirs_were_created)
    '''

    # Split the package/module names
    pkg_mod_names = subdir.split(".")

    # Discard what we are suppose to
    if num_name_components_to_trim > 0 :
        pkg_mod_names = pkg_mod_names[:-num_name_components_to_trim]

    # Put them back together and prepend the root dir 
    pathname = os.path.join(state_root(),
                            *[ str(subdir) for subdir in pkg_mod_names],
                            '' ) # The empty string at the end means
                                 # pathname will end in a /

    # Make something if we need to
    return create_path_if_needed(pathname,
                                 create_reqd_subdirs)

def state_filename( subdir, filename,
                           create_reqd_subdirs=False,
                           num_name_components_to_trim=0) :

    ''' Returns the absolute path of a pathname for an application
    to read/write a file named "filename".

    subdir is typically __name__, but this isn't enforced

    Combines, creates as necessary, and returns
        state_subdir(subdir, create_reqd_subdirs,num_name_components_to_trim)
        filename

    Removes num_name_components_to_trim from "." separated tokens in name.
    Normally 0, but set to 1 if you want filename to be available package-wide
    (as opposed to module-wide)

    If any of the subdirs in the path don't exist, they  will be created
    if create_if_nonexistant is True.

    The filename will NOT ever be created.

    Returns a tuple (absolute path of filename, filename_exists(T/F), dirs_created(T/F)
    '''

    # let this guy do the heavy lifting
    (dir_name, exists, dirs_created) = state_subdir(subdir,
                                                           create_reqd_subdirs,
                                                           num_name_components_to_trim)

    # Tack on the filename and see if file exists
    full_pathname = os.path.join( dir_name, filename) 
    exists = os.path.exists( full_pathname )

    return (full_pathname, exists, dirs_created)



def expand_abs_vars_user(pathname) :
    ''' Returns absolute path of pathname,
    expanding environment variables and ~'s
    '''
    return os.path.abspath(
           os.path.expandvars(
           os.path.expanduser(pathname
           )))


def create_path_if_needed(pathname, create_if_nonexistant) :
    ''' If pathname doesn't exist, it will be created if
    created_if_nonexistant is True.

    Returns (pathname, exists, subdirs_created)
        pathname           (as modified)
        exists             True if pathname exists when we are done
        subdirs_created    True if any directories created
    '''
    try :
        pathname = expand_abs_vars_user(pathname)
        exists = os.path.exists(pathname)

        subdirs_created = False # Assume not
        if not exists and create_if_nonexistant :
            os.makedirs(pathname)
            exists = os.path.exists(pathname)
            subdirs_created = True

        return (pathname, exists, subdirs_created)

    except Exception as exc :
        # Catch any errors and reraise them
        # See writeup on ExcOSError above
        raise ExcOSError( exc ) from None
    


# Test code
import unittest
import sys
import shutil

class Test_test_state_space(unittest.TestCase) :
    # Various tests need a place to read/write files for test
    # This is that place.  It gets created in setUp() and
    # removed in tearDown().
    #   A nice feature to have would be to not remove it
    #   on error, but a preliminary search made it appear
    #   that that would be complicated
    def setUp(self) :
        ''' Creates (if non-existant) a directory
        playpen in the same directory as the executable
        file

        Restores space root to the default as some tests
        diddle the space root and one can't control the
        order of the tests
        '''
        dirname_to_create = "test_playpen"
        self._playpen_dirname = None # Full absolute path 

        # Publish the name of the directory
        exe_dir = os.path.dirname(sys.argv[0])
        self._playpen_dirname = os.path.join(exe_dir, dirname_to_create)
        self._playpen_dirname = os.path.abspath(self._playpen_dirname)

        # Create it if need be
        create_path_if_needed( self._playpen_dirname, True)

        # Restore the space root to default.
        reset_state_root()

    def tearDown(self) :
        ''' Remove the playpen created by setUp()
        '''
        shutil.rmtree( self._playpen_dirname )

    def test_dinkum_default_state_dir(self) :
        # Confirm the root matches the default.
        default_root = "~/.dinkum/state_space"
        expected_default_root = os.path.abspath(
                                os.path.expandvars(
                                os.path.expanduser(default_root
                                )))
                                
        got_root = state_root()

        self.assertEqual( expected_default_root, got_root, 
                          "Expected:%s Got:%s" % (expected_default_root, got_root))

    def test_set_state_root(self) :
        # Try to set it non-existant directory
        nonexistant_dir = "/xyzzy_12345_54321_no_one_would_make_this/right/I/really/hope/this/directory/doesnt/exist"
        self.assertRaises( ExcAttemptToChangeStateRootToNonExistantDir,
                           set_state_root, nonexistant_dir )        # Defaults to not creating subdirs
        self.assertRaises( ExcAttemptToChangeStateRootToNonExistantDir,
                           set_state_root, nonexistant_dir, False ) # False ==> don't create subdirs

        # Try to have it create a file it can't
        self.assertRaises( ExcOSError, set_state_root, nonexistant_dir, True)

        # Switch the state root directory to playpen, so we can
        # make files and such with destroying anything else
        new_root_name = os.path.join(self._playpen_dirname, __name__)
        (root_name, exists, subdirs_created) = set_state_root( new_root_name, True )
        self.assertTrue (exists          )
        self.assertTrue (subdirs_created  )

        # Create an empty FILE (not dir)
        filename = os.path.join(self._playpen_dirname, "i_am_a_file")
        with open( filename, "w") as f :
            pass

        # try to change state root dir to it
        self.assertRaises( ExcAttemptToChangeStateRootToFile, 
                           set_state_root, filename )
        

    def test_state_subdir(self) :
        # Make a place to play
        new_root_name = os.path.join(self._playpen_dirname, __name__)
        root_dir,exists,subdirs_created = set_state_root( new_root_name, True)

        subdirs = "1.2.3.4"
        expected_path = os.path.join( state_root(), "1", "2", "3", "4")

        # Just return the full path, ie don't make the dirs
        path, exists, made = state_subdir(subdirs) 
        self.assertEqual ( path, expected_path )
        self.assertFalse (exists)
        self.assertFalse (made)
        
        # Now make it
        path, exists, made = state_subdir(subdirs, True) 
        self.assertEqual ( path, expected_path )
        self.assertTrue (exists)
        self.assertTrue (made)

        # Now tell it to make it again, but it won't because already exists
        path, exists, made = state_subdir(subdirs, True) 
        self.assertEqual ( path, expected_path )
        self.assertTrue (exists)
        self.assertFalse (made)
        
        # Now whack off some package/module levels

        # Confirm we don't remake an existing subdir
        subdirs_less_one = "1.2.3"
        subdirs_less_one_expected_path = os.path.join( state_root(), "1", "2", "3")

        path, exists, made = state_subdir(subdirs_less_one, False) 
        self.assertEqual ( path, subdirs_less_one_expected_path )

        path, exists, made = state_subdir(subdirs, False, 1) 
        self.assertEqual ( path, subdirs_less_one_expected_path )        
        
    def test_state_filename(self) :
        # Make a place to play
        new_root_name = os.path.join(self._playpen_dirname, __name__)
        root_dir = set_state_root( new_root_name, True)

        subdirs="one.two.three.four"
        filename="just-a-testfile"
        expected_pathname=os.path.join( state_root(), *subdirs.split("."), filename )

        # Query, don't make subdirs
        (pathname, exists, made ) = state_filename(subdirs, filename)
        self.assertEqual (pathname, expected_pathname)
        self.assertFalse (exists)
        self.assertFalse (made)
        
        # Query, do make subdirs
        (pathname, exists, made ) = state_filename(subdirs, filename, True)
        self.assertEqual (pathname, expected_pathname)
        self.assertFalse (exists)
        self.assertTrue  (made)

        # We make the file
        with open (pathname, "w") as f :
            pass # Create an empty file

        # Try again and file should exist with no dirs made
        (pathname, exists, made ) = state_filename(subdirs, filename, True)
        self.assertEqual (pathname, expected_pathname)
        self.assertTrue  (exists)
        self.assertFalse (made)
        

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()


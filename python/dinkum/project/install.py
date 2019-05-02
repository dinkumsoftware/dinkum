''' install

Series of functions to install, uninstall, and support all the software
produced by dinkum software.

    install_from_git       Copies from a git to .dinkum/git-copy-root and
                             configures so user can use it
    remove_install_from_git undoes the above

    helper functions:
      announce             Handles verbose and dry_run
'''
#2019-05-02 tc@DinkumSoftware.com Initial

import os       # makedirs
import shutil   # copytree, rmtree

# Where dinkumsoftware stores "private" stuff
dinkum_data = "~/.dinkum"
dinkum_data = os.path.expanduser(dinkum_data) # ~ expansion
dinkum_data = os.path.abspath( dinkum_data)


# Where part of a "git clone dinkum software is copied to
# in install_from_git()
dinkum_git_copy_root = os.path.join(dinkum_data, "git-copy-root")

# If a file named the following exists in a subdirectory of git_root_dir,
# then that directory is NOT copied into dinkum_git_copy_root
magic_filename_to_not_publish = 'DINKUM_NOT_TO_PUBLISH'

def install_from_git(git_root_dir, verbose=False, dry_run=False) :
    ''' Installs a partial COPY of git clone at git_root_dir
    so the software can be used without the git_root_dir, i.e.
    once copied the original git at git_root_dir may be deleted.

    if verbose is True, announce what is being done
    if dry_run is Tru, announce what what would be done,
                        but don't actually do it

    Recursively copy from "git_root_dir" to "dinkum_root_copy"
         We publish all files in git_root_dir
           except: .gitignore
         We publish every subdirectory of git_root_dir
         that does NOT contain a file currently named
           DINKUM_NOT_TO_PUBLISH (See magic_filename_to_no_publish_above)
         We do not publish the .git directory itself.

    Any existing installation from git is UNINSTALLED and then reinstalled.
    This is due to limitations of some underlying tools

    ''' # <todo> f'string? to avoid entering defs twice
    
    # Silently remove any existing prior installation
    # the shutil.copytree and os.makedirs() complain if there are
    # preexisting files.
    remove_install_from_git(verbose, dry_run) 
    
    # Everything is copied to dinkum_git_copy_root
    
    # Create the directory, it is an error if already exists
    announce("mkdir", verbose, dry_run, None, dinkum_git_copy_root )
    if not dry_run :
        os.makedirs( dinkum_git_copy_root )

    # All the files (or dirs) in git_root_dir are
    # targets to publish.  Iterate thru them
    # Produce list of files and list of dirs
    files_to_copy = []
    dirs_to_copy  = []
    names_to_ignore = [".git", ".gitignore"]
    for file_or_dir in os.listdir( git_root_dir ) :
        # Don't publish stufff we are ignoring
        if file_or_dir in names_to_ignore :
            continue

        # Don't publish dirs that contain a file
        # with magic name indicating not to publish it
        if os.path.isfile( os.path.join(git_root_dir, file_or_dir,
                                        magic_filename_to_not_publish)) :
            continue 
                           
        # We want to publish this subdir or file
        # src ==> dinkum_git_copy_root
        src = os.path.join( git_root_dir, file_or_dir )
        if os.path.isdir (src) :
            dirs_to_copy.append(src)
        else :
            files_to_copy.append(src)

    # Iterate thru the files
    # note: we separate files and dirs just so verbose output looks nicer
    # when all the files come first
    files_to_copy.sort()  # alphabetical order
    for src in files_to_copy :
        #<todo> I suspect symbolic links don't work properly
        announce("File", verbose, dry_run, src, dinkum_git_copy_root)
        if not dry_run :
            shutil.copy2(src, dinkum_git_copy_root) # single file
        
    # recursive copy the directories
    dirs_to_copy.sort()
    for src in dirs_to_copy :
        # copy tree requires des be a non-existent dir
        # So we have to compute top level destination directory
        des = os.path.join(dinkum_git_copy_root, os.path.basename(src))
        announce("Dir", verbose, dry_run, src, des)
        if not dry_run :
            shutil.copytree(src, des, symlinks=True)
        
        

def remove_install_from_git(verbose=False, dry_run=False) :
    ''' Undoes an install_from_git().
        .dinkum/git-copy-root   is recursively deleted.
    It is NOT an error if none of the files exist

    if verbose is True, announce what is being done
    if dry_run is TRUE, announce what what would be done,
                        but don't actually do it

    '''

    # If ~/.dinkum/git-copy-root file tree exists
    if os.path.isdir( dinkum_git_copy_root) :
        # Wipe it out 
        announce ("rmdir", verbose, dry_run, None, dinkum_git_copy_root)
        if not dry_run :
            shutil.rmtree( dinkum_git_copy_root)

def announce(label, verbose, dry_run, src, des) :
    '''
If either "verbose" or "dry_run" or true, it
prints a line of the form:
  <label>: <src>      =>  <des>
'''

    label_width = len("rmdir") + 1 # Field width for label, +1 for :
                                   # This is currently longest label
    des_offset  = 50 # where to start printing destination
    arrow = '=> '    # how we separate src and des

    # Always be verbose on a dry_run
    if dry_run :
        verbose = True

    # anything to do?
    if not verbose :
        return # nope

    # Make up a string to print

    # The label
    s = label + ":"
    s = s.ljust(label_width)[:label_width] # space over and truncate

    if src :
        s += src   
    s = s.ljust(des_offset)[:des_offset] # space over and truncate

    if src and des :
        # Put in connecting arrow
        s = s[:-len(arrow)] # remove chars for arrow
        s += arrow          # and replace them with the arrow

    if des :
        s += des

    # Show them
    print s
    

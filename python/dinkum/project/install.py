''' install

Series of functions to install, uninstall, and support all the software
produced by dinkum software.

    install_from_git       Copies from a git to .dinkum/git-copy-root and
                             configures so user can use it
    remove_install_from_git undoes the above

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

def install_from_git(git_root_dir) :
    ''' Installs a partial COPY of git clone at git_root_dir
    so the software can be used without the git_root_dir, i.e.
    once copied the original git at git_root_dir may be deleted.

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
    remove_install_from_git() 
    
    # Everything is copied to dinkum_git_copy_root
    
    # Create the directory, it is an error if already exists
    # <todo> verbose=verbose, dry_run=dry_run)
    os.makedirs( dinkum_git_copy_root )

    # All the files (or dirs) in git_root_dir are
    # targets to publish.  Iterate thru them
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
            # copy tree requires des be a non-existent dir
            # So we have to compute top level destination directory
            des = os.path.join(dinkum_git_copy_root, os.path.basename(src))
            shutil.copytree(src, des, symlinks=True)
        else :
            #<todo> I suspect symbolic links don't work properly
            shutil.copy2(src, dinkum_git_copy_root) # single file


def remove_install_from_git() :
    ''' Undoes an install_from_git().
        .dinkum/git-copy-root   is recursively deleted.
    It is NOT an error if none of the files exist
    '''

    # If ~/.dinkum/git-copy-root file tree exists
    if os.path.isdir( dinkum_git_copy_root) :
        # Wipe it out 
        shutil.rmtree( dinkum_git_copy_root)


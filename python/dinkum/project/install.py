''' install

Series of functions to install, uninstall, and support all the software
produced by dinkum software.

'''
#2019-05-02 tc@DinkumSoftware.com Initial

import os       # makedirs
import shutil   # copytree

# Where dinkumsoftware stores "private" stuff
dinkum_data = "~/.dinkum"
dinkum_data = os.path.expanduser(dinkum_data) # ~ expansion
dinkum_data = os.path.abspath( dinkum_data)


# Where part of a "git clone dinkum software is copied to
# in install_from_git()
dinkum_git_copy_root = os.path.join(dinkum_data, "git-copy-root")

# If a file named this exists in a subdirectory of git_root_dir,
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
    ''' # <todo> f'string?
    
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
            shutil.copy2(src, dinkum_git_copy_root) # single file



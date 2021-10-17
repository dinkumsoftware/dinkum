# dot_profile.sh
#
# Intended to be sourced by ~/.profile
# Alters environment vars:
#    PATH
#    PYTHONPATH
#
# Requires environment variable DINKUM_FILETREE be set
# Silently does nothing if DINKUM_FILETREE isn't set
#
# 2021-08-15 tc Initial
# 2021-10-17 tc went to bin/symlinks

# Note Well: Changes to this file don't take full effect until
#            you logout and login.  You can avoid that in a
#            particular terminal window by:
#                bash --login

# Make sure required env var exists and points to a directory
if [ -d "$DINKUM_FILETREE" ] ; then

    # Put dinkum on python module search path
    dinkum_path_dir="$DINKUM_FILETREE/.."
    if [ -d "$dinkum_path_dir" ] ; then
        # convert to absolute path and prepend to PYTHONPATH
        dinkum_path_dir=$(cd "$dinkum_path_dir" 2> /dev/null && pwd -P)
        export PYTHONPATH="$dinkum_path_dir:$PYTHONPATH"
    fi


    # Make a place to put symlinks to all
    # the dinkum executables
    dinkum_symlinks_dir="$DINKUM_FILETREE/bin/symlinks"
    mkdir -p "$dinkum_symlinks_dir"
    rm -f  "$dinkum_symlinks_dir/*"    # clean out prior work

    # Put it on the path
    PATH="$dinkum_symlinks_dir":"$PATH"

    # symlink all the dinkum executables in bin/sym_links
    for dinkum_a_bin_dir in $(find "$DINKUM_FILETREE" -type d -name bin'*' ) ; do
        # iterate over all executables in the directory that aren't
        #    directories    ! -type d
        #    *~ backup file ! -name '*'~
        #    *~ backup file ! -name '*''#'
        # and make bin/symlinks/<name> point to actual dinkum/a/b/bin/<name>
        for dinkum_target in $(find "$dinkum_a_bin_dir" -executable ! -type d \
                                    ! -name '*'~                              \
                                    ! -name '*''#' ) ; do
            dinkum_link="$dinkum_symlinks_dir"/"$(basename $dinkum_target)"
            ln --symbolic --force --relative "$dinkum_target"  "$dinkum_link"
        done
    done

    # Diddle the links in bin/symlinks that point to python executables
    #    change _ to -
    #    remove the trailing .py
    for dinkum_curr_py_link in $(find "$dinkum_symlinks_dir" -name '*'.py) ; do
        dinkum_curr_py_dirname=$(dirname   $dinkum_curr_py_link)
        dinkum_curr_py_basename=$(basename $dinkum_curr_py_link)

        # _ to -  and  remove trailing .py
        dinkum_new_py_basename=$(echo "$dinkum_curr_py_basename" | tr _ - | rev | cut -c 4- | rev)
        dinkum_new_py_link="$dinkum_curr_py_dirname"/"$dinkum_new_py_basename"

        # replace the link
        mv "$dinkum_curr_py_link" "$dinkum_new_py_link"
    done


    # Be tidy
    unset dinkum_path_dir
    unset dinkum_symlinks_dir
    unset dinkum_a_bin_dir
    unset dinkum_target
    unset dinkum_link
    unset dinkum_curr_py_link
    unset dinkum_curr_py_basename
    unset dinkum_new_py_basename
    unset dinkum_new_py_link

fi


    

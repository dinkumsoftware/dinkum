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


# Make sure required env var exists and points to a directory
if [ -d "$DINKUM_FILETREE" ] ; then

   # Put bin on the exe search path
   path_dir="$DINKUM_FILETREE/bin"
   if [ -d "$path_dir" ] ; then
      # convert to absolute path and prepend to PATH
      path_dir=$(cd "$path_dir" 2> /dev/null && pwd -P)
      export PATH="$path_dir:$PATH"
    fi
    
    # Put dinkum on python module search path
    path_dir="$DINKUM_FILETREE/.."
    if [ -d "$path_dir" ] ; then
        # convert to absolute path and prepend to PYTHONPATH
        path_dir=$(cd "$path_dir" 2> /dev/null && pwd -P)
        export PYTHONPATH="$path_dir:$PYTHONPATH"
    fi

    # Be tidy
    unset path_dir
fi


    

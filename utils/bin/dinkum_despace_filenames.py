#!/usr/bin/env python3
#<filename> dinkum_despace_filenames.py
#<path> utils/bin
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
Renames all the files/directories on the command line to remove the
space character, i.e. " ".  Each space character is normally replaced by
"_", but the substituted string can be specified by --sub_str.
'''
#<\mod_doc>

#<copyright> Copyright (c) 2020 Dinkum Software
#<lic>
'''Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
''' #</lic>

#<authors> tc    tom campbell, www.DinkumSoftware.com <todo> change to .org

#<history>
#    2020-12-19 tc Initial
#    2025-05-13 tc bug fixes
#</history>

import sys
import argparse
import textwrap    # dedent
import os


def main() :
    ''' See module doc

    Normally returns NONE
    On error, returns a printable description of the error
    '''

    # Specify and parse the command line arguments
    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__)
    )

    # Common optional arguments
    parser.add_argument("-v", "--verbose",
                        help="Print all changed filenames.",
                        action="store_true")

    parser.add_argument("-d", "--dry_run",
                        help="Nothing changed, only print what would be done.",
                        action="store_true")

    parser.add_argument("-r", "--recursive",
                        help="Rename all files in a directory and it's subdirs.",
                        action="store_true")

    # Specific optional arguments
    parser.add_argument("-s", "--sub_str",
                        default="_" ,
                        help="Specifies the string used to replace each space.\n"
                        "Default:'%(default)s'" )


    # Everything else on the command line is a file or directory
    parser.add_argument("file_or_dir", nargs="+",
                        help="File or Directory to rename without spaces")

    args = parser.parse_args()

    # Iterate thru file/dir-names to despace
    for ford in args.file_or_dir :
        error_msg = despace_filename( ford, args.sub_str,
                                      verbose=args.verbose,
                                      dry_run=args.dry_run,
                                      recursive=args.recursive)
        # Bail on any error
        if error_msg : return error_msg
            

    # Successfully done
    return None

def despace_filename( file_or_dirname, sub_str, **kwargs) :
    ''' If file_or_dirname has any spaces in it's name, it will be renamed replacing each space
    with sub_str.
    In kwargs:
      verbose  =True will print the renamed file_or_dir on sys.stdout.
      dry_run  =True will print any would be renamed file_or_dir's on sys.stdout, but NOT actually rename it.
      recursive=True will descend into any directories, despacing all their contents.
    
    Normally returns None.  Returns human readable error message on error.
    '''

    # Pull what we know from kwargs
    verbose  = kwargs.get( "verbose"  , False)
    dry_run  = kwargs.get( "dry_run"  , False)
    recursive= kwargs.get( "recursive", False)

    # Figure out what we are dealing with
    isdir  = os.path.isdir (file_or_dirname)
    isfile = os.path.isfile(file_or_dirname)

    # Make sure file_or_dirname exists
    if not isdir and not isfile :
        return "%s is NOT a file or directory." % file_or_dirname

    # Replace all the spaces
    new_file_or_dirname = file_or_dirname.replace(" ", sub_str)
    
    # Any thing to do ?
    if new_file_or_dirname != file_or_dirname :

        # We need to rename file_or_dirname to new_file_or_dirname
        if dry_run or verbose :
            # Tell 'um what we are doing.
            print ("'%s' ==> '%s'" % (file_or_dirname, new_file_or_dirname))

        if not dry_run :
            os.rename( file_or_dirname, new_file_or_dirname)

    # Recursive if required
    if isdir and recursive :
        for (dirpath, dirnames, filenames) in os.walk(new_file_or_dirname) :

            # Call ourself for every file or directory
            for ford_name in filenames + dirnames : 
                despace_filename( os.path.join(dirpath, ford_name), sub_str, **kwargs)
            
            # We only need one invocation of os.walk as we call ourselves to do the recursion.
            break


# main() launcher
if __name__ == '__main__':
    try:
        # This handles normal and error returns
        err_msg = main()    # returns human readable str on error
        if err_msg :
            err_msg = "ERROR:" + err_msg  # Label the output
        sys.exit( err_msg )

    except KeyboardInterrupt as e:
        # Ctrl-C
        sys.exit( "KeyboardInterrupt: Probably Control-C typed.")

    except SystemExit as e: # sys.exit()
        # Just pass it along
        raise e

    # Let any other Exception run it's course

    assert False, "Can't get here"



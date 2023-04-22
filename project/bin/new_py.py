#!/usr/bin/env python3
#<filename> [filename] new_py.py
#<path>     [path]     project/bin

#<repo> https://github.com/dinkumsoftware/dinkum.git

#<copyright> Copyright (c) 2023 Dinkum Software
#<lic> Licensed under the Apache License, Version 2.0 (the "License");

'''
Used to create a new python element:
    exe      => name.py  ; executable for /bin directory
    module   => name.py  ; python module
    package  => dir:name and name/__init__.py

The file is created in the current directory by
default.  Use --output_dir to create it somewhere else.

version: {version}
'''
version="0.0"

# 2023-04-22 tc Initial

import sys
import argparse
import textwrap    # dedent
import os.path      # basename()
import shutil       # copy()

def template_file_dir() :
    ''' returns the location of *.py template files
    '''
    return os.path.join( os.environ.get("DINKUM_FILETREE"),
                         "project", "templates", "python")

def main() :
    ''' See module doc

    Normally returns NONE
    On error, returns a printable description of the error
    '''

    # Specify and parse the command line arguments
    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__.format(version=version))
    )

    parser.add_argument("-V", "--version",
                        help="Show the version number of the program.",
                        action="store_true")

    # Figure out what "new" file they want
    parser.add_argument ('what', choices=['exe', 'module', 'package'],
                         help="What kind of new file you want")

    # What they want to name the new file/dir
    parser.add_argument('name',
                        help="name of new file (sans .py) or directory for a package")


    # Figure out where they want to generate the file
    parser.add_argument('-o', "--output_dir",
                        default=".",  # the current directory
                        help="directory to generate the files in")

    

    # Common optional arguments
    parser.add_argument("-v", "--verbose",
                        help="Print what doing",
                        action="store_true")

    #parser.add_argument("-d", "--dry_run",
    #                    help="Nothing changed, only print what would be done.",
    #                    action="store_true")

    args = parser.parse_args()

    # Just printing the version # ?
    if args.version :
        prog_name = os.path.basename( sys.argv[0])
        print ( "%s: version: %s" % (prog_name, version) )
        return None # no errors

    # Code goes here 

    # Get to the directory where we want to make the files
    os.chdir( args.output_dir)
    
    # Figure out which type of file
    # The convention is that the template filename
    # is the name of args.what plus .py
    template_filename = args.what + '.py'
    output_filename   = args.name + '.py'

    # We have to special case a package as
    # it must create a directory
    if args.what == 'package' :
        # Create the package directory
        if args.verbose :
            print ("creating directory: ", args.what)
        os.mkdir (args.name)
        os.chdir(args.name)  # go there

        # and set what file we are copying there
        template_filename = "package__init__.py"
        output_filename   = "__init__.py"

    # We are in the directory where we want to copy
    # template_filename ==> output_filename
    # We prepend the template_filename's directory
    template_filename = os.path.join ( template_file_dir(),
                                       template_filename)

    if args.verbose :
        print ("%s => %s" % (template_filename, output_filename))
    shutil.copy(template_filename, output_filename)

#<lic-full>
'''Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
''' #</lic-full>


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



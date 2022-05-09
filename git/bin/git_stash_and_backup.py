#!/usr/bin/env python3
#<filename> git_stash_and_backup.py
#<path>  dinkum/git/bin
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
Makes a backup copy of the current directory (if it's under
git control) and regardless, git stashes the current git branch.

  message:          labels the git stash and backup_dir

  backup_parent_dir Where git directory is copied
                    Default: ~/git-stashed-backups/

IF the current directory is under git control, it is recursively copied to:
  <backup-dir-parent>/git-stashed-backups/<timestamp>-<de-spaced message>/<curr-dir-basename>/

All <spaces> in the messages changed to '_' to avoid spaces in directory names.

############ <todo> need to repo/branch name in the directory name or a subdir above.
###########         maybe 

An example:
user@host:$ pwd
where-ever/dinkum-sandbox/subdir

user@host:$ git status
Changes not staged for commit:
	modified:   bar
	modified:   sub-sub-dir/oof
Untracked files:
	x

user@host:$ git_stash_and_backup.py "label we use"
Backing up from: ~/dinkum-sandbox/subdir
             to: ~/git-stashed-backups/2022-05-09z00:30:40-label_we_use/subdir
executing:git stash push -m "label_we_use"
Saved working directory and index state On main: label_we_use


user@host:$ git stash list
stash@{0}: On main: how we label this

user@host:$ git status
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	x

user@host:$ tree ~/git-stashed-backups/2022-05-09z00:30:40-label_we_use/
~/git-stashed-backups/2022-05-09z00:30:40-label_we_use/
└── subdir
    ├── bar
    ├── foo
    ├── sub-sub-dir
    │   ├── oof
    │   └── rab
    └── x

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
# 2022-05-08 tc Initial
#</history>

import sys
import argparse
import textwrap    # dedent

from os      import * # 
from os.path import * # dirname()
from shutil  import * # copytree()

from subprocess import call


import dinkum.time
from   dinkum.git.utils import *



def main() :
    ''' See module doc

    Normally returns NONE
    On error, returns a printable description of the error
    '''

    # Specify and parse the command line arguments
    # USAGE: git-stash-and-backup   message [<backup_parent_dir>/]

    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__)
    )

    # Required arguments
    parser.add_argument("message",
                        help="how backup dirname and git stash labeled")

    # Optional backup directory 
    args = parser.add_argument('backup_parent_dir', # argparse does not like - and _
                               help="Parent of the directory where current directory is copied",
                               nargs='?',
                               default=abspath(expanduser('~')))

    args = parser.parse_args()

    # real work starts here ..................................

    # All <spaces> in the messages changed to '_' to avoid spaces in directory names.
    message = args.message.replace(' ', '_')

    # Is the current directory under git control?
    curr_dir = getcwd()
    if is_a_gitfile(curr_dir) :
        # yes, backup the directory
        backup_dir = git_stash_and_backup_backup_dir(args.backup_parent_dir,
                                                     message,
                                                     curr_dir)
        # what we are gonna do
        print ("Backing up from: %s" % curr_dir  )
        print ("             to: %s" % backup_dir)
               
        # do the backup
        makedirs( dirname(backup_dir) )  # Make sure we have a place to put the stuff
        copytree( curr_dir, backup_dir)

    # Do the stash regardless
    git_cmd = 'git stash push -m "%s"' % message
    print("executing:" + git_cmd)
    system(git_cmd)
    

def git_stash_and_backup_backup_dir(backup_dir_parent, message, curr_dir) :
    '''\
    returns the absolute pathname of where git_stash_and_backup should
    places the file.

    From the module doc:
    <backup_dir_parent>/git-stashed-backups/<timestamp>-<de-spaced message>/<curr-dir-basename>/

    '''
    return join(backup_dir_parent,
                "git-stashed-backups",
                dinkum.time.timestamp() + '-' + message, 
                basename(curr_dir)
                )
                
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



#filename: utils.py
#path: dinkum/file
#repo: http://github.com/dinkumsoftware/dinkum.git

'''
A series of file support utilities.

Run pydoc for a table of contents

AUTHOR
    dinkumsoftware.com/tc

LICENSE
    Copyright(c) 2019 Dinkum Software
    Licensed under Apache Version 2.0, January 2004
    http://www.apache.org/licenses/
    Full license text at end of file.
'''
# history:
# 2019-05-06 tc@DinkumSoftware.com Initial

import os
from shutil    import copy2
from itertools import chain
from shutil    import copy2
from textwrap  import dedent

def copytree(src_dir, des_dir, verbose=0, dry_run=0, ignore_func=None) :
    '''Recursively copies "src_dir" INTO "des_dir".
    i.e. src_dir=/a/b/c gets copied into des_dir/c/....
    "src_dir" and "des_dir" must exist. Exceptions raised if not the case
    Symbolic links are copied "as is", i.e. not referenced

    It does NOT copy over any files or directories.  It raises an exception
    if this is the case.

    if verbose is non-zero, announces what is being done to stdout.
    if dry_run is non-zero, only announces what it WOULD do, but doesn't do it.

    ignore_func(dir, contents) called with the current directory and all
    the contents of that directory, a la os.listdir().  It is expected to return
    a list that is a subset of "contents" of the files/dir TO COPY.
    '''

    # Inforce our assumptions
    if not os.path.isdir(src_dir) :
        err_msg="{src_dir} is NOT a directory or does not exist.".format(src_dir=src_dir)
        class srcNotExistingDir(Exception) : pass
        raise srcNotExistingDir(err_msg)
    src_dir = os.path.expanduser(src_dir)
    src_dir = os.path.abspath(src_dir)

    # Since we are called recursively
    # lower level directories won't exist on a dry_run.
    # so we can can't check that
    if not dry_run and not os.path.isdir(des_dir) :
        err_msg="{des_dir} is NOT a directory or does not exist.".format(des_dir=des_dir)
        class srcNotExistingDir(Exception) : pass
        raise srcNotExistingDir(err_msg)
    des_dir = os.path.expanduser(des_dir)
    des_dir = os.path.abspath(des_dir)

    # Create the destination directory (same name as basename of src_dir)
    # in the destination parent dir
    des_dir = os.path.join( des_dir, os.path.basename(src_dir))
    mkdir_with_parents( des_dir, verbose, dry_run, src_dir)

    # Get list of src contents to copy
    # These are basenames, i.e. no path
    contents = os.listdir(src_dir)
    if ignore_func :
        # let user filter it
        contents = ignore_func(src_dir, contents)

    # Separate the list into files, symlinks, and dirs
    # and sort them.  This is so a verbose output is pleasently ordered
    files = []
    symlinks = []
    dirs=[]
    unknowns=[] # none of the above, treat as files
    for basename in contents :
        # construct full pathname for testing type
        # We will return [] of only basenames (what's in contents)
        pathname = os.path.join(src_dir, basename) 
        if os.path.isdir(pathname) :
            dirs.append(basename)
        elif os.path.islink(pathname) :
            symlinks.append(basename)
        elif os.path.isfile(pathname) :
            files.append(basename)
        # we treat everything else as a file (file, socket, fifo)
        elif os.path.exists(pathname) :
            unknowns.append(basename)
        else :
            # Anything else is an error
            err_msg = '''IMPOSSIBLE SITUATION: Does not exist: {pathname}'''.format(pathname=pathname)
            class ImpossiblePlacePathnameDoesNotExist(Exception) : pass
            raise ImpossiblePlacePathnameDoesNotExist(err_msg)



    # Sort first so verbose output in alphabetical order
    for d in [dirs, symlinks, files, unknowns] :
        d.sort()      # Make the output order pretty

    # Do the copies
    # We treat unknows (sockets, fifos, whatever) as if they were a file
    # files,symlinks, and dirs only have basenames in them (no path)
    for f in chain(files, unknowns) :
        src = os.path.join(src_dir, f)
        des = os.path.join(des_dir, f)
        announce("file", verbose, dry_run, src, des)
        if not dry_run :
            copy2(src, des_dir)

    for s in symlinks :
        src = os.path.join(src_dir, s)
        des = os.path.join(des_dir, s)
        announce("symlnk", verbose, dry_run, src, des)
        if not dry_run :
            curr_link_contents = os.readlink(src)
            os.symlink( curr_link_contents, des)

    # For directories, we just recurse
    for d in dirs :
        src = os.path.join(src_dir, d)
        copytree( src, des_dir, verbose, dry_run, ignore_func)


def mkdir_with_parents(dir, verbose=0, dry_run=0, src_dir_for_labeling_only=None) :
    '''Creates directory "dir" and all required parents.
    It is an error if it exists.  Exception raised.

    if verbose is non-zero, announces what is being done to stdout.
    if dry_run is non-zero, only announces what it WOULD do, but doesn't do it.

    "src_dir_for_labeling_only" is only used for verbose announcements.
    It is passed along to announce().  If this is part of a copytree() it
    should be the directory in the source tree which corresponds to "dir"
    '''

    # Say what we are going to do
    announce("mkdir", verbose, dry_run, src_dir_for_labeling_only, dir )
    if not dry_run :
        # Do it
        os.makedirs( dir )


# "static" data for announce()
#  Set  with label=mkdir
#  Used with label=file -or- symlnk
_announce_src_dir    = None
_announce_des_dir    = None
_announce_indent_str = ""

def announce(label, verbose, dry_run, src, des) :
    '''
verbose/dry_run tool for copytree() and the like.
It's job is tell the user what is being copied or
created.

If either "verbose" or "dry_run" or true, it in general
prints a line of the form:
  <label>: <src>      =>  <des>

<src> and <des> are expected to be full pathnames

We special case a <label>s of "file","symlnk" or "mkdir" to strip off the pathnames of files
readability and to keep from running over the alloted width.

An example:
mkdir: /home/tc/projects/dinkum/               => /home/tc/.dinkum/git-copy-root/dinkum/
File:   CONVENTIONS.txt                        =>  CONVENTIONS.txt
File:   LICENSE                                =>  LICENSE
mkdir: /home/tc/projects/dinkum/backups        => /home/tc/.dinkum/git-copy-root/dinkum/backups
mkdir: /home/tc/projects/dinkum/backups/bin    => /home/tc/projects/dinkum/backups/bin       
File:     dinkum-root-rsync-push               =>    dinkum-root-rsync-push

'''
    # static var's just above where we remember stuff from call to call
    global _announce_src_dir
    global _announce_des_dir
    global _announce_indent_str

    # Always be verbose on a dry_run
    if dry_run :
        verbose = True

    # anything to do?
    if not verbose :
        return # nope

    # Format parameters
    label_width = len("symlnk") + 1 # Field width for label, +1 for :
                                    # This is currently longest label
    des_offset  = 50 # where to start printing destination
    arrow = '=> '    # how we separate src and des

    # Special case files
    # We test for mkdir to remember des directory
    if label == "mkdir" :
        _announce_src_dir = None  # Gets set on first file: label
        _announce_des_dir = des
        _announce_indent_str = "" # Gets set on first file label
    # <todo> tack on a / here

    stripping_paths = (label == "file") or (label == "symlnk")

    if stripping_paths :
        # First file after a mkdir?
        if not _announce_src_dir :
            # Yes, remember the directory of the source
            _announce_src_dir = os.path.dirname(src)

            # Figure out how much to indent each File
            # The deeper in the copied tree, the more indent
            # We start looking from bottom of tree up and
            # stop when a directory doesn't match
            spaces_per_depth_in_tree = 2
            _announce_indent_str = ""
            src_dirs_in_path = _announce_src_dir.split( os.path.sep )
            des_dirs_in_path = _announce_des_dir.split( os.path.sep )

            src_dirs_in_path.reverse()    # we will compare from bottom up
            des_dirs_in_path.reverse()
            
            for (sd, dd) in zip(src_dirs_in_path, des_dirs_in_path) :
                if sd == dd :
                    # Still in part of tree being copied
                    _announce_indent_str += ' ' * spaces_per_depth_in_tree

        # Strip off leading pathnames and indent it
        src_dir = os.path.dirname(src)
        src = _announce_indent_str + os.path.basename(src)

        des_dir = os.path.dirname(des)
        des = _announce_indent_str + os.path.basename(des)

        # Sanity check
        # The dirs we just stripped off should match what
        # we remember from a call with label=mkdir
        if src_dir != _announce_src_dir :
            err_msg = '''\
                Source Directory paths don't match.
                prior:{prior} curr:{curr}
                Probable Software error.
                Perhaps no intervening announce("mkdir",..) call ? '''
            err_msg=dedent(err_msg.format( prior=_announce_src_dir,
                                               curr=src_dir))
            class SourceDirsDontMatch(Exception) : pass
            raise SourceDirsDontMatch(err_msg)

        if des_dir != _announce_des_dir :
            err_msg = '''\
                Source Directory paths don't match.
                prior:{prior} curr:{curr}
                Probable Software error.
                Perhaps no intervening announce("mkdir",..) call ? '''
            err_msg=dedent(err_msg.format( prior=_announce_des_dir,
                                               curr=des_dir))
            class DestinationDirsDontMatch(Exception) : pass
            raise DestinationDirsDontMatch(err_msg)


        # Modify source and destination
        # We just use the basename.
        src = os.path.basename(src)
        des = os.path.basename(des)

        # We indent it over one space for the depth of the enclosing
        # directory
        # Figure out the indent strings


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


# full-license:
'''
Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {yyyy} {name of copyright owner}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.        
'''

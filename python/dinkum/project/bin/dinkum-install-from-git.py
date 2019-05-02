#!/usr/bin/env python

"""
DESCRIPTION
 This installs all the dinkumsoftware programs & code in ~/.dinkum/git-copy
     by copying files from the git clone of dinkumsoftware.
 It puts symbolic links in ~/doc/dinkum/* to all the documentation
     files under ~/.dinkum/git-copy
 It makes mild alteration to ~/.bashrc
     Puts ~/dinkum/git-copy/bin on the PATH
     Puts ~/.dinkum/git-copy/python on PYTHONPATH
 It does NOT require sudo.
 It assumes you have done a full git checkout of the source. (See EXAMPLES)

 It's OK to run this as many times as you like.  If a new version of
 something shows up in git, you can rerun this to get it on your machine

 Any existing installation from git is UNINSTALLED and then reinstalled.
 This is due to limitations of some underlying tools.

EXAMPLES
  cd ~/<somewhere>
  git clone http://github.com/dinkumsoftware/dinkum.git
  <somewhere>/bin/dinkum-install-from-git

  [optional] rm -rf ~/<somewhere>/dinkum # Don't need git copy after install
                                         # But feel free to keep it
To undo these actions:
  rm -rf ~/.dinkum
  [optional] edit ~/.bashrc (see end of file) to remove dinkum stuff.
            # This is not required, won't break anything if you leave it in
  <todo> fix this

USAGE
dinkum-install-from-git
optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Announce what it is doing
  -d, --dry-run  Announce what WOULD do, but don't do it

  You will have to log out and log in to pick up the .bashrc changes.
  If you want to just try it in a terminal window:
      bash

EXIT STATUS
    0  All is good
    1  Something went wrong, maybe error printout
    2  Some kind of exception tossed

AUTHOR
    <todo> move this out of docstring
    2019-04-30 tc@DinkumSoftware.com Initial
    2019-04-30 tc@DinkumSoftware.com Switched to shutil.copytree()

LICENSE
    Copyright(c) 2019 Dinkum Software
    Licensed under Apache Version 2.0, January 2004
    Full text at end of file.
    http://www.apache.org/licenses/

VERSION
    0.0
"""
# <todo> only put version # one place, f'string?
program_version = 0.0

import sys, os, traceback, argparse
import textwrap # for getting file docs to screen


# Other imports from dinkum.x.y.z must wait a bit
# until PYTHONPATH is set up

#  returned "err_msg" will be printed for user
def main ():
    ''' dinkum-install-from-git
optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Announce what it is doing
  -d, --dry-run  Announce what WOULD do, but don't do it

Normally returns None.  On error, return "err_msg" .

We install by copying from a git clone of dinkumsoftware to the
directory ~/.dinkum.  

    Find the git root dir and validate it
    Find and use python library code in git
    Enumerate all the subdirs to publish
'''

    # Specify and parse the command line arguments
    parser = argparse.ArgumentParser(
        # print document string "as is" on --help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__))
    parser.add_argument("-v", "--verbose",
                        help="Announce what it is doing",
                        action="store_true")
    parser.add_argument("-d", "--dry-run",
                        help="Announce what WOULD do, but don't do it",
                        action="store_true")
    parser.parse_args()
    args = parser.parse_args()
    verbose = args.verbose
    dry_run = args.dry_run

    # these are fragile times as we are a dinkum install
    # program.  Can't make assumptions about where to find
    # stuff.  We expect we are running from a git clone
    # copy of dinkumsoftware.
    # <x>/dinkum                                # git root dir
    # <x>/dinkum/bin/dinkum-install-from-git    # where we live
    # <x>/dinkum/python/dinkum/...              # Where python package dirs live

    # Get our inclosing directory <x>/dinkum/bin
    our_dir = os.path.dirname (sys.argv[0] )
    our_dir = os.path.abspath(our_dir)

    # Find the git root dir <x>/dinkum
    # It should be the parent of our_dir
    # and it must contain a .git directory
    git_dirname = ".git"
    git_root_dir = os.path.dirname(our_dir)
    if not os.path.isdir ( os.path.join( git_root_dir,
                                         git_dirname)) :
        # Error
        err_msg = '''
ERROR: This program is NOT part of a dinkumsoftware git clone.
Expecting directory {} to be a git root directory.
It is not as there is no directory {}.
Run again with --help switch.
'''.format(git_root_dir,git_dirname)
        return err_msg

    # where our python packages in git live
    pkg_dir = os.path.join(our_dir, '../python' )
    pkg_dir = os.path.abspath(pkg_dir)
    
    # Validate the package directory
    if not os.path.isdir(pkg_dir) :
        err_msg='''
ERROR. Directory {} does not exist.
It is suppose to be the parent directory of dinkum python packages.
Sure you are running from a good git clone of dinkumsoftware?
Rerun with --help to see usage and description.
'''.format(pkg_dir)
        return err_msg ;

    # insert that at head of search path
    # So that we can use that software
    sys.path.insert(0, pkg_dir)

    # We can now use dinkum python package
    from dinkum.project.install import install_from_git
    install_from_git(git_root_dir, verbose, dry_run)

    # Warn them if we didn't do anything
    if dry_run :
        print "** This was a DRY-RUN.  Nothing was written. **"

    # Life is good
    return None


if __name__ == '__main__':
    try:
        # Invoke the actual program
        # It's an error if it returns anything
        main_return = main()

        if main_return :
            print main_return # ERROR: print whatever it returns
        # Pass back to the OS the proper exit code. 0 is good
        sys.exit( 1 if main_return else 0)

    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(2)



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

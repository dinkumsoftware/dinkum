#!/usr/bin/env python3
#<filename> [filename] <fixme>
#<path>  [path] <fixme>
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
    <fixme>
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
#    2020-10-02 tc Initial
#</history>

import sys

def main() :
    ''' See module doc

    Normally returns NONE
    On error, returns a printable description of the error
    '''

    pass #<fixme>

# main() launcher
if __name__ == '__main__':
    try:
        # This handles normal and error returns
        sys.exit( main() )

    except KeyboardInterrupt as e:
        # Ctrl-C
        sys.exit( "KeyboardInterrupt: Probably Control-C typed.")

    except SystemExit as e: # sys.exit()
        # Just pass it along
        raise e

    # Let any other Exception run it's course

    assert False, "Can't get here"



#!/usr/bin/env python3
#<filename> [filename] datestamp.py
#<path>  [path] dinkum/time/
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
Returns the date, e.g.
    2022-05-08z

UTC aka gmt aka zulu (hence the z)

Almost iso 8601 http://www.cl.cam.ac.uk/~mgk25/iso-time.html
deviations: 
    I use lower case z instead of T between date and time
    for readability and to designate UTC (zulu)
'''
#<\mod_doc>

#<copyright> Copyright (c) 2020-2022 Dinkum Software

#<history>
#  2005-12-01 tc  Initial
#  2006-12-06 tc  Renamed dinkum-timestamp
#                 T=>t, added z to end
#  2022-05-08 tc  t=>z, it's been a while
#                 converted to python
#</history>

import sys
import argparse
import textwrap    # dedent

import dinkum.time

def main() :
    ''' See module doc

    Normally returns NONE
    On error, returns a printable description of the error
    '''

    print (dinkum.time.timestamp())


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



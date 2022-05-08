#!/usr/bin/env python3
#<filename> [__init__.py]
#<path>  [dinkum/time/]
#<repo> https://github.com/dinkumsoftware/dinkum.git

#<mod_doc>
'''
Has useful functions and programs for dealing with time.

bin/datestamp.py and datestamp()   return 2022-05-08z
bin/timestamp.py and timestamp()   return 2022-05-08z21:52:46

Produces the current date and time UTC (aka gmt aka zulu)
in "almost" iso 8601 format:

    Standard:
        Google: "iso 8601" ==>
        http://www.cl.cam.ac.uk/~mgk25/iso-time.html

Deviations:
    I use lower case z instead of T between date and time
    for readability and to designate UTC (zulu)
'''
#<\mod_doc>

#<authors> tc    tom campbell, www.DinkumSoftware.com <todo> change to .org

#<history>
#  2005-12-01T12:15:22Z tc  Initial
#  2006-12-06           tc  Renamed dinkum-timestamp
#                           T=>t, added z to end
#  2022-05-08           tc  t=>z, it's been a while
#                           converted bash=>python __init__.py
#</history>

from time import *   # gmtime()

# The offsets into a time.struct_time
# from https://docs.python.org/3/library/time.html#time.struct_time
tm_year = 0 # 1993
tm_mon  = 1 # 1-12
tm_mday = 2 # 1-31
tm_hour = 3 # 0-23
tm_min  = 4 # 0-59
tm_sec  = 5 # 0-61 eh..why 61? not 60
tm_wday = 6 # 0-6  mon is 0
tm_yday = 7 # 1-366



def datestamp() :
    '''\
    Returns the current date, e.g.
        2005-12-01z

    see module doc for more info
    '''

    # get the time (zulu)
    struct_time = gmtime()

    return "%04d-%02d-%02dz" % ( struct_time[tm_year],
                                 struct_time[tm_mon ],
                                 struct_time[tm_mday])


def timestamp() :
    '''/
    Returns the current time, e.g.
        2022-05-08z21:52:46    
    see module doc for more info
    '''

    # get the time (zulu)
    struct_time = gmtime()

    return datestamp() + "%02d:%02d:%02d" % ( struct_time[tm_hour],
                                              struct_time[tm_min ],
                                              struct_time[tm_sec ])


#<copyright> Copyright (c) 2020-2022 Dinkum Software
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




#<unittests>
import unittest

class Test_time(unittest.TestCase):
        
    #           1         2
    # 0.........0.........0
    #  2022-05-08z
    def test_datestamp(self) :
        self.assertEqual( len(datestamp()), 11)
        
    #           1         2
    # 0.........0.........0
    #  2022-05-08z21:52:46
    def test_timestamp(self) :
        self.assertEqual( len(timestamp()), 19 )


#</unittests>

if __name__ == "__main__" :
    # Run the unittests
    unittest.main()


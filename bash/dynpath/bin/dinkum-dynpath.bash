# http://github.com/dinkumsoftware/dinkum.git
# bash-addons/dynpath/bin/dinkm-dynpath.bash
# 
# expected to be source from .bashrc
#
# echos to stdout the path to use in PS1 prompt:
#    normally current path
#     but shortens it if it's longer than $COLUMNS/4, so that
#
# <todo> fix the eclise characters.
# /usr/share/doc/foo would become /u-/s-/d-/foo
# Usage: PS1="\u@\h \$(_dynpath) \$ "

# 2016-11-22 forked from https://gist.github.com/ehamberg/1197104
# 2016-11-22 tc@DinkumSoftware Bug fixes:
#    Wasn't inserting ~
#    eclipse char (...) wasn't printing.  Replaced with -
# 2016-11-28 tc@DinkumSoftware.com Neutered, buggy
# 2016-12-09 tc@DinkumSoftware.com debugging

_dynpath()
{
  # Get current directory, replacing /home/username with ~
  CURR="${PWD/#$HOME/'~'}"
  MAX_WIDTH=$(($COLUMNS/4))

  # while   prompt to long        and has dirs to shorten (no -)
  while [[ ${#CURR} -gt $MAX_WIDTH && $CURR =~ /.[^-].*/ ]] ; do
    # shorten another directory
    #  /dirname/  ===>  /d-/
    CURR=$(echo ${CURR}|sed 's,/\(\.\?.\)[^-/]\+/,/\1-/,')
  done
  echo $CURR
}


# Useful snippets for testing this function
# cd <test-dir>
# mkdir -p one/two/three/four/five/six/seven/eight/nine/ten/eleven/twelve/thirteen/fourteen/fifteen/sixteen/seventeen/eighteen/nineteen/twenty/twentyone/twentytwo/twentythree/twentyfour/twentyfiv/twentysix/twentyseven/twentyeight/twentynine/thirty
#
# cd one
# for (( i=1 ; i<300 ; i++ )) ; do _dynpath ; cd $(ls) ; done ; cd<test-dir>/one




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
# /usr/share/doc/foo would become /u…/s…/d…/foo
# Usage: PS1="\u@\h \$(_dynpath) \$ "

# 2016-11-22 forked from https://gist.github.com/ehamberg/1197104
# 2016-11-22 tc@DinkumSoftware Bug fixes:
#    Wasn't inserting ~
#    eclipse char (...) wasn't printing.  Replaced with -
# 2016-11-28 tc@DinkumSoftware.com Neutered, buggy

_dynpath()
{
  # It is currently buggy
  # Just use the full 

  # Get current directory, replacing /home/username with ~
  CURR="${PWD/#$HOME/'~'}"
  MAX_WIDTH=$(($COLUMNS/4))

  # &&&&& PATCH
  echo $CURR
  return
  # &&&&& 

  while [[ ${#CURR} -gt $MAX_WIDTH && $CURR =~ /.[^-].*/ ]] ; do
    CURR=$(echo ${CURR}|sed 's,/\(\.\?.\)[^-/]\+/,/\1-/,')
    echo "debug:$CURR"
  done
  echo $CURR
}

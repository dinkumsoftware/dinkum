#returns current path, but shortens it if it's longer than $COLUMNS/4, so that
# /usr/share/doc/foo would become /u…/s…/d…/foo
# Usage: PS1="\u@\h \$(_dynpath) \$ "

# Initial from https://gist.github.com/ehamberg/1197104
# 2016-11-22 tc@DinkumSoftware Bug fixes:
#    Wasn't inserting ~
#    eclipse char (...) wasn't printing.  Replaced with -

_dynpath()
{
  # Get current directory, replacing /home/username with ~
  CURR="${PWD/#$HOME/'~'}"
  MAX_WIDTH=$(($COLUMNS/4))

  while [[ ${#CURR} -gt $MAX_WIDTH && $CURR =~ /.[^-].*/ ]] ; do
    CURR=$(echo ${CURR}|sed 's,/\(\.\?.\)[^-/]\+/,/\1-/,')
    echo "debug:$CURR"
  done
  echo $CURR
}

#returns current path, but shortens it if it's longer than $COLUMNS/4, so that
# /usr/share/doc/foo would become /u…/s…/d…/foo
# Usage: PS1="\u@\h \$(_dynpath) \$ "

_dynpath()
{
  CURR="${PWD/#$HOME/~}"
  MAX_WIDTH=$(($COLUMNS/4))

  while [[ ${#CURR} -gt $MAX_WIDTH && $CURR =~ /.[^…].*/ ]] ; do
    CURR=$(echo ${CURR}|sed 's,/\(\.\?.\)[^…/]\+/,/\1…/,')
  done
  echo $CURR
}
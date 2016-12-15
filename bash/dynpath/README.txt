http://github.com/dinkumsoftware/dinkum.git
bash-addons/dynpath/README.txt

A bash enhancement which automatically shrinks the bash prompt
when it gets too long.  This happens when one gets "deep" in
a filesystem tree.

<todo> provide example

2016-11-21 tc@DinkumSoftware.com Initial
2016-11-27 tc@DinkumSoftware.com Refactored out of bash-addons

Table of contents:
    bin/dynpath.bash    Must be sourced out of bash-rc


To install:
   cd <whereever>
   git clone http://github.com/dinkumsoftware/dinkum.git
   dinkum/bash-addons/dynpath/bin/dinkum-install-bash-addons
       # maybe alters ~/.bashrc to source dinkum-bashrc
       # copies ../dinkum-bashrc to ~/.dinkum/bash-addons/bin
       # copies *.bash (scripts be sourced) to ~/.dinkum/bash-addons/dynpath/bin
   rm -rf dinkum # optional if you like to be tidy, dinkum/... not required after install

To uninstall:
   rm -rf ~/.dinkum/bash-addons/dynpath


dinkum-dynpath.bash:
    Must be sourced (See to install above)
    dinkum-bashrc sources dinkum-dynpath.bash to define a bash function: _dynpath()
                  Modifies PS1 to call _dynpath()
Forked from from:
        https://gist.github.com/ehamberg/1197104
        2016-11-21
        1197104-9ffb9b100edb60e425d307389ed0c0066da4c393.zip



dinkum/bash/README.txt

A collection of bash enhancements

2016-11-21 tc@DinkumSoftware.com Initial
2016-12-06 tc@DinkumSoftware.com Added bash-cheatsheet.txt

Table of contents:
    bash-cheatsheet.txt  bash commands I can never remember      
    dynpath    Automagically shrink bash prompt when it is too long


To install:
   cd <whereever>
   git clone http://github.com/dinkumsoftware/dinkum.git
   dinkum/bash/bin/dinkum-install-bash-addons
       # maybe alters ~/.bashrc
       # copies scripts to ~/.dinkum/bash/


dynpath:
    requires .bashrc modified to source .dinkum/bash/dinkum-bashrc
    dinkum-bashrc sources dynpath.bash to define a bash function: _dynpath()
                  Modifies PS1 to call _dynpath()
    Taken from:
        https://gist.github.com/ehamberg/1197104
        2016-11-21
        1197104-9ffb9b100edb60e425d307389ed0c0066da4c393.zip



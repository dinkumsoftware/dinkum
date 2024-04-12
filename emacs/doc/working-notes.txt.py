f''' 

2024-01-21 tc

For many years I've been wanting to edit text boxes on the net with emacs.
The problem has gotten much worse as the gitHubs/gitLabs/micros**t Teams become
more prominent.  Each has it's on syntax.  Their handling of lists and the like
isn't too my liking. So ...

This is also my first use of changing:
    working-notes.txt into working-notes.txt.py with running text in the doc string.
    <done> first bug, emacs is in python-mode and doesn't handle tabs
           the way I want. fixed. go to emacs text mode.

using edit-server.el forgot where I got it from.

Installed ok on emacs.
    note: There is different init code for already running emacs
    and "emacs --daemon". src: edit-server.el reflected in tc-init.emacs

    Had to put in a chrome extension.
    Google install of extension went smoothly.

First click of icon/edit button brought up a window
in already running emacs and edit's went fine.

What I couldn't do was "write" the buffer back to the web page.

Question to stackoverflow:

emacs edit-server.el can't save buffer to web page

Just installed emacs edit-server.el and it's associated Chrome extension.

Install went well.

Only problem I have is I couldn't figure out to "write" the emacs buffer back to web page.  All I saw was web buffer flashing yellow, but no editted text.

I tried various combinations of ^x^m , save etc.



'''


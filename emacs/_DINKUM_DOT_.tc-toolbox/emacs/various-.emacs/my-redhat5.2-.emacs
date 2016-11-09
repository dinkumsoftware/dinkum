;;.emacs
;; Emacs private customizations
;;
;; 21-jul-97   Copied from bugfest, merged tcs private
;;             customizations from .emacs and tc/vg
;;             common stuff from locusers
;; 23-july-97  Code to get emacs to find my private mock-lisp
;;             Bound F3 to date-stamp
;;             Wrote and bound F4 to date-and-sign
;;             Bound F9 to undo
;; 30-Jul-97   Made F1 do a pwd, Made F7 do a cd, F8 a shell
;; 04-Aug-97   Set up framework for private customizations so
;;             this file remains managable
;; 06-Aug-97   Tried to install cc-mode 5.14, failed
;; 29-jan-98   Ported to Linux as part of ~tc/.tc-toolbox
;;  3-Feb-98   Changed ~ to to ~tc


;; To Do
;;     F10		redo
;;     C-X C-E  compile always write the modified files,
;;              Maybe be smarter about makefile that is invoked


;; Linux Directory Structure
;; ~tc
;;   .emacs          ; symbolic link to ~tc/.tc-toolbox/emacs/.emacs
;;   .tc-toolbox
;;      emacs
;;        .emacs     ; This file
;;        mylisp     ; directory where all my custom mock lisp lives



;; Where all the emacs add-ons live
(defvar local-emacs-base-install-directory "~tc/.tc-toolbox/emacs"
    "The directory which contains all of the add on emacs packages
    subdirectories.  Used by init-add-on-package.
    29-Jan-98 tc@dinkum-software.com "
)

;; Each addon package has its own subdirectory in
;; 'local-emacs-base-install-directory.  The file AAA.emacs in that
;; subdirectory is eval'ed.  Put all customizations and load's there
     (load (concat local-emacs-base-install-directory "/mylisp/" 
                   "init-add-on-package" ))  ;; does all the work


;; cc-mode
;; (init-add-on-package "ftp.python.org-pub-emacs")

;; My customizations.  Mostly keybinds
(init-add-on-package "mylisp")

;; Tack current directory (nil) on the front of load-path
(setq load-path (append (list nil) load-path))


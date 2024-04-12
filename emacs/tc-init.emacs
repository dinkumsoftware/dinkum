;; tc-init.emacs
;;
;; All of tc's user based emacs customization
;; Usage:  Add following line to ~/.emacs or ~/.emacs.d/init.el
;;         (load "~/.emacs.d/tc-init.emacs")
;; -or- run
;;      https://github.com/dinkumsoftware/dinkum.git
;;      dinkum/emacs/bin/dinkum-install-tc-emacs

;; 04-Aug-97 tc Initial, moved from .emacs
;; 20-Mar-98 tc Changed date-and-sign from
;; 21-Apr-01 tc Set the background color
;;                                 new-h-file, new-cc-file
;;  8-Apr-04 tc on whoops
;;                                   (menu-bar-enable-clipboard)
;;                                   made F7 and F8 do a shell to
;;                                     avoid the vncviewer F8 trap
;;                                   made F1 do nothing(was Polaroid cd)
;;  9-Dec-04 tc Removed set-backgorund-color "Thistle"
;;  3-May-05 tc Getting clipboard to work on Fedora Core 3
;;                                   removed: (menu-bar-enable-clipboard)
;;                                    added:   (setq x-select-enable-clipboard t)
;;                                  Changed background colors:
;;                                      tc          thistle
;;                                      root        AliceBlue
;;                                      other       OliveDrab
;;  4-May-05 tc Fedora Core 3; getting ls to not issue
;;                                 terminal control chars
;;                                 (add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)
;; 2007.05.06 tc
;;   Fedora 7 test 4  Changed my emacs customization approach.
;;   Retired the old emacs add-ons with AAA.emacs that I had been using.
;;   Now require one line modification of ~/.emacs, which reads this file.
;;   Combed thru years of customizations and tossed some stuff
;; 2016-11-10 tc Moved from svn to git.
;;                                  changed names (tc-init.emacs) and locations (~/.emacs.c)
;;                                  do  not change background color
;;   
;; 2019-11-07 tc get emacs shells to read ~/.bashrc
;; 2020-04-28 tc my-insert-file-name
;; 2022-02-05 tc put in use-package to rebind C-g to 
;;               https://github.com/jwiegley/use-package.git
;; 2022-02-05 tc Remap C-g from keyboard-quit => keyboard-quit-context"
;;               Make a single C-g leave minibuffer instead of two C-g's
;; 2023-05-09 tc package gitlab https://github.com/nlamirault/emacs-gitlab
;;               didn't work.  Dependency woes.
;; 2024-01-16 tc https://wikemacs.org/wiki/Edit_with_Emacs


;;;-----------------------------------------------------------------------
;; **** package gitlab https://github.com/nlamirault/emacs-gitlab
;; Fails on require(s) in emacs-gitlab/gitlab.el
;;(add-to-list 'load-path "~/.emacs.d/emacs-gitlab")
;;(require 'gitlab)

;;;-----------------------------------------------------------------------
;; Set an emacs variable with this directory name (where tc.emacs lives)
;; Any stuff that gets added on, ought to be go in it's own sub-directory
;; in this directory.  Any one-liner kind of stuff that is requested in .emacs
;; can go in this file.

(defvar tc-emacs-addons-directory "~/.emacs.d"
    "The directory which contains all of the add on emacs packages
    subdirectories that are part of tc's customizations."
)

;; ****  tc's customizations from subdirectory: tc-lisp

    ;; Build up full pathname of subdir so AAA.emacs can use it
    (defvar tc-lisp-subdirectory
        (concat tc-emacs-addons-directory  "/tc-lisp")
	"The directory which contains tc written lisp code.  See tc-init.emacs"
    )

    ;; Stick my private lisp directory at the front of the search
    (setq load-path (append (list tc-lisp-subdirectory)
                     load-path))

    ;; load up function definitions that tc wrote
    (load "date-stamp")
    (load "date-and-sign")
    (load "scroll-one")
    (load "save-all-buffers")
    (load "my-insert-file-name")
;;######################################    (load "keyboard-quit-context")

    ;; execute more code
    ;;  (load "tc-diddle-background-color.emacs") ; use the default
    (load "tc-key-mappings.emacs")

    ;; Behaviour changes
    ;; Spaces for tab.... always
    (setq-default indent-tabs-mode nil)
    (setq-default tab-width          4)

    ;; These are disabled by default, turn 'um on
    (put 'narrow-to-region 'disabled nil)
    (put 'downcase-region  'disabled nil)
    (put 'upcase-region    'disabled nil)

    ;; Connect up OS clipboard with our yank/stuff
    ;; (menu-bar-enable-clipboard)    No longer needed in Fedora Core 3
    (setq x-select-enable-clipboard t)

    ;; always end a file with a newline
    (setq require-final-newline 'query)

    ;; get emacs shells to use bash and read ~/.bashrc
    ;; Thanks to
    ;; https://stackoverflow.com/questions/12224909/is-there-a-way-to-get-my-emacs-to-recognize-my-bash-aliases-and-custom-functions/12229404#12229404
    (setq shell-file-name "bash")
    (setq shell-command-switch "-ic")

    ;; https://wikemacs.org/wiki/Edit_with_Emacs
    ;; <todo> ? Probably want to refactor this to init.el or dinkum.el
    ;; Need Chrome extension @
    ;; https://chromewebstore.google.com/detail/edit-with-emacs/ljobjlafonikaiipfkggjbhkghgicgoh?pli=1


    (add-to-list 'load-path "~/projects/dinkum/emacs/edit-server/")
    (require 'edit-server)
    (edit-server-start)

;; To open pages for editing in new buffers in your existing Emacs
;; instance:
;;
   (when (require 'edit-server nil t)
     (setq edit-server-new-frame nil)
     (edit-server-start))

;; To open pages for editing in new frames using a running emacs
;; started in --daemon mode:

;;   (when (and (require 'edit-server nil t) (daemonp))
;;     (edit-server-start))

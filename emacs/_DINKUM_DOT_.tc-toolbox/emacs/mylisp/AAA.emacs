;; AAA.emacs
;;
;; My private emacs customizations.  This was yanked from .emacs to
;; make that file read a little cleaner
;;
;; Global variables of interest
;;  local-emacs-base-install-directory      Our parent directory, c:\emacs
;;  local-emacs-base-install-subdirectory   Our directory, c:\emacs\mylisp
;;
;;
;;04-Aug-97 tc@dinkum-software.com      Initial, moved from .emacs
;;20-Mar-98 tc@dinkum-software.com      Changed date-and-sign from
;;    tc@dinkum-software.com to tc@DinkumSoftware.com
;; 21-Apr-01 tc@DinkumSoftware.com Set the background color
;;                                 new-h-file, new-cc-file
;;  8-Apr-04 tc@DinkumSoftware.com on whoops
;;                                   (menu-bar-enable-clipboard)
;;                                   made F7 and F8 do a shell to
;;                                     avoid the vncviewer F8 trap
;;                                   made F1 do nothing(was Polaroid cd)
;;  9-Dec-04 tc@DinkumSoftware.com Removed set-backgorund-color "Thistle"
;;  3-May-05 tc@DinkumSoftware.com Getting clipboard to work on Fedora Core 3
;;                                   removed: (menu-bar-enable-clipboard)
;;                                    added:   (setq x-select-enable-clipboard t)
;;                                  Changed background colors:
;;                                      tc          thistle
;;                                      root        AliceBlue
;;                                      other       OliveDrab
;;  4-May-05 tc@DinkumSoftware.com Fedora Core 3; getting ls to not issue
;;                                 terminal control chars
;;                                 (add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)


;; Pick the background color based on username
(set-background-color 
    (if (string= user-real-login-name "tc"  ) "thistle"  
    (if (string= user-real-login-name "root") "OliveDrab"
                                              "CadetBlue"
    ))
)

;; Stick my private lisp directory at the front of the search
(setq load-path (append (list local-emacs-base-install-subdirectory)
                         load-path))

;; Load up my private mock lisp
(load "scroll-one")
(load "date-stamp")
(load "new-h-file")
(load "new-cc-file")


(defun date-and-sign ()
  "Inserts the current date and email signature in current window.
  23-Jul-97"
	(interactive)
	(date-stamp)                          ; Put in the date
        (insert " tc@DinkumSoftware.com ")   ; and signature
)



;; Do my key remappings
;; F1 A regular place I go
;; EXAMPLE ONLY NOW
;;(defun cd-to-polaroid-home ()
;;"Goes to Polaroid home directory"
;;	(interactive)
;;	(cd-absolute "c:/dosstuff/polaroid/pka")
;;	(pwd)
;;)
;; (global-set-key [f1] 'cd-to-polaroid-home)


(global-set-key [f3] 'date-stamp)
(global-set-key [f4] 'date-and-sign)
(global-set-key [f7] 'shell)
(global-set-key [f8] 'shell)
(global-set-key [f9] 'undo)

(global-set-key "\C-z" 'scroll-up-one-line)
(define-key esc-map "z" 'scroll-down-one-line)
(define-key esc-map " " 'set-mark-command)

(define-key esc-map "?" 'help-command)

(define-key ctl-x-map "n" 'other-window)
(define-key ctl-x-map "p" 'other-window)
(define-key ctl-x-map "/" 'delete-horizontal-space)
(define-key ctl-x-map "g" 'goto-line)
(define-key ctl-x-map "q" 'quoted-insert)
(define-key ctl-x-map "z" 'enlarge-window)
(define-key ctl-x-map "\C-v" 'find-file)
(define-key esc-map "h" 'backward-kill-word)
(define-key ctl-x-map "d" 'delete-window)
(define-key ctl-x-map "\C-d" 'dired)

(defun save-all-buffers ()
	(interactive)
	(save-some-buffers 1 nil) )
(define-key ctl-x-map "\C-m" 'save-all-buffers)

(define-key ctl-x-map "\C-z" 'shrink-window)

(define-key esc-map "s" 'isearch-forward)
(define-key esc-map "r" 'replace-string)
(define-key esc-map "q" 'query-replace)


(define-key ctl-x-map "\C-e" 'compile)
(define-key ctl-x-map "\C-n" 'next-error)

;; Behaviour changes
;; Spaces for tab.... always
(setq-default indent-tabs-mode nil)
(setq-default tab-width          4)


;; I don't know who put this here
(put 'narrow-to-region 'disabled nil)
(put 'downcase-region  'disabled nil)
(put 'upcase-region    'disabled nil)


;; Connect up OS clipboard with our yank/stuff
;; (menu-bar-enable-clipboard)    No longer needed in Fedora Core 3
(setq x-select-enable-clipboard t)


;; stop ls from issuing terminal control chars in shell
;; showed up in Fedora Core 3
(add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)


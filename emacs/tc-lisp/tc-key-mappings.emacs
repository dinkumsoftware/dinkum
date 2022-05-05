;; tc-key-mappings.emacs
;;
;; Sets the key binds to tc's liking
;;
;; 2007.05.07  tc  Initial, moved from AAA.emacs inline code
;; 2016-11-10  tc  bug fix,
;;                   previous-window() renamed to tc-previous-window()
;;                   to avoid internal emacs name collision.
;;                   removed f7 binding to shell
;; 2022-02-05 tc   Remap C-g from keyboard-quit => keyboard-quit-context"
;;                 Make a single C-g leave minibuffer instead of two C-g's


(global-set-key [f3] 'date-stamp)         ; requires date-stamp.el
(global-set-key [f4] 'date-and-sign)      ; requires date-and-sign.el
(global-set-key [f8] 'shell)
(global-set-key [f9] 'undo)

(global-set-key "\C-z" 'scroll-up-one-line)    ; requires scroll-one.el
(define-key esc-map "z" 'scroll-down-one-line) ; requires scroll-one.el
(define-key esc-map " " 'set-mark-command)

(define-key esc-map "?" 'help-command)

(define-key ctl-x-map "n"    'other-window)
(define-key ctl-x-map "p"    'tc-previous-window)  ; requires scroll-one.el
(define-key ctl-x-map "/"    'delete-horizontal-space)
(define-key ctl-x-map "g"    'goto-line)
(define-key ctl-x-map "q"    'quoted-insert)
(define-key ctl-x-map "z"    'enlarge-window)
(define-key ctl-x-map "\C-v" 'find-file)
(define-key esc-map "h"      'backward-kill-word)
(define-key ctl-x-map "d"    'delete-window)
(define-key ctl-x-map "\C-d" 'dired)

(define-key ctl-x-map "\C-m" 'save-all-buffers) ; requires save-all-buffers.el

(define-key ctl-x-map "\C-z" 'shrink-window)

(define-key esc-map "s" 'search-forward)
(define-key esc-map "r" 'replace-string)
(define-key esc-map "q" 'query-replace)


(define-key ctl-x-map "\C-e" 'compile)
(define-key ctl-x-map "\C-n" 'next-error)

;; remap C-g
;; See https://emacs.stackexchange.com/questions/70357/it-now-takes-multiple-c-g-presses-to-cancel-actions-in-minibuffer-window?noredirect=1#comment113167_70357

;;########## (global-set-key [remap keyboard-quit] #'keyboard-quit-context+)
;;########## (global-set-key [remap keyboard-quit] #'keyboard-quit-context+)




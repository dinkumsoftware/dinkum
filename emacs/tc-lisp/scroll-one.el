;; scroll-one.el
;;
;; Emacs Lisp functions to scroll the current buffer one line in either
;; direction
;;
;; 23-may-95  tc  Initial
;; 2007.05.07 tc  Added previous-window
;; 2016-11-10 tc@DinkumSoftware.com bug fix,
;;               previous-window() renamed to tc-previous-window()
;;               to avoid internal emacs name collision.

;;
;; Table of contents
;;     scroll-up-one-line
;;     scroll-down-one-line
;;     previous-window

(defun scroll-up-one-line ()
"Scroll text of current window upward one line"
	(interactive)
	(scroll-up 1) )


(defun scroll-down-one-line ()
"Scroll text of current window downward one line"
	(interactive)
	(scroll-down 1) )


(defun tc-previous-window()
"Move cursor to other-window in reverse direction"
       (interactive)
       (other-window -1)
)

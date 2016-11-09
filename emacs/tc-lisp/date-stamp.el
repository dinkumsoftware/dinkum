;; date-stamp.el
;;
;; An EMACS LISP file 
;;
;; 23-may-95  tc  Initial
;; 2007-05-07 tc@DinkumSoftware.com Switch to yyyy-mm-dd
;; 2007.05.08 tc@DinkumSoftware.com Switch to yyyy.mm.dd
;; 2016.11.10 tc@DinkumSoftware.com switched back to yyyy-mm-dd

(defun date-stamp ()
"Insert the current date in current window
 Inserts fixed length string with following format
 2007-05-08"
    (interactive)
    (insert (format-time-string "%Y-%m-%d"))
)







    







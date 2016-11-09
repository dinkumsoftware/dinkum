;; date-stamp.el
;;
;; An EMACS LISP file 
;;
;; 23-may-95  tc  Initial

(defun date-stamp ()
"Insert the current date in current window
 Inserts fixed length string with following format
 23-may-95"
    (interactive)
    ; capture date/time into a string so we know it doesn't change
    ; 123456789.123456789.1234
    ; Sun Sep 16 01:03:52 1973
    (let ((str (current-time-string)))
      (insert 
       (substring str 8 10)     ; day in month
       "-"
       (substring str 4 7)      ; month
       "-"
       (substring str 22 24)))) ; year




    







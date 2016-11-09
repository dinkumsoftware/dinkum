;; date-and-sign-el
;;
;; Inserts a date and email address
;;
;; NOTE: should probably dig the email address out of the envirnoment
;;       instead of hardwiring it
;;
;; 2007.05.07 tc@DinkumSoftware.com  Switched from 07-may-07 to 2007.05.07

(defun date-and-sign ()
  "Inserts the current date and email signature in current window.
  2007.05.07"
	(interactive)
	(date-stamp)                          ; Put in the date
        (insert " tc@DinkumSoftware.com ")   ; and signature
)


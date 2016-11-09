;; date-and-sign.el
;;
;; Inserts a date and email address
;;
;; The email address is taken from:
;;    environment variable: DINKUM_USER_EMAIL
;; If that doesn't exist, taken from:
;;    environment variable: USER
;;
;; 2007.05.07 tc@DinkumSoftware.com Switched from 07-may-07 to 2007.05.07
;; 2016.11.10 tc@DinkumSoftware.com Switch to 2016-11-10
;;                                  take email address from enviornment variables

;; Pick what to use as the users signature
;; If environment variable DINKUM_USER_EMAIL exists...., use it
;; Otherwise Default to user-login-name (from env var USER or LOGNAME)
(defvar dinkum-user-signature
     ( if (getenv "DINKUM_USER_EMAIL") (getenv "DINKUM_USER_EMAIL") user-login-name)
    "The text to use to sign via date-and-sign().  Normally an email address"


)


(defun date-and-sign ()
  "Inserts the current date and email signature in current window.
  2007-05-07 someone@whereever.com"
	(interactive)
	(date-stamp)                          ; Put in the date
    (insert " " dinkum-user-signature)    ; and signature
)


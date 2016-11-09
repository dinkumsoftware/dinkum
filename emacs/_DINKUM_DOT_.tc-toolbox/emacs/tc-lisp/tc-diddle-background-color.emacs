;; tc-diddle-background-color.emacs
;;
;; 2007.05.07  Initial, moved from AAA.emacs inline code

;; Pick the background color based on username
(set-background-color 
    (if (string= user-real-login-name "tc"  ) "LightGray"  
    (if (string= user-real-login-name "root") "OliveDrab"
                                              "CadetBlue"
    ))
)



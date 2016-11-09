;; save-all-buffers.el
;;
;; Writes all modified buffers to disk
;; 
;; 2007.05.07 Moved from inline in AAA.emacs

(defun save-all-buffers ()
 "Saves all modified buffers"
	(interactive)
	(save-some-buffers 1 nil)
)
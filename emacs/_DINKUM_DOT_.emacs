;; .emacs

;;; uncomment this line to disable loading of "default.el" at startup
;; (setq inhibit-default-init t)

;; turn on font-lock mode
(when (fboundp 'global-font-lock-mode)
  (global-font-lock-mode t))

;; enable visual feedback on selections
;(setq transient-mark-mode t)

;; default to better frame titles
(setq frame-title-format
      (concat  "%b - emacs@" system-name))


;; ###########################################
;; Spliced on to get tc's customization on CentOS
;; Quick and dirty to get up and running on temp laptop
;; 19-nov-06
;; 061201 tc  copied into nellie (centos 4.4)
;;            changed my custom files back to ~/.tc-toolbox

;; Where all the emacs add-ons live
(defvar local-emacs-base-install-directory "~tc/.tc-toolbox/emacs"
    "The directory which contains all of the add on emacs packages
    subdirectories.  Used by init-add-on-package.
    29-Jan-98 tc@dinkum-software.com "
)

;; Each addon package has its own subdirectory in
;; 'local-emacs-base-inXSstall-directory.  The file AAA.emacs in that
;; subdirectory is eval'ed.  Put all customizations and load's there
     (load (concat local-emacs-base-install-directory "/mylisp/" 
                   "init-add-on-package" ))  ;; does all the work

;; My customizations.  Mostly keybinds
(init-add-on-package "mylisp")

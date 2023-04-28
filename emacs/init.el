;; Read tc of Dinkum Software's emacs customization
;; See https://github.com/dinkumsoftware/dinkum.git/emacs
;; written by dinkum-install-tc-emacs on Thu Apr 11 15:50:32 EDT 2019

;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.
(package-initialize)

(load "~/projects/dinkum/emacs/tc-init.emacs")

;; gitlab
;; https://github.com/nlamirault/emacs-gitlab
;; 2023-04-28 tc  Didn't work... 
;;                error: Package ‘gitlab-’ is unavailable

;; (unless (package-installed-p 'gitlab)
;; (package-install 'gitlab))

;; init-add-on-package
;;
;; This is just a handy function called from .emacs for splicing in
;; emacs add on packages.
;;
;; Each package has a directory in local-emacs-base-install-directory
;; You pass subdirectory name to init-add-on-package, which:
;;        evals local-emacs-base-install-directory/<subdir>/AAA.emacs
;; AAA.emacs should do the load-path alterative, loads, etc
;;
;; Variables available to AAA.emacs
;;  local-emacs-base-install-directory      parent directory, c:\emacs
;;  local-emacs-base-install-subdirectory   subdirectory,     c:\emacs\mylisp

;;
;; 04-Aug-97 tc@dinkum-software.com         Initial


(defun init-add-on-package (subdir)
        "Used in .emacs to install emacs add on packages.
         Global variable local-emacs-base-install-directory tells where
         subdir lives.  Each package must have a file named AAA.emacs in its
         subdirectory.  AAA.emacs is eval'ed.  Put your customizations there.
         04-Aug-97 tc@dinkum-software.com"

        ;; Build up full pathname of subdir so AAA.emacs can use it
        (setq local-emacs-base-install-subdirectory
              (concat local-emacs-base-install-directory "/" subdir) )

        ;; Build up the name of file to evaluate
        (setq init-add-on-package-eval-file
              (concat local-emacs-base-install-subdirectory "/" "AAA.emacs")
        )

        ;; Make sure it exists
        (if (file-readable-p init-add-on-package-eval-file)
            ;; File exists "eval it"
            (load init-add-on-package-eval-file)

            ;; File does not exist
            (error "Add on package does NOT exist: %s"
                    init-add-on-package-eval-file)
        )
)


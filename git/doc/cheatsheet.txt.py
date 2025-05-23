https://github.com/dinkumsoftware/dinkum.git
git/git-cheatsheet.txt

Frequently used git commands.

2016-11-21 tc Initial
2016-11-22 tc add Changing state.
2016-11-23 tc add Deleting commits
2016-11-28 tc add How to tell if file under git
2016-11-29 tc how to delete a branch
              how to pretty log
2016-12-02 tc Added username/password caching
2016-12-05 tc squashing since last push
2016-12-14 tc git reset --hard HEAD
2017-05-09 tc git merge-base branchA branchB
2017-05-11 tc bunch of additions
2019-11-13 tc Listed some git gui's
2019-11-14 tc moved gui listing to git-tools.txt
2019-11-22 tc Added meld and git-cat-files notes
2020-07-04 tc Added List files changed in a commit:
2021-01-28 tc fixed up rebase instructions
2021-08-18 tc added simple workflow
              Added ssh git clone examples
2021-10-26 tc how to see all history of a file
2021-10-27 tc how to see why file is being ignored
2021-11-03 tc added how to see files changed in a commit.
2021-12-19 tc git log --pretty
2022-01-04 tc how to pick either file from merge conflict.
2022-01-04 tc clarifed how to pick either file from merge conflict.
2022-02-16 tc added revision specification syntax
2022-02-20 tc squash/merge automagically
2022-03-01 tc improved rebase/squash
2022-04-25 tc rearranged a bit.
2022-10-08 tc merge tips
2024-12-16 tc how to delete a file in repo

Table of contents
    *** Creating stuff
    *** Looking at stuff
    *** Changing state
    *** Fixing stuff
    *** Deleting stuff
    *** Publishing Stuff
    *** Determining state
    *** username/password caching
    *** revision specification syntax
    *** simple workflow
==================================================
*** Creating stuff
# Initial copy of a repo from GitHub
cd parent
    # creates in directory parent/repo
    git clone https://<USERNAME>@github.com/whatever/repo.git      
    git clone git@github.com:dinkumsoftware/repo.git

    # creates in directory parent/DIR
    git clone https://<USERNAME>@github.com/whatever/repo.git  DIR 
    git clone git@github.com:dinkumsoftware/repo.git           DIR


# Create new LOCAL branch based on REMOTE
git branch       LOCAL origin/REMOTE
git checkout -b  LOCAL origin/REMOTE

# Change who you "pull" from
git branch --set-upstream-to origin/REMOTE

*** Looking at stuff
Using meld as a diff viewer
    git difftool <files, etc>

printing a file in git:
    git ver >= 2.24.0 :
        git-cat-file
    otherwise:
        from https://stackoverflow.com/questions/11007552/git-whole-file-to-stdout
        git show HEAD:<file>

See log of all commits since last push:
    git log origin/master..HEAD

To see what files changed in a commit:
    git show --stat <commit-hash>

See full history of a file (even deleted):
https://intellipaat.com/community/9088/git-how-to-find-a-deleted-file-in-the-project-commit-history
    git log --all --full-history -- <path-to-file>  # show the history
    git show <SHA>               -- <path-to-file>  # print a specific one
    git checkout <SHA>^          -- <path-to-file>  # get to working dir
                                                    # The ^ is prior to deletion

See why file/dir is being .gitignore'd
    git check-ignore [<options>] <pathname>...
      -v, --verbose Tell which .gitignore applies

*** Changing state
git add --all # stages modified, deleted, new
git add -u    # stages modified and deleted, without new
git add .     # stages new and modified, without deleted


git commit -a # stage modified/deleted (not new) and commit

# Changing the upstream source that branch will pull from.
git branch --set-upstream-to <origin/whatever> [<branchname>] 
                                               # only reqd if not current branch


*** Fixing stuff


 SQUASHING
# squash <N> commits into one
# Do NOT do this after a push
git rebase -i HEAD~<N> ; 1st pick, remainder squash

# squash all commits on a branch
# Choice A
   # thanks to: https://stackoverflow.com/questions/25356810/git-how-to-squash-all-commits-on-branch
   $ git checkout master
   $ git merge --squash yourBranch
   $ git commit # all commit messages of yourBranch in one, really useful
    > [status 5007e77] Squashed commit of the following: ...
1
# Choice B
   # Thanks to https://makandracards.com/makandra/527-squashing-several-git-commits-into-a-single-commit
   # This example squashes all commits on topic-branch.  It's done on another branch for safety in case
   # of rebase screwups.
   git checkout topic-branch
   git checkout -b squashed-topic-branch
   git rebase -i master
   git checkout master
   git merge squashed-topic-branch

    Note: that rebasing to the master does not work if you merged the
    master into your feature branch while you were working on the new
    feature. If you did this you will need to find the original branch
    point and call git rebase with a SHA1 revision.

# squash all commits since last push
git rebase -i origin/master   ; 1st editor:
                              ;   all but 1st entry: pick==>squash
                              ;   to bail: delete entire editor window
                              ; 2nd editor: make commit msg
                              ; to undo: git rebase --abort

# merge conflict, pick one file in entirty
# after a merge conflict on file: foo.bar
# This will pick the one from a later commit, which
# is generally what you want.  If not, use --ours
# instead of --theirs

git checkout --theirs -- foo.bar
git add                  foo.bar
git rebase --continue

# The following commands will keep the original file for mine.y
# and then use the merged in file only for merged.x
git checkout --ours    mine.y
git checkout --theirs  merged.x

Note that a rebase merge works by replaying each commit from the
     working branch on top of the <upstream> branch. Because of this,
     when a merge conflict happens, the side reported as ours is the
     so-far rebased series, starting with <upstream>, and theirs is
     the working branch. In other words, the sides are swapped.

# edit the last commit message
git commit --amend
git commit --amend -m "New commit message"


# edit the previous commit message
git rebase -i origin/master
    # select r (reword)


# manually fixing merges from:
https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

Git stores all of these versions in the index under “stages” which each
have numbers associated with them.
    Stage 1 is the common ancestor,
    stage 2 is your version and
    stage 3 is from the MERGE_HEAD, the version you’re merging in (“theirs”).

You can extract a copy of each of these versions of the conflicted file with the git show command and a special syntax.

    $ git show :1:hello.rb > hello.common.rb
    $ git show :2:hello.rb > hello.ours.rb
    $ git show :3:hello.rb > hello.theirs.rb

To compare your result to what you had in your branch before the merge,
in other words, to see what the merge introduced, you can run:
    git diff --ours
If we want to see how the result of the merge differed from what
was on their side, you can run:
    git diff --theirs

*** Deleting stuff

# Throw away all uncommitted changes to tracked file in the
# working directory
git reset --hard HEAD

# Delete all untracked files
git clean  

# throwaway the last attempted merge
git merge --abort

# Delete <N> commits
# http://stackoverflow.com/questions/1338728/delete-commits-from-a-branch-in-git
# WARNING! Stash first, deletes working dir changes
git reset --hard HEAD~<N>

# Delete a branch
git branch -d LOCAL    # local branch LOCAL
git push origin --delete REMOTE # Remote branch REMOTE

# Delete a file COMPLETELY warning: DANGEROUS
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

    sudo snap install git-filter-repo
    cd YOUR-REPOSITORY
    git filter-repo --invert-paths --path PATH-TO-YOUR-FILE-WITH-SENSITIVE-DATA
        # Might need a --force if repo not freshly cloned.
        # If there are filenames with spaces or other special chars:
            create (outside repo) file: files-to-delete.txt
            and put each filename on one line.  Then
            git filter-repo --invert-paths --paths-from-file <whereever>/files-to-delete.txt

    git remote add origin https://github.com/OWNER/REPOSITORY.git
    git remote set-url origin git@github.com:<Username>/<Project>.git
    git push origin --force --all

*** Publishing Stuff
# Local branch is LOCAL

# upstream branch is set and named LOCAL
git push

# upstream branch has a different name
# Want to push to branch of same name
git push origin LOCAL


*** Determining state
# How to tell if file under git control
# http://stackoverflow.com/questions/2405305/how-to-tell-if-a-file-is-git-tracked-by-shell-exit-code
git ls-files <file-name> --error-unmatch  &>>/dev/null  # returns 0 if in git, 1 if not

List files changed in a commit:
Thanks to https://stackoverflow.com/questions/5096268/how-to-get-a-list-of-all-files-that-changed-between-two-git-commits
       git diff --name-only <commit1> <commit2>   # in general
       git diff --name-only <starting SHA> HEAD   # e.g. HEAD~1
       git diff --name-only <starting SHA>        # if you want to include changed-but-not-yet-committed files


# Pretty one line log list
# Thanks to: http://stackoverflow.com/questions/1441010/the-shortest-possible-output-from-git-log-containing-author-and-date
# example output: 2016-11-23 tom campbell    dacf92c   test-socketCAN user interface enhancements.
git log --pretty=format:"%ad %<(15,trunc)%an %<(9,trunc)%h %s" --date=short
    # to make this default for --pretty :
    #    git config --global log.date       short
    #    git config --global format.pretty  format:"%ad %<(15,trunc)%an %<(9,trunc)%h %s"
    #    sigh: last line doesn't work.  It is applied to ALL git log, not just git log --pretty

# git log useful options
--oneline      Suppress commit message
--name-only    list files that changed in commit
--name-status  list files that changed in commit along with single char status code
                 Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R),
                 have their type (i.e. regular file, symlink, submodule, ...) changed (T)
                 are Unmerged (U), are Unknown (X), or have had their pairing Broken (B). 
--no-merges    suppress printout of commits that are the result of merges (2 parents)

# What is upstream?
git remote show origin
git branch -vv

# See all the files in a commit
git diff-tree  --no-commit-id --name-only -r <SHA1> # Just the names

git show       --pretty=""    --name-only    <SHA1> # names and commit info
git log                       --name-only           #    ditto

# Find out the common ancestor of two different branches
git merge-base branchA branchB


*** username/password caching

This will remember the username for a give repo.  You must supply password
once per session and then it will be remembered forever.

# Remember password in memory for a week
git config --global credential.helper 'cache --timeout=604800'

# If you remember, clone the repo with username in URL
git clone https://<USERNAME>@github.com/whatever/repo.git

# Associate remote USERNAME with a REPO
# Thanks to http://superuser.com/questions/199507/how-do-i-ensure-git-doesnt-ask-me-for-my-github-username-and-password
git config --global url."https://username@github.com/REPO".insteadOf "https://github.com/REPO"


*** revision specification syntax
from https://git-scm.com/docs/gitrevisions

commit references:
  <sha1>
  HEAD      @  names the commit on which you based the changes in
               the working tree.

Revision Range Summary 
<rev>
Include commits that are reachable from <rev> (i.e. <rev> and its
ancestors).

^<rev>
Exclude commits that are reachable from <rev> (i.e. <rev> and its
ancestors).

<rev1>..<rev2>

Include commits that are reachable from <rev2> but exclude those that
are reachable from <rev1>. When either <rev1> or <rev2> is omitted, it
defaults to HEAD.

<rev1>...<rev2>

Include commits that are reachable from either <rev1> or <rev2> but
exclude those that are reachable from both. When either <rev1> or
<rev2> is omitted, it defaults to HEAD.

<rev>^@, e.g. HEAD^@

A suffix ^ followed by an at sign is the same as listing all parents
of <rev> (meaning, include anything reachable from its parents, but
not the commit itself).

<rev>^!, e.g. HEAD^!

A suffix ^ followed by an exclamation mark is the same as giving
commit <rev> and then all its parents prefixed with ^ to exclude them
(and their ancestors).

<rev>^-<n>, e.g. HEAD^-, HEAD^-2
Equivalent to <rev>^<n>..<rev>, with <n> = 1 if not given.


*** simple workflow

; a branch to work on
git checkout -b dev-<monitor>-whatever_you_are_working-on

iterate:
    edit
    git commit

; squash all topic-branch commits to single commit
; (with backup to squashed-topic-branch)
git checkout -b squashed-topic-branch
git rebase -i main/master

; merge to master
git checkout master
git merge squashed-topic-branch

; tidy up at your leisure
git checkout master
git branch -d squashed-topic-branch
git branch -D topic-branch     ; -D req'd because topic-branch never merged.

    

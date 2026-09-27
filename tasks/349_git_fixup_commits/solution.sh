git commit -a --fixup="$(git log --format=%H --grep='^add parser$' -1)"
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash main

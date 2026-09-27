GIT_SEQUENCE_EDITOR="sed -i -e '2s/^pick/fixup/' -e '3s/^pick/fixup/' -e '4s/^pick/reword/' -e '5s/^pick/drop/'" GIT_EDITOR="sed -i '1s/.*/validate the {form} form/'" git rebase -i main

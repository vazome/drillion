git reset --soft HEAD~2
git commit -m "add {format} export"
git switch experiment
git reset --hard HEAD~1
git switch main

git merge feature/{topic} || true
printf '%s\n' '[server]' 'port = {port}' 'workers = {workers}' > config.ini
git add config.ini
git commit --no-edit

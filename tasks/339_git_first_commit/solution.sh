printf '%s\n' '{secret}' > .gitignore
git add .gitignore {app}.py test_{app}.py
git commit -m "add the {app}"

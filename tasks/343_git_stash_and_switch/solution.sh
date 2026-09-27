git stash push -u
git switch main
sed -i 's/^RETRIES = 1$/RETRIES = {retries}/' config.py
git commit -am "raise retries to {retries}"
git switch feature/{feature}
git stash pop

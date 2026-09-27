git tag introduced "$(git log -S 'MAX_UPLOAD_MB = {limit}' --format=%H | tail -n 1)"
git tag last-docs "$(git log -1 --author='{author}' --format=%H -- docs/)"

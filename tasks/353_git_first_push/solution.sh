git push -u origin main
git switch -c docs/{topic}
mkdir -p docs
printf '%s\n' '# {title}' > docs/{topic}.md
git add docs/{topic}.md
git commit -m "describe {topic}"
git push -u origin docs/{topic}

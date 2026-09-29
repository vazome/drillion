#!/usr/bin/env bash
set -euo pipefail

# Poll because a version tag may arrive while main's push workflow is still queued.
# The release gate has 25 minutes total; main CI itself has 20-minute job limits.
for ((attempt = 1; attempt <= 80; attempt++)); do
  runs=$(gh api --method GET "repos/$GITHUB_REPOSITORY/actions/workflows/ci.yml/runs" \
    -f head_sha="$GITHUB_SHA" -f event=push -f branch=main -f per_page=10)
  state=$(jq -r --arg sha "$GITHUB_SHA" '
    [.workflow_runs[] | select(.head_sha == $sha and .event == "push" and .head_branch == "main")]
    | first
    | if . == null or .status != "completed" then "waiting" else .conclusion end
  ' <<< "$runs")

  case "$state" in
    success)
      echo "Main CI passed for $GITHUB_SHA"
      exit 0
      ;;
    waiting)
      if ((attempt < 80)); then sleep 15; fi
      ;;
    *)
      echo "::error::Main CI for $GITHUB_SHA concluded $state; release refused"
      exit 1
      ;;
  esac
done

echo "::error::Main CI for $GITHUB_SHA did not finish in time; retry the release after CI passes"
exit 1

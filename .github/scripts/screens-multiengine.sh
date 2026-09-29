#!/usr/bin/env bash
set -euo pipefail

# Each Playwright process starts its own server. Distinct roots and ports keep the
# browser sessions independent while reusing this job's container and installs.
DRILLION_E2E_ROOT="$RUNNER_TEMP/drillion-firefox" DRILLION_PORT=8766 \
  pnpm screens --project=firefox --output=test-results/firefox &
firefox=$!
DRILLION_E2E_ROOT="$RUNNER_TEMP/drillion-webkit" DRILLION_PORT=8767 \
  pnpm screens --project=webkit --output=test-results/webkit &
webkit=$!

status=0
wait "$firefox" || status=1
wait "$webkit" || status=1
exit "$status"

#!/usr/bin/env bash
set -euo pipefail

# File-level shards include new specs automatically. Each process owns its server,
# task copy and progress database; both reuse this job's container and installs.
DRILLION_E2E_ROOT="$RUNNER_TEMP/drillion-chromium-1" DRILLION_PORT=8766 \
  pnpm screens --project=chromium '--grep-invert=@render|@capture' \
    --shard=1/2 --output=test-results/chromium-1 &
first=$!
DRILLION_E2E_ROOT="$RUNNER_TEMP/drillion-chromium-2" DRILLION_PORT=8767 \
  pnpm screens --project=chromium '--grep-invert=@render|@capture' \
    --shard=2/2 --output=test-results/chromium-2 &
second=$!

status=0
wait "$first" || status=1
wait "$second" || status=1
exit "$status"

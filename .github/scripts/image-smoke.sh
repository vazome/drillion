#!/usr/bin/env bash
set -euo pipefail

echo 'start the image'
docker run -d --name drillion --user "$(id -u):$(id -g)" -v "$PWD:/data" -p 127.0.0.1:8765:8765 drillion:ci

echo 'wait for healthy'
(
  for _ in $(seq 30); do
    case "$(docker inspect -f '{{.State.Health.Status}}' drillion)" in
      healthy) exit 0 ;;
      unhealthy) break ;;
    esac
    sleep 2
  done
  echo "::error::the container never reported healthy"
  docker logs drillion
  exit 1
)

echo 'image selfcheck'
docker exec drillion drillion selfcheck

# selfcheck does not open /lsp; verify that the packaged language server starts.
echo "the editor's language server answers on /lsp"
docker exec -i drillion python - <<'PY'
import json
from websockets.sync.client import connect

# the origin the page itself would send; api._allowed_origins() refuses any other
with connect("ws://127.0.0.1:8765/lsp", origin="http://127.0.0.1:8765") as ws:
    ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"processId": None, "rootUri": None,
                                   "capabilities": {}}}))
    for _ in range(50):  # the server logs a few notifications before it answers
        reply = json.loads(ws.recv(timeout=120))
        if reply.get("id") == 1:
            break
    else:
        raise SystemExit("::error::no reply to the LSP initialize")
assert "capabilities" in reply.get("result", {}), reply
print("lsp initialize ok:", reply["result"].get("serverInfo"))
PY

echo 'start it again with nothing but a volume'
docker rm -f drillion
docker run -d --name seeded -v drillion-data:/data -p 127.0.0.1:8765:8765 drillion:ci
for _ in $(seq 30); do
  case "$(docker inspect -f '{{.State.Health.Status}}' seeded)" in
    healthy) break ;;
    unhealthy) docker logs seeded; exit 1 ;;
  esac
  sleep 2
done
test "$(curl -fsS http://127.0.0.1:8765/api/health | jq .tasks)" = 174
curl -fsS -o /dev/null http://127.0.0.1:8765/
curl -fsS -o /dev/null -X POST http://127.0.0.1:8765/api/task/017_fstrings/open


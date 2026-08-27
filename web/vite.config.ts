import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API is served by `uv run drillion` on 8765; in dev Vite proxies to it. The language
// server rides the same origin over a websocket, so it needs the proxy too.
export default defineConfig({
  plugins: [react()],
  // two copies of the vscode API register the same extension ids and assert at startup
  resolve: { dedupe: ["vscode"] },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8765",
      "/lsp": { target: "ws://127.0.0.1:8765", ws: true },
    },
  },
});

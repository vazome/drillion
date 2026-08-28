import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API is served by `uv run drillion` on 8765; in dev Vite proxies to it. The language
// server rides the same origin over a websocket, so it needs the proxy too.
const API = "http://127.0.0.1:8765";

export default defineConfig({
  plugins: [react()],
  // two copies of the vscode API register the same extension ids and assert at startup
  resolve: { dedupe: ["vscode"] },
  server: {
    // the server refuses a foreign Origin, and Vite forwards the browser's own (5173)
    // untouched — changeOrigin only rewrites Host. Present the proxied call as same-origin.
    proxy: {
      "/api": { target: API, headers: { Origin: API } },
      "/lsp": { target: API.replace("http", "ws"), ws: true, headers: { Origin: API } },
    },
  },
});

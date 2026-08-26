import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API is served by `uv run drillion` on 8765; in dev Vite proxies to it.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8765" } },
});

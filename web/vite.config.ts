import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // The API runs on 8000; proxying keeps the browser on one origin so the
    // X-Principal header never becomes a cross-origin preflight in dev.
    // `ws: true` is what carries the live-collaboration sockets through — the
    // proxy silently 404s WebSocket upgrades without it.
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true, ws: true },
    },
  },
});

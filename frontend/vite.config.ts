import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api → the Polaris FastAPI backend (default :8000),
// so the browser can call it without CORS headaches. Override with POLARIS_API.
const API = process.env.POLARIS_API || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: API, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") },
    },
  },
});

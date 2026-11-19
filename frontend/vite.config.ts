import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  base: process.env.VITE_READ_ONLY === "true" ? "/reproscout/" : "/",
  plugins: [react()],
  build: { outDir: process.env.VITE_READ_ONLY === "true" ? "dist-pages" : "../src/reproscout/static", emptyOutDir: true },
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
        configure(proxy) {
          proxy.on("proxyReq", (outgoing, incoming) => {
            if (
              ["http://127.0.0.1:5173", "http://localhost:5173"].includes(
                incoming.headers.origin || "",
              )
            ) {
              outgoing.setHeader("Origin", "http://127.0.0.1:8765");
            }
          });
        },
      },
      "/archive": { target: "http://127.0.0.1:8765", changeOrigin: true },
    },
  },
});

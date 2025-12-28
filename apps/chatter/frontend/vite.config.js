import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        host: '0.0.0.0',
        port: 5173,
        strictPort: true,
        allowedHosts: [
            'srv1154036.hstgr.cloud' // Allow your specific Hostinger domain
        ],
        watch: {
            usePolling: true, // Crucial for syncing files to a remote VPS
        },
        hmr: {
            clientPort: 80
        },

    }
})
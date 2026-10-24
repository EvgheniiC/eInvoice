import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

function prerenderPublicHtml(): Plugin {
  return {
    name: 'prerender-public-html',
    apply: 'build',
    closeBundle(): void {
      const root: string = path.dirname(fileURLToPath(import.meta.url))
      const result = spawnSync(process.execPath, ['scripts/prerender.mjs'], {
        cwd: root,
        stdio: 'inherit',
      })
      if (result.status !== 0) {
        throw new Error('Prerender of public pages failed')
      }
    },
  }
}

export default defineConfig({
  plugins: [react(), prerenderPublicHtml()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})

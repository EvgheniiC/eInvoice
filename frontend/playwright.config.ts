import { defineConfig, devices } from '@playwright/test'

const PREVIEW_PORT: number = 4173
const PREVIEW_URL: string = `http://127.0.0.1:${PREVIEW_PORT}`
const previewCommand: string = process.env.CI
  ? `npx vite preview --host 127.0.0.1 --port ${String(PREVIEW_PORT)}`
  : `npx vite build && npx vite preview --host 127.0.0.1 --port ${String(PREVIEW_PORT)}`

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: PREVIEW_URL,
    trace: 'on-first-retry',
  },
  webServer: {
    command: previewCommand,
    url: PREVIEW_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})

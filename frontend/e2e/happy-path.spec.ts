import { expect, test, type Download, type Page, type Route } from '@playwright/test'
import { buildInvoice } from '../src/test/fixtures'
import type { InvoiceParseResponse } from '../src/types/invoice'

const SUCCESS_INVOICE: InvoiceParseResponse = buildInvoice()

async function fulfillJson(route: Route, body: unknown, status: number = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

test('happy path: landing, upload, result, Steuerberater package', async ({
  page,
}: {
  page: Page
}): Promise<void> => {
  await page.route('**/api/invoices/parse', async (route: Route): Promise<void> => {
    await fulfillJson(route, SUCCESS_INVOICE)
  })
  await page.route(
    '**/api/invoices/export/accountant-package',
    async (route: Route): Promise<void> => {
      await route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'application/zip',
          'Content-Disposition': 'attachment; filename="buchhaltung_2025-10294.zip"',
        },
        body: 'PK',
      })
    },
  )

  await page.goto('/')
  await page.getByRole('button', { name: 'Rechnung hochladen' }).first().click()
  await expect(page).toHaveURL(/\/upload$/)
  await expect(page.getByRole('heading', { name: 'Rechnung empfangen' })).toBeVisible()

  await page.locator('#invoice-file-input').setInputFiles({
    name: 'sample.xml',
    mimeType: 'text/xml',
    buffer: Buffer.from('<Invoice/>'),
  })

  await expect(page.getByText('Kann verarbeitet werden')).toBeVisible()
  await expect(page.getByText('KMLZ Rechtsanwaltsges. mbH').first()).toBeVisible()
  await expect(page.getByText('270,73 EUR').first()).toBeVisible()
  await expect(page.getByText('14.02.2025').first()).toBeVisible()
  await expect(page.getByText(/DE95 7004 0041 0228 8405 00/).first()).toBeVisible()
  await expect(page.getByRole('button', { name: 'Lesbare PDF herunterladen' })).toBeVisible()

  const downloadPromise: Promise<Download> = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Paket für Steuerberater' }).click()
  const download: Download = await downloadPromise
  expect(download.suggestedFilename()).toContain('buchhaltung')
})

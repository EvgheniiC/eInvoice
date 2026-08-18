import { afterEach, describe, expect, it, vi } from 'vitest'
import { parseInvoice } from './client'
import { buildInvoice } from '../test/fixtures'
import type { InvoiceParseResponse } from '../types/invoice'

describe('parseInvoice', (): void => {
  afterEach((): void => {
    vi.unstubAllGlobals()
  })

  it('posts the file and returns the parsed invoice', async (): Promise<void> => {
    const invoice: InvoiceParseResponse = buildInvoice()
    const fetchMock: ReturnType<typeof vi.fn> = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(invoice), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const file: File = new File(['<Invoice/>'], 'sample.xml', { type: 'text/xml' })
    const result: InvoiceParseResponse = await parseInvoice(file)

    expect(result.invoice_number).toBe('2025/10294')
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init]: [string, RequestInit] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/api/invoices/parse')
    expect(init.method).toBe('POST')
    expect(init.body).toBeInstanceOf(FormData)
  })

  it('uses the API error detail when the request fails', async (): Promise<void> => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Datei zu groß.' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )

    const file: File = new File(['x'], 'huge.xml', { type: 'text/xml' })
    await expect(parseInvoice(file)).rejects.toThrow('Datei zu groß.')
  })

  it('falls back to a generic message when the error body is not JSON', async (): Promise<void> => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response('plain error', { status: 500 })),
    )

    const file: File = new File(['x'], 'broken.xml', { type: 'text/xml' })
    await expect(parseInvoice(file)).rejects.toThrow('Upload fehlgeschlagen.')
  })
})

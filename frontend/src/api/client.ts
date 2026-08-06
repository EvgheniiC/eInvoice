import type { ExportFormat, InvoiceParseResponse } from '../types/invoice'

const API_BASE: string = '/api'

export async function parseInvoice(file: File): Promise<InvoiceParseResponse> {
  const formData: FormData = new FormData()
  formData.append('file', file)

  const response: Response = await fetch(`${API_BASE}/invoices/parse`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let detail: string = 'Upload fehlgeschlagen.'
    try {
      const errorBody: { detail?: string } = await response.json()
      if (errorBody.detail) {
        detail = errorBody.detail
      }
    } catch {
      // keep default message
    }
    throw new Error(detail)
  }

  return response.json() as Promise<InvoiceParseResponse>
}

export async function exportInvoice(
  invoice: InvoiceParseResponse,
  format: ExportFormat,
): Promise<void> {
  const response: Response = await fetch(`${API_BASE}/invoices/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format, invoice }),
  })

  if (!response.ok) {
    let detail: string = 'Export fehlgeschlagen.'
    try {
      const errorBody: { detail?: string } = await response.json()
      if (errorBody.detail) {
        detail = errorBody.detail
      }
    } catch {
      // keep default
    }
    throw new Error(detail)
  }

  const blob: Blob = await response.blob()
  const disposition: string | null = response.headers.get('Content-Disposition')
  const filename: string = parseFilename(disposition) ?? defaultFilename(invoice, format)

  const url: string = URL.createObjectURL(blob)
  const anchor: HTMLAnchorElement = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

export async function checkHealth(): Promise<{ status: string }> {
  const response: Response = await fetch(`${API_BASE}/health`)
  if (!response.ok) {
    throw new Error('API nicht erreichbar.')
  }
  return response.json() as Promise<{ status: string }>
}

function parseFilename(disposition: string | null): string | null {
  if (!disposition) {
    return null
  }
  const match: RegExpMatchArray | null = /filename="([^"]+)"/i.exec(disposition)
  return match?.[1] ?? null
}

function defaultFilename(invoice: InvoiceParseResponse, format: ExportFormat): string {
  const ext: string = format === 'excel' ? 'xlsx' : 'csv'
  const prefix: string = format === 'datev' ? 'datev_' : ''
  return `${prefix}export_${invoice.invoice_number ?? 'invoice'}.${ext}`
}

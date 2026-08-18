import type {
  AccountantPackageRequest,
  ExportFormat,
  ExportRequest,
  HealthResponse,
  InvoiceParseResponse,
  ValidationReportRequest,
} from '../types/invoice'

const API_BASE: string = '/api'

function createRequestId(): string {
  if (typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID().replace(/-/g, '').slice(0, 12)
  }
  return Math.random().toString(16).slice(2, 14)
}

function withRequestId(init: RequestInit): RequestInit {
  const headers: Headers = new Headers(init.headers)
  headers.set('X-Request-ID', createRequestId())
  return { ...init, headers }
}

export async function parseInvoice(file: File): Promise<InvoiceParseResponse> {
  const formData: FormData = new FormData()
  formData.append('file', file)

  const response: Response = await fetch(
    `${API_BASE}/invoices/parse`,
    withRequestId({
      method: 'POST',
      body: formData,
    }),
  )

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
  const body: ExportRequest = { format, invoice }
  const response: Response = await fetch(
    `${API_BASE}/invoices/export`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )

  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Export fehlgeschlagen.'))
  }

  await downloadResponseBlob(response, defaultFilename(invoice, format))
}

export async function downloadValidationReport(
  invoice: InvoiceParseResponse,
): Promise<void> {
  const body: ValidationReportRequest = { invoice }
  const response: Response = await fetch(
    `${API_BASE}/invoices/export/validation-report`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )

  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Prüfbericht-Download fehlgeschlagen.'))
  }

  await downloadResponseBlob(
    response,
    `pruefbericht_${invoice.invoice_number ?? 'invoice'}.txt`,
  )
}

export async function downloadAccountantPackage(
  invoice: InvoiceParseResponse,
  sourceFile?: File | null,
): Promise<void> {
  const body: AccountantPackageRequest = { invoice }

  if (sourceFile && isPdfFile(sourceFile)) {
    body.pdf_base64 = await fileToBase64(sourceFile)
    body.pdf_filename = sourceFile.name
  } else if (sourceFile && isXmlFile(sourceFile)) {
    body.xml_base64 = await fileToBase64(sourceFile)
    body.xml_filename = sourceFile.name
  }

  const response: Response = await fetch(
    `${API_BASE}/invoices/export/accountant-package`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )

  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Paket-Download fehlgeschlagen.'))
  }

  await downloadResponseBlob(
    response,
    `buchhaltung_${invoice.invoice_number ?? 'invoice'}.zip`,
  )
}

export async function checkHealth(): Promise<HealthResponse> {
  const response: Response = await fetch(`${API_BASE}/health`, withRequestId({ method: 'GET' }))
  if (!response.ok) {
    throw new Error('API nicht erreichbar.')
  }
  return response.json() as Promise<HealthResponse>
}

async function downloadResponseBlob(response: Response, fallbackName: string): Promise<void> {
  const blob: Blob = await response.blob()
  const disposition: string | null = response.headers.get('Content-Disposition')
  const filename: string = parseFilename(disposition) ?? fallbackName

  const url: string = URL.createObjectURL(blob)
  const anchor: HTMLAnchorElement = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

async function readErrorDetail(response: Response, fallback: string): Promise<string> {
  try {
    const errorBody: { detail?: string } = await response.json()
    if (errorBody.detail) {
      return errorBody.detail
    }
  } catch {
    // keep fallback
  }
  return fallback
}

function isPdfFile(file: File): boolean {
  if (file.type === 'application/pdf') {
    return true
  }
  return file.name.toLowerCase().endsWith('.pdf')
}

function isXmlFile(file: File): boolean {
  const name: string = file.name.toLowerCase()
  if (name.endsWith('.xml')) {
    return true
  }
  return file.type === 'application/xml' || file.type === 'text/xml'
}

async function fileToBase64(file: File): Promise<string> {
  const buffer: ArrayBuffer = await file.arrayBuffer()
  const bytes: Uint8Array = new Uint8Array(buffer)
  let binary: string = ''
  const chunkSize: number = 0x8000
  for (let offset: number = 0; offset < bytes.length; offset += chunkSize) {
    const chunk: Uint8Array = bytes.subarray(offset, offset + chunkSize)
    binary += String.fromCharCode(...chunk)
  }
  return btoa(binary)
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

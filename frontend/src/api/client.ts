import type {
  AccountantPackageRequest,
  BatchJobResponse,
  CapabilitiesResponse,
  ExportFormat,
  ExportRequest,
  FeedbackRequest,
  FeedbackResponse,
  FunnelEventRequest,
  HealthResponse,
  InvoiceParseResponse,
  MeResponse,
  MessageResponse,
  OrgResponse,
  RegisterResponse,
  ValidationReportRequest,
} from '../types/invoice'
import { DEFAULT_CAPABILITIES } from '../content/capabilities'

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
  return { ...init, headers, credentials: 'include' }
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

export async function createInvoiceBatch(files: File[]): Promise<BatchJobResponse> {
  const formData: FormData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  const response: Response = await fetch(
    `${API_BASE}/invoices/batch`,
    withRequestId({
      method: 'POST',
      body: formData,
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Batch-Upload fehlgeschlagen.'))
  }
  return response.json() as Promise<BatchJobResponse>
}

export async function fetchBatchJob(jobId: string): Promise<BatchJobResponse> {
  const response: Response = await fetch(
    `${API_BASE}/invoices/batch/${jobId}`,
    withRequestId({ method: 'GET' }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Batch-Status nicht verfügbar.'))
  }
  return response.json() as Promise<BatchJobResponse>
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

export async function fetchCapabilities(): Promise<CapabilitiesResponse> {
  try {
    const response: Response = await fetch(
      `${API_BASE}/capabilities`,
      withRequestId({ method: 'GET' }),
    )
    if (!response.ok) {
      return DEFAULT_CAPABILITIES
    }
    return (await response.json()) as CapabilitiesResponse
  } catch {
    return DEFAULT_CAPABILITIES
  }
}

export function recordFunnel(step: FunnelEventRequest['step']): void {
  const body: FunnelEventRequest = { step }
  try {
    void fetch(
      `${API_BASE}/telemetry/funnel`,
      withRequestId({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }),
    ).catch(() => {
      return
    })
  } catch {
    return
  }
}

export async function submitFeedback(
  payload: FeedbackRequest,
): Promise<FeedbackResponse> {
  const response: Response = await fetch(
    `${API_BASE}/feedback`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Feedback konnte nicht gesendet werden.'))
  }
  return response.json() as Promise<FeedbackResponse>
}

export async function fetchMe(): Promise<MeResponse | null> {
  try {
    const response: Response = await fetch(`${API_BASE}/me`, withRequestId({ method: 'GET' }))
    if (response.status === 401 || response.status === 503) {
      return null
    }
    if (!response.ok) {
      return null
    }
    return (await response.json()) as MeResponse
  } catch {
    return null
  }
}

export async function registerAccount(
  email: string,
  password: string,
  organizationName: string = '',
): Promise<RegisterResponse> {
  const trimmedOrg: string = organizationName.trim()
  const payload: { email: string; password: string; organization_name?: string } = {
    email,
    password,
  }
  if (trimmedOrg.length >= 2) {
    payload.organization_name = trimmedOrg
  }
  const response: Response = await fetch(
    `${API_BASE}/auth/register`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Registrierung fehlgeschlagen.'))
  }
  return response.json() as Promise<RegisterResponse>
}

export async function loginAccount(email: string, password: string): Promise<MeResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/login`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Anmeldung fehlgeschlagen.'))
  }
  return response.json() as Promise<MeResponse>
}

export async function logoutAccount(): Promise<void> {
  await fetch(
    `${API_BASE}/auth/logout`,
    withRequestId({ method: 'POST' }),
  )
}

export async function verifyEmail(token: string): Promise<MeResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/verify-email`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Bestätigung fehlgeschlagen.'))
  }
  return response.json() as Promise<MeResponse>
}

export async function requestMagicLink(email: string): Promise<MessageResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/magic-link`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Anmeldelink konnte nicht gesendet werden.'))
  }
  return response.json() as Promise<MessageResponse>
}

export async function requestPasswordReset(email: string): Promise<MessageResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/forgot-password`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Zurücksetzen konnte nicht gestartet werden.'))
  }
  return response.json() as Promise<MessageResponse>
}

export async function resetAccountPassword(token: string, newPassword: string): Promise<MessageResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/reset-password`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: newPassword }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Passwort konnte nicht gesetzt werden.'))
  }
  return response.json() as Promise<MessageResponse>
}

export async function resendVerification(email: string): Promise<MessageResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/resend-verification`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Bestätigungs-E-Mail konnte nicht gesendet werden.'))
  }
  return response.json() as Promise<MessageResponse>
}

export async function consumeMagicLink(token: string): Promise<MeResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/magic-link/consume`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Anmeldelink ungültig.'))
  }
  return response.json() as Promise<MeResponse>
}

export async function changeAccountPassword(
  currentPassword: string,
  newPassword: string,
): Promise<MessageResponse> {
  const response: Response = await fetch(
    `${API_BASE}/auth/change-password`,
    withRequestId({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Passwort konnte nicht geändert werden.'))
  }
  return response.json() as Promise<MessageResponse>
}

export async function updateOrganizationName(name: string): Promise<OrgResponse> {
  const response: Response = await fetch(
    `${API_BASE}/org`,
    withRequestId({
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }),
  )
  if (!response.ok) {
    throw new Error(await readErrorDetail(response, 'Organisation konnte nicht gespeichert werden.'))
  }
  return response.json() as Promise<OrgResponse>
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

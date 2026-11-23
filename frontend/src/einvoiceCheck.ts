import type { InvoiceParseResponse } from './types/invoice'

export type EInvoiceCheckResult = 'einvoice' | 'not_einvoice' | 'unreadable'

export type KositCheckResult = 'conform' | 'not_conform' | 'not_checked'

const KOSIT_ACCEPT_CODE: string = 'KOSIT_OK'

const KOSIT_REJECT_CODES: ReadonlySet<string> = new Set(['KOSIT_FAILED', 'KOSIT_NO_SCENARIO'])

const NOT_EINVOICE_CODES: ReadonlySet<string> = new Set([
  'NOT_ZUGFERD',
  'UNSUPPORTED_TYPE',
  'UNSUPPORTED_XML_FORMAT',
  'UNSUPPORTED_OPENTRANS',
  'FILE_TYPE_MISMATCH',
])

const NOT_EINVOICE_FILE_TYPES: ReadonlySet<string> = new Set([
  'pdf_unknown',
  'unsupported',
  'unsupported_xml',
  'opentrans_xml',
  'type_mismatch',
])

export function classifyEInvoice(invoice: InvoiceParseResponse): EInvoiceCheckResult {
  const code: string = invoice.validation_issues[0]?.code ?? ''
  const fileType: string = invoice.file_type ?? ''
  if (NOT_EINVOICE_CODES.has(code) || NOT_EINVOICE_FILE_TYPES.has(fileType)) {
    return 'not_einvoice'
  }
  if (fileType === 'zugferd_pdf') {
    return 'einvoice'
  }
  if (fileType === 'xrechnung_xml' && invoice.status !== 'error') {
    return 'einvoice'
  }
  return 'unreadable'
}

export function eInvoiceFormatLabel(fileType: string | null): string {
  if (fileType === 'zugferd_pdf') {
    return 'ZUGFeRD / Factur-X (PDF mit XML)'
  }
  if (fileType === 'xrechnung_xml') {
    return 'XRechnung (XML)'
  }
  return 'unbekannt'
}

export function classifyKosit(invoice: InvoiceParseResponse): KositCheckResult {
  if (classifyEInvoice(invoice) !== 'einvoice') {
    return 'not_checked'
  }
  const completed: boolean =
    invoice.validation_meta.engine === 'kosit' && invoice.validation_meta.full_check_completed
  if (!completed) {
    return 'not_checked'
  }
  const codes: string[] = invoice.validation_issues.map((issue) => issue.code ?? '')
  if (codes.some((code: string) => KOSIT_REJECT_CODES.has(code))) {
    return 'not_conform'
  }
  if (codes.includes(KOSIT_ACCEPT_CODE)) {
    return 'conform'
  }
  return 'not_conform'
}

export function kositStatusLabel(result: KositCheckResult, invoice: InvoiceParseResponse): string {
  if (result === 'conform') {
    const version: string | null = invoice.validation_meta.engine_version
    const suffix: string = version ? ` (KoSIT ${version})` : ''
    return `KoSIT: entspricht${suffix}`
  }
  if (result === 'not_conform') {
    return 'KoSIT: entspricht nicht'
  }
  return 'KoSIT: nicht geprüft'
}

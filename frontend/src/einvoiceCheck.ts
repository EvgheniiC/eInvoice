import type { InvoiceParseResponse, ValidationStatus } from './types/invoice'

export type EInvoiceCheckResult = 'einvoice' | 'not_einvoice' | 'unreadable'

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

export function validationStatusLabel(status: ValidationStatus): string {
  switch (status) {
    case 'valid':
      return 'Prüfung: gültig'
    case 'warning':
      return 'Prüfung: Warnung'
    case 'invalid':
      return 'Prüfung: ungültig'
    default:
      return 'Prüfung: nicht geprüft'
  }
}

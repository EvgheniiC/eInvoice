import type { CapabilitiesResponse, PlanInfo } from '../types/invoice'

export const DEFAULT_CAPABILITIES: CapabilitiesResponse = {
  max_upload_size_mb: 10,
  allowed_extensions: ['.xml', '.pdf'],
  max_files_per_request: 1,
  rate_limit_per_minute: 30,
  account_rate_limit_per_minute: 60,
  parse_per_day: 10,
  export_per_day: 10,
  max_parallel: 1,
  stores_invoice_files: false,
  requires_account: false,
  processing_model: 'guest',
  standard_version: 'EN 16931:2017',
  xrechnung_version: '3.0.2',
  formats: [
    {
      id: 'ubl_invoice',
      label: 'XRechnung UBL Invoice',
      extensions: ['.xml'],
      notes: 'EN 16931 UBL Invoice.',
    },
    {
      id: 'ubl_credit_note',
      label: 'XRechnung UBL CreditNote',
      extensions: ['.xml'],
      notes: 'EN 16931 UBL CreditNote.',
    },
    {
      id: 'cii',
      label: 'UN/CEFACT CII',
      extensions: ['.xml'],
      notes: 'Cross Industry Invoice XML.',
    },
    {
      id: 'zugferd_pdf',
      label: 'ZUGFeRD / Factur-X',
      extensions: ['.pdf'],
      notes: 'PDF with embedded invoice XML.',
    },
  ],
  profiles: ['EN 16931:2017', 'XRechnung 3.0.2', 'ZUGFeRD / Factur-X EN 16931'],
  limitations: [
    'Eine Datei pro Anfrage, maximal 10 MB, bis zu 10 Prüfungen und 10 Exporte pro Tag.',
    'Gastmodus: die Datei wird nur während der Anfrage verarbeitet und danach gelöscht.',
    'Normale PDFs ohne eingebettetes XML, Scans, openTRANS und andere XML-Formate werden abgelehnt.',
    'Der DATEV-Export ist eine Buchungsstapel-CSV und kein DATEVconnect.',
    'Keine Vorsteuer- oder Rechtsgarantie.',
  ],
}

export function formatLimitsLine(capabilities: CapabilitiesResponse): string {
  const extensions: string = capabilities.allowed_extensions.join(' / ')
  return (
    `Eine Datei bis ${String(capabilities.max_upload_size_mb)} MB · ` +
    `${String(capabilities.parse_per_day)} Prüfungen / Tag · ` +
    `${extensions} · UBL Invoice/CreditNote, UN/CEFACT CII oder ZUGFeRD/Factur-X`
  )
}

export function formatUploadLimitsLine(
  capabilities: CapabilitiesResponse,
  plan: PlanInfo | null,
): string {
  const extensions: string = capabilities.allowed_extensions.join(' / ')
  if (plan?.allows_batch) {
    return (
      `Bis zu ${String(plan.max_batch_files)} Dateien · ` +
      `jeweils ${String(plan.max_upload_size_mb)} MB · ` +
      `${String(plan.parse_per_day)} Prüfungen / Tag · ${extensions}`
    )
  }
  if (plan) {
    return (
      `Eine Datei bis ${String(plan.max_upload_size_mb)} MB · ` +
      `${String(plan.parse_per_day)} Prüfungen / Tag · ${extensions}`
    )
  }
  return formatLimitsLine(capabilities)
}

import type {
  InvoiceParseResponse,
  InvoiceTotals,
  LineItem,
  PartyInfo,
  ValidationIssue,
  ValidationMeta,
} from '../types/invoice'

const DEFAULT_SELLER: PartyInfo = {
  name: 'KMLZ Rechtsanwaltsges. mbH',
  address: 'Musterstraße 1, 80331 München',
  vat_id: 'DE814742004',
  iban: 'DE95700400410228840500',
}

const DEFAULT_BUYER: PartyInfo = {
  name: 'Buyer AG',
  address: null,
  vat_id: 'DE123',
  iban: null,
}

const DEFAULT_TOTALS: InvoiceTotals = {
  net: '227.50',
  tax: '43.23',
  gross: '270.73',
  currency: 'EUR',
  allowance: null,
  charge: null,
  tax_breakdown: [{ rate: '19', amount: '43.23' }],
}

const DEFAULT_META: ValidationMeta = {
  standard_version: 'EN 16931',
  profile: 'XRechnung 3.0',
  profile_id: 'urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0',
  engine: 'kosit',
  engine_version: '1.5.0',
  scenarios_version: 'XRechnung 3.0',
  full_check_completed: true,
}

const DEFAULT_LINE_ITEMS: LineItem[] = [
  {
    position: 1,
    description: 'Beratung',
    quantity: '1',
    unit: 'HUR',
    unit_price: '227.50',
    tax_rate: '19',
    net_amount: '227.50',
    gross_amount: '270.73',
  },
]

const DEFAULT_NEXT_STEPS: string[] = ['Rechnung an die Buchhaltung übergeben.']

export function buildInvoice(
  overrides: Partial<InvoiceParseResponse> = {},
): InvoiceParseResponse {
  return {
    status: 'success',
    message: 'Rechnung gelesen und geprüft.',
    filename: 'sample.xml',
    file_type: 'xrechnung_xml',
    document_type: 'invoice',
    invoice_number: '2025/10294',
    issue_date: '2025-01-31',
    due_date: '2025-02-14',
    payment_reference: 'REF-1',
    validation_status: 'valid',
    mismatch_warnings: [],
    mismatch_fields: [],
    ...overrides,
    seller: overrides.seller !== undefined ? overrides.seller : DEFAULT_SELLER,
    buyer: overrides.buyer !== undefined ? overrides.buyer : DEFAULT_BUYER,
    totals: overrides.totals !== undefined ? overrides.totals : DEFAULT_TOTALS,
    validation_meta: {
      ...DEFAULT_META,
      ...(overrides.validation_meta ?? {}),
    },
    line_items: overrides.line_items ?? [...DEFAULT_LINE_ITEMS],
    validation_issues: overrides.validation_issues ?? [],
    next_steps: overrides.next_steps ?? [...DEFAULT_NEXT_STEPS],
  }
}

export function buildInvalidInvoice(
  issue: ValidationIssue = {
    level: 'error',
    category: 'business',
    code: 'BR-01',
    message: 'Pflichtfeld fehlt.',
    explanation: 'Bitte den Lieferanten um eine korrigierte Rechnung bitten.',
    bt_code: 'BT-1',
    field: 'invoice_number',
  },
): InvoiceParseResponse {
  return buildInvoice({
    status: 'partial',
    validation_status: 'invalid',
    invoice_number: null,
    validation_issues: [issue],
    next_steps: ['Lieferanten kontaktieren und Korrektur anfordern.'],
  })
}

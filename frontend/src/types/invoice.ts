export type ParseStatus = 'success' | 'partial' | 'error' | 'not_implemented'
export type ValidationStatus = 'valid' | 'invalid' | 'warning' | 'not_checked'
export type ExportFormat = 'csv' | 'excel' | 'datev'

export interface PartyInfo {
  name: string | null
  address: string | null
  vat_id: string | null
  iban: string | null
}

export interface LineItem {
  position: number | null
  description: string | null
  quantity: number | null
  unit: string | null
  unit_price: number | null
  tax_rate: number | null
  net_amount: number | null
  gross_amount: number | null
}

export interface InvoiceTotals {
  net: number | null
  tax: number | null
  gross: number | null
  currency: string | null
}

export interface ValidationIssue {
  level: string
  category: string
  code: string | null
  message: string
}

export interface MismatchField {
  field: string
  label: string
  xml_value: string | null
  pdf_value: string | null
  matched: boolean
}

export interface InvoiceParseResponse {
  status: ParseStatus
  message: string
  filename: string
  file_type: string | null
  invoice_number: string | null
  issue_date: string | null
  due_date: string | null
  seller: PartyInfo | null
  buyer: PartyInfo | null
  totals: InvoiceTotals | null
  line_items: LineItem[]
  payment_reference: string | null
  validation_status: ValidationStatus
  validation_issues: ValidationIssue[]
  mismatch_warnings: string[]
  mismatch_fields: MismatchField[]
  next_steps: string[]
}

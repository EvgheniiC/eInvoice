export type ParseStatus = 'success' | 'partial' | 'error' | 'not_implemented'
export type ValidationStatus = 'valid' | 'invalid' | 'warning' | 'not_checked'
export type ExportFormat = 'csv' | 'excel' | 'datev'
export type DecimalValue = string | number

export interface PartyInfo {
  name: string | null
  address: string | null
  vat_id: string | null
  iban: string | null
}

export interface LineItem {
  position: number | null
  description: string | null
  quantity: DecimalValue | null
  unit: string | null
  unit_price: DecimalValue | null
  tax_rate: DecimalValue | null
  net_amount: DecimalValue | null
  gross_amount: DecimalValue | null
}

export interface TaxBreakdown {
  rate: DecimalValue
  amount: DecimalValue | null
}

export interface InvoiceTotals {
  net: DecimalValue | null
  tax: DecimalValue | null
  gross: DecimalValue | null
  currency: string | null
  allowance: DecimalValue | null
  charge: DecimalValue | null
  tax_breakdown: TaxBreakdown[]
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
  document_type: 'invoice' | 'credit_note' | null
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

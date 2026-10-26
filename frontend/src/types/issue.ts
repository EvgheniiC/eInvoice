/** Outgoing e-invoice draft. Decimals arrive as strings from the API. */

import type { ValidationIssue, ValidationStatus } from './invoice'

export type IssueAddress = {
  line: string | null
  postcode: string | null
  city: string | null
  country: string | null
}

export type IssueParty = {
  name: string | null
  address: IssueAddress
  vat_id: string | null
  email: string | null
  contact_name: string | null
  phone: string | null
  iban: string | null
}

export type IssueLineInput = {
  description: string | null
  quantity: string | number | null
  unit_code: string | null
  unit_price: string | number | null
  tax_rate: string | number | null
}

export type IssueDraft = {
  invoice_number: string | null
  issue_date: string | null
  currency: string
  buyer_reference: string | null
  seller: IssueParty
  buyer: IssueParty
  lines: IssueLineInput[]
}

export type FieldHint = {
  field: string
  source: 'pdf' | 'organization' | 'empty'
  message: string
}

export type IssueDraftResponse = {
  filename: string
  text_found: boolean
  draft: IssueDraft
  hints: FieldHint[]
  warnings: string[]
}

export type IssueArtifactFormat = 'xrechnung' | 'zugferd_xml' | 'zugferd_pdf'

export type IssueArtifact = {
  format: IssueArtifactFormat
  filename: string
  media_type: string
  content_base64: string | null
  download_allowed: boolean
  validation_status: ValidationStatus
  validation_issues: ValidationIssue[]
}

export type IssueBuildResponse = {
  ready: boolean
  message: string
  blocking_issues: ValidationIssue[]
  artifacts: IssueArtifact[]
}

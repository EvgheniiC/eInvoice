import { describe, expect, it } from 'vitest'
import { classifyEInvoice, eInvoiceFormatLabel, type EInvoiceCheckResult } from './einvoiceCheck'
import { buildInvoice } from './test/fixtures'
import type { InvoiceParseResponse, ValidationIssue } from './types/invoice'

function withIssue(code: string, fileType: string): InvoiceParseResponse {
  const issue: ValidationIssue = {
    level: 'error',
    category: 'schema',
    code,
    message: 'Hinweis',
    explanation: null,
    bt_code: null,
    field: null,
  }
  return buildInvoice({
    status: 'error',
    file_type: fileType,
    validation_status: 'invalid',
    validation_issues: [issue],
  })
}

describe('classifyEInvoice', (): void => {
  it('accepts a parsed XRechnung and a ZUGFeRD PDF', (): void => {
    const xml: EInvoiceCheckResult = classifyEInvoice(buildInvoice())
    const pdf: EInvoiceCheckResult = classifyEInvoice(
      buildInvoice({ file_type: 'zugferd_pdf', status: 'partial', validation_status: 'invalid' }),
    )
    expect(xml).toBe('einvoice')
    expect(pdf).toBe('einvoice')
  })

  it('rejects a plain PDF and an unsupported XML', (): void => {
    expect(classifyEInvoice(withIssue('NOT_ZUGFERD', 'pdf_unknown'))).toBe('not_einvoice')
    expect(classifyEInvoice(withIssue('UNSUPPORTED_XML_FORMAT', 'unsupported_xml'))).toBe(
      'not_einvoice',
    )
  })

  it('keeps a broken XML file unreadable', (): void => {
    expect(classifyEInvoice(withIssue('XML_NOT_WELL_FORMED', 'xrechnung_xml'))).toBe('unreadable')
  })
})

describe('eInvoiceFormatLabel', (): void => {
  it('names the two supported invoice kinds', (): void => {
    expect(eInvoiceFormatLabel('xrechnung_xml')).toBe('XRechnung (XML)')
    expect(eInvoiceFormatLabel('zugferd_pdf')).toBe('ZUGFeRD / Factur-X (PDF mit XML)')
    expect(eInvoiceFormatLabel(null)).toBe('unbekannt')
  })
})

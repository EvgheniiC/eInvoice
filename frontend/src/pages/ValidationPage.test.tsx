import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { parseInvoice } from '../api/client'
import { buildInvoice } from '../test/fixtures'
import type { InvoiceParseResponse, ValidationIssue } from '../types/invoice'
import { ValidationPage } from './ValidationPage'

vi.mock('../api/client', (): { parseInvoice: ReturnType<typeof vi.fn> } => ({
  parseInvoice: vi.fn(),
}))

describe('ValidationPage', (): void => {
  it('reports a parsed file as an e-invoice', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const invoice: InvoiceParseResponse = buildInvoice({ filename: 'sample.xml' })
    vi.mocked(parseInvoice).mockResolvedValue(invoice)

    render(<ValidationPage onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'eRechnung validation' })).toBeInTheDocument()
    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    const file: File = new File(['<Invoice/>'], 'sample.xml', { type: 'text/xml' })
    await user.upload(input, file)

    expect(await screen.findByText('Ja. Das ist eine E-Rechnung.')).toBeInTheDocument()
    expect(screen.getByText('Format: XRechnung (XML)')).toBeInTheDocument()
    expect(screen.getByText('Prüfung: gültig')).toBeInTheDocument()
    expect(parseInvoice).toHaveBeenCalledTimes(1)
  })

  it('reports a plain PDF as not an e-invoice', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const issue: ValidationIssue = {
      level: 'error',
      category: 'schema',
      code: 'NOT_ZUGFERD',
      message: 'Die PDF enthält kein erkennbares eingebettetes Rechnungs-XML.',
      explanation: null,
      bt_code: null,
      field: null,
    }
    const invoice: InvoiceParseResponse = buildInvoice({
      status: 'error',
      message: 'PDF ohne eingebettetes ZUGFeRD/Factur-X XML.',
      filename: 'scan.pdf',
      file_type: 'pdf_unknown',
      validation_status: 'invalid',
      validation_issues: [issue],
    })
    vi.mocked(parseInvoice).mockResolvedValue(invoice)

    render(<ValidationPage onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)
    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    await user.upload(input, new File(['%PDF'], 'scan.pdf', { type: 'application/pdf' }))

    expect(await screen.findByText('Nein. Das ist keine E-Rechnung.')).toBeInTheDocument()
    expect(screen.getByText(invoice.message)).toBeInTheDocument()
  })
})

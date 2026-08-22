import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { downloadViewPdf } from '../api/client'
import { InvoiceView } from './InvoiceView'
import { buildInvoice, buildInvalidInvoice } from '../test/fixtures'
import type { InvoiceParseResponse } from '../types/invoice'

vi.mock('../api/client', (): Record<string, ReturnType<typeof vi.fn>> => ({
  exportInvoice: vi.fn(),
  downloadAccountantPackage: vi.fn(),
  downloadValidationReport: vi.fn(),
  downloadViewPdf: vi.fn(),
}))

describe('InvoiceView', (): void => {
  it('shows supplier, amount, due date, IBAN and a processable outcome first', (): void => {
    const invoice: InvoiceParseResponse = buildInvoice()
    render(<InvoiceView invoice={invoice} />)

    expect(screen.getByText('Kann verarbeitet werden')).toBeInTheDocument()
    expect(screen.getByText('Lieferant', { selector: 'dt' })).toBeInTheDocument()
    expect(screen.getAllByText('KMLZ Rechtsanwaltsges. mbH').length).toBeGreaterThan(0)
    expect(screen.getAllByText(/270,73/).length).toBeGreaterThan(0)
    expect(screen.getAllByText('14.02.2025').length).toBeGreaterThan(0)
    expect(screen.getAllByText(/DE95 7004 0041 0228 8405 00/).length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: 'Paket für Steuerberater' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Lesbare PDF herunterladen' })).toBeEnabled()
  })

  it('locks export until the user confirms errors on an invalid invoice', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const invoice: InvoiceParseResponse = buildInvalidInvoice()
    render(<InvoiceView invoice={invoice} />)

    expect(screen.getByText('Korrektur anfordern')).toBeInTheDocument()
    const packageButton: HTMLButtonElement = screen.getByRole('button', {
      name: 'Paket für Steuerberater',
    })
    expect(packageButton).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Lesbare PDF herunterladen' })).toBeEnabled()

    await user.click(
      screen.getByLabelText(/Ich habe die Fehler gesehen und möchte trotzdem exportieren/i),
    )
    expect(packageButton).toBeEnabled()
  })

  it('shows a prior-processing banner when the same Beleg was already checked', (): void => {
    const invoice: InvoiceParseResponse = buildInvoice({
      duplicate: {
        processed_at: '2026-08-15T12:00:00+00:00',
        message: 'Diesen Beleg haben Sie bereits am 15.08.2026 verarbeitet.',
        match: 'file',
        history_id: '00000000-0000-0000-0000-000000000099',
      },
    })
    render(<InvoiceView invoice={invoice} />)

    expect(
      screen.getByText('Diesen Beleg haben Sie bereits am 15.08.2026 verarbeitet.'),
    ).toBeInTheDocument()
    expect(screen.getByText(/zweite Buchung oder Zahlung/)).toBeInTheDocument()
  })

  it('downloads a working-copy PDF without accounting confirmation', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(downloadViewPdf).mockResolvedValue()
    const invoice: InvoiceParseResponse = buildInvoice()
    render(<InvoiceView invoice={invoice} />)

    await user.click(screen.getByRole('button', { name: 'Lesbare PDF herunterladen' }))
    expect(downloadViewPdf).toHaveBeenCalledWith(invoice)
  })
})

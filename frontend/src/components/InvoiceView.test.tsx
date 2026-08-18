import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { InvoiceView } from './InvoiceView'
import { buildInvoice, buildInvalidInvoice } from '../test/fixtures'
import type { InvoiceParseResponse } from '../types/invoice'

vi.mock('../api/client', (): Record<string, ReturnType<typeof vi.fn>> => ({
  exportInvoice: vi.fn(),
  downloadAccountantPackage: vi.fn(),
  downloadValidationReport: vi.fn(),
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

    await user.click(
      screen.getByLabelText(/Ich habe die Fehler gesehen und möchte trotzdem exportieren/i),
    )
    expect(packageButton).toBeEnabled()
  })
})

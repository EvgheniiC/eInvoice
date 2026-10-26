import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { buildIssue, createIssueDraft } from '../api/client'
import type { IssueBuildResponse, IssueDraftResponse } from '../types/issue'
import { IssuePage } from './IssuePage'

vi.mock('../api/client', (): {
  createIssueDraft: ReturnType<typeof vi.fn>
  buildIssue: ReturnType<typeof vi.fn>
} => ({
  createIssueDraft: vi.fn(),
  buildIssue: vi.fn(),
}))

const DRAFT: IssueDraftResponse = {
  filename: 'rechnung.pdf',
  text_found: true,
  hints: [],
  warnings: ['Positionen werden nicht automatisch übernommen.'],
  draft: {
    invoice_number: 'RE-1',
    issue_date: '2026-10-26',
    currency: 'EUR',
    buyer_reference: null,
    seller: {
      name: 'Muster GmbH',
      address: { line: null, postcode: null, city: null, country: 'DE' },
      vat_id: null,
      email: null,
      contact_name: null,
      phone: null,
      iban: null,
    },
    buyer: {
      name: null,
      address: { line: null, postcode: null, city: null, country: 'DE' },
      vat_id: null,
      email: null,
      contact_name: null,
      phone: null,
      iban: null,
    },
    lines: [
      {
        description: null,
        quantity: null,
        unit_code: 'C62',
        unit_price: null,
        tax_rate: '19',
      },
    ],
  },
}

const BLOCKED: IssueBuildResponse = {
  ready: false,
  message: 'Die E-Rechnung ist noch nicht freigegeben.',
  blocking_issues: [
    {
      level: 'error',
      category: 'business',
      code: 'BT-1_MISSING',
      message: 'Pflichtfeld fehlt: Rechnungsnummer (BT-1).',
      explanation: null,
      bt_code: null,
      field: 'invoice_number',
    },
  ],
  artifacts: [
    {
      format: 'xrechnung',
      filename: 'RE-1-xrechnung.xml',
      media_type: 'application/xml',
      content_base64: null,
      download_allowed: false,
      validation_status: 'not_checked',
      validation_issues: [],
    },
  ],
}

describe('IssuePage', (): void => {
  it('keeps the download closed until the build explicitly allows it', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(createIssueDraft).mockResolvedValue(DRAFT)
    vi.mocked(buildIssue).mockResolvedValue(BLOCKED)
    render(<IssuePage onNavigate={() => undefined} session={null} onLogout={() => undefined} />)

    expect(screen.getByRole('heading', { name: 'E-Rechnung aus PDF erstellen' })).toBeInTheDocument()
    expect(screen.getByText(/Maßgeblich ist die XML/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /herunterladen/ })).not.toBeInTheDocument()

    const file: File = new File(['%PDF'], 'rechnung.pdf', { type: 'application/pdf' })
    await user.upload(screen.getByLabelText('Eigene PDF-Rechnung'), file)
    await user.click(screen.getByRole('button', { name: 'Entwurf lesen' }))
    expect(await screen.findByDisplayValue('RE-1')).toBeInTheDocument()

    await user.click(screen.getByLabelText(/Ich bin der Rechnungsaussteller/))
    await user.click(screen.getByRole('button', { name: 'E-Rechnung prüfen' }))

    expect(await screen.findByText('Download geschlossen.')).toBeInTheDocument()
    expect(screen.getByText('Pflichtfeld fehlt: Rechnungsnummer (BT-1).')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /herunterladen/ })).not.toBeInTheDocument()
  })
})

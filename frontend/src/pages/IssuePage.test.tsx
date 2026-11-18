import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { buildIssue, createIssueDraft } from '../api/client'
import { buildSession } from '../test/fixtures'
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
    {
      level: 'error',
      category: 'business',
      code: 'BT-129_MISSING',
      message: 'Position 1: Menge fehlt oder ist ungültig.',
      explanation: null,
      bt_code: null,
      field: 'lines.1.quantity',
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

const READY: IssueBuildResponse = {
  ready: true,
  message: 'KoSIT hat die Datei als gültig abgeschlossen.',
  blocking_issues: [],
  artifacts: [
    {
      format: 'xrechnung',
      filename: 'RE-1-xrechnung.xml',
      media_type: 'application/xml',
      content_base64: btoa('<xml/>'),
      download_allowed: true,
      validation_status: 'valid',
      validation_issues: [],
    },
    {
      format: 'zugferd_pdf',
      filename: 'RE-1-zugferd.pdf',
      media_type: 'application/pdf',
      content_base64: btoa('%PDF'),
      download_allowed: true,
      validation_status: 'valid',
      validation_issues: [],
    },
  ],
}

async function fillRequired(user: UserEvent): Promise<void> {
  const streets: HTMLElement[] = screen.getAllByLabelText('Straße')
  const postcodes: HTMLElement[] = screen.getAllByLabelText('PLZ')
  const cities: HTMLElement[] = screen.getAllByLabelText('Ort')
  const names: HTMLElement[] = screen.getAllByLabelText('Name')
  await user.type(streets[0], 'Hauptstr. 1')
  await user.type(postcodes[0], '80331')
  await user.type(cities[0], 'München')
  await user.type(screen.getByLabelText('USt-IdNr.'), 'DE123456789')
  await user.type(screen.getByLabelText('IBAN'), 'DE89370400440532013000')
  await user.type(names[1], 'Kunde GmbH')
  await user.type(streets[1], 'Nebenstr. 2')
  await user.type(postcodes[1], '10115')
  await user.type(cities[1], 'Berlin')
  await user.type(screen.getByLabelText('Position 1'), 'Beratung')
  await user.type(screen.getByLabelText('Menge'), '1')
  await user.type(screen.getByLabelText('Einzelpreis netto'), '10')
}

describe('IssuePage', (): void => {
  it('keeps the download closed until the build explicitly allows it', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup({ delay: null })
    const createObjectURL: ReturnType<typeof vi.spyOn> = vi
      .spyOn(URL, 'createObjectURL')
      .mockReturnValue('blob:test')
    vi.mocked(createIssueDraft).mockResolvedValue(DRAFT)
    vi.mocked(buildIssue).mockResolvedValue(BLOCKED)
    render(
      <IssuePage
        onNavigate={() => undefined}
        session={buildSession({ is_admin: true })}
        sessionReady
        onLogout={() => undefined}
      />,
    )

    expect(screen.getByRole('heading', { name: 'E-Rechnung aus PDF erstellen' })).toBeInTheDocument()
    expect(screen.getByText(/Maßgeblich ist die XML/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Download als ZUGFeRD PDF' })).not.toBeInTheDocument()

    const file: File = new File(['%PDF'], 'rechnung.pdf', { type: 'application/pdf' })
    await user.upload(screen.getByLabelText('Eigene PDF-Rechnung'), file)
    await user.click(screen.getByRole('button', { name: 'Entwurf lesen' }))
    expect(await screen.findByDisplayValue('RE-1')).toBeInTheDocument()
    await user.type(screen.getByLabelText('Ansprechpartner'), 'Anna Schmidt')
    expect(screen.getByLabelText('Ansprechpartner')).toHaveValue('Anna Schmidt')
    expect(screen.getByLabelText('Ansprechpartner')).toHaveAttribute('maxLength', '200')
    expect(screen.getByRole('button', { name: 'Download als ZUGFeRD PDF' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Download als XRechnung (XML)' })).toBeDisabled()

    await fillRequired(user)
    expect(screen.getByRole('button', { name: 'Download als ZUGFeRD PDF' })).toBeDisabled()
    expect(screen.getByRole('checkbox', { name: /Ich bin der Rechnungsaussteller/ })).toHaveAttribute(
      'aria-invalid',
      'true',
    )
    await user.click(screen.getByLabelText(/Ich bin der Rechnungsaussteller/))
    expect(screen.getByRole('checkbox', { name: /Ich bin der Rechnungsaussteller/ })).not.toHaveAttribute(
      'aria-invalid',
    )
    await user.click(screen.getByRole('button', { name: 'Download als ZUGFeRD PDF' }))

    expect(await screen.findByText('Pflichtfeld fehlt: Rechnungsnummer (BT-1).')).toBeInTheDocument()
    expect(createObjectURL).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Rechnungsnummer')).toHaveAttribute('aria-invalid', 'true')
    createObjectURL.mockRestore()
  })

  it('downloads the chosen format after a valid build', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup({ delay: null })
    const createObjectURL: ReturnType<typeof vi.spyOn> = vi
      .spyOn(URL, 'createObjectURL')
      .mockReturnValue('blob:test')
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined)
    vi.mocked(createIssueDraft).mockResolvedValue(DRAFT)
    vi.mocked(buildIssue).mockResolvedValue(READY)
    render(
      <IssuePage
        onNavigate={() => undefined}
        session={buildSession({ is_admin: true })}
        sessionReady
        onLogout={() => undefined}
      />,
    )

    const file: File = new File(['%PDF'], 'rechnung.pdf', { type: 'application/pdf' })
    await user.upload(screen.getByLabelText('Eigene PDF-Rechnung'), file)
    await user.click(screen.getByRole('button', { name: 'Entwurf lesen' }))
    await screen.findByDisplayValue('RE-1')
    await fillRequired(user)
    await user.click(screen.getByLabelText(/Ich bin der Rechnungsaussteller/))
    await user.click(screen.getByRole('button', { name: 'Download als XRechnung (XML)' }))

    expect(await screen.findByText('KoSIT hat die Datei als gültig abgeschlossen.')).toBeInTheDocument()
    expect(createObjectURL).toHaveBeenCalledTimes(1)
    createObjectURL.mockRestore()
  })

  it('shows that the check is running while the download request is open', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup({ delay: null })
    let resolveBuild: (value: IssueBuildResponse) => void = (): void => undefined
    vi.mocked(createIssueDraft).mockResolvedValue(DRAFT)
    vi.mocked(buildIssue).mockImplementation(
      (): Promise<IssueBuildResponse> =>
        new Promise((resolve: (value: IssueBuildResponse) => void): void => {
          resolveBuild = resolve
        }),
    )
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test')
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation((): void => undefined)
    render(
      <IssuePage
        onNavigate={() => undefined}
        session={buildSession({ is_admin: true })}
        sessionReady
        onLogout={() => undefined}
      />,
    )

    const file: File = new File(['%PDF'], 'rechnung.pdf', { type: 'application/pdf' })
    await user.upload(screen.getByLabelText('Eigene PDF-Rechnung'), file)
    await user.click(screen.getByRole('button', { name: 'Entwurf lesen' }))
    await screen.findByDisplayValue('RE-1')
    await fillRequired(user)
    await user.click(screen.getByLabelText(/Ich bin der Rechnungsaussteller/))
    await user.click(screen.getByRole('button', { name: 'Download als XRechnung (XML)' }))

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Die Rechnung wird geprüft. Das kann einen Moment dauern.',
    )
    expect(screen.getByRole('button', { name: 'Wird geprüft…' })).toBeDisabled()
    resolveBuild(READY)
    expect(await screen.findByText('KoSIT hat die Datei als gültig abgeschlossen.')).toBeInTheDocument()
  })

  it('shows the form to a signed-in user', (): void => {
    render(
      <IssuePage
        onNavigate={() => undefined}
        session={buildSession({ is_admin: false })}
        sessionReady
        onLogout={() => undefined}
      />,
    )
    expect(screen.getByLabelText('Eigene PDF-Rechnung')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows the form to a guest', (): void => {
    render(
      <IssuePage
        onNavigate={() => undefined}
        session={null}
        sessionReady
        onLogout={() => undefined}
      />,
    )
    expect(screen.getByLabelText('Eigene PDF-Rechnung')).toBeInTheDocument()
    expect(screen.getByText(/Ohne Tarif sind 10 E-Rechnungen pro Tag/)).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })
})

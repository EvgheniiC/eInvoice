import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchOrganization, updateOrganization } from '../api/client'
import { buildSession } from '../test/fixtures'
import type { MeResponse, OrgResponse } from '../types/invoice'
import { OrgSettingsPage } from './OrgSettingsPage'

vi.mock('../api/client', (): {
  fetchOrganization: ReturnType<typeof vi.fn>
  updateOrganization: ReturnType<typeof vi.fn>
  changeAccountPassword: ReturnType<typeof vi.fn>
} => ({
  fetchOrganization: vi.fn(),
  updateOrganization: vi.fn(),
  changeAccountPassword: vi.fn(),
}))

function orgResponse(overrides: Partial<OrgResponse> = {}): OrgResponse {
  const session = buildSession()
  return {
    organization_id: session.organization_id,
    name: session.organization_name,
    role: session.role,
    plan: session.plan,
    created_at: '2026-08-22T10:00:00+00:00',
    history_enabled: false,
    store_originals_enabled: false,
    tax_number: null,
    vat_id: null,
    iban: null,
    accountant_email: null,
    ...overrides,
  }
}

describe('OrgSettingsPage', (): void => {
  beforeEach((): void => {
    vi.mocked(fetchOrganization).mockReset()
    vi.mocked(updateOrganization).mockReset()
    vi.mocked(fetchOrganization).mockResolvedValue(orgResponse())
  })

  it('asks guests to sign in', (): void => {
    render(
      <OrgSettingsPage
        onNavigate={vi.fn()}
        session={null}
        onSession={vi.fn()}
        onLogout={vi.fn()}
      />,
    )
    expect(screen.getByRole('heading', { name: 'Organisation' })).toBeInTheDocument()
    expect(screen.getByText('Bitte zuerst anmelden.')).toBeInTheDocument()
  })

  it('loads and saves the firm profile', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onSession: (session: MeResponse | null) => void = vi.fn()
    vi.mocked(fetchOrganization).mockResolvedValue(
      orgResponse({
        tax_number: '12/345/67890',
        vat_id: 'DE123456789',
        iban: 'DE89370400440532013000',
        accountant_email: 'sb@kanzlei.de',
      }),
    )
    vi.mocked(updateOrganization).mockResolvedValue(
      orgResponse({
        name: 'Muster Handwerk GmbH',
        tax_number: '12/345/67890',
        vat_id: 'DE123456789',
        iban: 'DE89370400440532013000',
        accountant_email: 'sb@kanzlei.de',
      }),
    )

    render(
      <OrgSettingsPage
        onNavigate={vi.fn()}
        session={buildSession()}
        onSession={onSession}
        onLogout={vi.fn()}
      />,
    )

    expect(await screen.findByDisplayValue('12/345/67890')).toBeInTheDocument()
    const nameInput: HTMLElement = screen.getByLabelText('Name der Organisation')
    await user.clear(nameInput)
    await user.type(nameInput, 'Muster Handwerk GmbH')
    await user.click(screen.getByRole('button', { name: 'Profil speichern' }))

    await waitFor((): void => {
      expect(updateOrganization).toHaveBeenCalledWith({
        name: 'Muster Handwerk GmbH',
        tax_number: '12/345/67890',
        vat_id: 'DE123456789',
        iban: 'DE89370400440532013000',
        accountant_email: 'sb@kanzlei.de',
      })
    })
    expect(onSession).toHaveBeenCalled()
    expect(screen.getByText(/Firmenprofil gespeichert/)).toBeInTheDocument()
  })

  it('shows field errors next to invalid USt-IdNr and IBAN', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(fetchOrganization).mockResolvedValue(orgResponse({ name: 'ABC' }))

    render(
      <OrgSettingsPage
        onNavigate={vi.fn()}
        session={buildSession({ organization_name: 'ABC' })}
        onSession={vi.fn()}
        onLogout={vi.fn()}
      />,
    )

    expect(await screen.findByDisplayValue('ABC')).toBeInTheDocument()
    await user.type(screen.getByLabelText(/USt-IdNr/), '123')
    await user.type(screen.getByLabelText(/^IBAN/), 'TEST12345')
    await user.click(screen.getByRole('button', { name: 'Profil speichern' }))

    expect(updateOrganization).not.toHaveBeenCalled()
    expect(screen.getByText(/USt-IdNr\. ist ungültig/)).toBeInTheDocument()
    expect(screen.getByText(/IBAN ist ungültig/)).toBeInTheDocument()
    expect(screen.getByLabelText(/USt-IdNr/)).toHaveClass('auth-form__input--error')
    expect(screen.getByLabelText(/^IBAN/)).toHaveClass('auth-form__input--error')
  })
})

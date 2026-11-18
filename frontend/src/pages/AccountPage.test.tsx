import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { REGISTRATION_BENEFITS } from '../content/accountBenefits'
import { buildSession } from '../test/fixtures'
import type { AppRoute } from '../routing'
import { AccountPage } from './AccountPage'

describe('AccountPage', (): void => {
  it('explains registration benefits to a guest', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute) => void = vi.fn()

    render(<AccountPage onNavigate={onNavigate} session={null} onLogout={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Konto' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Was die Registrierung bringt' })).toBeInTheDocument()
    for (const benefit of REGISTRATION_BENEFITS) {
      expect(screen.getByText(benefit)).toBeInTheDocument()
    }

    await user.click(screen.getByRole('button', { name: 'Registrieren' }))
    expect(onNavigate).toHaveBeenCalledWith('register')
  })

  it('shows the plan, quotas and the three tasks for a signed-in user', (): void => {
    render(
      <AccountPage
        onNavigate={vi.fn()}
        session={buildSession({
          plan: {
            code: 'free',
            name: 'Free',
            parse_per_day: 10,
            export_per_day: 10,
            issue_per_day: 10,
            max_upload_size_mb: 10,
            max_parallel: 1,
            allows_batch: false,
            allows_history: false,
            max_batch_files: 0,
            quotas_enforced: true,
            parse_used_today: 2,
            export_used_today: 1,
            issue_used_today: 0,
          },
        })}
        onLogout={vi.fn()}
      />,
    )

    expect(screen.getByText(/Muster Handwerk/)).toBeInTheDocument()
    expect(screen.getByText(/Tarif Free/)).toBeInTheDocument()
    expect(screen.getByText('Heute: 2/10 Prüfungen, 1/10 Exporte, 0/10 E-Rechnungen.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Eingangsrechnung öffnen' })).toHaveAttribute('href', '/upload')
    expect(screen.getByRole('link', { name: 'Validierung öffnen' })).toHaveAttribute(
      'href',
      '/erechnung-validation',
    )
    expect(screen.getByRole('link', { name: 'E-Rechnung aus PDF' })).toHaveAttribute('href', '/erstellen')
    expect(screen.getByRole('button', { name: 'Verlauf ab Plus' })).toBeInTheDocument()
  })
})

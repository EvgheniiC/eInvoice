import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { fetchAdminStats } from '../api/client'
import type { AppRoute } from '../routing'
import { buildSession } from '../test/fixtures'
import type { AdminStatsResponse } from '../types/invoice'
import { AdminStatsPage } from './AdminStatsPage'

vi.mock('../api/client', (): { fetchAdminStats: ReturnType<typeof vi.fn> } => ({
  fetchAdminStats: vi.fn(),
}))

const stats: AdminStatsResponse = {
  visits_today: 3,
  paid_plan_users: 2,
  visits_by_day: [{ visit_date: '2026-10-06', visitors: 3 }],
}

describe('AdminStatsPage', (): void => {
  it('shows daily visits and paid-plan people to an administrator', async (): Promise<void> => {
    vi.mocked(fetchAdminStats).mockResolvedValue(stats)
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute) => void = vi.fn()

    render(
      <AdminStatsPage
        onNavigate={onNavigate}
        session={buildSession({ email: 'admin@example.com', is_admin: true })}
        sessionReady={true}
        onLogout={vi.fn()}
      />,
    )

    expect(await screen.findByRole('heading', { name: 'Statistik' })).toBeInTheDocument()
    expect(screen.getByText('Besuche heute').parentElement).toHaveTextContent('3')
    expect(screen.getByText('Personen mit Plus oder Team').parentElement).toHaveTextContent('2')
    expect(screen.getByRole('cell', { name: '06.10.2026' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Statistik' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: '← eInvoice' }))
    expect(onNavigate).toHaveBeenCalledWith('landing')
  })

  it('hides the page from other accounts', (): void => {
    render(
      <AdminStatsPage
        onNavigate={vi.fn()}
        session={buildSession({ is_admin: false })}
        sessionReady={true}
        onLogout={vi.fn()}
      />,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('Kein Zugriff.')
    expect(screen.queryByRole('button', { name: 'Statistik' })).not.toBeInTheDocument()
    expect(fetchAdminStats).not.toHaveBeenCalled()
  })
})

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { createPlanRequest } from '../api/client'
import type { AppRoute } from '../routing'
import { buildSession } from '../test/fixtures'
import type { PlanUpgradeRequestResponse } from '../types/invoice'
import { PricingPage } from './PricingPage'

vi.mock('../api/client', (): { createPlanRequest: ReturnType<typeof vi.fn> } => ({
  createPlanRequest: vi.fn(),
}))

function requestResponse(): PlanUpgradeRequestResponse {
  return {
    id: '00000000-0000-0000-0000-000000000077',
    organization_id: '00000000-0000-0000-0000-000000000002',
    requested_by_user_id: '00000000-0000-0000-0000-000000000001',
    requested_plan: 'plus',
    status: 'pending',
    message: null,
    created_at: '2026-08-25T18:00:00+00:00',
    updated_at: '2026-08-25T18:00:00+00:00',
  }
}

describe('PricingPage', (): void => {
  it('shows public plans and sends an upgrade request for the owner', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(createPlanRequest).mockResolvedValue(requestResponse())

    render(
      <PricingPage
        onNavigate={vi.fn()}
        session={buildSession()}
        onLogout={vi.fn()}
      />,
    )

    expect(screen.getByRole('heading', { name: 'Free' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Plus' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Team' })).toBeInTheDocument()
    expect(screen.getByText('12,90 €')).toBeInTheDocument()
    expect(screen.getByText('24,90 €')).toBeInTheDocument()

    const requestButtons: HTMLElement[] = screen.getAllByRole('button', {
      name: 'Freischaltung anfragen',
    })
    await user.click(requestButtons[0])

    await waitFor((): void => {
      expect(createPlanRequest).toHaveBeenCalledWith('plus')
    })
    expect(screen.getByText(/Anfrage für Plus ist eingegangen/)).toBeInTheDocument()
  })

  it('sends guests to registration', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute) => void = vi.fn()

    render(
      <PricingPage
        onNavigate={onNavigate}
        session={null}
        onLogout={vi.fn()}
      />,
    )

    await user.click(screen.getAllByRole('button', { name: 'Konto erstellen' })[0])
    expect(onNavigate).toHaveBeenCalledWith('register')
    expect(createPlanRequest).not.toHaveBeenCalled()
  })
})

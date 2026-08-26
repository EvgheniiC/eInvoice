import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { completeBillingCheckout, createBillingCheckout, fetchMe } from '../api/client'
import type { AppRoute } from '../routing'
import { buildSession } from '../test/fixtures'
import type { BillingCheckoutResponse, BillingCompleteResponse, MeResponse } from '../types/invoice'
import { PricingPage } from './PricingPage'

vi.mock('../api/client', (): {
  createBillingCheckout: ReturnType<typeof vi.fn>
  completeBillingCheckout: ReturnType<typeof vi.fn>
  fetchMe: ReturnType<typeof vi.fn>
} => ({
  createBillingCheckout: vi.fn(),
  completeBillingCheckout: vi.fn(),
  fetchMe: vi.fn(),
}))

function checkoutResponse(): BillingCheckoutResponse {
  return {
    checkout_url: 'http://localhost:5173/tarife?checkout=success&session=stub_paid_token',
    session_id: 'stub_paid_token',
    provider: 'stub',
  }
}

function completeResponse(): BillingCompleteResponse {
  return {
    accepted: true,
    provider: 'stub',
    plan_code: 'plus',
    plan_name: 'Plus',
    message: 'Zahlung bestätigt. Ihr Tarif ist jetzt Plus.',
  }
}

function plusSession(): MeResponse {
  return buildSession({
    plan: {
      code: 'plus',
      name: 'Plus',
      parse_per_day: 100,
      export_per_day: 100,
      max_upload_size_mb: 25,
      max_parallel: 2,
      allows_batch: true,
      allows_history: true,
      max_batch_files: 20,
      quotas_enforced: true,
      parse_used_today: 0,
      export_used_today: 0,
    },
  })
}

describe('PricingPage', (): void => {
  it('starts checkout and applies the plan after the stub return', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute, query?: string) => void = vi.fn()
    const onSession: (session: MeResponse | null) => void = vi.fn()
    vi.mocked(createBillingCheckout).mockResolvedValue(checkoutResponse())
    vi.mocked(completeBillingCheckout).mockResolvedValue(completeResponse())
    vi.mocked(fetchMe).mockResolvedValue(plusSession())

    const view = render(
      <PricingPage
        onNavigate={onNavigate}
        session={buildSession()}
        onSession={onSession}
        locationSearch=""
        onLogout={vi.fn()}
      />,
    )

    expect(screen.getByRole('heading', { name: 'Free' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Plus' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Team' })).toBeInTheDocument()
    expect(screen.getByText('4,99 €')).toBeInTheDocument()
    expect(screen.getByText('9,99 €')).toBeInTheDocument()

    const upgradeButtons: HTMLElement[] = screen.getAllByRole('button', { name: 'Jetzt upgraden' })
    await user.click(upgradeButtons[0])

    await waitFor((): void => {
      expect(createBillingCheckout).toHaveBeenCalledWith('plus')
    })
    expect(onNavigate).toHaveBeenCalledWith('pricing', '?checkout=success&session=stub_paid_token')

    view.rerender(
      <PricingPage
        onNavigate={onNavigate}
        session={buildSession()}
        onSession={onSession}
        locationSearch="?checkout=success&session=stub_paid_token"
        onLogout={vi.fn()}
      />,
    )

    expect(await screen.findByText('Zahlung bestätigt. Ihr Tarif ist jetzt Plus.')).toBeInTheDocument()
    expect(completeBillingCheckout).toHaveBeenCalledWith('stub_paid_token')
    expect(onSession).toHaveBeenCalledWith(plusSession())
    expect(onNavigate).toHaveBeenCalledWith('pricing')
  })

  it('sends guests to registration', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute, query?: string) => void = vi.fn()

    render(
      <PricingPage
        onNavigate={onNavigate}
        session={null}
        onSession={vi.fn()}
        locationSearch=""
        onLogout={vi.fn()}
      />,
    )

    await user.click(screen.getAllByRole('button', { name: 'Konto erstellen' })[0])
    expect(onNavigate).toHaveBeenCalledWith('register')
    expect(createBillingCheckout).not.toHaveBeenCalled()
  })
})

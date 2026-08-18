import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { loginAccount } from '../api/client'
import { LoginPage } from './LoginPage'
import type { AppRoute } from '../routing'
import type { MeResponse } from '../types/invoice'

vi.mock('../api/client', (): {
  loginAccount: ReturnType<typeof vi.fn>
  requestMagicLink: ReturnType<typeof vi.fn>
} => ({
  loginAccount: vi.fn(),
  requestMagicLink: vi.fn(),
}))

describe('LoginPage', (): void => {
  it('submits email and password', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onLoggedIn: (session: MeResponse) => void = vi.fn()
    const onNavigate: (route: AppRoute) => void = vi.fn()
    const session: MeResponse = {
      user_id: '00000000-0000-0000-0000-000000000001',
      email: 'meister@example.com',
      email_verified: true,
      organization_id: '00000000-0000-0000-0000-000000000002',
      organization_name: 'Muster Handwerk',
      role: 'inhaber',
      plan: {
        code: 'free',
        name: 'Free',
        parse_per_day: null,
        export_per_day: null,
        max_upload_size_mb: 10,
        allows_batch: false,
        allows_history: false,
        quotas_enforced: false,
      },
      memberships: [],
    }
    vi.mocked(loginAccount).mockResolvedValue(session)

    render(
      <LoginPage
        onNavigate={onNavigate}
        onLoggedIn={onLoggedIn}
        session={null}
        onLogout={vi.fn()}
      />,
    )

    await user.type(screen.getByLabelText('E-Mail'), 'meister@example.com')
    await user.type(screen.getByLabelText('Passwort'), 'sicher-passwort-1')
    await user.click(screen.getByRole('button', { name: 'Mit Passwort anmelden' }))

    expect(loginAccount).toHaveBeenCalledWith('meister@example.com', 'sicher-passwort-1')
    expect(onLoggedIn).toHaveBeenCalledWith(session)
    expect(onNavigate).toHaveBeenCalledWith('org')
  })
})

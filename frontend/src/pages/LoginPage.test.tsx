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
  resendVerification: ReturnType<typeof vi.fn>
} => ({
  loginAccount: vi.fn(),
  requestMagicLink: vi.fn(),
  resendVerification: vi.fn(),
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
        parse_per_day: 10,
        export_per_day: 10,
        max_upload_size_mb: 10,
        max_parallel: 1,
        allows_batch: false,
        allows_history: false,
        max_batch_files: 0,
        quotas_enforced: true,
        parse_used_today: 0,
        export_used_today: 0,
      },
      memberships: [],
    }
    vi.mocked(loginAccount).mockResolvedValue(session)

    render(
      <LoginPage
        onNavigate={onNavigate}
        onLoggedIn={onLoggedIn}
        onForgotPassword={vi.fn()}
        session={null}
        onLogout={vi.fn()}
        notice={null}
        initialEmail=""
        verificationToken={null}
      />,
    )

    await user.type(screen.getByLabelText('E-Mail'), 'meister@example.com')
    await user.type(screen.getByLabelText('Passwort'), 'sicher-passwort-1')
    await user.click(screen.getByRole('button', { name: 'Mit Passwort anmelden' }))

    expect(loginAccount).toHaveBeenCalledWith('meister@example.com', 'sicher-passwort-1')
    expect(onLoggedIn).toHaveBeenCalledWith(session)
    expect(onNavigate).toHaveBeenCalledWith('org')
  })

  it('lets the monkey toggle password visibility', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()

    render(
      <LoginPage
        onNavigate={vi.fn()}
        onLoggedIn={vi.fn()}
        onForgotPassword={vi.fn()}
        session={null}
        onLogout={vi.fn()}
        notice={null}
        initialEmail=""
        verificationToken={null}
      />,
    )

    const passwordInput: HTMLInputElement = screen.getByLabelText('Passwort')
    expect(passwordInput).toHaveAttribute('type', 'password')

    await user.click(screen.getByRole('button', { name: 'Passwort anzeigen' }))
    expect(passwordInput).toHaveAttribute('type', 'text')

    await user.click(screen.getByRole('button', { name: 'Passwort verbergen' }))
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('shows the registration notice and prefills email', (): void => {
    render(
      <LoginPage
        onNavigate={vi.fn()}
        onLoggedIn={vi.fn()}
        onForgotPassword={vi.fn()}
        session={null}
        onLogout={vi.fn()}
        notice="Bitte prüfen Sie Ihre E-Mail und bestätigen Sie das Konto."
        initialEmail="lucky1.lucky@gmx.de"
        verificationToken="dev-token"
      />,
    )

    expect(screen.getByRole('status')).toHaveTextContent(
      'Bitte prüfen Sie Ihre E-Mail und bestätigen Sie das Konto.',
    )
    expect(screen.getByLabelText('E-Mail')).toHaveValue('lucky1.lucky@gmx.de')
    expect(screen.getByRole('button', { name: 'Bestätigungslink öffnen' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Bestätigung erneut senden' })).toBeInTheDocument()
  })

  it('opens the forgot-password page', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onForgotPassword: (email: string) => void = vi.fn()

    render(
      <LoginPage
        onNavigate={vi.fn()}
        onLoggedIn={vi.fn()}
        onForgotPassword={onForgotPassword}
        session={null}
        onLogout={vi.fn()}
        notice={null}
        initialEmail=""
        verificationToken={null}
      />,
    )

    await user.type(screen.getByLabelText('E-Mail'), 'meister@example.com')
    await user.click(screen.getByRole('button', { name: 'Passwort vergessen?' }))
    expect(onForgotPassword).toHaveBeenCalledWith('meister@example.com')
  })
})

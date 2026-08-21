import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { registerAccount } from '../api/client'
import { RegisterPage, type RegisterSuccess } from './RegisterPage'
import type { AppRoute } from '../routing'
import type { RegisterResponse } from '../types/invoice'

vi.mock('../api/client', (): {
  registerAccount: ReturnType<typeof vi.fn>
} => ({
  registerAccount: vi.fn(),
}))

describe('RegisterPage', (): void => {
  it('registers without organisation when passwords match', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute) => void = vi.fn()
    const onRegistered: (result: RegisterSuccess) => void = vi.fn()
    const result: RegisterResponse = {
      accepted: true,
      message: 'Bitte prüfen Sie Ihre E-Mail und bestätigen Sie das Konto.',
      verification_token: 'dev-token',
    }
    vi.mocked(registerAccount).mockResolvedValue(result)

    render(
      <RegisterPage
        onNavigate={onNavigate}
        onRegistered={onRegistered}
        session={null}
        onLogout={vi.fn()}
      />,
    )

    await user.type(screen.getByLabelText('E-Mail'), 'meister@example.com')
    await user.type(screen.getByLabelText('Passwort (mind. 10 Zeichen)'), 'sicher-passwort-1')
    await user.type(screen.getByLabelText('Passwort wiederholen'), 'sicher-passwort-1')
    await user.click(screen.getByRole('button', { name: 'Registrieren' }))

    expect(registerAccount).toHaveBeenCalledWith('meister@example.com', 'sicher-passwort-1', '')
    expect(onRegistered).toHaveBeenCalledWith({
      email: 'meister@example.com',
      message: result.message,
      verificationToken: 'dev-token',
    })
    expect(onNavigate).not.toHaveBeenCalled()
  })

  it('blocks submit when passwords do not match', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onRegistered: (result: RegisterSuccess) => void = vi.fn()

    render(
      <RegisterPage
        onNavigate={vi.fn()}
        onRegistered={onRegistered}
        session={null}
        onLogout={vi.fn()}
      />,
    )

    await user.type(screen.getByLabelText('E-Mail'), 'meister@example.com')
    await user.type(screen.getByLabelText('Passwort (mind. 10 Zeichen)'), 'sicher-passwort-1')
    await user.type(screen.getByLabelText('Passwort wiederholen'), 'anderes-passwort-9')
    await user.click(screen.getByRole('button', { name: 'Registrieren' }))

    expect(registerAccount).not.toHaveBeenCalled()
    expect(onRegistered).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent('Die Passwörter stimmen nicht überein.')
  })

  it('lets the monkey toggle password visibility', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()

    render(
      <RegisterPage onNavigate={vi.fn()} onRegistered={vi.fn()} session={null} onLogout={vi.fn()} />,
    )

    const passwordInput: HTMLInputElement = screen.getByLabelText('Passwort (mind. 10 Zeichen)')
    expect(passwordInput).toHaveAttribute('type', 'password')

    await user.click(screen.getByRole('button', { name: 'Passwort (mind. 10 Zeichen) anzeigen' }))
    expect(passwordInput).toHaveAttribute('type', 'text')

    await user.click(screen.getByRole('button', { name: 'Passwort (mind. 10 Zeichen) verbergen' }))
    expect(passwordInput).toHaveAttribute('type', 'password')
  })
})

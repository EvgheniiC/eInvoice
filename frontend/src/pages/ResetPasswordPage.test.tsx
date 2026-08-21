import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { resetAccountPassword } from '../api/client'
import { ResetPasswordPage } from './ResetPasswordPage'
import type { MessageResponse } from '../types/invoice'

vi.mock('../api/client', (): {
  resetAccountPassword: ReturnType<typeof vi.fn>
} => ({
  resetAccountPassword: vi.fn(),
}))

describe('ResetPasswordPage', (): void => {
  it('sets a new password when both fields match', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onReset: (message: string) => void = vi.fn()
    const result: MessageResponse = {
      accepted: true,
      message: 'Passwort geändert. Bitte erneut anmelden.',
      token: null,
    }
    vi.mocked(resetAccountPassword).mockResolvedValue(result)

    render(
      <ResetPasswordPage
        onNavigate={vi.fn()}
        onReset={onReset}
        session={null}
        onLogout={vi.fn()}
        token="reset-token"
      />,
    )

    await user.type(screen.getByLabelText('Neues Passwort (mind. 10 Zeichen)'), 'anderes-passwort-9')
    await user.type(screen.getByLabelText('Passwort wiederholen'), 'anderes-passwort-9')
    await user.click(screen.getByRole('button', { name: 'Passwort speichern' }))

    expect(resetAccountPassword).toHaveBeenCalledWith('reset-token', 'anderes-passwort-9')
    expect(onReset).toHaveBeenCalledWith(result.message)
  })

  it('blocks submit when passwords do not match', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onReset: (message: string) => void = vi.fn()

    render(
      <ResetPasswordPage
        onNavigate={vi.fn()}
        onReset={onReset}
        session={null}
        onLogout={vi.fn()}
        token="reset-token"
      />,
    )

    await user.type(screen.getByLabelText('Neues Passwort (mind. 10 Zeichen)'), 'anderes-passwort-9')
    await user.type(screen.getByLabelText('Passwort wiederholen'), 'sicher-passwort-1')
    await user.click(screen.getByRole('button', { name: 'Passwort speichern' }))

    expect(resetAccountPassword).not.toHaveBeenCalled()
    expect(onReset).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent('Die Passwörter stimmen nicht überein.')
  })

  it('shows an error when the email token is missing', (): void => {
    render(
      <ResetPasswordPage
        onNavigate={vi.fn()}
        onReset={vi.fn()}
        session={null}
        onLogout={vi.fn()}
        token=""
      />,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('Der Link ist unvollständig.')
    expect(screen.getByRole('button', { name: 'Passwort speichern' })).toBeDisabled()
  })
})

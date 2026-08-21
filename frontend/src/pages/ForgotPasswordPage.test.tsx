import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { requestPasswordReset } from '../api/client'
import { ForgotPasswordPage } from './ForgotPasswordPage'
import type { AppRoute } from '../routing'
import type { MessageResponse } from '../types/invoice'

vi.mock('../api/client', (): {
  requestPasswordReset: ReturnType<typeof vi.fn>
} => ({
  requestPasswordReset: vi.fn(),
}))

describe('ForgotPasswordPage', (): void => {
  it('sends a reset mail for the entered address', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const result: MessageResponse = {
      accepted: true,
      message: 'Wenn ein bestätigtes Konto existiert, wurde eine E-Mail zum Zurücksetzen des Passworts gesendet.',
      token: null,
    }
    vi.mocked(requestPasswordReset).mockResolvedValue(result)

    render(
      <ForgotPasswordPage
        onNavigate={vi.fn()}
        session={null}
        onLogout={vi.fn()}
        initialEmail=""
      />,
    )

    await user.type(screen.getByLabelText('E-Mail'), 'meister@example.com')
    await user.click(screen.getByRole('button', { name: 'Link senden' }))

    expect(requestPasswordReset).toHaveBeenCalledWith('meister@example.com')
    expect(screen.getByRole('status')).toHaveTextContent(result.message)
  })

  it('goes back to login', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onNavigate: (route: AppRoute) => void = vi.fn()

    render(
      <ForgotPasswordPage
        onNavigate={onNavigate}
        session={null}
        onLogout={vi.fn()}
        initialEmail="meister@example.com"
      />,
    )

    expect(screen.getByLabelText('E-Mail')).toHaveValue('meister@example.com')
    await user.click(screen.getByRole('button', { name: 'Anmeldung' }))
    expect(onNavigate).toHaveBeenCalledWith('login')
  })
})

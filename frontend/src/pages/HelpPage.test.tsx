import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { submitFeedback } from '../api/client'
import { HelpPage } from './HelpPage'

vi.mock('../api/client', (): {
  submitFeedback: ReturnType<typeof vi.fn>
} => ({
  submitFeedback: vi.fn(),
}))

describe('HelpPage', (): void => {
  it('shows FAQ answers and submits text-only feedback', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(submitFeedback).mockResolvedValue({
      accepted: true,
      message: 'Vielen Dank. Ihre Nachricht wurde aufgenommen.',
    })

    render(<HelpPage onNavigate={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Hilfe & FAQ' })).toBeInTheDocument()
    expect(screen.getByText('Was ist eine XML-Rechnung?')).toBeInTheDocument()
    expect(
      screen.getByText(/PDF und XML weichen ab/i),
    ).toBeInTheDocument()

    await user.type(
      screen.getByLabelText('Nachricht'),
      'Die Export-Schaltflaeche war auf dem Handy schwer zu finden.',
    )
    await user.click(screen.getByRole('button', { name: 'Nachricht senden' }))

    expect(submitFeedback).toHaveBeenCalledTimes(1)
    expect(await screen.findByRole('status')).toHaveTextContent('Vielen Dank')
  })
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import App from './App'

describe('App', (): void => {
  afterEach((): void => {
    window.history.replaceState(null, '', '/')
  })

  it('opens the upload page from the landing CTA', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    window.history.replaceState(null, '', '/')
    render(<App />)

    const startButtons: HTMLElement[] = screen.getAllByRole('button', {
      name: 'Rechnung hochladen',
    })
    await user.click(startButtons[0])

    expect(screen.getByRole('heading', { name: 'Rechnung empfangen' })).toBeInTheDocument()
    expect(window.location.pathname).toBe('/upload')
    expect(document.title).toBe('XRechnung oder ZUGFeRD hochladen | eInvoice')
  })
})

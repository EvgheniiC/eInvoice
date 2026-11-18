import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { buildSession } from '../test/fixtures'
import { LandingPage } from './LandingPage'

vi.mock('../api/client', (): {
  fetchCapabilities: ReturnType<typeof vi.fn>
  recordFunnel: ReturnType<typeof vi.fn>
} => ({
  fetchCapabilities: vi.fn((): Promise<never> => new Promise((): void => undefined)),
  recordFunnel: vi.fn(),
}))

describe('LandingPage', (): void => {
  it('places the issue hint after the upload button for a signed-in user', (): void => {
    render(
      <LandingPage
        onNavigate={vi.fn()}
        session={buildSession({ is_admin: false })}
        onLogout={vi.fn()}
      />,
    )

    const hint: HTMLElement = screen.getByText(
      /Eigene PDF-Rechnung als E-Rechnung vorbereiten/,
    )
    const uploadButton: HTMLElement = screen.getAllByRole('link', {
      name: 'Rechnung hochladen',
    })[0]

    expect(hint).toHaveClass('landing-hero__issue')
    expect(hint).not.toHaveClass('landing-hero__note')
    expect(uploadButton.contains(hint)).toBe(false)
    expect(
      uploadButton.compareDocumentPosition(hint) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
  })

  it('shows the issue hint for a guest', (): void => {
    render(<LandingPage onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)

    expect(
      screen.getByText(/Eigene PDF-Rechnung als E-Rechnung vorbereiten/),
    ).toBeInTheDocument()
    const validationLinks: HTMLElement[] = screen.getAllByRole('link', { name: 'Validierung' })
    expect(validationLinks.length).toBeGreaterThan(0)
    for (const link of validationLinks) {
      expect(link).toHaveAttribute('href', '/erechnung-validation')
    }
  })
})

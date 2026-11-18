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
  it('places E-Rechnung erstellen next to the other hero buttons', (): void => {
    render(
      <LandingPage
        onNavigate={vi.fn()}
        session={buildSession({ is_admin: false })}
        onLogout={vi.fn()}
      />,
    )

    const heroButton = (name: string): HTMLElement =>
      screen
        .getAllByRole('link', { name })
        .find((link: HTMLElement): boolean => link.classList.contains('btn')) as HTMLElement

    const uploadButton: HTMLElement = heroButton('Rechnung hochladen')
    const validationButton: HTMLElement = heroButton('Validierung')
    const createButton: HTMLElement = heroButton('E-Rechnung erstellen')
    const actions: HTMLElement | null = uploadButton.parentElement

    expect(createButton).toHaveClass('btn', 'btn--secondary')
    expect(createButton).toHaveAttribute('href', '/erstellen')
    expect(actions).toHaveClass('landing-hero__cta')
    expect(validationButton.parentElement).toBe(actions)
    expect(createButton.parentElement).toBe(actions)
  })

  it('shows the create button for a guest', (): void => {
    render(<LandingPage onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)

    const createLinks: HTMLElement[] = screen.getAllByRole('link', {
      name: 'E-Rechnung erstellen',
    })
    expect(createLinks.some((link: HTMLElement): boolean => link.classList.contains('btn'))).toBe(
      true,
    )
    const validationLinks: HTMLElement[] = screen.getAllByRole('link', { name: 'Validierung' })
    expect(validationLinks.length).toBeGreaterThan(0)
    for (const link of validationLinks) {
      expect(link).toHaveAttribute('href', '/erechnung-validation')
    }
  })
})

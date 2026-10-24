import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import { CONSENT_STORAGE_KEY, GA_MEASUREMENT_ID, resetAnalyticsState } from '../analytics'
import { ConsentBanner } from './ConsentBanner'
import { SiteFooter } from './SiteFooter'

describe('ConsentBanner', (): void => {
  afterEach((): void => {
    localStorage.removeItem(CONSENT_STORAGE_KEY)
    document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)?.remove()
    document.documentElement.classList.remove('has-consent-banner')
    resetAnalyticsState()
    window.history.replaceState(null, '', '/')
  })

  it('loads analytics only after Akzeptieren and hides the banner', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    window.history.replaceState(null, '', '/upload')
    render(<ConsentBanner />)

    expect(screen.getByRole('region', { name: 'Einwilligung für Google Analytics' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Akzeptieren' }))

    expect(screen.queryByRole('region', { name: 'Einwilligung für Google Analytics' })).not.toBeInTheDocument()
    expect(localStorage.getItem(CONSENT_STORAGE_KEY)).toBe('granted')
    expect(document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)).not.toBeNull()
  })

  it('remembers Ablehnen and opens again from the footer', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    render(
      <>
        <ConsentBanner />
        <SiteFooter />
      </>,
    )

    await user.click(screen.getByRole('button', { name: 'Ablehnen' }))
    expect(screen.queryByRole('region', { name: 'Einwilligung für Google Analytics' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Cookie-Einstellungen' }))
    expect(screen.getByRole('region', { name: 'Einwilligung für Google Analytics' })).toBeInTheDocument()
  })
})

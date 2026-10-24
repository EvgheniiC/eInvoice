import { afterEach, describe, expect, it } from 'vitest'
import {
  CONSENT_STORAGE_KEY,
  GA_MEASUREMENT_ID,
  isTrackableLocation,
  openAnalyticsConsentPrompt,
  readAnalyticsConsent,
  resetAnalyticsState,
  saveAnalyticsConsent,
  trackPublicPage,
} from './analytics'
import { DATENSCHUTZ } from './content/legal'

describe('analytics consent', (): void => {
  afterEach((): void => {
    localStorage.removeItem(CONSENT_STORAGE_KEY)
    document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)?.remove()
    document.documentElement.classList.remove('has-consent-banner')
    resetAnalyticsState()
  })

  it('tracks public pages and skips account pages and secrets in the query', (): void => {
    expect(isTrackableLocation('/upload', '')).toBe(true)
    expect(isTrackableLocation('/hilfe/datei', '')).toBe(true)
    expect(isTrackableLocation('/statistik', '')).toBe(false)
    expect(isTrackableLocation('/anmelden', '')).toBe(false)
    expect(isTrackableLocation('/passwort-zuruecksetzen', '?token=secret')).toBe(false)
    expect(isTrackableLocation('/tarife', '?checkout=success&session=cs_test_123')).toBe(false)
  })

  it('does not load the tag until the visitor accepts', (): void => {
    trackPublicPage('/upload', '')
    expect(document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)).toBeNull()

    saveAnalyticsConsent('granted', '/anmelden', '')
    expect(readAnalyticsConsent()).toBe('granted')
    expect(document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)).toBeNull()

    saveAnalyticsConsent('granted', '/hilfe', '')
    const script: Element | null = document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)
    expect(script?.getAttribute('src')).toContain(GA_MEASUREMENT_ID)
    const pageViews: unknown[] = (window.dataLayer ?? []).filter((entry: unknown): boolean => {
      if (entry === null || typeof entry !== 'object') {
        return false
      }
      const command: ArrayLike<unknown> = entry as ArrayLike<unknown>
      return command[0] === 'event' && command[1] === 'page_view'
    })
    expect(pageViews).toHaveLength(1)
    const pageView: ArrayLike<unknown> = pageViews[0] as ArrayLike<unknown>
    expect(Array.isArray(pageView)).toBe(false)
    expect(pageView[2]).toEqual({
      page_path: '/hilfe',
      page_location: `${window.location.origin}/hilfe`,
      page_title: document.title,
    })
  })

  it('stores a refusal and can ask again', (): void => {
    saveAnalyticsConsent('denied', '/', '')
    expect(readAnalyticsConsent()).toBe('denied')
    expect(document.querySelector(`script[data-ga="${GA_MEASUREMENT_ID}"]`)).toBeNull()
    openAnalyticsConsentPrompt()
    expect(localStorage.getItem(CONSENT_STORAGE_KEY)).toBe('denied')
  })
})

describe('datenschutz', (): void => {
  it('describes Google Analytics as consent-based', (): void => {
    const text: string = JSON.stringify(DATENSCHUTZ)
    expect(text).toContain('Google Analytics')
    expect(text).toContain('Google Ireland Limited')
    expect(text).toContain('Cookie-Einstellungen')
    expect(text).toContain('Art. 6 Abs. 1 lit. a DSGVO')
  })
})

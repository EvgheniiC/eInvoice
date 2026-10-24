import { useEffect, useState, type JSX } from 'react'
import {
  consentPromptRequested,
  readAnalyticsConsent,
  saveAnalyticsConsent,
  subscribeAnalyticsConsent,
  type AnalyticsConsent,
} from '../analytics'
import { AppLink } from '../navigation'

export function ConsentBanner(): JSX.Element | null {
  const [choice, setChoice] = useState<AnalyticsConsent | null>(() => readAnalyticsConsent())
  const [promptOpen, setPromptOpen] = useState<boolean>(() => consentPromptRequested())

  useEffect((): (() => void) => {
    return subscribeAnalyticsConsent((): void => {
      setChoice(readAnalyticsConsent())
      setPromptOpen(consentPromptRequested())
    })
  }, [])

  const visible: boolean = choice === null || promptOpen

  useEffect((): (() => void) => {
    if (!visible) {
      return (): void => undefined
    }
    document.documentElement.classList.add('has-consent-banner')
    return (): void => {
      document.documentElement.classList.remove('has-consent-banner')
    }
  }, [visible])

  if (!visible) {
    return null
  }

  function choose(next: AnalyticsConsent): void {
    saveAnalyticsConsent(next, window.location.pathname, window.location.search)
  }

  return (
    <div className="consent-banner" role="region" aria-label="Einwilligung für Google Analytics">
      <div className="consent-banner__text">
        <h2>Seitenaufrufe messen</h2>
        <p>
          Mit Ihrer Einwilligung erfasst Google Analytics, welche öffentlichen Seiten aufgerufen
          werden. Rechnungsinhalte und Kontoseiten werden nicht gesendet.{' '}
          <AppLink href="/datenschutz" className="consent-banner__link">
            Datenschutz
          </AppLink>
        </p>
      </div>
      <div className="consent-banner__actions">
        <button type="button" className="btn btn--secondary" onClick={() => choose('denied')}>
          Ablehnen
        </button>
        <button type="button" className="btn btn--primary" onClick={() => choose('granted')}>
          Akzeptieren
        </button>
      </div>
    </div>
  )
}

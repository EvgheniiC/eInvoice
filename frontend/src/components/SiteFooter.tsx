import type { JSX } from 'react'
import { openAnalyticsConsentPrompt } from '../analytics'
import { AppLink } from '../navigation'

type SiteFooterProps = {
  pageLinks?: boolean
}

export function SiteFooter({ pageLinks = true }: SiteFooterProps): JSX.Element {
  return (
    <footer className="site-footer">
      <nav className="site-footer__nav" aria-label="Fußzeile">
        {pageLinks ? (
          <>
            <AppLink href="/tarife" className="site-footer__link">
              Tarife
            </AppLink>
            <AppLink href="/hilfe" className="site-footer__link">
              Hilfe &amp; FAQ
            </AppLink>
            <AppLink href="/impressum" className="site-footer__link">
              Impressum
            </AppLink>
          </>
        ) : null}
        <AppLink href="/datenschutz" className="site-footer__link">
          Datenschutz
        </AppLink>
        <button type="button" className="site-footer__link" onClick={openAnalyticsConsentPrompt}>
          Cookie-Einstellungen
        </button>
      </nav>
      <p>
        eInvoice unterstützt bei der technischen und inhaltlichen Prüfung, ersetzt aber keine
        Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug. Die
        Entscheidung liegt bei Ihnen bzw. Ihrem Steuerberater.
      </p>
    </footer>
  )
}

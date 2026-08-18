import type { JSX } from 'react'
import type { AppRoute } from '../routing'

type SiteFooterProps = {
  onNavigate?: (route: AppRoute) => void
}

export function SiteFooter({ onNavigate }: SiteFooterProps): JSX.Element {
  return (
    <footer className="site-footer">
      {onNavigate ? (
        <nav className="site-footer__nav" aria-label="Fußzeile">
          <button type="button" className="site-footer__link" onClick={() => onNavigate('help')}>
            Hilfe &amp; FAQ
          </button>
          <button type="button" className="site-footer__link" onClick={() => onNavigate('legal')}>
            Impressum &amp; Datenschutz
          </button>
        </nav>
      ) : null}
      <p>
        eInvoice unterstützt bei der technischen und inhaltlichen Prüfung, ersetzt aber keine
        Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug. Die
        Entscheidung liegt bei Ihnen bzw. Ihrem Steuerberater.
      </p>
    </footer>
  )
}

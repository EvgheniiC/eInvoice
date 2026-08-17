import type { JSX } from 'react'
import type { AppRoute } from '../routing'

type SiteFooterProps = {
  onNavigate: (route: AppRoute) => void
  showDisclaimer?: boolean
}

export function SiteFooter({ onNavigate, showDisclaimer = true }: SiteFooterProps): JSX.Element {
  return (
    <footer className="site-footer">
      {showDisclaimer ? (
        <p>
          eInvoice unterstützt bei der technischen und inhaltlichen Prüfung, ersetzt aber
          keine Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug.
          Die Entscheidung liegt bei Ihnen bzw. Ihrem Steuerberater.
        </p>
      ) : null}
      <nav className="site-footer__nav" aria-label="Rechtliches">
        <button type="button" className="site-footer__link" onClick={() => onNavigate('impressum')}>
          Impressum
        </button>
        <button
          type="button"
          className="site-footer__link"
          onClick={() => onNavigate('datenschutz')}
        >
          Datenschutzerklärung
        </button>
      </nav>
    </footer>
  )
}

import type { JSX } from 'react'

export function SiteFooter(): JSX.Element {
  return (
    <footer className="site-footer">
      <p>
        eInvoice unterstützt bei der technischen und inhaltlichen Prüfung, ersetzt aber keine
        Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug. Die
        Entscheidung liegt bei Ihnen bzw. Ihrem Steuerberater.
      </p>
    </footer>
  )
}

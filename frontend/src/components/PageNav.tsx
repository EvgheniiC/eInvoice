import type { JSX } from 'react'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type { MeResponse } from '../types/invoice'

type PageNavProps = {
  onNavigate: (route: AppRoute) => void
  overlay?: boolean
  session?: MeResponse | null
  onLogout?: () => void
}

export function PageNav({
  onNavigate,
  overlay = false,
  session = null,
  onLogout,
}: PageNavProps): JSX.Element {
  const className: string = overlay ? 'page-nav page-nav--overlay' : 'page-nav'
  if (session) {
    return (
      <nav className={className} aria-label="Seiten">
        <button type="button" className="page-nav__link" onClick={() => onNavigate('account')}>
          Konto
        </button>
        <AppLink href="/hilfe" className="page-nav__link">
          Hilfe
        </AppLink>
        {session.is_admin ? (
          <button type="button" className="page-nav__link" onClick={() => onNavigate('stats')}>
            Statistik
          </button>
        ) : null}
        {onLogout ? (
          <button type="button" className="page-nav__link" onClick={onLogout}>
            Abmelden
          </button>
        ) : null}
      </nav>
    )
  }

  return (
    <nav className={className} aria-label="Seiten">
      <AppLink href="/erstellen" className="page-nav__link">
        E-Rechnung erstellen
      </AppLink>
      <AppLink href="/tarife" className="page-nav__link">
        Tarife
      </AppLink>
      <AppLink href="/hilfe" className="page-nav__link">
        Hilfe
      </AppLink>
      <AppLink href="/impressum" className="page-nav__link">
        Impressum
      </AppLink>
      <button type="button" className="page-nav__link" onClick={() => onNavigate('login')}>
        Anmelden
      </button>
      <AppLink href="/erechnung-validation" className="page-nav__link">
        Validierung
      </AppLink>
      <AppLink href="/upload" className="page-nav__link">
        Rechnung hochladen
      </AppLink>
    </nav>
  )
}

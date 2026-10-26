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
  return (
    <nav className={className} aria-label="Seiten">
      <AppLink href="/tarife" className="page-nav__link">
        Tarife
      </AppLink>
      <AppLink href="/hilfe" className="page-nav__link">
        Hilfe
      </AppLink>
      <AppLink href="/impressum" className="page-nav__link">
        Impressum
      </AppLink>
      {session ? (
        <>
          {session.is_admin ? (
            <button type="button" className="page-nav__link" onClick={() => onNavigate('stats')}>
              Statistik
            </button>
          ) : null}
          {session.plan.allows_history ? (
            <button type="button" className="page-nav__link" onClick={() => onNavigate('history')}>
              Verlauf
            </button>
          ) : null}
          <button type="button" className="page-nav__link" onClick={() => onNavigate('org')}>
            Organisation
          </button>
          {onLogout ? (
            <button type="button" className="page-nav__link" onClick={onLogout}>
              Abmelden
            </button>
          ) : null}
        </>
      ) : (
        <button type="button" className="page-nav__link" onClick={() => onNavigate('login')}>
          Anmelden
        </button>
      )}
      <AppLink href="/upload" className="page-nav__link">
        Rechnung hochladen
      </AppLink>
      <AppLink href="/erstellen" className="page-nav__link">
        E-Rechnung erstellen
      </AppLink>
    </nav>
  )
}

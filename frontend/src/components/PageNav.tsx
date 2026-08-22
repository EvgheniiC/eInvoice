import type { JSX } from 'react'
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
      <button type="button" className="page-nav__link" onClick={() => onNavigate('help')}>
        Hilfe
      </button>
      <button
        type="button"
        className="page-nav__link"
        onClick={() => onNavigate('legal')}
        aria-label="Impressum und Datenschutz"
      >
        Impressum
      </button>
      {session ? (
        <>
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
    </nav>
  )
}

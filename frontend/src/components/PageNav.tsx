import type { JSX } from 'react'
import type { AppRoute } from '../routing'

type PageNavProps = {
  onNavigate: (route: AppRoute) => void
  overlay?: boolean
}

export function PageNav({ onNavigate, overlay = false }: PageNavProps): JSX.Element {
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
    </nav>
  )
}

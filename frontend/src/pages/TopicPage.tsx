import type { JSX } from 'react'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { publicPageByPath, type PublicPage, type PublicPageLink } from '../content/publicPages'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type { MeResponse } from '../types/invoice'

type TopicPageProps = {
  pathname: string
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function TopicPage({
  pathname,
  onNavigate,
  session,
  onLogout,
}: TopicPageProps): JSX.Element {
  const page: PublicPage | null = publicPageByPath(pathname)
  if (page === null || page.kind !== 'topic') {
    return (
      <main id="main-content" className="page" tabIndex={-1}>
        <h1 tabIndex={-1}>Seite nicht gefunden</h1>
        <AppLink href="/">Zur Startseite</AppLink>
      </main>
    )
  }

  return (
    <main id="main-content" className="page page--legal" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <AppLink href="/" className="page__home">
            ← eInvoice
          </AppLink>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>{page.h1}</h1>
      </header>
      {page.paragraphs.map((paragraph: string, index: number) => (
        <p key={`${page.path}-p-${index}`}>{paragraph}</p>
      ))}
      <p>
        <AppLink href="/upload" className="btn btn--primary">
          Rechnung hochladen
        </AppLink>
      </p>
      {page.links && page.links.length > 0 ? (
        <ul>
          {page.links.map((link: PublicPageLink) => (
            <li key={link.href}>
              <AppLink href={link.href}>{link.label}</AppLink>
            </li>
          ))}
        </ul>
      ) : null}
      <SiteFooter />
    </main>
  )
}

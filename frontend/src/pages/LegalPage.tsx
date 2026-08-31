import { useEffect, type JSX } from 'react'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { LegalDocument, LegalSection } from '../content/legal'
import type { AppRoute } from '../routing'
import type { MeResponse } from '../types/invoice'

type LegalPageProps = {
  documents: LegalDocument[]
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function LegalPage({
  documents,
  onNavigate,
  session,
  onLogout,
}: LegalPageProps): JSX.Element {
  useEffect(() => {
    const hash: string = window.location.hash.replace('#', '')
    const fromPath: string = window.location.pathname.includes('datenschutz')
      ? 'datenschutz'
      : ''
    const targetId: string = hash || fromPath
    if (!targetId) {
      return
    }
    document.getElementById(targetId)?.scrollIntoView({ block: 'start' })
  }, [])

  return (
    <main id="main-content" className="page page--legal" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Impressum &amp; Datenschutz</h1>
        <p className="page__lead">
          Angaben zum Diensteanbieter und zur Verarbeitung hochgeladener Rechnungsdateien.
        </p>
        <nav className="legal-toc" aria-label="Abschnitte">
          {documents.map((document: LegalDocument) => (
            <a key={document.id} href={`#${document.id}`}>
              {document.title}
            </a>
          ))}
        </nav>
      </header>

      {documents.map((document: LegalDocument) => (
        <article key={document.id} id={document.id} className="legal-document">
          <h2 className="legal-document__title">{document.title}</h2>
          <p className="page__lead">{document.intro}</p>
          <p className="page__limits">{document.updatedLabel}</p>
          {document.sections.map((section: LegalSection) => (
            <section key={`${document.id}-${section.heading}`} className="legal-section">
              <h3>{section.heading}</h3>
              {section.paragraphs.map((paragraph: string, index: number) => (
                <p key={`${section.heading}-p-${index}`}>{paragraph}</p>
              ))}
              {section.listItems ? (
                <ul>
                  {section.listItems.map((item: string, index: number) => (
                    <li key={`${section.heading}-li-${index}`}>{item}</li>
                  ))}
                </ul>
              ) : null}
            </section>
          ))}
        </article>
      ))}

      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}

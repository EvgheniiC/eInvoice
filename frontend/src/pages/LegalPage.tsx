import type { JSX } from 'react'
import { SiteFooter } from '../components/SiteFooter'
import type { LegalDocument, LegalSection } from '../content/legal'
import type { AppRoute } from '../routing'

type LegalPageProps = {
  document: LegalDocument
  onNavigate: (route: AppRoute) => void
}

export function LegalPage({ document, onNavigate }: LegalPageProps): JSX.Element {
  return (
    <main className="page page--legal">
      <header className="page__header">
        <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
          ← eInvoice
        </button>
        <h1>{document.title}</h1>
        <p className="page__lead">{document.intro}</p>
        <p className="page__limits">{document.updatedLabel}</p>
      </header>

      {document.sections.map((section: LegalSection) => (
        <section key={section.heading} className="legal-section">
          <h2>{section.heading}</h2>
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

      <SiteFooter onNavigate={onNavigate} showDisclaimer={false} />
    </main>
  )
}

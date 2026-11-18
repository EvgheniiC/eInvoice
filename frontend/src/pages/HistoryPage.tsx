import type { JSX } from 'react'
import { HistoryPanel } from '../components/HistoryPanel'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { MeResponse } from '../types/invoice'

type HistoryPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function HistoryPage({ onNavigate, session, onLogout }: HistoryPageProps): JSX.Element {
  return (
    <main id="main-content" className="page" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            Startseite
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Verlauf</h1>
        <p className="page__lead">
          Nach Zustimmung speichert Plus nur Metadaten: Datum, Lieferant, Nummer, Betrag, Status
          und Datei-Hash. Die Originaldatei nur mit „Dateien merken“.
        </p>
      </header>
      <HistoryPanel onNavigate={onNavigate} session={session} />
      <SiteFooter />
    </main>
  )
}

import { useEffect, useState, type JSX } from 'react'
import { fetchAdminStats } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type { ActionDayStat, AdminStatsResponse, MeResponse } from '../types/invoice'

type AdminStatsPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  sessionReady: boolean
  onLogout: () => void
}

function packageTotal(days: ActionDayStat[]): number {
  return days.reduce((sum: number, day: ActionDayStat) => sum + day.accountant_package, 0)
}

function formatCount(value: number): string {
  return new Intl.NumberFormat('de-DE').format(value)
}

function formatVisitDate(value: string): string {
  const parsed: Date = new Date(`${value}T00:00:00`)
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(parsed)
}

export function AdminStatsPage({
  onNavigate,
  session,
  sessionReady,
  onLogout,
}: AdminStatsPageProps): JSX.Element {
  const [stats, setStats] = useState<AdminStatsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionReady || !session?.is_admin) {
      setStats(null)
      setError(null)
      return
    }
    let cancelled: boolean = false
    setError(null)
    void fetchAdminStats()
      .then((value: AdminStatsResponse) => {
        if (!cancelled) {
          setStats(value)
        }
      })
      .catch((err: unknown) => {
        if (cancelled) {
          return
        }
        const text: string = err instanceof Error ? err.message : 'Statistik ist nicht verfügbar.'
        setError(text)
        setStats(null)
      })
    return () => {
      cancelled = true
    }
  }, [session, sessionReady])

  return (
    <main id="main-content" className="page page--legal" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Statistik</h1>
        <p className="page__lead">
          Besuche zählen jeden Browser einmal pro Tag, einschließlich Gäste ohne Konto. Gelesen und
          Steuerberater-Paket zählt der Server nur nach einer echten Prüfung oder einem echten ZIP.
          Seitenaufrufe kann derselbe Browser mehrfach auslösen. Ältere Tage bleiben bei 0, bis diese
          Zählung läuft.
        </p>
      </header>

      {!sessionReady ? (
        <p className="status status--info" role="status">
          Wird geladen…
        </p>
      ) : !session ? (
        <>
          <p className="status status--info" role="status">
            Bitte anmelden.
          </p>
          <button type="button" className="btn btn--primary" onClick={() => onNavigate('login')}>
            Anmelden
          </button>
        </>
      ) : !session.is_admin ? (
        <p className="status status--error" role="alert">
          Kein Zugriff.
        </p>
      ) : error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : !stats ? (
        <p className="status status--info" role="status">
          Wird geladen…
        </p>
      ) : (
        <>
          <dl className="stats-summary">
            <div className="stats-card">
              <dt>Besuche heute</dt>
              <dd>{formatCount(stats.visits_today)}</dd>
            </div>
            <div className="stats-card">
              <dt>Rechnungen gelesen heute</dt>
              <dd>{formatCount(stats.parses_today)}</dd>
            </div>
            <div className="stats-card">
              <dt>Steuerberater-Pakete heute</dt>
              <dd>{formatCount(stats.packages_today)}</dd>
            </div>
            <div className="stats-card">
              <dt>Steuerberater-Pakete, 14 Tage</dt>
              <dd>{formatCount(packageTotal(stats.actions_by_day))}</dd>
            </div>
            <div className="stats-card">
              <dt>Personen mit Plus oder Team</dt>
              <dd>{formatCount(stats.paid_plan_users)}</dd>
            </div>
          </dl>
          <h2>Aktionen pro Tag</h2>
          <div className="stats-table-wrap">
            <table className="stats-table">
              <thead>
                <tr>
                  <th scope="col">Datum</th>
                  <th className="num" scope="col">Besuche</th>
                  <th className="num" scope="col">Startseite</th>
                  <th className="num" scope="col">Empfang</th>
                  <th className="num" scope="col">Gelesen</th>
                  <th className="num" scope="col">Paket</th>
                  <th className="num" scope="col">Downloads</th>
                </tr>
              </thead>
              <tbody>
                {stats.actions_by_day.map((day: ActionDayStat) => (
                  <tr key={day.event_date}>
                    <td>{formatVisitDate(day.event_date)}</td>
                    <td className="num">{formatCount(day.visitors)}</td>
                    <td className="num">{formatCount(day.landing)}</td>
                    <td className="num">{formatCount(day.upload)}</td>
                    <td className="num">{formatCount(day.parse_success)}</td>
                    <td className="num">{formatCount(day.accountant_package)}</td>
                    <td className="num">{formatCount(day.export)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      <SiteFooter />
    </main>
  )
}

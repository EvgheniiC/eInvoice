import { useEffect, useState, type JSX } from 'react'
import { downloadHistoryAccountantPackage, fetchInvoiceHistory } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import type { AppRoute } from '../routing'
import type {
  DecimalValue,
  HistoryItemResponse,
  HistoryItemStatus,
  HistoryListResponse,
  MeResponse,
} from '../types/invoice'

type HistoryPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

const STATUS_LABEL: Record<HistoryItemStatus, string> = {
  gueltig: 'gültig',
  pruefen: 'prüfen',
  ablehnen: 'ablehnen',
}

export function HistoryPage({
  onNavigate,
  session,
  onLogout,
}: HistoryPageProps): JSX.Element {
  const [data, setData] = useState<HistoryListResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [downloadingId, setDownloadingId] = useState<string | null>(null)

  const canUseHistory: boolean = session?.plan.allows_history === true

  useEffect(() => {
    if (session === null || !canUseHistory) {
      return
    }
    let cancelled: boolean = false
    setLoading(true)
    setError(null)
    void fetchInvoiceHistory()
      .then((value: HistoryListResponse) => {
        if (!cancelled) {
          setData(value)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Verlauf nicht verfügbar.')
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [session, canUseHistory])

  async function onDownload(recordId: string): Promise<void> {
    setDownloadingId(recordId)
    setError(null)
    try {
      await downloadHistoryAccountantPackage(recordId)
      const refreshed: HistoryListResponse = await fetchInvoiceHistory()
      setData(refreshed)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Paket-Download fehlgeschlagen.')
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <main id="main-content" className="page" tabIndex={-1}>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={() => onNavigate('landing')}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Verlauf</h1>
        <p className="page__lead">
          Nach Zustimmung speichert Plus nur Metadaten: Datum, Lieferant, Nummer, Betrag, Status
          und Datei-Hash. Die Originaldatei nur mit „Dateien merken“.
        </p>
      </header>

      {session === null ? (
        <>
          <p>Bitte zuerst anmelden.</p>
          <button type="button" className="btn btn--primary" onClick={() => onNavigate('login')}>
            Anmelden
          </button>
        </>
      ) : !canUseHistory ? (
        <section className="legal-section">
          <p>Verlauf ist in Plus enthalten. Im Gast- und Free-Tarif wird nichts gespeichert.</p>
        </section>
      ) : loading ? (
        <p className="status status--info" role="status">
          Verlauf wird geladen…
        </p>
      ) : data !== null && !data.history_enabled ? (
        <section className="legal-section">
          <p>Der Verlauf ist ausgeschaltet. Ohne Zustimmung wird nichts gespeichert.</p>
          <button type="button" className="btn btn--primary" onClick={() => onNavigate('org')}>
            Verlauf unter Organisation aktivieren
          </button>
        </section>
      ) : data !== null && data.items.length === 0 ? (
        <section className="legal-section">
          <p>Noch keine Einträge. Geprüfte Rechnungen erscheinen hier nach der nächsten Prüfung.</p>
        </section>
      ) : data !== null ? (
        <section className="legal-section">
          <p className="page__limits">
            {data.store_originals_enabled
              ? `Originaldateien werden ${String(data.original_retention_days)} Tage aufbewahrt.`
              : 'Originaldateien werden nicht gespeichert.'}
          </p>
          <div className="table-scroll">
            <table className="batch-table history-table">
              <thead>
                <tr>
                  <th scope="col">Datum</th>
                  <th scope="col">Lieferant</th>
                  <th scope="col">Nummer</th>
                  <th scope="col">Betrag</th>
                  <th scope="col">Status</th>
                  <th scope="col">Paket</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item: HistoryItemResponse) => (
                  <tr key={item.id}>
                    <td>{formatProcessedAt(item.processed_at)}</td>
                    <td>{item.seller_name ?? '—'}</td>
                    <td>{item.invoice_number ?? '—'}</td>
                    <td>{formatAmount(item.gross_amount, item.currency)}</td>
                    <td>
                      <span className={statusBadgeClass(item.status)}>{STATUS_LABEL[item.status]}</span>
                    </td>
                    <td>
                      {item.original_available ? (
                        <button
                          type="button"
                          className="btn btn--secondary"
                          disabled={downloadingId === item.id}
                          onClick={() => {
                            void onDownload(item.id)
                          }}
                        >
                          {downloadingId === item.id ? 'Lädt…' : 'Paket'}
                        </button>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : null}
      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}

function statusBadgeClass(status: HistoryItemStatus): string {
  if (status === 'gueltig') {
    return 'badge badge--ok'
  }
  if (status === 'pruefen') {
    return 'badge badge--warn'
  }
  return 'badge badge--error'
}

function formatProcessedAt(value: string): string {
  const parsed: Date = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return parsed.toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })
}

function formatAmount(value: DecimalValue | null | undefined, currency: string | null): string {
  if (value === null || value === undefined) {
    return '—'
  }
  const numericValue: number = Number(value)
  if (!Number.isFinite(numericValue)) {
    return '—'
  }
  const formatted: string = numericValue.toLocaleString('de-DE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return currency ? `${formatted} ${currency}` : formatted
}

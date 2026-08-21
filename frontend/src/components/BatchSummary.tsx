import type { JSX } from 'react'
import type { BatchItemResponse, BatchItemStatus, BatchJobResponse, DecimalValue } from '../types/invoice'

type BatchSummaryProps = {
  job: BatchJobResponse
  selectedItemId: string | null
  onSelectItem: (item: BatchItemResponse) => void
}

const STATUS_LABEL: Record<BatchItemStatus, string> = {
  queued: 'wartend',
  processing: 'wird geprüft',
  gueltig: 'gültig',
  pruefen: 'prüfen',
  ablehnen: 'ablehnen',
}

export function BatchSummary({ job, selectedItemId, onSelectItem }: BatchSummaryProps): JSX.Element {
  const percent: number = job.item_count === 0 ? 0 : Math.round((job.done_count / job.item_count) * 100)

  return (
    <section className="batch-summary" aria-live="polite">
      <div className="progress" role="status">
        <div className="progress__track" aria-hidden="true">
          <div className="progress__bar" style={{ width: `${String(percent)}%`, animation: 'none' }} />
        </div>
        <p className="progress__label">
          {job.status === 'completed'
            ? `${String(job.item_count)} Dateien geprüft.`
            : `${String(job.done_count)} von ${String(job.item_count)} Dateien geprüft…`}
        </p>
      </div>
      <div className="table-scroll">
        <table className="batch-table">
          <thead>
            <tr>
              <th scope="col">Datei</th>
              <th scope="col">Status</th>
              <th scope="col">Betrag</th>
              <th scope="col">Lieferant</th>
            </tr>
          </thead>
          <tbody>
            {job.items.map((item: BatchItemResponse) => {
              const clickable: boolean = item.invoice !== null && item.invoice !== undefined
              const selected: boolean = item.id === selectedItemId
              const className: string = [
                clickable ? 'batch-table__row--clickable' : '',
                selected ? 'batch-table__row--selected' : '',
              ]
                .filter((value: string): boolean => value.length > 0)
                .join(' ')
              return (
                <tr
                  key={item.id}
                  className={className || undefined}
                  onClick={() => {
                    if (clickable) {
                      onSelectItem(item)
                    }
                  }}
                >
                  <td>{item.filename}</td>
                  <td>
                    <span className={statusBadgeClass(item.status)}>{STATUS_LABEL[item.status]}</span>
                  </td>
                  <td>{formatAmount(item.gross_amount, item.currency)}</td>
                  <td>{item.seller_name ?? '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="batch-summary__hint">
        Klick auf eine geprüfte Zeile zeigt die Rechnung rechts. Originaldateien werden nach der
        Prüfung gelöscht.
      </p>
      <button type="button" className="batch-summary__zip" disabled>
        Ein ZIP für die Buchhaltung (folgt)
      </button>
    </section>
  )
}

function statusBadgeClass(status: BatchItemStatus): string {
  if (status === 'gueltig') {
    return 'badge badge--ok'
  }
  if (status === 'pruefen' || status === 'processing') {
    return 'badge badge--warn'
  }
  if (status === 'ablehnen') {
    return 'badge badge--error'
  }
  return 'badge'
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

import { useState } from 'react'
import { downloadAccountantPackage, exportInvoice } from '../api/client'
import type {
  DecimalValue,
  ExportFormat,
  InvoiceParseResponse,
  LineItem,
  MismatchField,
  PartyInfo,
  TaxBreakdown,
  ValidationIssue,
  ValidationStatus,
} from '../types/invoice'

type ExportAction = ExportFormat | 'package'
type UserOutcome = 'process' | 'review' | 'request_correction'

interface InvoiceViewProps {
  invoice: InvoiceParseResponse
  sourceFile?: File | null
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

function validationBadgeClass(status: ValidationStatus): string {
  if (status === 'valid') {
    return 'badge badge--ok'
  }
  if (status === 'warning') {
    return 'badge badge--warn'
  }
  if (status === 'invalid') {
    return 'badge badge--error'
  }
  return 'badge'
}

function validationLabel(status: ValidationStatus): string {
  switch (status) {
    case 'valid':
      return 'Prüfung: gültig'
    case 'warning':
      return 'Prüfung: Warnung'
    case 'invalid':
      return 'Prüfung: ungültig'
    default:
      return 'Prüfung: nicht geprüft'
  }
}

function userOutcome(invoice: InvoiceParseResponse): UserOutcome {
  const hasValidationError: boolean = invoice.validation_issues.some(
    (issue: ValidationIssue): boolean => issue.level === 'error',
  )
  const hasMismatch: boolean = invoice.mismatch_fields.some(
    (item: MismatchField): boolean => Boolean(item.xml_value) && !item.matched,
  )

  if (invoice.validation_status === 'invalid' || hasValidationError || hasMismatch) {
    return 'request_correction'
  }
  if (
    invoice.status === 'partial' ||
    invoice.validation_status === 'warning' ||
    invoice.validation_status === 'not_checked'
  ) {
    return 'review'
  }
  return 'process'
}

function outcomeLabel(outcome: UserOutcome): string {
  switch (outcome) {
    case 'process':
      return 'Kann verarbeitet werden'
    case 'review':
      return 'Bitte prüfen'
    case 'request_correction':
      return 'Korrektur anfordern'
  }
}

function outcomeDescription(outcome: UserOutcome): string {
  switch (outcome) {
    case 'process':
      return 'Die Rechnung wurde gelesen und ohne erkennbare Fehler geprüft.'
    case 'review':
      return 'Vor der Buchung bitte die Hinweise und fehlenden Angaben kontrollieren.'
    case 'request_correction':
      return 'Nicht zahlen oder buchen, bevor die Fehler beziehungsweise Abweichungen geklärt sind.'
  }
}

function PartyBlock({ title, party }: { title: string; party: PartyInfo | null }) {
  if (!party || (!party.name && !party.address && !party.vat_id && !party.iban)) {
    return null
  }
  return (
    <div className="party">
      <h3>{title}</h3>
      {party.name && <p className="party__name">{party.name}</p>}
      {party.address && <p>{party.address}</p>}
      {party.vat_id && <p>USt-IdNr.: {party.vat_id}</p>}
      {party.iban && <p>IBAN: {party.iban}</p>}
    </div>
  )
}

export function InvoiceView({ invoice, sourceFile = null }: InvoiceViewProps) {
  const currency: string | null = invoice.totals?.currency ?? null
  const [exportError, setExportError] = useState<string | null>(null)
  const [exporting, setExporting] = useState<ExportAction | null>(null)
  const outcome: UserOutcome = userOutcome(invoice)

  const outcomeClass: string = `outcome outcome--${outcome}`

  const hasMismatch: boolean = invoice.mismatch_fields.some(
    (item: MismatchField) => Boolean(item.xml_value) && !item.matched,
  )
  const allMatched: boolean =
    invoice.file_type === 'zugferd_pdf' &&
    invoice.mismatch_fields.length > 0 &&
    !hasMismatch

  async function handleExport(format: ExportFormat): Promise<void> {
    setExportError(null)
    setExporting(format)
    try {
      await exportInvoice(invoice, format)
    } catch (err: unknown) {
      const message: string = err instanceof Error ? err.message : 'Export fehlgeschlagen.'
      setExportError(message)
    } finally {
      setExporting(null)
    }
  }

  async function handleAccountantPackage(): Promise<void> {
    setExportError(null)
    setExporting('package')
    try {
      await downloadAccountantPackage(invoice, sourceFile)
    } catch (err: unknown) {
      const message: string =
        err instanceof Error ? err.message : 'Paket-Download fehlgeschlagen.'
      setExportError(message)
    } finally {
      setExporting(null)
    }
  }

  return (
    <section className="invoice" aria-live="polite">
      <div className="invoice__meta">
        <div>
          <p className="invoice__label">
            {invoice.document_type === 'credit_note' ? 'Gutschrift' : 'Rechnung'}
          </p>
          <h2>{invoice.invoice_number ?? 'Ohne Nummer'}</h2>
        </div>
        <div className="invoice__badges">
          <span className={validationBadgeClass(invoice.validation_status)}>
            {validationLabel(invoice.validation_status)}
          </span>
        </div>
      </div>

      <p className="invoice__message">{invoice.message}</p>

      <div className={outcomeClass} role="status">
        <p className="outcome__label">Ergebnis</p>
        <strong>{outcomeLabel(outcome)}</strong>
        <p>{outcomeDescription(outcome)}</p>
      </div>

      <div className="export-bar">
        <p className="export-bar__label">Für Buchhaltung exportieren</p>
        <div className="export-bar__actions">
          <button
            type="button"
            className="export-bar__primary"
            disabled={exporting !== null}
            onClick={() => void handleAccountantPackage()}
          >
            {exporting === 'package' ? 'Paket…' : 'Paket für Steuerberater'}
          </button>
          <button type="button" disabled={exporting !== null} onClick={() => handleExport('csv')}>
            {exporting === 'csv' ? 'CSV…' : 'CSV'}
          </button>
          <button type="button" disabled={exporting !== null} onClick={() => handleExport('excel')}>
            {exporting === 'excel' ? 'Excel…' : 'Excel'}
          </button>
          <button type="button" disabled={exporting !== null} onClick={() => handleExport('datev')}>
            {exporting === 'datev' ? 'DATEV…' : 'DATEV'}
          </button>
        </div>
        <p className="export-bar__hint">
          Paket = Kurzfassung + Excel + DATEV
          {invoice.file_type === 'zugferd_pdf' ? ' + visuelle PDF' : ''}.
        </p>
        {exportError && <p className="status status--error">{exportError}</p>}
      </div>

      {hasMismatch && (
        <div className="banner banner--mismatch" role="alert">
          <strong>PDF und XML weichen ab</strong>
          <p>Bitte Lieferanten kontaktieren, bevor Sie die Rechnung zahlen oder buchen.</p>
        </div>
      )}
      {allMatched && (
        <div className="banner banner--match" role="status">
          <strong>PDF und XML stimmen überein</strong>
          <p>Geprüfte Felder: Nummer, Datum, Brutto, MwSt, IBAN.</p>
        </div>
      )}

      <dl className="invoice__facts">
        <div>
          <dt>Datei</dt>
          <dd>{invoice.filename}</dd>
        </div>
        <div>
          <dt>Typ</dt>
          <dd>
            {invoice.document_type === 'credit_note' ? 'Gutschrift · ' : ''}
            {invoice.file_type ?? '—'}
          </dd>
        </div>
        <div>
          <dt>Datum</dt>
          <dd className={fieldClass(invoice, 'issue_date')}>{invoice.issue_date ?? '—'}</dd>
        </div>
        <div>
          <dt>Fälligkeitsdatum</dt>
          <dd>{invoice.due_date ?? '—'}</dd>
        </div>
        {invoice.payment_reference && (
          <div>
            <dt>Zahlungsreferenz</dt>
            <dd>{invoice.payment_reference}</dd>
          </div>
        )}
      </dl>

      <div className="invoice__parties">
        <PartyBlock title="Lieferant" party={invoice.seller} />
        <PartyBlock title="Empfänger" party={invoice.buyer} />
      </div>

      {invoice.totals && (
        <div className="invoice__totals">
          <div>
            <span>Netto</span>
            <strong>{formatAmount(invoice.totals.net, currency)}</strong>
          </div>
          <div className={fieldClass(invoice, 'tax')}>
            <span>MwSt</span>
            <strong>{formatAmount(invoice.totals.tax, currency)}</strong>
          </div>
          <div className={fieldClass(invoice, 'gross')}>
            <span>Brutto</span>
            <strong>{formatAmount(invoice.totals.gross, currency)}</strong>
          </div>
          {invoice.totals.allowance !== null && (
            <div>
              <span>Nachlässe</span>
              <strong>{formatAmount(invoice.totals.allowance, currency)}</strong>
            </div>
          )}
          {invoice.totals.charge !== null && (
            <div>
              <span>Zuschläge</span>
              <strong>{formatAmount(invoice.totals.charge, currency)}</strong>
            </div>
          )}
        </div>
      )}

      {invoice.totals && invoice.totals.tax_breakdown.length > 0 && (
        <div className="invoice__tax-breakdown">
          <h3>MwSt-Aufschlüsselung</h3>
          <ul>
            {invoice.totals.tax_breakdown.map((tax: TaxBreakdown, index: number) => (
              <li key={`${String(tax.rate)}-${index}`}>
                {String(tax.rate)} %: {formatAmount(tax.amount, currency)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {invoice.mismatch_fields.length > 0 && (
        <div className="mismatch-table-wrap">
          <h3>PDF ↔ XML Abgleich</h3>
          <table className="mismatch-table">
            <thead>
              <tr>
                <th>Feld</th>
                <th>XML</th>
                <th>PDF</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {invoice.mismatch_fields.map((item: MismatchField) => (
                <tr key={item.field} className={item.matched ? undefined : 'row--mismatch'}>
                  <td>{item.label}</td>
                  <td>{item.xml_value ?? '—'}</td>
                  <td>{item.pdf_value ?? '—'}</td>
                  <td>{item.matched ? 'OK' : 'Abweichung'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {invoice.line_items.length > 0 && (
        <div className="invoice__lines-wrap">
          <h3>Positionen</h3>
          <table className="invoice__lines">
            <thead>
              <tr>
                <th>#</th>
                <th>Beschreibung</th>
                <th>Menge</th>
                <th>Preis</th>
                <th>MwSt %</th>
                <th>Netto</th>
                <th>Brutto</th>
              </tr>
            </thead>
            <tbody>
              {invoice.line_items.map((item: LineItem, index: number) => (
                <tr key={`${item.position ?? index}-${index}`}>
                  <td>{item.position ?? index + 1}</td>
                  <td className="invoice__desc">{item.description ?? '—'}</td>
                  <td>
                    {item.quantity ?? '—'}
                    {item.unit ? ` ${item.unit}` : ''}
                  </td>
                  <td>{formatAmount(item.unit_price, currency)}</td>
                  <td>{item.tax_rate !== null ? `${String(item.tax_rate)} %` : '—'}</td>
                  <td>{formatAmount(item.net_amount, currency)}</td>
                  <td>{formatAmount(item.gross_amount, currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {invoice.validation_issues.length > 0 && (
        <div className="invoice__issues-wrap">
          <h3>Prüfungshinweise</h3>
          <ul className="invoice__issues">
            {invoice.validation_issues.map((issue: ValidationIssue, index: number) => (
              <li
                key={`${issue.code ?? 'issue'}-${index}`}
                className={`issue issue--${issue.level}`}
              >
                <span className="issue__cat">[{issue.category}]</span> {issue.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {invoice.next_steps.length > 0 && (
        <div className="next-steps">
          <h3>Was tun als Nächstes?</h3>
          <ol>
            {invoice.next_steps.map((step: string, index: number) => (
              <li key={`step-${index}`}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}

function fieldClass(invoice: InvoiceParseResponse, fieldName: string): string {
  const mismatch: MismatchField | undefined = invoice.mismatch_fields.find(
    (item: MismatchField) => item.field === fieldName && !item.matched && Boolean(item.xml_value),
  )
  return mismatch ? 'field--mismatch' : ''
}

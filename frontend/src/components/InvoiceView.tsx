import { useEffect, useRef, useState, type ChangeEvent, type JSX, type RefObject } from 'react'
import {
  downloadAccountantPackage,
  downloadValidationReport,
  downloadViewPdf,
  exportInvoice,
} from '../api/client'
import type {
  DecimalValue,
  ExportFormat,
  InvoiceParseResponse,
  LineItem,
  MismatchField,
  PartyInfo,
  TaxBreakdown,
  ValidationIssue,
  ValidationMeta,
  ValidationStatus,
} from '../types/invoice'

type ExportAction = ExportFormat | 'package' | 'report' | 'view-pdf'
type UserOutcome = 'process' | 'review' | 'request_correction'
type FieldState = 'ok' | 'missing' | 'error' | 'mismatch'

interface InvoiceViewProps {
  invoice: InvoiceParseResponse
  sourceFile?: File | null
  onUpgrade?: () => void
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

function formatDateDe(value: string | null | undefined): string {
  if (!value) {
    return '—'
  }
  if (value.length >= 10 && value[4] === '-' && value[7] === '-') {
    return `${value.slice(8, 10)}.${value.slice(5, 7)}.${value.slice(0, 4)}`
  }
  return value
}

function formatIban(value: string | null | undefined): string {
  if (!value) {
    return '—'
  }
  const compact: string = value.replace(/\s+/g, '')
  return compact.replace(/(.{4})/g, '$1 ').trim()
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

function hasPdfXmlMismatch(invoice: InvoiceParseResponse): boolean {
  return invoice.mismatch_fields.some(
    (item: MismatchField): boolean => Boolean(item.xml_value) && !item.matched,
  )
}

function isRiskyExport(invoice: InvoiceParseResponse): boolean {
  if (invoice.validation_status === 'invalid') {
    return true
  }
  if (hasPdfXmlMismatch(invoice)) {
    return true
  }
  return invoice.validation_issues.some(
    (issue: ValidationIssue): boolean => issue.level === 'error',
  )
}

function userOutcome(invoice: InvoiceParseResponse): UserOutcome {
  if (isRiskyExport(invoice)) {
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

interface IssueGroup {
  id: string
  title: string
  issues: ValidationIssue[]
}

function groupedIssues(issues: ValidationIssue[]): IssueGroup[] {
  const visible: ValidationIssue[] = issues.filter(
    (issue: ValidationIssue): boolean => issue.category !== 'mismatch',
  )
  const groups: IssueGroup[] = [
    {
      id: 'schema',
      title: 'Schemafehler',
      issues: visible.filter(
        (issue: ValidationIssue): boolean => issue.category === 'schema' && issue.level === 'error',
      ),
    },
    {
      id: 'business',
      title: 'Geschäftsregeln',
      issues: visible.filter(
        (issue: ValidationIssue): boolean => issue.category === 'business' && issue.level === 'error',
      ),
    },
    {
      id: 'warning',
      title: 'Warnungen',
      issues: visible.filter((issue: ValidationIssue): boolean => issue.level === 'warning'),
    },
    {
      id: 'info',
      title: 'Hinweise',
      issues: visible.filter((issue: ValidationIssue): boolean => issue.level === 'info'),
    },
  ]
  return groups.filter((group: IssueGroup): boolean => group.issues.length > 0)
}

function engineLabel(meta: ValidationMeta): string {
  if (meta.engine === 'kosit') {
    const version: string = meta.engine_version ? ` ${meta.engine_version}` : ''
    const scenarios: string = meta.scenarios_version ? ` · ${meta.scenarios_version}` : ''
    return `KoSIT Validator${version}${scenarios}`
  }
  return 'Interne Geschäftsregeln (keine volle KoSIT-Prüfung)'
}

function isEmptyValue(value: unknown): boolean {
  return value === null || value === undefined || value === ''
}

function fieldState(
  invoice: InvoiceParseResponse,
  fieldName: string,
  value: unknown,
  markMissing: boolean = false,
): FieldState {
  const mismatch: MismatchField | undefined = invoice.mismatch_fields.find(
    (item: MismatchField): boolean =>
      item.field === fieldName && !item.matched && Boolean(item.xml_value),
  )
  if (mismatch) {
    return 'mismatch'
  }
  const hasError: boolean = invoice.validation_issues.some(
    (issue: ValidationIssue): boolean => issue.field === fieldName && issue.level === 'error',
  )
  if (hasError) {
    return 'error'
  }
  if (markMissing && isEmptyValue(value)) {
    return 'missing'
  }
  return 'ok'
}

function fieldClassName(state: FieldState): string {
  if (state === 'ok') {
    return ''
  }
  return `field field--${state}`
}

function fieldHint(state: FieldState): string | null {
  switch (state) {
    case 'missing':
      return 'fehlt'
    case 'error':
      return 'Fehler'
    case 'mismatch':
      return 'Abweichung'
    default:
      return null
  }
}

function DisplayValue({ value }: { value: string }): JSX.Element {
  if (value === '—') {
    return (
      <>
        <span aria-hidden="true">—</span>
        <span className="visually-hidden">nicht angegeben</span>
      </>
    )
  }
  return <>{value}</>
}

function issueLevelLabel(level: string): string {
  if (level === 'error') {
    return 'Fehler'
  }
  if (level === 'warning') {
    return 'Warnung'
  }
  if (level === 'info') {
    return 'Hinweis'
  }
  return level
}

function SnapshotField({
  label,
  value,
  state,
}: {
  label: string
  value: string
  state: FieldState
}): JSX.Element {
  const hint: string | null = fieldHint(state)
  return (
    <div className={`snapshot__item ${fieldClassName(state)}`}>
      <dt>{label}</dt>
      <dd>
        <DisplayValue value={value} />
        {hint && (
          <span className="snapshot__mark">
            {' '}
            · {hint}
          </span>
        )}
      </dd>
    </div>
  )
}

function MarkedValue({
  value,
  state,
}: {
  value: string
  state: FieldState
}): JSX.Element {
  const hint: string | null = fieldHint(state)
  return (
    <>
      <DisplayValue value={value} />
      {hint && <span className="snapshot__mark"> · {hint}</span>}
    </>
  )
}

function PartyBlock({
  title,
  party,
  nameField,
  vatField,
  ibanField,
  invoice,
}: {
  title: string
  party: PartyInfo | null
  nameField: string
  vatField: string
  ibanField: string | null
  invoice: InvoiceParseResponse
}): JSX.Element {
  const nameState: FieldState = fieldState(invoice, nameField, party?.name, true)
  const vatState: FieldState = fieldState(invoice, vatField, party?.vat_id, false)
  const ibanState: FieldState | null = ibanField
    ? fieldState(invoice, ibanField, party?.iban, true)
    : null

  return (
    <div className="party">
      <h3>{title}</h3>
      <p className={`party__name ${fieldClassName(nameState)}`}>
        <MarkedValue value={party?.name || '—'} state={nameState} />
      </p>
      {party?.address && <p>{party.address}</p>}
      {(party?.vat_id || vatState === 'error') && (
        <p className={fieldClassName(vatState)}>
          USt-IdNr.: <MarkedValue value={party?.vat_id || '—'} state={vatState} />
        </p>
      )}
      {ibanState && (
        <p className={fieldClassName(ibanState)}>
          IBAN: <MarkedValue value={formatIban(party?.iban)} state={ibanState} />
        </p>
      )}
    </div>
  )
}

export function InvoiceView({
  invoice,
  sourceFile = null,
  onUpgrade,
}: InvoiceViewProps): JSX.Element {
  const currency: string | null = invoice.totals?.currency ?? null
  const [exportError, setExportError] = useState<string | null>(null)
  const [exporting, setExporting] = useState<ExportAction | null>(null)
  const [exportConfirmed, setExportConfirmed] = useState<boolean>(false)
  const exportingRef: RefObject<boolean> = useRef<boolean>(false)
  const outcome: UserOutcome = userOutcome(invoice)
  const outcomeClass: string = `outcome outcome--${outcome}`
  const hasMismatch: boolean = hasPdfXmlMismatch(invoice)
  const riskyExport: boolean = isRiskyExport(invoice)
  const exportLocked: boolean = riskyExport && !exportConfirmed
  const allMatched: boolean =
    invoice.file_type === 'zugferd_pdf' &&
    invoice.mismatch_fields.length > 0 &&
    !hasMismatch
  const issueGroups: IssueGroup[] = groupedIssues(invoice.validation_issues)

  const sellerState: FieldState = fieldState(invoice, 'seller', invoice.seller?.name, true)
  const amountState: FieldState = fieldState(invoice, 'gross', invoice.totals?.gross, true)
  const dueState: FieldState = fieldState(invoice, 'due_date', invoice.due_date, true)
  const ibanState: FieldState = fieldState(invoice, 'iban', invoice.seller?.iban, true)
  const numberState: FieldState = fieldState(
    invoice,
    'invoice_number',
    invoice.invoice_number,
    true,
  )
  const issueDateState: FieldState = fieldState(invoice, 'issue_date', invoice.issue_date, true)
  const taxState: FieldState = fieldState(invoice, 'tax', invoice.totals?.tax, false)

  useEffect(() => {
    setExportConfirmed(false)
    setExportError(null)
  }, [invoice.filename, invoice.invoice_number, invoice.validation_status])

  async function handleViewPdf(): Promise<void> {
    if (exportingRef.current) {
      return
    }
    setExportError(null)
    setExporting('view-pdf')
    exportingRef.current = true
    try {
      await downloadViewPdf(invoice)
    } catch (err: unknown) {
      const message: string = err instanceof Error ? err.message : 'PDF-Download fehlgeschlagen.'
      setExportError(message)
    } finally {
      exportingRef.current = false
      setExporting(null)
    }
  }

  async function handleExport(format: ExportFormat): Promise<void> {
    if (exportingRef.current) {
      return
    }
    if (exportLocked) {
      setExportError('Bitte zuerst die Fehler bestätigen.')
      return
    }
    setExportError(null)
    setExporting(format)
    exportingRef.current = true
    try {
      await exportInvoice(invoice, format)
    } catch (err: unknown) {
      const message: string = err instanceof Error ? err.message : 'Export fehlgeschlagen.'
      setExportError(message)
    } finally {
      exportingRef.current = false
      setExporting(null)
    }
  }

  async function handleAccountantPackage(): Promise<void> {
    if (exportingRef.current) {
      return
    }
    if (exportLocked) {
      setExportError('Bitte zuerst die Fehler bestätigen.')
      return
    }
    setExportError(null)
    setExporting('package')
    exportingRef.current = true
    try {
      await downloadAccountantPackage(invoice, sourceFile)
    } catch (err: unknown) {
      const message: string =
        err instanceof Error ? err.message : 'Paket-Download fehlgeschlagen.'
      setExportError(message)
    } finally {
      exportingRef.current = false
      setExporting(null)
    }
  }

  async function handleValidationReport(): Promise<void> {
    if (exportingRef.current) {
      return
    }
    setExportError(null)
    setExporting('report')
    exportingRef.current = true
    try {
      await downloadValidationReport(invoice)
    } catch (err: unknown) {
      const message: string =
        err instanceof Error ? err.message : 'Prüfbericht-Download fehlgeschlagen.'
      setExportError(message)
    } finally {
      exportingRef.current = false
      setExporting(null)
    }
  }

  const amountLabel: string =
    invoice.document_type === 'credit_note' ? 'Gutschrift' : 'Zu zahlen'
  const exportBusy: boolean = exporting !== null

  return (
    <section className="invoice">
      <div className="invoice__meta">
        <div>
          <p className="invoice__label">
            {invoice.document_type === 'credit_note' ? 'Gutschrift' : 'Rechnung'}
          </p>
          <h2 className={fieldClassName(numberState)}>
            <MarkedValue value={invoice.invoice_number ?? 'Ohne Nummer'} state={numberState} />
          </h2>
        </div>
        <div className="invoice__badges">
          <span className={validationBadgeClass(invoice.validation_status)} role="status">
            {validationLabel(invoice.validation_status)}
          </span>
        </div>
      </div>

      <div className={outcomeClass} role="status">
        <p className="outcome__label">Ergebnis</p>
        <strong>{outcomeLabel(outcome)}</strong>
        <p>{outcomeDescription(outcome)}</p>
      </div>

      <dl className="invoice__snapshot">
        <SnapshotField
          label="Lieferant"
          value={invoice.seller?.name || '—'}
          state={sellerState}
        />
        <SnapshotField
          label={amountLabel}
          value={formatAmount(invoice.totals?.gross, currency)}
          state={amountState}
        />
        <SnapshotField
          label="Fällig"
          value={formatDateDe(invoice.due_date)}
          state={dueState}
        />
        <SnapshotField
          label="IBAN"
          value={formatIban(invoice.seller?.iban)}
          state={ibanState}
        />
      </dl>

      {invoice.duplicate !== null && invoice.duplicate !== undefined && (
        <div className="banner banner--warn" role="status">
          <strong>{invoice.duplicate.message}</strong>
          <p>Prüfen Sie, ob eine zweite Buchung oder Zahlung nötig ist.</p>
        </div>
      )}
      {hasMismatch && (
        <div className="banner banner--mismatch" role="alert">
          <strong>Nicht zahlen — PDF und XML weichen ab</strong>
          <p>
            Bitte den Lieferanten kontaktieren und eine korrigierte Rechnung anfordern, bevor Sie
            überweisen oder buchen.
          </p>
        </div>
      )}
      {allMatched && (
        <div className="banner banner--match" role="status">
          <strong>PDF und XML stimmen überein</strong>
          <p>Geprüfte Felder: Nummer, Datum, Brutto, MwSt, IBAN.</p>
        </div>
      )}
      {!invoice.validation_meta.full_check_completed && invoice.status !== 'error' && (
        <div className="banner banner--warn" role="status">
          <strong>Keine volle KoSIT-Prüfung</strong>
          <p>
            Geprüft wurden Pflichtfelder und Summen. Das ist kein EN-16931-/XRechnung-Nachweis.
          </p>
        </div>
      )}

      {invoice.next_steps.length > 0 && (
        <div className="next-steps next-steps--primary">
          <h3>Was tun als Nächstes?</h3>
          <ol>
            {invoice.next_steps.map((step: string, index: number) => (
              <li key={`step-${index}`}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      <div className="export-bar export-bar--view" aria-labelledby="view-pdf-label" aria-busy={exportBusy}>
        <p className="export-bar__label" id="view-pdf-label">
          Lesbare Ansicht
        </p>
        <p className="visually-hidden" aria-live="polite">
          {exporting === 'view-pdf' ? 'Lesbare PDF wird erstellt' : ''}
        </p>
        <div className="export-bar__actions">
          <button
            type="button"
            className="export-bar__primary"
            disabled={exportBusy}
            onClick={() => void handleViewPdf()}
          >
            {exporting === 'view-pdf' ? 'PDF…' : 'Lesbare PDF herunterladen'}
          </button>
        </div>
        <p className="export-bar__hint">
          Arbeitskopie aus den gelesenen XML-Daten. Keine Originalrechnung und kein steuerlicher
          Beleg.
        </p>
      </div>

      <div
        className={riskyExport ? 'export-bar export-bar--risky' : 'export-bar'}
        aria-labelledby="export-label"
        aria-busy={exportBusy}
      >
        <p className="export-bar__label" id="export-label">
          Für Buchhaltung exportieren
        </p>
        <p className="visually-hidden" aria-live="polite">
          {exporting === 'package'
            ? 'Paket wird erstellt'
            : exporting === 'csv'
              ? 'CSV wird erstellt'
              : exporting === 'excel'
                ? 'Excel wird erstellt'
                : exporting === 'datev'
                  ? 'DATEV-Datei wird erstellt'
                  : exporting === 'report'
                    ? 'Prüfbericht wird erstellt'
                    : ''}
        </p>
        {riskyExport && (
          <p className="export-bar__warn" role="alert">
            Diese Rechnung enthält Fehler oder Abweichungen. Exportieren Sie sie nur, wenn Sie das
            bewusst an den Steuerberater weitergeben möchten — nicht als gültigen Beleg behandeln.
          </p>
        )}
        {riskyExport && (
          <label className="export-confirm">
            <input
              type="checkbox"
              checked={exportConfirmed}
              onChange={(event: ChangeEvent<HTMLInputElement>) => {
                setExportConfirmed(event.target.checked)
                setExportError(null)
              }}
            />
            Ich habe die Fehler gesehen und möchte trotzdem exportieren.
          </label>
        )}
        <div className="export-bar__actions">
          <button
            type="button"
            className="export-bar__primary"
            disabled={exportBusy || exportLocked}
            onClick={() => void handleAccountantPackage()}
          >
            {exporting === 'package' ? 'Paket…' : 'Paket für Steuerberater'}
          </button>
          <button
            type="button"
            disabled={exportBusy || exportLocked}
            onClick={() => void handleExport('csv')}
          >
            {exporting === 'csv' ? 'CSV…' : 'CSV'}
          </button>
          <button
            type="button"
            disabled={exportBusy || exportLocked}
            onClick={() => void handleExport('excel')}
          >
            {exporting === 'excel' ? 'Excel…' : 'Excel'}
          </button>
          <button
            type="button"
            disabled={exportBusy || exportLocked}
            onClick={() => void handleExport('datev')}
          >
            {exporting === 'datev' ? 'DATEV…' : 'DATEV'}
          </button>
          <button
            type="button"
            className="export-bar__report"
            disabled={exportBusy}
            onClick={() => void handleValidationReport()}
          >
            {exporting === 'report' ? 'Bericht…' : 'Prüfbericht herunterladen'}
          </button>
        </div>
        <p className="export-bar__hint">
          Paket = Originaldatei + Kurzfassung + Prüfbericht + Excel + DATEV-CSV
          {invoice.file_type === 'zugferd_pdf' ? ' (ZUGFeRD-PDF mit eingebettetem XML)' : ''}.
          DATEV-CSV ist ein Buchungsvorschlag, kein DATEVconnect. Der Prüfbericht ist für
          Lieferanten oder Steuerberater.
        </p>
        {exportError && (
          <>
            <p className="status status--error" role="alert">
              {exportError}
            </p>
            {onUpgrade !== undefined && /(Kontingent|Tarif|Plus|Limit)/i.test(exportError) ? (
              <button type="button" className="btn btn--secondary" onClick={onUpgrade}>
                Höhere Kontingente ansehen
              </button>
            ) : null}
          </>
        )}
      </div>

      <p className="invoice__message">{invoice.message}</p>

      <dl className="validation-meta">
        <div>
          <dt>Standard</dt>
          <dd>{invoice.validation_meta.standard_version ?? '—'}</dd>
        </div>
        <div>
          <dt>Profil</dt>
          <dd>{invoice.validation_meta.profile ?? '—'}</dd>
        </div>
        <div>
          <dt>Prüfengine</dt>
          <dd>{engineLabel(invoice.validation_meta)}</dd>
        </div>
      </dl>

      <dl className="invoice__facts">
        <div>
          <dt>Datei</dt>
          <dd className="break-text">{invoice.filename}</dd>
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
          <dd className={fieldClassName(issueDateState)}>
            <MarkedValue value={formatDateDe(invoice.issue_date)} state={issueDateState} />
          </dd>
        </div>
        <div>
          <dt>Fälligkeitsdatum</dt>
          <dd className={fieldClassName(dueState)}>
            <MarkedValue value={formatDateDe(invoice.due_date)} state={dueState} />
          </dd>
        </div>
        {invoice.payment_reference && (
          <div>
            <dt>Zahlungsreferenz</dt>
            <dd className="break-text">{invoice.payment_reference}</dd>
          </div>
        )}
      </dl>

      <div className="invoice__parties">
        <PartyBlock
          title="Lieferant"
          party={invoice.seller}
          nameField="seller"
          vatField="seller_vat_id"
          ibanField="iban"
          invoice={invoice}
        />
        <PartyBlock
          title="Empfänger"
          party={invoice.buyer}
          nameField="buyer"
          vatField="buyer_vat_id"
          ibanField={null}
          invoice={invoice}
        />
      </div>

      {invoice.totals && (
        <div className="invoice__totals">
          <div>
            <span>Netto</span>
            <strong>{formatAmount(invoice.totals.net, currency)}</strong>
          </div>
          <div className={fieldClassName(taxState)}>
            <span>MwSt</span>
            <strong>
              <MarkedValue value={formatAmount(invoice.totals.tax, currency)} state={taxState} />
            </strong>
          </div>
          <div className={fieldClassName(amountState)}>
            <span>Brutto</span>
            <strong>
              <MarkedValue
                value={formatAmount(invoice.totals.gross, currency)}
                state={amountState}
              />
            </strong>
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
          <h3 id="mismatch-heading">PDF ↔ XML Abgleich</h3>
          <div className="table-scroll">
            <table className="mismatch-table">
              <caption className="visually-hidden">Vergleich der Felder zwischen PDF und XML</caption>
              <thead>
                <tr>
                  <th scope="col">Feld</th>
                  <th scope="col">XML</th>
                  <th scope="col">PDF</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {invoice.mismatch_fields.map((item: MismatchField) => (
                  <tr key={item.field} className={item.matched ? undefined : 'row--mismatch'}>
                    <td>{item.label}</td>
                    <td className="break-text">
                      <DisplayValue value={item.xml_value ?? '—'} />
                    </td>
                    <td className="break-text">
                      <DisplayValue value={item.pdf_value ?? '—'} />
                    </td>
                    <td>
                      {item.matched ? 'Übereinstimmung' : 'Abweichung'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {invoice.line_items.length > 0 && (
        <div className="invoice__lines-wrap">
          <h3 id="lines-heading">Positionen</h3>
          <div className="table-scroll">
            <table className="invoice__lines">
              <caption className="visually-hidden">Rechnungspositionen</caption>
              <thead>
                <tr>
                  <th scope="col">#</th>
                  <th scope="col">Beschreibung</th>
                  <th scope="col">Menge</th>
                  <th scope="col">Preis</th>
                  <th scope="col">MwSt %</th>
                  <th scope="col">Netto</th>
                  <th scope="col">Brutto</th>
                </tr>
              </thead>
              <tbody>
                {invoice.line_items.map((item: LineItem, index: number) => (
                  <tr key={`${item.position ?? index}-${index}`}>
                    <td>{item.position ?? index + 1}</td>
                    <td className="invoice__desc">
                      <DisplayValue value={item.description ?? '—'} />
                    </td>
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
        </div>
      )}

      {issueGroups.map((group: IssueGroup) => (
        <div key={group.id} className="invoice__issues-wrap">
          <h3>{group.title}</h3>
          <ul className="invoice__issues">
            {group.issues.map((issue: ValidationIssue, index: number) => (
              <li
                key={`${issue.code ?? 'issue'}-${index}`}
                className={`issue issue--${issue.level}`}
              >
                <div className="issue__head">
                  <span className="issue__level">{issueLevelLabel(issue.level)}</span>
                  <span className="issue__cat">[{issue.category}]</span>
                  {issue.bt_code && <span className="issue__bt">{issue.bt_code}</span>}
                  {issue.code && <span className="issue__code">{issue.code}</span>}
                </div>
                <p className="issue__message">{issue.message}</p>
                {issue.explanation && issue.explanation !== issue.message && (
                  <p className="issue__explain">{issue.explanation}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  )
}

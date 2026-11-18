import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { buildIssue, createIssueDraft } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type {
  IssueAddress,
  IssueArtifact,
  IssueArtifactFormat,
  IssueBuildResponse,
  IssueDraft,
  IssueDraftResponse,
  IssueLineInput,
  IssueParty,
} from '../types/issue'
import type { MeResponse, ValidationIssue } from '../types/invoice'

type IssuePageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  sessionReady: boolean
  onLogout: () => void
}

const UNIT_OPTIONS: readonly { code: string; label: string }[] = [
  { code: 'C62', label: 'Stück (C62)' },
  { code: 'HUR', label: 'Stunde (HUR)' },
  { code: 'DAY', label: 'Tag (DAY)' },
  { code: 'KGM', label: 'Kilogramm (KGM)' },
  { code: 'MTR', label: 'Meter (MTR)' },
  { code: 'LTR', label: 'Liter (LTR)' },
  { code: 'SET', label: 'Satz (SET)' },
  { code: 'MON', label: 'Monat (MON)' },
]

const DOWNLOADS: readonly { format: 'zugferd_pdf' | 'xrechnung'; label: string }[] = [
  { format: 'zugferd_pdf', label: 'Download als ZUGFeRD PDF' },
  { format: 'xrechnung', label: 'Download als XRechnung (XML)' },
]

const FIELD_LIMITS: {
  invoiceNumber: number
  buyerReference: number
  name: number
  street: number
  postcode: number
  city: number
  country: number
  vatId: number
  iban: number
  contactName: number
  phone: number
  email: number
  lineDescription: number
  quantity: number
  unitPrice: number
} = {
  invoiceNumber: 50,
  buyerReference: 50,
  name: 200,
  street: 200,
  postcode: 20,
  city: 80,
  country: 2,
  vatId: 16,
  iban: 42,
  contactName: 200,
  phone: 40,
  email: 254,
  lineDescription: 200,
  quantity: 16,
  unitPrice: 16,
}

export function IssuePage({
  onNavigate,
  session,
  sessionReady,
  onLogout,
}: IssuePageProps): JSX.Element {
  const [pdf, setPdf] = useState<File | null>(null)
  const [draft, setDraft] = useState<IssueDraft | null>(null)
  const [hints, setHints] = useState<string[]>([])
  const [warnings, setWarnings] = useState<string[]>([])
  const [confirmed, setConfirmed] = useState<boolean>(false)
  const [pending, setPending] = useState<null | 'read' | 'xrechnung' | 'zugferd_pdf'>(null)
  const loading: boolean = pending !== null
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<IssueBuildResponse | null>(null)
  const [dismissedFields, setDismissedFields] = useState<ReadonlySet<string>>(new Set())
  const invalidFields: ReadonlySet<string> = highlightedFields(draft, result, dismissedFields)

  function dismissField(field: string): void {
    setDismissedFields((current: ReadonlySet<string>): ReadonlySet<string> => {
      if (current.has(field)) {
        return current
      }
      const next: Set<string> = new Set(current)
      next.add(field)
      return next
    })
  }

  async function onReadPdf(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (pdf === null || loading) {
      return
    }
    setPending('read')
    setError(null)
    setResult(null)
    setDismissedFields(new Set())
    try {
      const response: IssueDraftResponse = await createIssueDraft(pdf)
      setDraft(response.draft)
      setHints(response.hints.map((hint) => hint.message))
      setWarnings(response.warnings)
      setConfirmed(false)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'PDF konnte nicht gelesen werden.')
    } finally {
      setPending(null)
    }
  }

  async function onDownload(format: 'zugferd_pdf' | 'xrechnung'): Promise<void> {
    if (draft === null || pdf === null || loading || !confirmed) {
      return
    }
    if (missingRequiredFields(draft).size > 0) {
      return
    }
    setPending(format)
    setError(null)
    try {
      const response: IssueBuildResponse = await buildIssue(draft, pdf, confirmed, format)
      setDismissedFields(new Set())
      setResult(response)
      const artifact: IssueArtifact | undefined = response.artifacts.find(
        (item: IssueArtifact): boolean => item.format === format,
      )
      if (artifact !== undefined && artifact.download_allowed && artifact.content_base64 !== null) {
        saveArtifact(artifact)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'E-Rechnung konnte nicht erzeugt werden.')
    } finally {
      setPending(null)
    }
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
        <h1 tabIndex={-1}>E-Rechnung erstellen</h1>
        <p className="page__lead">
          Für Rechnungsaussteller, deren Kunde eine normale PDF nicht mehr annimmt.
          Der Empfang eingehender XRechnungen bleibt getrennt.
        </p>
      </header>

      {sessionReady ? (
        <>
      <section className="issue-note" aria-label="Hinweis">
        <p>
          Nur der Rechnungsaussteller darf die erzeugte Datei versenden. Das Auslesen füllt einen
          Entwurf; es garantiert keine steuerliche oder rechtliche Konformität. Maßgeblich ist die
          XML, nicht das sichtbare PDF. Ein Download gibt es erst, wenn KoSIT die Datei als gültig
          abgeschlossen hat. Die PDF wird danach nicht gespeichert. Ohne Tarif sind 10 E-Rechnungen
          pro Tag möglich, mit Plus 100 und mit Team 500. Jede gelesene PDF zählt einmal; der
          Download derselben Rechnung zählt nicht erneut. Leere Felder füllt der Aussteller selbst.
          Ohne Konto bleiben die eigenen Angaben leer.
        </p>
      </section>

      <form className="issue-form" onSubmit={(event) => void onReadPdf(event)}>
        <label htmlFor="issue-pdf">Eigene PDF-Rechnung</label>
        <input
          id="issue-pdf"
          type="file"
          accept="application/pdf,.pdf"
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setPdf(event.target.files?.[0] ?? null)
          }}
        />
        <div className="auth-form__actions">
          <button className="btn btn--secondary" type="submit" disabled={pdf === null || loading}>
            {pending === 'read' ? 'Wird gelesen…' : 'Entwurf lesen'}
          </button>
        </div>
      </form>

      {error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : null}

      {draft ? (
        <form
          className="issue-form"
          onSubmit={(event: FormEvent<HTMLFormElement>) => event.preventDefault()}
        >
          {warnings.length > 0 ? (
            <ul className="issue-warnings">
              {warnings.map((warning: string) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
          {hints.length > 0 ? (
            <ul className="issue-hints">
              {hints.map((hint: string) => (
                <li key={hint}>{hint}</li>
              ))}
            </ul>
          ) : null}

          <div className="issue-columns">
            <fieldset>
              <legend>Rechnung</legend>
              <TextField
                id="invoice-number"
                label="Rechnungsnummer"
                maxLength={FIELD_LIMITS.invoiceNumber}
                value={draft.invoice_number}
                invalid={invalidFields.has('invoice_number')}
                onChange={(value: string) => {
                  dismissField('invoice_number')
                  setDraft({ ...draft, invoice_number: emptyToNull(value) })
                }}
              />
              <TextField
                id="issue-date"
                label="Rechnungsdatum"
                type="date"
                value={draft.issue_date}
                invalid={invalidFields.has('issue_date')}
                onChange={(value: string) => {
                  dismissField('issue_date')
                  setDraft({ ...draft, issue_date: emptyToNull(value) })
                }}
              />
              <TextField
                id="due-date"
                label="Fälligkeitsdatum"
                type="date"
                value={draft.due_date ?? null}
                invalid={invalidFields.has('due_date')}
                onChange={(value: string) => {
                  dismissField('due_date')
                  setDraft({ ...draft, due_date: emptyToNull(value) })
                }}
              />
              <TextField
                id="delivery-date"
                label="Liefer-/Leistungsdatum"
                type="date"
                value={draft.delivery_date ?? null}
                invalid={invalidFields.has('delivery_date')}
                onChange={(value: string) => {
                  dismissField('delivery_date')
                  setDraft({ ...draft, delivery_date: emptyToNull(value) })
                }}
              />
              <p className="issue-form__hint">Leer gelassen gilt das Rechnungsdatum.</p>
              <TextField
                id="buyer-reference"
                label="Käuferreferenz / Leitweg-ID"
                maxLength={FIELD_LIMITS.buyerReference}
                value={draft.buyer_reference}
                invalid={invalidFields.has('buyer_reference')}
                onChange={(value: string) => {
                  dismissField('buyer_reference')
                  setDraft({ ...draft, buyer_reference: emptyToNull(value) })
                }}
              />
            </fieldset>
            <PartyFields
              title="Verkäufer"
              idPrefix="seller"
              party={draft.seller}
              showPayment
              invalidFields={invalidFields}
              onEdit={dismissField}
              onChange={(party: IssueParty) => setDraft({ ...draft, seller: party })}
            />
            <PartyFields
              title="Käufer"
              idPrefix="buyer"
              party={draft.buyer}
              showPayment={false}
              showEmail
              invalidFields={invalidFields}
              onEdit={dismissField}
              onChange={(party: IssueParty) => setDraft({ ...draft, buyer: party })}
            />
          </div>

          <fieldset>
            <legend>Positionen</legend>
            {draft.lines.map((line: IssueLineInput, index: number) => (
              <div className="issue-line" key={`line-${index}`}>
                <TextField
                  id={`line-${index}-description`}
                  label={`Position ${index + 1}`}
                  maxLength={FIELD_LIMITS.lineDescription}
                  value={line.description}
                  invalid={invalidFields.has(lineField(index, 'description'))}
                  onChange={(value: string) => {
                    dismissField(lineField(index, 'description'))
                    setDraft(updateLine(draft, index, 'description', value))
                  }}
                />
                <TextField
                  id={`line-${index}-quantity`}
                  label="Menge"
                  maxLength={FIELD_LIMITS.quantity}
                  value={textValue(line.quantity)}
                  invalid={invalidFields.has(lineField(index, 'quantity'))}
                  onChange={(value: string) => {
                    dismissField(lineField(index, 'quantity'))
                    setDraft(updateLine(draft, index, 'quantity', value))
                  }}
                />
                <label htmlFor={`line-${index}-unit`}>Einheit</label>
                <select
                  id={`line-${index}-unit`}
                  value={line.unit_code ?? 'C62'}
                  {...invalidInputProps(invalidFields.has(lineField(index, 'unit_code')))}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                    dismissField(lineField(index, 'unit_code'))
                    setDraft(updateLine(draft, index, 'unit_code', event.target.value))
                  }}
                >
                  {UNIT_OPTIONS.map((option) => (
                    <option key={option.code} value={option.code}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <TextField
                  id={`line-${index}-price`}
                  label="Einzelpreis netto"
                  maxLength={FIELD_LIMITS.unitPrice}
                  value={textValue(line.unit_price)}
                  invalid={invalidFields.has(lineField(index, 'unit_price'))}
                  onChange={(value: string) => {
                    dismissField(lineField(index, 'unit_price'))
                    setDraft(updateLine(draft, index, 'unit_price', value))
                  }}
                />
                <label htmlFor={`line-${index}-tax`}>MwSt. %</label>
                <select
                  id={`line-${index}-tax`}
                  value={normalizeRate(line.tax_rate)}
                  {...invalidInputProps(invalidFields.has(lineField(index, 'tax_rate')))}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                    dismissField(lineField(index, 'tax_rate'))
                    setDraft(updateLine(draft, index, 'tax_rate', event.target.value))
                  }}
                >
                  <option value="19">19</option>
                  <option value="7">7</option>
                </select>
              </div>
            ))}
            <div className="auth-form__actions">
              <button
                className="btn btn--secondary"
                type="button"
                onClick={() => setDraft(addLine(draft))}
              >
                Position hinzufügen
              </button>
              {draft.lines.length > 1 ? (
                <button
                  className="btn btn--secondary"
                  type="button"
                  onClick={() => setDraft(removeLastLine(draft))}
                >
                  Letzte Position entfernen
                </button>
              ) : null}
            </div>
          </fieldset>

          <label
            className={confirmed ? 'issue-confirm issue-confirm--done' : 'issue-confirm'}
            htmlFor="issue-confirmed"
          >
            <input
              id="issue-confirmed"
              type="checkbox"
              checked={confirmed}
              aria-invalid={confirmed ? undefined : true}
              onChange={(event: ChangeEvent<HTMLInputElement>) => {
                dismissField('confirmed')
                setConfirmed(event.target.checked)
              }}
            />
            <span>Ich bin der Rechnungsaussteller und bestätige, dass diese Angaben stimmen.</span>
          </label>
          <div className="issue-downloads">
            {pending === 'xrechnung' || pending === 'zugferd_pdf' ? (
              <p className="status status--info" role="status">
                Die Rechnung wird geprüft. Das kann einen Moment dauern.
              </p>
            ) : null}
            {DOWNLOADS.map((item) => (
              <button
                key={item.format}
                className="btn btn--primary"
                type="button"
                disabled={loading || !confirmed || missingRequiredFields(draft).size > 0}
                aria-busy={pending === item.format}
                onClick={() => void onDownload(item.format)}
              >
                <DownloadIcon />
                {pending === item.format ? 'Wird geprüft…' : item.label}
              </button>
            ))}
          </div>
        </form>
      ) : null}

      {result ? <BuildResult result={result} /> : null}
        </>
      ) : (
        <p className="status status--info" role="status">
          Wird geladen…
        </p>
      )}
      <SiteFooter />
    </main>
  )
}

const RESULT_FORMATS: readonly IssueArtifactFormat[] = ['xrechnung', 'zugferd_pdf']

function artifactTitle(format: IssueArtifactFormat): string {
  if (format === 'xrechnung') {
    return 'XRechnung'
  }
  return 'ZUGFeRD PDF'
}

function BuildResult({ result }: { result: IssueBuildResponse }): JSX.Element {
  const visible: IssueArtifact[] = result.artifacts.filter(
    (artifact: IssueArtifact): boolean =>
      RESULT_FORMATS.includes(artifact.format) && artifact.validation_issues.length > 0,
  )
  return (
    <section aria-live="polite">
      <p>{result.message}</p>
      <IssueList issues={result.blocking_issues} />
      {visible.map((artifact: IssueArtifact) => (
        <div key={artifact.format}>
          <p>
            <strong>{artifactTitle(artifact.format)}</strong>
          </p>
          <IssueList issues={artifact.validation_issues} />
        </div>
      ))}
    </section>
  )
}

function DownloadIcon(): JSX.Element {
  return (
    <svg className="issue-downloads__icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 3a1 1 0 0 1 1 1v9.59l2.3-2.3a1 1 0 1 1 1.4 1.42l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 0 1 1.4-1.42l2.3 2.3V4a1 1 0 0 1 1-1zm-7 16a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1z"
      />
    </svg>
  )
}

function IssueList({ issues }: { issues: ValidationIssue[] }): JSX.Element | null {
  if (issues.length === 0) {
    return null
  }
  return (
    <ul>
      {issues.map((issue: ValidationIssue) => (
        <li key={`${issue.code ?? 'issue'}-${issue.message}`}>{issue.message}</li>
      ))}
    </ul>
  )
}

function PartyFields({
  title,
  idPrefix,
  party,
  showPayment,
  showEmail = false,
  invalidFields,
  onEdit,
  onChange,
}: {
  title: string
  idPrefix: string
  party: IssueParty
  showPayment: boolean
  showEmail?: boolean
  invalidFields: ReadonlySet<string>
  onEdit: (field: string) => void
  onChange: (party: IssueParty) => void
}): JSX.Element {
  function setField(key: keyof IssueParty, value: string): void {
    onEdit(`${idPrefix}.${key}`)
    onChange({ ...party, [key]: emptyToNull(value) })
  }

  function setAddress(key: keyof IssueAddress, value: string): void {
    onEdit(`${idPrefix}.address.${key}`)
    onChange({ ...party, address: { ...party.address, [key]: emptyToNull(value) } })
  }

  return (
    <fieldset>
      <legend>{title}</legend>
      <TextField
        id={`${idPrefix}-name`}
        label="Name"
        maxLength={FIELD_LIMITS.name}
        spellCheck={false}
        value={party.name}
        invalid={invalidFields.has(`${idPrefix}.name`)}
        onChange={(value: string) => setField('name', value)}
      />
      <TextField
        id={`${idPrefix}-line`}
        label="Straße"
        maxLength={FIELD_LIMITS.street}
        value={party.address.line}
        invalid={invalidFields.has(`${idPrefix}.address.line`)}
        onChange={(value: string) => setAddress('line', value)}
      />
      <TextField
        id={`${idPrefix}-postcode`}
        label="PLZ"
        maxLength={FIELD_LIMITS.postcode}
        value={party.address.postcode}
        invalid={invalidFields.has(`${idPrefix}.address.postcode`)}
        onChange={(value: string) => setAddress('postcode', value)}
      />
      <TextField
        id={`${idPrefix}-city`}
        label="Ort"
        maxLength={FIELD_LIMITS.city}
        value={party.address.city}
        invalid={invalidFields.has(`${idPrefix}.address.city`)}
        onChange={(value: string) => setAddress('city', value)}
      />
      <TextField
        id={`${idPrefix}-country`}
        label="Land"
        maxLength={FIELD_LIMITS.country}
        value={party.address.country}
        invalid={invalidFields.has(`${idPrefix}.address.country`)}
        onChange={(value: string) => setAddress('country', value)}
      />
      {showPayment ? (
        <>
          <TextField
            id={`${idPrefix}-vat`}
            label="USt-IdNr."
            maxLength={FIELD_LIMITS.vatId}
            value={party.vat_id}
            invalid={invalidFields.has(`${idPrefix}.vat_id`)}
            onChange={(value: string) => setField('vat_id', value)}
          />
          <TextField
            id={`${idPrefix}-iban`}
            label="IBAN"
            maxLength={FIELD_LIMITS.iban}
            value={party.iban}
            invalid={invalidFields.has(`${idPrefix}.iban`)}
            onChange={(value: string) => setField('iban', value)}
          />
          <TextField
            id={`${idPrefix}-contact`}
            label="Ansprechpartner"
            maxLength={FIELD_LIMITS.contactName}
            spellCheck={false}
            value={party.contact_name}
            invalid={invalidFields.has(`${idPrefix}.contact_name`)}
            onChange={(value: string) => setField('contact_name', value)}
          />
          <TextField
            id={`${idPrefix}-phone`}
            label="Telefon"
            maxLength={FIELD_LIMITS.phone}
            value={party.phone}
            invalid={invalidFields.has(`${idPrefix}.phone`)}
            onChange={(value: string) => setField('phone', value)}
          />
          <TextField
            id={`${idPrefix}-email`}
            label="E-Mail"
            maxLength={FIELD_LIMITS.email}
            value={party.email}
            invalid={invalidFields.has(`${idPrefix}.email`)}
            onChange={(value: string) => setField('email', value)}
          />
        </>
      ) : showEmail ? (
        <TextField
          id={`${idPrefix}-email`}
          label="E-Mail"
          maxLength={FIELD_LIMITS.email}
          value={party.email}
          invalid={invalidFields.has(`${idPrefix}.email`)}
          onChange={(value: string) => setField('email', value)}
        />
      ) : null}
    </fieldset>
  )
}

function TextField({
  id,
  label,
  value,
  onChange,
  type = 'text',
  invalid = false,
  maxLength,
  spellCheck,
}: {
  id: string
  label: string
  value: string | null
  onChange: (value: string) => void
  type?: 'text' | 'date'
  invalid?: boolean
  maxLength?: number
  spellCheck?: boolean
}): JSX.Element {
  return (
    <>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type={type}
        value={value ?? ''}
        maxLength={maxLength}
        spellCheck={spellCheck}
        autoComplete="off"
        {...invalidInputProps(invalid)}
        onChange={(event: ChangeEvent<HTMLInputElement>) => onChange(event.target.value)}
      />
    </>
  )
}

function invalidInputProps(invalid: boolean): {
  className?: string
  'aria-invalid'?: true
} {
  if (!invalid) {
    return {}
  }
  return { className: 'issue-form__input--error', 'aria-invalid': true }
}

function lineField(index: number, key: keyof IssueLineInput): string {
  return `lines.${index + 1}.${key}`
}

function highlightedFields(
  draft: IssueDraft | null,
  result: IssueBuildResponse | null,
  dismissed: ReadonlySet<string>,
): ReadonlySet<string> {
  const active: Set<string> = missingRequiredFields(draft)
  if (result !== null) {
    for (const field of issueErrorFields(result)) {
      active.add(field)
    }
  }
  for (const field of dismissed) {
    active.delete(field)
  }
  return active
}

function missingRequiredFields(draft: IssueDraft | null): Set<string> {
  const fields: Set<string> = new Set()
  if (draft === null) {
    return fields
  }
  if (!hasText(draft.invoice_number)) {
    fields.add('invoice_number')
  }
  if (!hasText(draft.issue_date)) {
    fields.add('issue_date')
  }
  addPartyGaps(fields, 'seller', draft.seller, true)
  addPartyGaps(fields, 'buyer', draft.buyer, false)
  draft.lines.forEach((line: IssueLineInput, index: number): void => {
    const prefix: string = `lines.${index + 1}`
    if (!hasText(line.description)) {
      fields.add(`${prefix}.description`)
    }
    if (!hasAmount(line.quantity)) {
      fields.add(`${prefix}.quantity`)
    }
    if (!hasAmount(line.unit_price)) {
      fields.add(`${prefix}.unit_price`)
    }
  })
  return fields
}

function addPartyGaps(fields: Set<string>, prefix: string, party: IssueParty, seller: boolean): void {
  if (!hasText(party.name)) {
    fields.add(`${prefix}.name`)
  }
  if (!hasText(party.address.line)) {
    fields.add(`${prefix}.address.line`)
  }
  if (!hasText(party.address.postcode)) {
    fields.add(`${prefix}.address.postcode`)
  }
  if (!hasText(party.address.city)) {
    fields.add(`${prefix}.address.city`)
  }
  if (!hasText(party.address.country)) {
    fields.add(`${prefix}.address.country`)
  }
  if (!seller) {
    return
  }
  if (!hasText(party.vat_id)) {
    fields.add(`${prefix}.vat_id`)
  }
  if (!hasText(party.iban)) {
    fields.add(`${prefix}.iban`)
  }
}

function hasText(value: string | null): boolean {
  return value !== null && value.trim() !== ''
}

function hasAmount(value: string | number | null): boolean {
  if (value === null) {
    return false
  }
  return String(value).trim() !== ''
}

function issueErrorFields(result: IssueBuildResponse): Set<string> {
  const fields: Set<string> = new Set()
  collectErrorFields(result.blocking_issues, fields)
  for (const artifact of result.artifacts) {
    collectErrorFields(artifact.validation_issues, fields)
  }
  return fields
}

function collectErrorFields(issues: ValidationIssue[], fields: Set<string>): void {
  for (const issue of issues) {
    if (issue.level === 'error' && issue.field) {
      fields.add(issue.field)
    }
  }
}

function emptyToNull(value: string): string | null {
  if (value.trim() === '') {
    return null
  }
  return value
}

function textValue(value: string | number | null): string | null {
  if (value === null) {
    return null
  }
  return String(value)
}

function normalizeRate(value: string | number | null): string {
  const text: string = value === null ? '' : String(value)
  return text.startsWith('7') ? '7' : '19'
}

function updateLine(
  draft: IssueDraft,
  index: number,
  key: keyof IssueLineInput,
  value: string,
): IssueDraft {
  const lines: IssueLineInput[] = draft.lines.map((line: IssueLineInput, lineIndex: number) => {
    if (lineIndex !== index) {
      return line
    }
    return { ...line, [key]: emptyToNull(value) }
  })
  return { ...draft, lines }
}

function addLine(draft: IssueDraft): IssueDraft {
  const line: IssueLineInput = {
    description: null,
    quantity: null,
    unit_code: 'C62',
    unit_price: null,
    tax_rate: '19',
  }
  return { ...draft, lines: [...draft.lines, line] }
}

function removeLastLine(draft: IssueDraft): IssueDraft {
  return { ...draft, lines: draft.lines.slice(0, -1) }
}

function saveArtifact(artifact: IssueArtifact): void {
  if (!artifact.download_allowed || artifact.content_base64 === null) {
    return
  }
  const binary: string = atob(artifact.content_base64)
  const buffer: ArrayBuffer = new ArrayBuffer(binary.length)
  const bytes: Uint8Array = new Uint8Array(buffer)
  for (let index: number = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index)
  }
  const blob: Blob = new Blob([buffer], { type: artifact.media_type })
  const url: string = URL.createObjectURL(blob)
  const link: HTMLAnchorElement = document.createElement('a')
  link.href = url
  link.download = artifact.filename
  link.click()
  URL.revokeObjectURL(url)
}

import { useState, type ChangeEvent, type FormEvent, type JSX } from 'react'
import { buildIssue, createIssueDraft } from '../api/client'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type {
  IssueAddress,
  IssueArtifact,
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

const ARTIFACT_LABELS: Record<IssueArtifact['format'], string> = {
  xrechnung: 'XRechnung XML',
  zugferd_xml: 'ZUGFeRD XML',
  zugferd_pdf: 'ZUGFeRD PDF',
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
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<IssueBuildResponse | null>(null)

  async function onReadPdf(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (pdf === null || loading) {
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response: IssueDraftResponse = await createIssueDraft(pdf)
      setDraft(response.draft)
      setHints(response.hints.map((hint) => hint.message))
      setWarnings(response.warnings)
      setConfirmed(false)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'PDF konnte nicht gelesen werden.')
    } finally {
      setLoading(false)
    }
  }

  async function onBuild(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (draft === null || pdf === null || loading) {
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response: IssueBuildResponse = await buildIssue(draft, pdf, confirmed)
      setResult(response)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'E-Rechnung konnte nicht erzeugt werden.')
    } finally {
      setLoading(false)
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
        <h1 tabIndex={-1}>E-Rechnung aus PDF erstellen</h1>
        <p className="page__lead">
          Für Rechnungsaussteller, deren Kunde eine normale PDF nicht mehr annimmt.
          Der Empfang eingehender XRechnungen bleibt getrennt.
        </p>
      </header>

      {sessionReady && session?.is_admin ? (
        <>
      <section className="issue-note" aria-label="Hinweis">
        <p>
          Nur der Rechnungsaussteller darf die erzeugte Datei versenden. Das Auslesen füllt einen
          Entwurf; es garantiert keine steuerliche oder rechtliche Konformität. Maßgeblich ist die
          XML, nicht das sichtbare PDF. Ein Download gibt es erst, wenn KoSIT die Datei als gültig
          abgeschlossen hat. Die PDF wird danach nicht gespeichert.
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
            Entwurf lesen
          </button>
        </div>
      </form>

      {error ? (
        <p className="status status--error" role="alert">
          {error}
        </p>
      ) : null}

      {draft ? (
        <form className="issue-form" onSubmit={(event) => void onBuild(event)}>
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
                value={draft.invoice_number}
                onChange={(value: string) => setDraft({ ...draft, invoice_number: emptyToNull(value) })}
              />
              <TextField
                id="issue-date"
                label="Rechnungsdatum"
                type="date"
                value={draft.issue_date}
                onChange={(value: string) => setDraft({ ...draft, issue_date: emptyToNull(value) })}
              />
              <TextField
                id="buyer-reference"
                label="Käuferreferenz / Leitweg-ID"
                value={draft.buyer_reference}
                onChange={(value: string) => setDraft({ ...draft, buyer_reference: emptyToNull(value) })}
              />
            </fieldset>
            <PartyFields
              title="Verkäufer"
              idPrefix="seller"
              party={draft.seller}
              showPayment
              onChange={(party: IssueParty) => setDraft({ ...draft, seller: party })}
            />
            <PartyFields
              title="Käufer"
              idPrefix="buyer"
              party={draft.buyer}
              showPayment={false}
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
                  value={line.description}
                  onChange={(value: string) => setDraft(updateLine(draft, index, 'description', value))}
                />
                <TextField
                  id={`line-${index}-quantity`}
                  label="Menge"
                  value={textValue(line.quantity)}
                  onChange={(value: string) => setDraft(updateLine(draft, index, 'quantity', value))}
                />
                <label htmlFor={`line-${index}-unit`}>Einheit</label>
                <select
                  id={`line-${index}-unit`}
                  value={line.unit_code ?? 'C62'}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                    setDraft(updateLine(draft, index, 'unit_code', event.target.value))
                  }
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
                  value={textValue(line.unit_price)}
                  onChange={(value: string) => setDraft(updateLine(draft, index, 'unit_price', value))}
                />
                <label htmlFor={`line-${index}-tax`}>MwSt. %</label>
                <select
                  id={`line-${index}-tax`}
                  value={normalizeRate(line.tax_rate)}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                    setDraft(updateLine(draft, index, 'tax_rate', event.target.value))
                  }
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

          <label className="auth-form__check" htmlFor="issue-confirmed">
            <input
              id="issue-confirmed"
              type="checkbox"
              checked={confirmed}
              onChange={(event: ChangeEvent<HTMLInputElement>) => setConfirmed(event.target.checked)}
            />
            Ich bin der Rechnungsaussteller und bestätige, dass diese Angaben stimmen.
          </label>
          <div className="auth-form__actions">
            <button className="btn btn--primary" type="submit" disabled={loading || !confirmed}>
              E-Rechnung prüfen
            </button>
          </div>
        </form>
      ) : null}

      {result ? <BuildResult result={result} /> : null}
        </>
      ) : !sessionReady ? (
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
      ) : (
        <p className="status status--error" role="alert">
          Kein Zugriff.
        </p>
      )}
      <SiteFooter />
    </main>
  )
}

function BuildResult({ result }: { result: IssueBuildResponse }): JSX.Element {
  return (
    <section aria-live="polite">
      <p>{result.message}</p>
      <IssueList issues={result.blocking_issues} />
      <ul className="issue-artifacts">
        {result.artifacts.map((artifact: IssueArtifact) => (
          <li key={artifact.format}>
            <strong>{ARTIFACT_LABELS[artifact.format]}</strong>
            {artifact.download_allowed && artifact.content_base64 ? (
              <button
                className="btn btn--primary"
                type="button"
                onClick={() => saveArtifact(artifact)}
              >
                {artifact.filename} herunterladen
              </button>
            ) : (
              <p>Download geschlossen.</p>
            )}
            <IssueList issues={artifact.validation_issues} />
          </li>
        ))}
      </ul>
    </section>
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
  onChange,
}: {
  title: string
  idPrefix: string
  party: IssueParty
  showPayment: boolean
  onChange: (party: IssueParty) => void
}): JSX.Element {
  function setField(key: keyof IssueParty, value: string): void {
    onChange({ ...party, [key]: emptyToNull(value) })
  }

  function setAddress(key: keyof IssueAddress, value: string): void {
    onChange({ ...party, address: { ...party.address, [key]: emptyToNull(value) } })
  }

  return (
    <fieldset>
      <legend>{title}</legend>
      <TextField id={`${idPrefix}-name`} label="Name" value={party.name} onChange={(value) => setField('name', value)} />
      <TextField
        id={`${idPrefix}-line`}
        label="Straße"
        value={party.address.line}
        onChange={(value) => setAddress('line', value)}
      />
      <TextField
        id={`${idPrefix}-postcode`}
        label="PLZ"
        value={party.address.postcode}
        onChange={(value) => setAddress('postcode', value)}
      />
      <TextField
        id={`${idPrefix}-city`}
        label="Ort"
        value={party.address.city}
        onChange={(value) => setAddress('city', value)}
      />
      <TextField
        id={`${idPrefix}-country`}
        label="Land"
        value={party.address.country}
        onChange={(value) => setAddress('country', value)}
      />
      {showPayment ? (
        <>
          <TextField
            id={`${idPrefix}-vat`}
            label="USt-IdNr."
            value={party.vat_id}
            onChange={(value) => setField('vat_id', value)}
          />
          <TextField
            id={`${idPrefix}-iban`}
            label="IBAN"
            value={party.iban}
            onChange={(value) => setField('iban', value)}
          />
          <TextField
            id={`${idPrefix}-contact`}
            label="Ansprechpartner"
            value={party.contact_name}
            onChange={(value) => setField('contact_name', value)}
          />
          <TextField
            id={`${idPrefix}-phone`}
            label="Telefon"
            value={party.phone}
            onChange={(value) => setField('phone', value)}
          />
          <TextField
            id={`${idPrefix}-email`}
            label="E-Mail"
            value={party.email}
            onChange={(value) => setField('email', value)}
          />
        </>
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
}: {
  id: string
  label: string
  value: string | null
  onChange: (value: string) => void
  type?: 'text' | 'date'
}): JSX.Element {
  return (
    <>
      <label htmlFor={id}>{label}</label>
      <input id={id} type={type} value={value ?? ''} onChange={(event) => onChange(event.target.value)} />
    </>
  )
}

function emptyToNull(value: string): string | null {
  const trimmed: string = value.trim()
  return trimmed === '' ? null : trimmed
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

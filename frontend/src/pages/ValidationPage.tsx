import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { parseInvoice } from '../api/client'
import { FileUpload } from '../components/FileUpload'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { publicPageByPath, type PublicPage, type PublicPageLink } from '../content/publicPages'
import {
  classifyEInvoice,
  classifyKosit,
  eInvoiceFormatLabel,
  type EInvoiceCheckResult,
  type KositCheckResult,
} from '../einvoiceCheck'
import { AppLink } from '../navigation'
import type { AppRoute } from '../routing'
import type { InvoiceParseResponse, MeResponse, ValidationIssue } from '../types/invoice'

const NETWORK_ERROR_MESSAGE: string =
  'Der Dienst ist momentan nicht erreichbar. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.'

const PAGE_PATH: string = '/erechnung-validation'

type ValidationPageProps = {
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function ValidationPage({
  onNavigate,
  session,
  onLogout,
}: ValidationPageProps): JSX.Element {
  const page: PublicPage | null = publicPageByPath(PAGE_PATH)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<InvoiceParseResponse | null>(null)
  const inFlightRef: RefObject<boolean> = useRef<boolean>(false)
  const feedbackRef: RefObject<HTMLElement | null> = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (loading || (error === null && result === null)) {
      return
    }
    feedbackRef.current?.focus()
  }, [loading, error, result])

  async function handleFile(file: File): Promise<void> {
    if (inFlightRef.current) {
      return
    }
    inFlightRef.current = true
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response: InvoiceParseResponse = await parseInvoice(file)
      setResult(response)
    } catch (err: unknown) {
      const message: string = err instanceof Error ? err.message : NETWORK_ERROR_MESSAGE
      setError(message === 'Failed to fetch' ? NETWORK_ERROR_MESSAGE : message)
    } finally {
      inFlightRef.current = false
      setLoading(false)
    }
  }

  return (
    <main id="main-content" className="page" tabIndex={-1} aria-busy={loading}>
      <header className="page__header">
        <div className="page__header-row">
          <AppLink href="/" className="page__home">
            Startseite
          </AppLink>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>{page?.h1 ?? 'eRechnung validation'}</h1>
        <p className="page__lead">
          {page?.description ??
            'Prüfen, ob eine Datei eine E-Rechnung ist und ob KoSIT sie akzeptiert.'}
        </p>
      </header>

      {page?.paragraphs.map((paragraph: string, index: number) => (
        <p key={`${PAGE_PATH}-p-${index}`}>{paragraph}</p>
      ))}

      <FileUpload
        onFileSelected={(file: File) => {
          void handleFile(file)
        }}
        disabled={loading}
        title="Eine Rechnung hier ablegen"
        hint="oder Datei auswählen (.xml / .pdf) — genau eine Datei"
      />

      {loading ? (
        <div className="progress" role="status" aria-live="polite" aria-busy="true">
          <div className="progress__track" aria-hidden="true">
            <div className="progress__bar" />
          </div>
          <p className="progress__label">Datei wird geprüft… Bitte warten.</p>
        </div>
      ) : null}

      {error !== null ? (
        <section
          className="status status--error"
          role="alert"
          tabIndex={-1}
          ref={(node: HTMLElement | null) => {
            feedbackRef.current = node
          }}
        >
          <p>{error}</p>
        </section>
      ) : null}

      {result !== null ? <CheckResult invoice={result} feedbackRef={feedbackRef} /> : null}

      {page?.links && page.links.length > 0 ? (
        <ul>
          {page.links.map((link: PublicPageLink) => (
            <li key={link.href}>
              <AppLink href={link.href}>{link.label}</AppLink>
            </li>
          ))}
        </ul>
      ) : null}

      <SiteFooter />
    </main>
  )
}

type CheckResultProps = {
  invoice: InvoiceParseResponse
  feedbackRef: RefObject<HTMLElement | null>
}

type CheckTone = 'ok' | 'warn' | 'error'

function CheckResult({ invoice, feedbackRef }: CheckResultProps): JSX.Element {
  const verdict: EInvoiceCheckResult = classifyEInvoice(invoice)
  const kosit: KositCheckResult = classifyKosit(invoice)
  const tone: CheckTone = resultTone(verdict, kosit)
  const finding: ValidationIssue | null = kosit === 'not_conform' ? primaryKositIssue(invoice) : null
  const issues: ValidationIssue[] = invoice.validation_issues.filter(
    (issue: ValidationIssue): boolean => issue.code !== 'KOSIT_OK' && issue !== finding,
  )
  const showMessage: boolean = finding === null && (verdict !== 'einvoice' || kosit !== 'conform')
  return (
    <section
      className={`check-result check-result--${tone}`}
      role="status"
      tabIndex={-1}
      ref={(node: HTMLElement | null) => {
        feedbackRef.current = node
      }}
    >
      {invoice.filename ? <p className="check-result__file">{invoice.filename}</p> : null}
      <h2 className="check-result__title">{verdictHeadline(verdict)}</h2>
      <ul className="check-result__checks">
        <li>
          <span className="check-result__label">Format</span>
          <span className="check-result__value">{formatValue(verdict, invoice.file_type)}</span>
          <span className={`badge ${badgeClass(verdictTone(verdict))}`}>{formatBadge(verdict)}</span>
        </li>
        <li>
          <span className="check-result__label">KoSIT</span>
          <span className="check-result__value">{kositValue(kosit, verdict, invoice, finding)}</span>
          <span className={`badge ${badgeClass(kositTone(kosit))}`}>{kositBadge(kosit)}</span>
        </li>
      </ul>
      {showMessage ? <p className="check-result__note">{invoice.message}</p> : null}
      {issues.length > 0 ? (
        <ul className="check-result__issues">
          {issues.map((issue: ValidationIssue, index: number) => (
            <li key={`${issue.code ?? 'issue'}-${index}`}>{issue.message}</li>
          ))}
        </ul>
      ) : null}
    </section>
  )
}

function resultTone(verdict: EInvoiceCheckResult, kosit: KositCheckResult): CheckTone {
  if (verdict !== 'einvoice' || kosit === 'not_conform') {
    return 'error'
  }
  if (kosit === 'not_checked') {
    return 'warn'
  }
  return 'ok'
}

function verdictTone(verdict: EInvoiceCheckResult): CheckTone {
  if (verdict === 'einvoice') {
    return 'ok'
  }
  if (verdict === 'not_einvoice') {
    return 'error'
  }
  return 'warn'
}

function formatBadge(verdict: EInvoiceCheckResult): string {
  if (verdict === 'einvoice') {
    return 'Ja'
  }
  if (verdict === 'not_einvoice') {
    return 'Nein'
  }
  return 'Unklar'
}

function formatValue(verdict: EInvoiceCheckResult, fileType: string | null): string {
  if (verdict === 'einvoice') {
    return eInvoiceFormatLabel(fileType)
  }
  return 'Kein E-Rechnungsformat'
}

function kositTone(kosit: KositCheckResult): CheckTone {
  if (kosit === 'conform') {
    return 'ok'
  }
  if (kosit === 'not_conform') {
    return 'error'
  }
  return 'warn'
}

function kositBadge(kosit: KositCheckResult): string {
  if (kosit === 'conform') {
    return 'Entspricht'
  }
  if (kosit === 'not_conform') {
    return 'Entspricht nicht'
  }
  return 'Nicht geprüft'
}

function primaryKositIssue(invoice: InvoiceParseResponse): ValidationIssue | null {
  const errors: ValidationIssue[] = invoice.validation_issues.filter(
    (issue: ValidationIssue): boolean => issue.level === 'error' && issue.code !== 'KOSIT_OK',
  )
  const named: ValidationIssue | undefined = errors.find(
    (issue: ValidationIssue): boolean =>
      issue.code === 'KOSIT_NO_SCENARIO' || issue.code === 'KOSIT_FAILED',
  )
  return named ?? errors[0] ?? null
}

function kositValue(
  kosit: KositCheckResult,
  verdict: EInvoiceCheckResult,
  invoice: InvoiceParseResponse,
  finding: ValidationIssue | null,
): string {
  if (kosit === 'conform') {
    const parts: string[] = []
    const version: string | null = invoice.validation_meta.engine_version
    const scenarios: string | null = invoice.validation_meta.scenarios_version
    if (version) {
      parts.push(`Validator ${version}`)
    }
    if (scenarios) {
      parts.push(scenarios)
    }
    return parts.length > 0 ? parts.join(' · ') : 'Offizielle Prüfung abgeschlossen'
  }
  if (kosit === 'not_conform') {
    return finding?.message ?? 'Prüfregeln nicht erfüllt'
  }
  if (verdict === 'einvoice') {
    return 'Prüfung nicht ausgeführt'
  }
  return 'Nur für E-Rechnungen'
}

function badgeClass(tone: CheckTone): string {
  if (tone === 'ok') {
    return 'badge--ok'
  }
  if (tone === 'error') {
    return 'badge--error'
  }
  return 'badge--warn'
}

function verdictHeadline(verdict: EInvoiceCheckResult): string {
  if (verdict === 'einvoice') {
    return 'Ja. Das ist eine E-Rechnung.'
  }
  if (verdict === 'not_einvoice') {
    return 'Nein. Das ist keine E-Rechnung.'
  }
  return 'Die Datei konnte nicht als E-Rechnung gelesen werden.'
}

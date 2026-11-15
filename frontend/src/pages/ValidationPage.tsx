import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { parseInvoice } from '../api/client'
import { FileUpload } from '../components/FileUpload'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { publicPageByPath, type PublicPage, type PublicPageLink } from '../content/publicPages'
import {
  classifyEInvoice,
  eInvoiceFormatLabel,
  validationStatusLabel,
  type EInvoiceCheckResult,
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
            ← eInvoice
          </AppLink>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>{page?.h1 ?? 'eRechnung validation'}</h1>
        <p className="page__lead">
          {page?.description ??
            'Eine Datei hochladen und prüfen, ob es eine E-Rechnung ist.'}
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

function CheckResult({ invoice, feedbackRef }: CheckResultProps): JSX.Element {
  const verdict: EInvoiceCheckResult = classifyEInvoice(invoice)
  const className: string =
    verdict === 'einvoice' ? 'status status--info' : 'status status--error'
  return (
    <section
      className={className}
      role="status"
      tabIndex={-1}
      ref={(node: HTMLElement | null) => {
        feedbackRef.current = node
      }}
    >
      {invoice.filename ? <p className="status__file">Datei: {invoice.filename}</p> : null}
      <p>
        <strong>{verdictHeadline(verdict)}</strong>
      </p>
      {verdict === 'einvoice' ? (
        <p>Format: {eInvoiceFormatLabel(invoice.file_type)}</p>
      ) : null}
      {verdict === 'einvoice' ? <p>{validationStatusLabel(invoice.validation_status)}</p> : null}
      <p>{invoice.message}</p>
      {invoice.validation_issues.map((issue: ValidationIssue, index: number) => (
        <p key={`${issue.code ?? 'issue'}-${index}`}>{issue.message}</p>
      ))}
    </section>
  )
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

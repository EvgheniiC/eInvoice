import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { checkHealth, fetchCapabilities, parseInvoice, recordFunnel } from '../api/client'
import { FileUpload } from '../components/FileUpload'
import { InvoiceView } from '../components/InvoiceView'
import { PageNav } from '../components/PageNav'
import { PdfPreview } from '../components/PdfPreview'
import { SiteFooter } from '../components/SiteFooter'
import { DEFAULT_CAPABILITIES, formatLimitsLine } from '../content/capabilities'
import type { AppRoute } from '../routing'
import type {
  CapabilitiesResponse,
  HealthResponse,
  InvoiceParseResponse,
  MeResponse,
  ValidationIssue,
} from '../types/invoice'

const NETWORK_ERROR_MESSAGE: string =
  'Der Dienst ist momentan nicht erreichbar. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.'

type UploadPageProps = {
  onNavigateHome: () => void
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function UploadPage({
  onNavigateHome,
  onNavigate,
  session,
  onLogout,
}: UploadPageProps): JSX.Element {
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [result, setResult] = useState<InvoiceParseResponse | null>(null)
  const [showPdf, setShowPdf] = useState<boolean>(true)
  const [announcement, setAnnouncement] = useState<string>('')
  const [capabilities, setCapabilities] = useState<CapabilitiesResponse>(DEFAULT_CAPABILITIES)
  const [kositDegraded, setKositDegraded] = useState<boolean>(false)
  const inFlightRef: RefObject<boolean> = useRef<boolean>(false)
  const feedbackRef: RefObject<HTMLElement | null> = useRef<HTMLElement | null>(null)

  function bindFeedback(node: HTMLElement | null): void {
    feedbackRef.current = node
  }

  useEffect(() => {
    recordFunnel('upload')
    void fetchCapabilities().then((value: CapabilitiesResponse) => {
      setCapabilities(value)
    })
    void checkHealth()
      .then((health: HealthResponse) => {
        setKositDegraded(health.kosit_required && !health.kosit_ready)
      })
      .catch(() => {
        setKositDegraded(false)
      })
  }, [])

  useEffect(() => {
    if (loading || (!error && !result)) {
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
    setUploadedFile(file)
    setSelectedFilename(file.name)
    setShowPdf(true)
    setAnnouncement(`Datei ${file.name} wird gelesen und geprüft. Bitte warten.`)
    try {
      const response: InvoiceParseResponse = await parseInvoice(file)
      setResult(response)
      if (response.status === 'error') {
        setAnnouncement(response.message)
      } else {
        setAnnouncement(`Rechnung ${file.name} wurde gelesen.`)
      }
    } catch (err: unknown) {
      const message: string =
        err instanceof TypeError
          ? NETWORK_ERROR_MESSAGE
          : err instanceof Error
            ? err.message
            : 'Die Datei konnte nicht verarbeitet werden. Bitte versuchen Sie es erneut.'
      setError(message)
      setAnnouncement(message)
    } finally {
      inFlightRef.current = false
      setLoading(false)
    }
  }

  const canShowPdfSideBySide: boolean =
    result !== null &&
    result.status !== 'error' &&
    result.file_type === 'zugferd_pdf' &&
    uploadedFile !== null

  const pageClassName: string =
    canShowPdfSideBySide && showPdf ? 'page page--split' : 'page'

  return (
    <main id="main-content" className={pageClassName} tabIndex={-1} aria-busy={loading}>
      <div className="visually-hidden" aria-live="polite" aria-atomic="true">
        {announcement}
      </div>
      <header className="page__header">
        <div className="page__header-row">
          <button type="button" className="page__home" onClick={onNavigateHome}>
            ← eInvoice
          </button>
          <PageNav onNavigate={onNavigate} session={session} onLogout={onLogout} />
        </div>
        <h1 tabIndex={-1}>Rechnung empfangen</h1>
        <p className="page__lead">
          XRechnung-XML oder ZUGFeRD-PDF hochladen — lesbare Ansicht der Rechnungsdaten.
        </p>
        <p id="upload-limits" className="page__limits">
          {formatLimitsLine(capabilities)}
        </p>
      </header>

      {kositDegraded ? (
        <section className="banner banner--warn" role="status">
          <p>
            <strong>Vollprüfung gerade nicht verfügbar.</strong> Der offizielle KoSIT-Validator
            ist nicht erreichbar. Die Datei wird trotzdem gelesen; sie wird nicht als gültig
            gekennzeichnet. Bitte später erneut prüfen oder den Lieferanten um eine korrekte
            XRechnung bitten.
          </p>
        </section>
      ) : null}

      <FileUpload onFileSelected={handleFile} disabled={loading} describedBy="upload-limits" />

      {loading && (
        <div className="progress" role="status" aria-live="polite" aria-busy="true">
          <div className="progress__track" aria-hidden="true">
            <div className="progress__bar" />
          </div>
          <p className="progress__label">Datei wird gelesen und geprüft… Bitte warten.</p>
        </div>
      )}
      {error && (
        <section
          className="status status--error"
          role="alert"
          tabIndex={-1}
          ref={bindFeedback}
        >
          {selectedFilename && <p className="status__file">Datei: {selectedFilename}</p>}
          <p>{error}</p>
          <p>
            <strong>Nächster Schritt:</strong> Datei prüfen oder erneut hochladen. Bleibt das
            Problem bestehen, versuchen Sie es später erneut.
          </p>
        </section>
      )}

      {canShowPdfSideBySide && (
        <div className="pdf-toggle">
          <button
            type="button"
            aria-pressed={showPdf}
            onClick={() => setShowPdf((prev: boolean) => !prev)}
          >
            {showPdf ? 'PDF ausblenden' : 'PDF neben Daten anzeigen'}
          </button>
          <p className="pdf-toggle__hint">
            ZUGFeRD: visuelle PDF neben den aus dem XML gelesenen Daten — hilfreich bei Abweichungen.
          </p>
        </div>
      )}

      {result && result.status !== 'error' && canShowPdfSideBySide && showPdf && uploadedFile && (
        <div className="invoice-split" ref={bindFeedback} tabIndex={-1}>
          <div className="invoice-split__pdf">
            <PdfPreview file={uploadedFile} title="Visuelle PDF" />
          </div>
          <div className="invoice-split__data">
            <InvoiceView invoice={result} sourceFile={uploadedFile} />
          </div>
        </div>
      )}

      {result && result.status !== 'error' && !(canShowPdfSideBySide && showPdf) && (
        <div ref={bindFeedback} tabIndex={-1}>
          <InvoiceView invoice={result} sourceFile={uploadedFile} />
        </div>
      )}

      {result && result.status === 'error' && (
        <section
          className="status status--error"
          role="alert"
          tabIndex={-1}
          ref={bindFeedback}
        >
          {result.filename && <p className="status__file">Datei: {result.filename}</p>}
          <p>
            <strong>{result.message}</strong>
          </p>
          {result.validation_issues.map((issue: ValidationIssue, index: number) => (
            <p key={`${issue.code ?? 'err'}-${index}`}>{issue.message}</p>
          ))}
          {result.next_steps.length > 0 && (
            <div>
              <strong>Was tun als Nächstes?</strong>
              <ol>
                {result.next_steps.map((step: string, index: number) => (
                  <li key={`error-step-${index}`}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </section>
      )}

      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}

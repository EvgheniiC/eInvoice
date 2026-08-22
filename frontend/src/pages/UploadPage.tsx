import { useEffect, useRef, useState, type JSX, type RefObject } from 'react'
import { checkHealth, createInvoiceBatch, downloadBatchAccountantPackage, fetchBatchJob, fetchCapabilities, parseInvoice, recordFunnel } from '../api/client'
import { BatchSummary } from '../components/BatchSummary'
import { FileUpload } from '../components/FileUpload'
import { InvoiceView } from '../components/InvoiceView'
import { PageNav } from '../components/PageNav'
import { PdfPreview } from '../components/PdfPreview'
import { SiteFooter } from '../components/SiteFooter'
import { DEFAULT_CAPABILITIES, formatUploadLimitsLine } from '../content/capabilities'
import type { AppRoute } from '../routing'
import type {
  BatchItemResponse,
  BatchJobResponse,
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
  const [batchJob, setBatchJob] = useState<BatchJobResponse | null>(null)
  const [selectedBatchItemId, setSelectedBatchItemId] = useState<string | null>(null)
  const [showPdf, setShowPdf] = useState<boolean>(true)
  const [announcement, setAnnouncement] = useState<string>('')
  const [capabilities, setCapabilities] = useState<CapabilitiesResponse>(DEFAULT_CAPABILITIES)
  const [kositDegraded, setKositDegraded] = useState<boolean>(false)
  const [packageDownloading, setPackageDownloading] = useState<boolean>(false)
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
    if (loading || (!error && !result) || batchJob !== null) {
      return
    }
    feedbackRef.current?.focus()
  }, [loading, error, result, batchJob])

  useEffect(() => {
    if (batchJob === null || batchJob.status === 'completed') {
      return
    }
    const jobId: string = batchJob.id
    let cancelled: boolean = false
    const timer: number = window.setInterval((): void => {
      void fetchBatchJob(jobId)
        .then((next: BatchJobResponse) => {
          if (!cancelled) {
            setBatchJob(next)
          }
        })
        .catch(() => {
          return
        })
    }, 2000)
    return (): void => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [batchJob?.id, batchJob?.status])

  useEffect(() => {
    if (batchJob === null || selectedBatchItemId !== null) {
      return
    }
    const firstReady: BatchItemResponse | undefined = batchJob.items.find(
      (item: BatchItemResponse): boolean => item.invoice !== null && item.invoice !== undefined,
    )
    if (firstReady === undefined || firstReady.invoice === undefined || firstReady.invoice === null) {
      return
    }
    const readyInvoice: InvoiceParseResponse = firstReady.invoice
    setSelectedBatchItemId(firstReady.id)
    setResult(readyInvoice)
    setUploadedFile(null)
    setShowPdf(false)
    setAnnouncement(`Rechnung ${firstReady.filename} geöffnet.`)
  }, [batchJob, selectedBatchItemId])

  async function handleFile(file: File): Promise<void> {
    if (inFlightRef.current) {
      return
    }
    inFlightRef.current = true
    setLoading(true)
    setError(null)
    setResult(null)
    setBatchJob(null)
    setSelectedBatchItemId(null)
    setPackageDownloading(false)
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

  async function handleFiles(files: File[]): Promise<void> {
    if (files.length === 1 && !isZipFile(files[0])) {
      await handleFile(files[0])
      return
    }
    await handleBatch(files)
  }

  async function handleBatch(files: File[]): Promise<void> {
    if (inFlightRef.current) {
      return
    }
    inFlightRef.current = true
    setLoading(true)
    setError(null)
    setResult(null)
    setUploadedFile(null)
    setSelectedFilename(`${String(files.length)} Dateien`)
    setSelectedBatchItemId(null)
    setPackageDownloading(false)
    setAnnouncement(`${String(files.length)} Dateien werden in die Prüfungswarteschlange gelegt.`)
    try {
      const created: BatchJobResponse = await createInvoiceBatch(files)
      setBatchJob(created)
      setAnnouncement(`${String(created.item_count)} Dateien in der Warteschlange.`)
    } catch (err: unknown) {
      const message: string =
        err instanceof TypeError
          ? NETWORK_ERROR_MESSAGE
          : err instanceof Error
            ? err.message
            : 'Die Dateien konnten nicht verarbeitet werden. Bitte versuchen Sie es erneut.'
      setError(message)
      setAnnouncement(message)
    } finally {
      inFlightRef.current = false
      setLoading(false)
    }
  }

  function openBatchItem(item: BatchItemResponse): void {
    if (!item.invoice) {
      return
    }
    setSelectedBatchItemId(item.id)
    setResult(item.invoice)
    setUploadedFile(null)
    setShowPdf(false)
    setAnnouncement(`Rechnung ${item.filename} geöffnet.`)
  }

  async function handleDownloadPackage(): Promise<void> {
    if (batchJob === null || packageDownloading) {
      return
    }
    setPackageDownloading(true)
    setError(null)
    setAnnouncement('Buchhaltungspaket wird erstellt.')
    try {
      await downloadBatchAccountantPackage(batchJob.id)
      setAnnouncement('Buchhaltungspaket wurde heruntergeladen.')
    } catch (err: unknown) {
      const message: string =
        err instanceof TypeError
          ? NETWORK_ERROR_MESSAGE
          : err instanceof Error
            ? err.message
            : 'Das Paket konnte nicht erstellt werden. Bitte versuchen Sie es erneut.'
      setError(message)
      setAnnouncement(message)
    } finally {
      setPackageDownloading(false)
    }
  }

  const allowsBatch: boolean = Boolean(session?.plan.allows_batch)
  const hasBatchWorkspace: boolean = batchJob !== null

  const canShowPdfSideBySide: boolean =
    result !== null &&
    result.status !== 'error' &&
    result.file_type === 'zugferd_pdf' &&
    uploadedFile !== null

  const pageClassName: string =
    canShowPdfSideBySide && showPdf
      ? 'page page--split'
      : hasBatchWorkspace
        ? 'page page--workspace'
        : 'page'

  function renderInvoicePanel(): JSX.Element | null {
    if (result === null) {
      return null
    }
    if (result.status === 'error') {
      return (
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
      )
    }
    if (canShowPdfSideBySide && showPdf && uploadedFile !== null) {
      return (
        <div className="invoice-split" ref={bindFeedback} tabIndex={-1}>
          <div className="invoice-split__pdf">
            <PdfPreview file={uploadedFile} title="Visuelle PDF" />
          </div>
          <div className="invoice-split__data">
            <InvoiceView invoice={result} sourceFile={uploadedFile} />
          </div>
        </div>
      )
    }
    return (
      <div ref={bindFeedback} tabIndex={-1}>
        <InvoiceView invoice={result} sourceFile={uploadedFile} />
      </div>
    )
  }

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
          {formatUploadLimitsLine(capabilities, session?.plan ?? null)}
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

      <FileUpload
        onFileSelected={allowsBatch ? undefined : handleFile}
        onFilesSelected={allowsBatch ? handleFiles : undefined}
        multiple={allowsBatch}
        disabled={loading}
        describedBy="upload-limits"
        title={
          allowsBatch
            ? 'Mehrere XRechnung-XML, ZUGFeRD-PDF oder ein ZIP hier ablegen'
            : 'XRechnung XML oder ZUGFeRD PDF hier ablegen'
        }
        hint={
          allowsBatch
            ? 'oder Dateien auswählen (.xml / .pdf / .zip)'
            : 'oder Datei auswählen (.xml / .pdf)'
        }
      />

      {session !== null && !allowsBatch ? (
        <p className="page__limits">
          Mehrere Dateien auf einmal sind in Plus enthalten. Dieser Tarif prüft eine Datei pro
          Vorgang.
        </p>
      ) : null}

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

      {hasBatchWorkspace && batchJob !== null ? (
        <div className="workspace-split">
          <aside className="workspace-split__files" aria-label="Geprüfte Dateien">
            <BatchSummary
              job={batchJob}
              selectedItemId={selectedBatchItemId}
              onSelectItem={openBatchItem}
              onDownloadPackage={() => {
                void handleDownloadPackage()
              }}
              packageDownloading={packageDownloading}
            />
          </aside>
          <section className="workspace-split__detail" aria-label="Rechnungsdaten">
            {renderInvoicePanel() ?? (
              <p className="workspace-split__placeholder">
                Datei in der Liste wählen, um die Rechnungsdaten zu sehen.
              </p>
            )}
          </section>
        </div>
      ) : (
        <>
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
                ZUGFeRD: visuelle PDF neben den aus dem XML gelesenen Daten — hilfreich bei
                Abweichungen.
              </p>
            </div>
          )}
          {renderInvoicePanel()}
        </>
      )}

      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}

function isZipFile(file: File): boolean {
  if (file.type === 'application/zip' || file.type === 'application/x-zip-compressed') {
    return true
  }
  return file.name.toLowerCase().endsWith('.zip')
}

import { useState, type JSX } from 'react'
import { parseInvoice } from '../api/client'
import { FileUpload } from '../components/FileUpload'
import { InvoiceView } from '../components/InvoiceView'
import { PdfPreview } from '../components/PdfPreview'
import type { InvoiceParseResponse } from '../types/invoice'

const NETWORK_ERROR_MESSAGE: string =
  'Der Dienst ist momentan nicht erreichbar. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.'

type UploadPageProps = {
  onNavigateHome: () => void
}

export function UploadPage({ onNavigateHome }: UploadPageProps): JSX.Element {
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [result, setResult] = useState<InvoiceParseResponse | null>(null)
  const [showPdf, setShowPdf] = useState<boolean>(true)

  async function handleFile(file: File): Promise<void> {
    setLoading(true)
    setError(null)
    setResult(null)
    setUploadedFile(file)
    setSelectedFilename(file.name)
    setShowPdf(true)
    try {
      const response: InvoiceParseResponse = await parseInvoice(file)
      setResult(response)
    } catch (err: unknown) {
      const message: string =
        err instanceof TypeError
          ? NETWORK_ERROR_MESSAGE
          : err instanceof Error
            ? err.message
            : 'Die Datei konnte nicht verarbeitet werden. Bitte versuchen Sie es erneut.'
      setError(message)
    } finally {
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
    <main className={pageClassName}>
      <header className="page__header">
        <button type="button" className="page__home" onClick={onNavigateHome}>
          ← eInvoice
        </button>
        <h1>Rechnung empfangen</h1>
        <p className="page__lead">
          XRechnung-XML oder ZUGFeRD-PDF hochladen — lesbare Ansicht der Rechnungsdaten.
        </p>
        <p className="page__limits">
          Eine Datei bis 10 MB · UBL Invoice/CreditNote, UN/CEFACT CII oder ZUGFeRD/Factur-X
        </p>
      </header>

      <FileUpload onFileSelected={handleFile} disabled={loading} />

      {loading && <p className="status status--info">Datei wird verarbeitet…</p>}
      {error && (
        <section className="status status--error" aria-live="polite">
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
          <button type="button" onClick={() => setShowPdf((prev: boolean) => !prev)}>
            {showPdf ? 'PDF ausblenden' : 'PDF neben Daten anzeigen'}
          </button>
          <p className="pdf-toggle__hint">
            ZUGFeRD: visuelle PDF neben den aus dem XML gelesenen Daten — hilfreich bei Abweichungen.
          </p>
        </div>
      )}

      {result && result.status !== 'error' && canShowPdfSideBySide && showPdf && uploadedFile && (
        <div className="invoice-split">
          <div className="invoice-split__pdf">
            <PdfPreview file={uploadedFile} title="Visuelle PDF" />
          </div>
          <div className="invoice-split__data">
            <InvoiceView invoice={result} sourceFile={uploadedFile} />
          </div>
        </div>
      )}

      {result && result.status !== 'error' && !(canShowPdfSideBySide && showPdf) && (
        <InvoiceView invoice={result} sourceFile={uploadedFile} />
      )}

      {result && result.status === 'error' && (
        <section className="status status--error" aria-live="polite">
          {result.filename && <p className="status__file">Datei: {result.filename}</p>}
          <p>
            <strong>{result.message}</strong>
          </p>
          {result.validation_issues.map((issue, index: number) => (
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

      <footer className="disclaimer">
        eInvoice unterstützt bei der technischen und inhaltlichen Prüfung, ersetzt aber keine
        Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug.
      </footer>
    </main>
  )
}

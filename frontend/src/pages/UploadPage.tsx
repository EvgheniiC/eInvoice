import { useState } from 'react'
import { parseInvoice } from '../api/client'
import { FileUpload } from '../components/FileUpload'
import { InvoiceView } from '../components/InvoiceView'
import type { InvoiceParseResponse } from '../types/invoice'

export function UploadPage() {
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)
  const [result, setResult] = useState<InvoiceParseResponse | null>(null)

  async function handleFile(file: File): Promise<void> {
    setLoading(true)
    setError(null)
    setResult(null)
    setSelectedFilename(file.name)
    try {
      const response: InvoiceParseResponse = await parseInvoice(file)
      setResult(response)
    } catch (err: unknown) {
      const message: string = err instanceof Error ? err.message : 'Unbekannter Fehler'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <header className="page__header">
        <p className="brand">eInvoice</p>
        <h1>Rechnung empfangen</h1>
        <p className="page__lead">
          XRechnung-XML oder ZUGFeRD-PDF hochladen — lesbare Ansicht der Rechnungsdaten.
        </p>
      </header>

      <FileUpload onFileSelected={handleFile} disabled={loading} />

      {loading && <p className="status status--info">Datei wird verarbeitet…</p>}
      {error && (
        <section className="status status--error" aria-live="polite">
          {selectedFilename && <p className="status__file">Datei: {selectedFilename}</p>}
          <p>{error}</p>
        </section>
      )}

      {result && result.status !== 'error' && <InvoiceView invoice={result} />}

      {result && result.status === 'error' && (
        <section className="status status--error" aria-live="polite">
          {result.filename && <p className="status__file">Datei: {result.filename}</p>}
          <p>
            <strong>{result.message}</strong>
          </p>
          {result.validation_issues.map((issue, index: number) => (
            <p key={`${issue.code ?? 'err'}-${index}`}>{issue.message}</p>
          ))}
        </section>
      )}

      <footer className="disclaimer">
        Die Prüfung betrifft Schema-/Standardkonformität. Die Entscheidung über den
        Vorsteuerabzug liegt bei Ihnen bzw. Ihrem Steuerberater.
      </footer>
    </main>
  )
}

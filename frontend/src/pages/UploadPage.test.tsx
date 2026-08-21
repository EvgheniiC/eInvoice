import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { checkHealth, createInvoiceBatch, fetchCapabilities, parseInvoice } from '../api/client'
import { DEFAULT_CAPABILITIES } from '../content/capabilities'
import { buildInvoice, buildSession } from '../test/fixtures'
import type { BatchJobResponse, HealthResponse, InvoiceParseResponse } from '../types/invoice'
import { UploadPage } from './UploadPage'

vi.mock('../api/client', (): {
  parseInvoice: ReturnType<typeof vi.fn>
  createInvoiceBatch: ReturnType<typeof vi.fn>
  fetchBatchJob: ReturnType<typeof vi.fn>
  exportInvoice: ReturnType<typeof vi.fn>
  downloadAccountantPackage: ReturnType<typeof vi.fn>
  downloadValidationReport: ReturnType<typeof vi.fn>
  fetchCapabilities: ReturnType<typeof vi.fn>
  checkHealth: ReturnType<typeof vi.fn>
  recordFunnel: ReturnType<typeof vi.fn>
} => ({
  parseInvoice: vi.fn(),
  createInvoiceBatch: vi.fn(),
  fetchBatchJob: vi.fn(),
  exportInvoice: vi.fn(),
  downloadAccountantPackage: vi.fn(),
  downloadValidationReport: vi.fn(),
  fetchCapabilities: vi.fn(),
  checkHealth: vi.fn(),
  recordFunnel: vi.fn(),
}))

describe('UploadPage', (): void => {
  const healthy: HealthResponse = {
    status: 'ok',
    ready: true,
    app_name: 'eInvoice API',
    version: '0.1.0',
    environment: 'test',
    kosit_required: false,
    kosit_ready: false,
    checks: [],
  }

  it('shows the parsed invoice after a successful upload', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const invoice: InvoiceParseResponse = buildInvoice()
    vi.mocked(parseInvoice).mockResolvedValue(invoice)
    vi.mocked(fetchCapabilities).mockResolvedValue(DEFAULT_CAPABILITIES)
    vi.mocked(checkHealth).mockResolvedValue(healthy)

    render(<UploadPage onNavigateHome={vi.fn()} onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)

    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    const file: File = new File(['<Invoice/>'], 'sample.xml', { type: 'text/xml' })
    await user.upload(input, file)

    expect(await screen.findByText('Kann verarbeitet werden')).toBeInTheDocument()
    expect(screen.getByText('2025/10294')).toBeInTheDocument()
    expect(parseInvoice).toHaveBeenCalledTimes(1)
  })

  it('shows a German network error when the API is unreachable', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(parseInvoice).mockRejectedValue(new TypeError('Failed to fetch'))
    vi.mocked(fetchCapabilities).mockResolvedValue(DEFAULT_CAPABILITIES)
    vi.mocked(checkHealth).mockResolvedValue(healthy)

    render(<UploadPage onNavigateHome={vi.fn()} onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)

    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    const file: File = new File(['<Invoice/>'], 'sample.xml', { type: 'text/xml' })
    await user.upload(input, file)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Der Dienst ist momentan nicht erreichbar. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.',
    )
  })

  it('queues several Plus files and shows the status table', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const invoice: InvoiceParseResponse = buildInvoice({ filename: 'one.xml' })
    const job: BatchJobResponse = {
      id: '00000000-0000-0000-0000-000000000099',
      status: 'queued',
      item_count: 2,
      done_count: 0,
      export_package_available: false,
      items: [
        {
          id: '00000000-0000-0000-0000-000000000011',
          filename: 'one.xml',
          status: 'queued',
          invoice_number: null,
          seller_name: null,
          gross_amount: null,
          currency: null,
          message: null,
          invoice: null,
        },
        {
          id: '00000000-0000-0000-0000-000000000012',
          filename: 'two.xml',
          status: 'queued',
          invoice_number: null,
          seller_name: null,
          gross_amount: null,
          currency: null,
          message: null,
          invoice: null,
        },
      ],
    }
    vi.mocked(createInvoiceBatch).mockResolvedValue(job)
    vi.mocked(fetchCapabilities).mockResolvedValue(DEFAULT_CAPABILITIES)
    vi.mocked(checkHealth).mockResolvedValue(healthy)

    render(
      <UploadPage
        onNavigateHome={vi.fn()}
        onNavigate={vi.fn()}
        session={buildSession({
          plan: {
            code: 'plus',
            name: 'Plus',
            parse_per_day: 100,
            export_per_day: 100,
            max_upload_size_mb: 25,
            max_parallel: 2,
            allows_batch: true,
            allows_history: true,
            max_batch_files: 20,
            quotas_enforced: true,
            parse_used_today: 0,
            export_used_today: 0,
          },
        })}
        onLogout={vi.fn()}
      />,
    )

    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    const first: File = new File(['<Invoice/>'], 'one.xml', { type: 'text/xml' })
    const second: File = new File(['<Invoice/>'], 'two.xml', { type: 'text/xml' })
    await user.upload(input, [first, second])

    expect(await screen.findByText('one.xml')).toBeInTheDocument()
    expect(screen.getByText('two.xml')).toBeInTheDocument()
    expect(screen.getByText('0 von 2 Dateien geprüft…')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ein ZIP für die Buchhaltung (folgt)' })).toBeDisabled()
    expect(createInvoiceBatch).toHaveBeenCalledTimes(1)
    expect(parseInvoice).not.toHaveBeenCalled()
    expect(invoice.filename).toBe('one.xml')
  })

  it('keeps a Free account on a single-file picker', async (): Promise<void> => {
    vi.mocked(fetchCapabilities).mockResolvedValue(DEFAULT_CAPABILITIES)
    vi.mocked(checkHealth).mockResolvedValue(healthy)

    render(
      <UploadPage
        onNavigateHome={vi.fn()}
        onNavigate={vi.fn()}
        session={buildSession()}
        onLogout={vi.fn()}
      />,
    )

    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    expect(input.multiple).toBe(false)
    expect(
      await screen.findByText(/Mehrere Dateien auf einmal sind in Plus enthalten/i),
    ).toBeInTheDocument()
  })
})

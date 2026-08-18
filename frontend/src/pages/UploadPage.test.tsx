import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { checkHealth, fetchCapabilities, parseInvoice } from '../api/client'
import { DEFAULT_CAPABILITIES } from '../content/capabilities'
import { buildInvoice } from '../test/fixtures'
import type { HealthResponse, InvoiceParseResponse } from '../types/invoice'
import { UploadPage } from './UploadPage'

vi.mock('../api/client', (): {
  parseInvoice: ReturnType<typeof vi.fn>
  exportInvoice: ReturnType<typeof vi.fn>
  downloadAccountantPackage: ReturnType<typeof vi.fn>
  downloadValidationReport: ReturnType<typeof vi.fn>
  fetchCapabilities: ReturnType<typeof vi.fn>
  checkHealth: ReturnType<typeof vi.fn>
  recordFunnel: ReturnType<typeof vi.fn>
} => ({
  parseInvoice: vi.fn(),
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

    render(<UploadPage onNavigateHome={vi.fn()} onNavigate={vi.fn()} />)

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

    render(<UploadPage onNavigateHome={vi.fn()} onNavigate={vi.fn()} />)

    const input: HTMLInputElement = document.querySelector('#invoice-file-input') as HTMLInputElement
    const file: File = new File(['<Invoice/>'], 'sample.xml', { type: 'text/xml' })
    await user.upload(input, file)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Der Dienst ist momentan nicht erreichbar. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.',
    )
  })
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { downloadHistoryAccountantPackage, fetchInvoiceHistory } from '../api/client'
import { buildSession } from '../test/fixtures'
import type { HistoryListResponse } from '../types/invoice'
import { HistoryPage } from './HistoryPage'

vi.mock('../api/client', (): {
  fetchInvoiceHistory: ReturnType<typeof vi.fn>
  downloadHistoryAccountantPackage: ReturnType<typeof vi.fn>
} => ({
  fetchInvoiceHistory: vi.fn(),
  downloadHistoryAccountantPackage: vi.fn(),
}))

function plusHistory(overrides: Partial<HistoryListResponse> = {}): HistoryListResponse {
  return {
    items: [
      {
        id: '00000000-0000-0000-0000-000000000099',
        processed_at: '2026-08-22T10:15:00+00:00',
        filename: 'one.xml',
        file_hash: 'a'.repeat(64),
        seller_name: 'Muster GmbH',
        invoice_number: 'RE-1',
        issue_date: '2026-08-22',
        gross_amount: '119.00',
        currency: 'EUR',
        status: 'gueltig',
        source: 'parse',
        original_available: true,
        original_expires_at: '2026-09-21T10:15:00+00:00',
      },
    ],
    total: 1,
    history_enabled: true,
    store_originals_enabled: true,
    original_retention_days: 30,
    ...overrides,
  }
}

describe('HistoryPage', (): void => {
  it('asks guests to sign in', (): void => {
    render(<HistoryPage onNavigate={vi.fn()} session={null} onLogout={vi.fn()} />)
    expect(screen.getByRole('heading', { name: 'Verlauf' })).toBeInTheDocument()
    expect(screen.getByText('Bitte zuerst anmelden.')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Anmelden' }).length).toBeGreaterThan(0)
  })

  it('points Plus users to org settings when history is off', async (): Promise<void> => {
    vi.mocked(fetchInvoiceHistory).mockResolvedValue(plusHistory({ items: [], total: 0, history_enabled: false }))
    render(
      <HistoryPage
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
    expect(await screen.findByText(/Der Verlauf ist ausgeschaltet/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Verlauf unter Organisation aktivieren' })).toBeInTheDocument()
  })

  it('lists metadata and downloads a retained package', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    vi.mocked(fetchInvoiceHistory).mockResolvedValue(plusHistory())
    vi.mocked(downloadHistoryAccountantPackage).mockResolvedValue()
    render(
      <HistoryPage
        onNavigate={vi.fn()}
        session={buildSession({
          history_enabled: true,
          store_originals_enabled: true,
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
    expect(await screen.findByText('Muster GmbH')).toBeInTheDocument()
    expect(screen.getByText('RE-1')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Paket' }))
    expect(downloadHistoryAccountantPackage).toHaveBeenCalledWith('00000000-0000-0000-0000-000000000099')
  })
})

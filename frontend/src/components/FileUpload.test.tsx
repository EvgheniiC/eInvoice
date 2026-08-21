import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { FileUpload } from './FileUpload'

describe('FileUpload', (): void => {
  it('notifies the parent when a file is chosen', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onFileSelected: (file: File) => void = vi.fn()
    render(<FileUpload onFileSelected={onFileSelected} />)

    const input: HTMLInputElement = screen.getByLabelText(
      /XRechnung XML oder ZUGFeRD PDF hier ablegen/i,
    )
    const file: File = new File(['<Invoice/>'], 'rechnung.xml', { type: 'text/xml' })
    await user.upload(input, file)

    expect(onFileSelected).toHaveBeenCalledTimes(1)
    expect(vi.mocked(onFileSelected).mock.calls[0][0].name).toBe('rechnung.xml')
  })

  it('does not accept files while disabled', (): void => {
    const onFileSelected: (file: File) => void = vi.fn()
    render(<FileUpload onFileSelected={onFileSelected} disabled />)

    const input: HTMLInputElement = screen.getByLabelText(
      /XRechnung XML oder ZUGFeRD PDF hier ablegen/i,
    )
    expect(input).toBeDisabled()
    expect(onFileSelected).not.toHaveBeenCalled()
  })

  it('notifies the parent with several files in batch mode', async (): Promise<void> => {
    const user: UserEvent = userEvent.setup()
    const onFilesSelected: (files: File[]) => void = vi.fn()
    render(
      <FileUpload
        multiple
        onFilesSelected={onFilesSelected}
        title="Mehrere XRechnung-XML oder ZUGFeRD-PDF hier ablegen"
        hint="oder Dateien auswählen (.xml / .pdf). ZIP folgt in einem nächsten Schritt."
      />,
    )

    const input: HTMLInputElement = screen.getByLabelText(
      /Mehrere XRechnung-XML oder ZUGFeRD-PDF hier ablegen/i,
    )
    const first: File = new File(['<Invoice/>'], 'one.xml', { type: 'text/xml' })
    const second: File = new File(['<Invoice/>'], 'two.xml', { type: 'text/xml' })
    await user.upload(input, [first, second])

    expect(onFilesSelected).toHaveBeenCalledTimes(1)
    const received: File[] = vi.mocked(onFilesSelected).mock.calls[0][0]
    expect(received.map((file: File): string => file.name)).toEqual(['one.xml', 'two.xml'])
  })
})

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
})

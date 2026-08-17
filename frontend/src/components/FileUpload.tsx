import { useState, type ChangeEvent, type DragEvent, type JSX } from 'react'

interface FileUploadProps {
  onFileSelected: (file: File) => void
  disabled?: boolean
  describedBy?: string
}

const ACCEPTED: string = '.xml,.pdf,application/xml,text/xml,application/pdf'
const INPUT_ID: string = 'invoice-file-input'
const TITLE_ID: string = 'invoice-file-title'
const HINT_ID: string = 'invoice-file-hint'

export function FileUpload({
  onFileSelected,
  disabled = false,
  describedBy,
}: FileUploadProps): JSX.Element {
  const [isDragging, setIsDragging] = useState<boolean>(false)

  function handleFiles(files: FileList | null): void {
    if (disabled || !files || files.length === 0) {
      return
    }
    onFileSelected(files[0])
  }

  function onDrop(event: DragEvent<HTMLLabelElement>): void {
    event.preventDefault()
    setIsDragging(false)
    handleFiles(event.dataTransfer.files)
  }

  function onBrowse(event: ChangeEvent<HTMLInputElement>): void {
    handleFiles(event.target.files)
    event.target.value = ''
  }

  const describedByIds: string = describedBy ? `${HINT_ID} ${describedBy}` : HINT_ID
  const className: string = [
    'upload-zone',
    isDragging ? 'upload-zone--active' : '',
    disabled ? 'upload-zone--disabled' : '',
  ]
    .filter((item: string): boolean => item.length > 0)
    .join(' ')

  return (
    <label
      className={className}
      aria-disabled={disabled}
      onDragOver={(event: DragEvent<HTMLLabelElement>) => {
        event.preventDefault()
        if (!disabled) {
          setIsDragging(true)
        }
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
    >
      <span id={TITLE_ID} className="upload-zone__title">
        XRechnung XML oder ZUGFeRD PDF hier ablegen
      </span>
      <span id={HINT_ID} className="upload-zone__hint">
        oder Datei auswählen (.xml / .pdf)
      </span>
      <input
        id={INPUT_ID}
        className="visually-hidden"
        type="file"
        accept={ACCEPTED}
        disabled={disabled}
        aria-labelledby={TITLE_ID}
        aria-describedby={describedByIds}
        onChange={onBrowse}
      />
    </label>
  )
}

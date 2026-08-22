import { useState, type ChangeEvent, type DragEvent, type JSX } from 'react'

interface FileUploadProps {
  onFileSelected?: (file: File) => void
  onFilesSelected?: (files: File[]) => void
  multiple?: boolean
  disabled?: boolean
  describedBy?: string
  title?: string
  hint?: string
}

const ACCEPTED_SINGLE: string = '.xml,.pdf,application/xml,text/xml,application/pdf'
const ACCEPTED_BATCH: string =
  '.xml,.pdf,.zip,application/xml,text/xml,application/pdf,application/zip'
const INPUT_ID: string = 'invoice-file-input'
const TITLE_ID: string = 'invoice-file-title'
const HINT_ID: string = 'invoice-file-hint'
const DEFAULT_TITLE: string = 'XRechnung XML oder ZUGFeRD PDF hier ablegen'
const DEFAULT_HINT: string = 'oder Datei auswählen (.xml / .pdf)'

export function FileUpload({
  onFileSelected,
  onFilesSelected,
  multiple = false,
  disabled = false,
  describedBy,
  title = DEFAULT_TITLE,
  hint = DEFAULT_HINT,
}: FileUploadProps): JSX.Element {
  const [isDragging, setIsDragging] = useState<boolean>(false)

  function handleFiles(files: FileList | null): void {
    if (disabled || !files || files.length === 0) {
      return
    }
    const list: File[] = Array.from(files)
    if (multiple && onFilesSelected) {
      onFilesSelected(list)
      return
    }
    if (onFileSelected) {
      onFileSelected(list[0])
    }
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
        {title}
      </span>
      <span id={HINT_ID} className="upload-zone__hint">
        {hint}
      </span>
      <input
        id={INPUT_ID}
        className="visually-hidden"
        type="file"
        accept={multiple ? ACCEPTED_BATCH : ACCEPTED_SINGLE}
        multiple={multiple}
        disabled={disabled}
        aria-labelledby={TITLE_ID}
        aria-describedby={describedByIds}
        onChange={onBrowse}
      />
    </label>
  )
}

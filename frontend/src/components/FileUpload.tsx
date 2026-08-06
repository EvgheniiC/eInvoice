import { useRef, useState, type ChangeEvent, type DragEvent } from 'react'

interface FileUploadProps {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

const ACCEPTED: string = '.xml,.pdf,application/xml,text/xml,application/pdf'

export function FileUpload({ onFileSelected, disabled = false }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState<boolean>(false)

  function handleFiles(files: FileList | null): void {
    if (!files || files.length === 0) {
      return
    }
    onFileSelected(files[0])
  }

  function onDrop(event: DragEvent<HTMLDivElement>): void {
    event.preventDefault()
    setIsDragging(false)
    if (disabled) {
      return
    }
    handleFiles(event.dataTransfer.files)
  }

  function onBrowse(event: ChangeEvent<HTMLInputElement>): void {
    handleFiles(event.target.files)
    event.target.value = ''
  }

  return (
    <div
      className={`upload-zone${isDragging ? ' upload-zone--active' : ''}${disabled ? ' upload-zone--disabled' : ''}`}
      onDragOver={(event: DragEvent<HTMLDivElement>) => {
        event.preventDefault()
        if (!disabled) {
          setIsDragging(true)
        }
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
      onClick={() => {
        if (!disabled) {
          inputRef.current?.click()
        }
      }}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if ((event.key === 'Enter' || event.key === ' ') && !disabled) {
          inputRef.current?.click()
        }
      }}
    >
      <p className="upload-zone__title">XRechnung XML oder ZUGFeRD PDF hier ablegen</p>
      <p className="upload-zone__hint">oder klicken zum Auswählen (.xml / .pdf)</p>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        hidden
        disabled={disabled}
        onChange={onBrowse}
      />
    </div>
  )
}

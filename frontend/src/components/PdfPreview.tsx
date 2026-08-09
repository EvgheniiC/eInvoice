import { useEffect, useState } from 'react'

interface PdfPreviewProps {
  file: File
  title?: string
}

export function PdfPreview({ file, title = 'PDF-Ansicht' }: PdfPreviewProps) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null)

  useEffect(() => {
    const url: string = URL.createObjectURL(file)
    setObjectUrl(url)
    return () => {
      URL.revokeObjectURL(url)
    }
  }, [file])

  if (!objectUrl) {
    return null
  }

  return (
    <section className="pdf-preview" aria-label={title}>
      <div className="pdf-preview__header">
        <h3>{title}</h3>
        <a href={objectUrl} download={file.name} className="pdf-preview__download">
          PDF herunterladen
        </a>
      </div>
      <iframe className="pdf-preview__frame" src={objectUrl} title={title} />
    </section>
  )
}

import type { JSX } from 'react'

type LegalEntryButtonProps = {
  onClick: () => void
  overlay?: boolean
}

export function LegalEntryButton({ onClick, overlay = false }: LegalEntryButtonProps): JSX.Element {
  const className: string = overlay ? 'legal-entry legal-entry--overlay' : 'legal-entry'

  return (
    <button type="button" className={className} onClick={onClick} aria-label="Impressum und Datenschutz">
      Impressum
    </button>
  )
}

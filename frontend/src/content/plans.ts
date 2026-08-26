export type PublicPlanCode = 'free' | 'plus' | 'team'

export type PublicPlan = {
  code: PublicPlanCode
  name: string
  priceMonthly: string
  summary: string
  features: readonly string[]
  highlighted: boolean
}

export const PUBLIC_PLANS: readonly PublicPlan[] = [
  {
    code: 'free',
    name: 'Free',
    priceMonthly: '0 €',
    summary: 'Für einzelne Rechnungen ohne Registrierung oder Vertragsbindung.',
    features: [
      '10 Prüfungen und Exporte pro Tag',
      'Eine Datei pro Vorgang, bis 10 MB',
      'XRechnung und ZUGFeRD prüfen',
      'Excel, DATEV-CSV und Steuerberater-Paket',
    ],
    highlighted: false,
  },
  {
    code: 'plus',
    name: 'Plus',
    priceMonthly: '12,90 €',
    summary: 'Für Handwerk und kleine Büros mit regelmäßigem Rechnungseingang.',
    features: [
      '100 Prüfungen und Exporte pro Tag',
      'Batch mit bis zu 20 Dateien, je 25 MB',
      'Verlauf mit ausdrücklicher Zustimmung',
      'Duplikate und ein ZIP für die Kanzlei',
    ],
    highlighted: true,
  },
  {
    code: 'team',
    name: 'Team',
    priceMonthly: '24,90 €',
    summary: 'Für Firmen mit höherem Volumen und größeren Stapeln.',
    features: [
      '500 Prüfungen und Exporte pro Tag',
      'Batch mit bis zu 50 Dateien, je 50 MB',
      'Alle Funktionen aus Plus',
      'Höhere parallele Verarbeitung',
    ],
    highlighted: false,
  },
]

export const PLAN_RANK: Readonly<Record<PublicPlanCode, number>> = {
  free: 0,
  plus: 1,
  team: 2,
}

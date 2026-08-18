import { useEffect, useState, type JSX } from 'react'
import { fetchCapabilities, recordFunnel } from '../api/client'
import { InvoiceHeroVisual } from '../components/InvoiceHeroVisual'
import { PageNav } from '../components/PageNav'
import { SiteFooter } from '../components/SiteFooter'
import { DEFAULT_CAPABILITIES } from '../content/capabilities'
import type { AppRoute } from '../routing'
import type { CapabilitiesResponse, MeResponse, SupportedFormat } from '../types/invoice'

type LandingPageProps = {
  onStart: () => void
  onNavigate: (route: AppRoute) => void
  session: MeResponse | null
  onLogout: () => void
}

export function LandingPage({
  onStart,
  onNavigate,
  session,
  onLogout,
}: LandingPageProps): JSX.Element {
  const [capabilities, setCapabilities] = useState<CapabilitiesResponse>(DEFAULT_CAPABILITIES)

  useEffect(() => {
    recordFunnel('landing')
    void fetchCapabilities().then((value: CapabilitiesResponse) => {
      setCapabilities(value)
    })
  }, [])

  const sizeLabel: string = `${String(capabilities.max_upload_size_mb)} MB`
  const profileLabel: string = capabilities.profiles.join(', ')

  return (
    <main id="main-content" className="landing" tabIndex={-1}>
      <section className="landing-hero">
        <PageNav overlay onNavigate={onNavigate} session={session} onLogout={onLogout} />
        <div className="landing-hero__copy">
          <p className="landing-brand">eInvoice</p>
          <h1 className="landing-hero__title" tabIndex={-1}>
            E-Rechnungen kommen als XML — und bleiben unlesbar.
          </h1>
          <p className="landing-hero__lead">
            XRechnung und ZUGFeRD in Sekunden verstehen, prüfen und für die Buchhaltung
            exportieren.
          </p>
          <p className="landing-hero__note">
            Ohne Registrierung. Die Datei wird nur für diese Anfrage verarbeitet und danach
            gelöscht.
          </p>
          <div className="landing-hero__cta">
            <button type="button" className="btn btn--primary" onClick={onStart}>
              Rechnung hochladen
            </button>
          </div>
        </div>
        <InvoiceHeroVisual />
      </section>

      <section className="landing-section" aria-labelledby="how-heading">
        <h2 id="how-heading" className="landing-section__title">
          Was eInvoice macht
        </h2>
        <p className="landing-section__lead">
          Ein Weg: Datei rein — lesbare Rechnung, Status und Export für den Steuerberater.
        </p>
        <ol className="landing-steps">
          <li>
            <span className="landing-steps__num">1</span>
            <div>
              <strong>Hochladen</strong>
              <p>XRechnung-XML oder ZUGFeRD-PDF per Drag &amp; Drop.</p>
            </div>
          </li>
          <li>
            <span className="landing-steps__num">2</span>
            <div>
              <strong>Verstehen &amp; prüfen</strong>
              <p>Lesbare Ansicht, Validierung und Warnung bei PDF/XML-Abweichungen.</p>
            </div>
          </li>
          <li>
            <span className="landing-steps__num">3</span>
            <div>
              <strong>Exportieren</strong>
              <p>Excel, DATEV-CSV oder fertiges Paket für den Steuerberater.</p>
            </div>
          </li>
        </ol>
        <div className="landing-section__cta">
          <button type="button" className="btn btn--primary" onClick={onStart}>
            Rechnung hochladen
          </button>
        </div>
      </section>

      <section className="landing-section" aria-labelledby="elster-heading">
        <h2 id="elster-heading" className="landing-section__title">
          Nicht ELSTER — sondern der lesbare Rechnungseingang
        </h2>
        <p className="landing-section__lead">
          ELSTER übermittelt Steuerdaten an die Finanzverwaltung. eInvoice hilft Ihnen davor
          im Arbeitsalltag: Eingangsrechnung lesen, prüfen und an die Buchhaltung übergeben.
        </p>
        <ul className="landing-benefits">
          <li>XML als verständliche Rechnung anzeigen</li>
          <li>Standard prüfen und PDF mit eingebettetem XML abgleichen</li>
          <li>CSV, Excel, DATEV-CSV oder Steuerberater-Paket exportieren</li>
        </ul>
      </section>

      <section className="landing-section" aria-labelledby="formats-heading">
        <h2 id="formats-heading" className="landing-section__title">
          Unterstützte Rechnungen
        </h2>
        <p className="landing-section__lead">
          Einzeldateien bis {sizeLabel}: XRechnung als UBL Invoice, UBL CreditNote oder UN/CEFACT
          CII sowie ZUGFeRD/Factur-X als PDF mit eingebettetem Rechnungs-XML.
        </p>
        <p className="landing-section__lead">
          Geprüfte Profile: {profileLabel}.
        </p>
        <ul className="landing-benefits">
          {capabilities.formats.map((item: SupportedFormat) => (
            <li key={item.id}>
              {item.label} ({item.extensions.join(', ')})
            </li>
          ))}
        </ul>
        <p className="landing-limitations">{capabilities.limitations.join(' ')}</p>
      </section>

      <section className="landing-section" aria-labelledby="privacy-heading">
        <h2 id="privacy-heading" className="landing-section__title">
          Was mit Ihrer Datei passiert
        </h2>
        <p className="landing-section__lead">
          Die Rechnung wird auf dem Server gelesen und geprüft. Es gibt kein Benutzerkonto und
          kein Rechnungsarchiv.
        </p>
        <ul className="landing-benefits">
          <li>Verarbeitung nur während der Anfrage, im Arbeitsspeicher und in temporären Dateien</li>
          <li>XML/PDF und Validator-Ergebnisse werden danach gelöscht</li>
          <li>Protokolle enthalten keinen Rechnungsinhalt (kein IBAN, kein XML)</li>
        </ul>
        <p className="landing-limitations">
          Betreiberangaben folgen vor dem öffentlichen Betrieb. Impressum, Datenschutz und Hilfe
          öffnen Sie oben rechts.
        </p>
      </section>

      <SiteFooter onNavigate={onNavigate} />
    </main>
  )
}

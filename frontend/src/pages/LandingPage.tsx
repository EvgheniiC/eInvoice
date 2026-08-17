import type { JSX } from 'react'
import { InvoiceHeroVisual } from '../components/InvoiceHeroVisual'

type LandingPageProps = {
  onStart: () => void
}

export function LandingPage({ onStart }: LandingPageProps): JSX.Element {
  return (
    <div className="landing">
      <section className="landing-hero">
        <div className="landing-hero__copy">
          <p className="landing-brand">eInvoice</p>
          <h1 className="landing-hero__title">
            E-Rechnungen kommen als XML — und bleiben unlesbar.
          </h1>
          <p className="landing-hero__lead">
            XRechnung und ZUGFeRD in Sekunden verstehen, prüfen und für die Buchhaltung
            exportieren.
          </p>
          <p className="landing-hero__note">
            Ohne Registrierung. Ihre Datei wird direkt verarbeitet.
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
              <p>Excel, DATEV oder fertiges Paket für den Steuerberater.</p>
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
          <li>CSV, Excel, DATEV-Datei oder Steuerberater-Paket exportieren</li>
        </ul>
      </section>

      <section className="landing-section" aria-labelledby="formats-heading">
        <h2 id="formats-heading" className="landing-section__title">
          Unterstützte Rechnungen
        </h2>
        <p className="landing-section__lead">
          Einzeldateien bis 10 MB: XRechnung als UBL Invoice, UBL CreditNote oder UN/CEFACT
          CII sowie ZUGFeRD/Factur-X als PDF mit eingebettetem Rechnungs-XML.
        </p>
        <p className="landing-limitations">
          Normale PDFs ohne eingebettetes XML, Scans, openTRANS und andere XML-Formate werden
          derzeit nicht verarbeitet.
        </p>
      </section>

      <footer className="landing-footer">
        <p>
          eInvoice unterstützt bei der technischen und inhaltlichen Prüfung, ersetzt aber
          keine Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug.
          Die Entscheidung liegt bei Ihnen bzw. Ihrem Steuerberater.
        </p>
      </footer>
    </div>
  )
}

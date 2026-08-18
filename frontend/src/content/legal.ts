export type LegalSection = {
  heading: string
  paragraphs: string[]
  listItems?: string[]
}

export type LegalDocument = {
  id: string
  title: string
  updatedLabel: string
  intro: string
  sections: LegalSection[]
}

const PLACEHOLDER: string = 'Angaben folgen vor dem öffentlichen Betrieb.'

export const IMPRESSUM: LegalDocument = {
  id: 'impressum',
  title: 'Impressum',
  updatedLabel: 'Stand: August 2026',
  intro:
    'Dieses Impressum erfüllt die Struktur nach § 5 DDG. Die Betreiberdaten sind ' +
    'noch nicht hinterlegt und werden ergänzt, bevor der Dienst öffentlich angeboten wird.',
  sections: [
    {
      heading: 'Diensteanbieter',
      paragraphs: [PLACEHOLDER],
      listItems: [
        'Name / Firma: —',
        'Anschrift: —',
        'Vertretungsberechtigte Person: —',
        'Kontakt (E-Mail): —',
      ],
    },
    {
      heading: 'Weitere Angaben (falls zutreffend)',
      paragraphs: [
        'Registergericht, Registernummer, Umsatzsteuer-ID und berufsrechtliche Angaben ' +
          'werden ergänzt, sobald sie feststehen. Bis dahin ist dieser Dienst nicht als ' +
          'öffentliches Angebot einer bestimmten Person oder Firma zu verstehen.',
      ],
    },
    {
      heading: 'Haftung für Inhalte und Links',
      paragraphs: [
        'eInvoice unterstützt bei der technischen Prüfung von E-Rechnungen, ersetzt aber ' +
          'keine Rechts- oder Steuerberatung und gibt keine Garantie für den Vorsteuerabzug.',
        'Für Inhalte externer Websites, auf die wir verlinken, sind ausschließlich deren ' +
          'Betreiber verantwortlich.',
      ],
    },
  ],
}

export const DATENSCHUTZ: LegalDocument = {
  id: 'datenschutz',
  title: 'Datenschutzerklärung',
  updatedLabel: 'Stand: August 2026',
  intro:
    'Diese Erklärung beschreibt, wie eInvoice Dateien und Nutzungsdaten verarbeitet. ' +
    'Name und Kontaktdaten des Verantwortlichen werden ergänzt, bevor der Dienst ' +
    'öffentlich betrieben wird.',
  sections: [
    {
      heading: '1. Verantwortlicher',
      paragraphs: [
        PLACEHOLDER,
        'Sobald der Verantwortliche feststeht, finden Sie Name, Anschrift und E-Mail ' +
          'in diesem Abschnitt sowie im Impressum.',
      ],
    },
    {
      heading: '2. Welche Daten verarbeitet werden',
      paragraphs: [
        'eInvoice arbeitet ohne Benutzerkonto. Es gibt keine Registrierung und keine ' +
          'dauerhafte Kundenakte. Es gelten zwei Verarbeitungsmodelle; aktiv ist nur das ' +
          'Gastmodell.',
      ],
      listItems: [
        'Gast (aktuell): Hochgeladene Rechnungsdatei (XRechnung-XML oder ZUGFeRD-PDF) und ' +
          'daraus gelesene Rechnungsinhalte (z. B. Namen, Adressen, Beträge, IBAN, USt-IdNr.). ' +
          'Die Datei wird nicht gespeichert.',
        'Konto (nicht aktiv): erst nach Registrierung, AVV und gesonderter Einwilligung. ' +
          'Dann nur Metadaten, Originaldatei nur bei Checkbox „Dateien merken“ mit kurzer ' +
          'Aufbewahrung. Dieses Modell wird derzeit nicht angeboten.',
        'Technische Verbindungsdaten beim Aufruf: IP-Adresse, Zeitpunkt, aufgerufene URL, ' +
          'User-Agent — soweit der Webserver sie für den Betrieb protokolliert.',
        'Anwendungsprotokolle: Request-ID, Dateiname (nur Basisname), Dateigröße, ' +
          'Statuscode. Kein Rechnungsinhalt, kein IBAN, kein XML/PDF-Rohtext.',
        'Optionales Feedback: Freitext ohne Dateianhang. Bitte keine Rechnungsdaten einfügen. ' +
          'Funnel-Zähler (Seite aufgerufen / Datei gewählt / Prüfung / Export) ohne ' +
          'Rechnungsinhalt und ohne Nutzerprofil.',
      ],
    },
    {
      heading: '3. Zweck und Rechtsgrundlage',
      paragraphs: [
        'Die Datei wird ausschließlich verarbeitet, um die Rechnung zu lesen, zu prüfen ' +
          'und auf Ihren Wunsch einen Export (CSV, Excel, DATEV-CSV oder Steuerberater-Paket) ' +
          'zu erzeugen.',
        'Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (Vertrag / vorvertragliche Anfrage), ' +
          'soweit Sie den Dienst nutzen, hilfsweise Art. 6 Abs. 1 lit. f DSGVO (berechtigtes ' +
          'Interesse an einem funktionierenden, sicheren Rechnungseingang). Server-Logs stützen ' +
          'sich auf Art. 6 Abs. 1 lit. f DSGVO (Sicherheit und Missbrauchsabwehr).',
      ],
    },
    {
      heading: '4. Wo die Datei verarbeitet wird — Speicherung und Löschung',
      paragraphs: [
        'Die Verarbeitung findet auf dem Server des Dienstes statt (geplante Region: ' +
          'Europäische Union; genauer Standort und Hosting-Anbieter folgen mit den ' +
          'Betreiberangaben). Die Datei wird nicht in eine Datenbank geschrieben und nicht ' +
          'für ein Benutzerkonto gespeichert.',
      ],
      listItems: [
        'Während der Anfrage liegt die Datei im Arbeitsspeicher.',
        'Für die Erkennung von ZUGFeRD und für den KoSIT-Validator entstehen kurzlebige ' +
          'temporäre Dateien in einem isolierten Temp-Verzeichnis.',
        'Nach Ende der Anfrage werden temporäre XML/PDF-Dateien und Validator-Berichte ' +
          'gelöscht. Es bleibt kein Rechnungsarchiv zurück.',
        'Der Export wird an Ihren Browser zurückgegeben und serverseitig nicht vorgehalten.',
        'Anwendungsprotokolle enthalten keinen Rechnungsinhalt. Sie dienen der Fehleranalyse ' +
          'und werden nicht als Ersatzarchiv genutzt.',
        'Gastmodell: keine Speicherung der Datei nach der Anfrage.',
        'Kontomodell (geplant, nicht aktiv): Rechtsgrundlage Art. 6 DSGVO plus AVV; ' +
          'Originaldatei nur mit Opt-in und begrenzter Aufbewahrung (Orientierung: 30 Tage).',
      ],
    },
    {
      heading: '5. Empfänger und Auftragsverarbeitung',
      paragraphs: [
        'Die Datei wird nicht an Steuerberater, DATEV oder andere Fachanwendungen gesendet. ' +
          'Ein Export verbleibt bei Ihnen, bis Sie ihn selbst weitergeben.',
        'Der KoSIT-Validator läuft als lokaler Java-Prozess auf demselben Server, nicht als ' +
          'externer Cloud-Dienst.',
        'Hosting-Anbieter, CDN oder E-Mail-Postfach für Support sind Auftragsverarbeiter, ' +
          'sobald sie eingesetzt werden. Die Liste folgt mit den Betreiberangaben. Ein ' +
          'AV-Vertrag (Art. 28 DSGVO) wird vor einem öffentlichen Cloud-Betrieb vorbereitet.',
      ],
    },
    {
      heading: '6. Cookies und Schriftarten',
      paragraphs: [
        'eInvoice setzt keine Tracking-Cookies und kein Nutzerprofil. Funnel-Zähler sind ' +
          'anonyme Zählereignisse ohne Cookie.',
        'Die Website kann Schriftarten von Google Fonts laden. Dabei erfährt Google Ihre ' +
          'IP-Adresse. Sobald der Dienst öffentlich ist, kann dies durch selbst gehostete ' +
          'Schriften ersetzt oder hier konkret beschrieben werden.',
      ],
    },
    {
      heading: '7. Ihre Rechte',
      paragraphs: [
        'Sie haben die Rechte auf Auskunft, Berichtigung, Löschung, Einschränkung, ' +
          'Datenübertragbarkeit und Widerspruch sowie das Beschwerderecht bei einer ' +
          'Aufsichtsbehörde.',
        'Weil Rechnungsdateien nach der Anfrage nicht gespeichert werden, können wir nach ' +
          'Abschluss der Verarbeitung in der Regel keine Kopie Ihrer hochgeladenen Datei ' +
          'mehr herausgeben oder löschen — sie ist dann bereits entfernt.',
        'Kontakt für Datenschutzanfragen: folgt mit den Betreiberangaben.',
      ],
    },
    {
      heading: '8. Keine Garantie für Steuerrecht',
      paragraphs: [
        'Die Prüfung ist technisch und fachlich unterstützend. Ob ein Vorsteuerabzug zulässig ' +
          'ist, entscheidet nicht dieser Dienst, sondern Sie bzw. Ihr Steuerberater.',
      ],
    },
  ],
}

export const LEGAL_PAGES: LegalDocument[] = [IMPRESSUM, DATENSCHUTZ]

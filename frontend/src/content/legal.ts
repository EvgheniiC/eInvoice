import { SUPPORT_EMAIL } from './contact'

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

export const IMPRESSUM: LegalDocument = {
  id: 'impressum',
  title: 'Impressum',
  updatedLabel: 'Stand: 2. September 2026',
  intro:
    'Dieses Impressum erfüllt die Struktur nach § 5 DDG. Diensteanbieterin ist ' +
    'Svetlana Costina (Einzelunternehmen). Steuernummer und USt-IdNr. werden nach ' +
    'Mitteilung des Finanzamts ergänzt.',
  sections: [
    {
      heading: 'Diensteanbieter',
      paragraphs: [
        'Svetlana Costina betreibt eInvoice als Einzelunternehmen.',
      ],
      listItems: [
        'Name / Firma: Svetlana Costina',
        'Rechtsform: Einzelunternehmen',
        'Anschrift: Elbinger Straße 70, 27755 Delmenhorst, Deutschland',
        'Vertretungsberechtigte Person: Svetlana Costina',
        `Kontakt (E-Mail): ${SUPPORT_EMAIL}`,
      ],
    },
    {
      heading: 'Weitere Angaben (falls zutreffend)',
      paragraphs: [
        'Ein Handelsregistereintrag ist für dieses Einzelunternehmen nicht vorgesehen. ' +
          'Steuernummer und USt-IdNr. liegen noch nicht vor und werden nach Mitteilung ' +
          'des Finanzamts hier ergänzt.',
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
  updatedLabel: 'Stand: 2. September 2026',
  intro:
    'Diese Erklärung beschreibt, wie eInvoice Dateien und Nutzungsdaten verarbeitet. ' +
    'Verantwortliche ist Svetlana Costina (Einzelunternehmen).',
  sections: [
    {
      heading: '1. Verantwortlicher',
      paragraphs: [
        'Svetlana Costina, Einzelunternehmen.',
        'Elbinger Straße 70, 27755 Delmenhorst, Deutschland.',
        `E-Mail: ${SUPPORT_EMAIL}`,
      ],
    },
    {
      heading: '2. Welche Daten verarbeitet werden',
      paragraphs: [
        'eInvoice kann ohne Benutzerkonto genutzt werden. Zusätzlich gibt es optionale ' +
          'Konten für Organisationen. Es gelten zwei getrennte Verarbeitungsmodelle; eine ' +
          'dauerhafte Speicherung von Rechnungsoriginalen ist in beiden Modellen nicht der Standard.',
      ],
      listItems: [
        'Gast (aktuell, ohne Konto): Hochgeladene Rechnungsdatei und daraus gelesene ' +
          'Rechnungsinhalte. Die Datei wird nicht gespeichert.',
        'Konto (optional): E-Mail, Passwort-Hash, Organisationsname, Rolle, Sitzungs-Cookie. ' +
          'Optional Firmendaten der Organisation: Steuernummer, USt-IdNr., IBAN, ' +
          'E-Mail des Steuerberaters — nur wenn der Inhaber sie unter Organisation speichert. ' +
          'Transaktionale Auth-Mails (Bestätigung, Anmeldelink, Passwort-Reset). ' +
          'Kein Rechnungsarchiv ohne Zustimmung. Bei Plus liegen Batch-Originale nur kurz ' +
          'in einem Temp-Verzeichnis. Verlauf: Metadaten und Datei-Hash nur nach Opt-in; ' +
          'Originaldatei nur mit „Dateien merken“ und begrenzter Aufbewahrung.',
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
        'Die Verarbeitung findet auf einem Server von Hetzner Online GmbH in Nürnberg, ' +
          'Deutschland, statt. Mit Hetzner besteht ein AV-Vertrag nach Art. 28 DSGVO. ' +
          'Im Gastmodus wird die Datei nicht in eine Datenbank geschrieben. Im Konto nur ' +
          'nach ausdrücklicher Zustimmung: Metadaten/Hash, optional das Original.',
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
        'Plus-Batch: Originaldateien bleiben wenige Stunden in einem Temp-Verzeichnis, ' +
          'damit Sie ein ZIP für die Buchhaltung laden können. Danach Löschung. Kein Archiv.',
        'Kontomodell Verlauf (nur nach Zustimmung, Plus/Team): Metadaten und Datei-Hash. ' +
          'Originaldatei nur mit Opt-in „Dateien merken“ und begrenzter Aufbewahrung ' +
          '(Orientierung: 30 Tage). Rechtsgrundlage Art. 6 DSGVO plus AVV.',
      ],
    },
    {
      heading: '5. Empfänger und Auftragsverarbeitung',
      paragraphs: [
        'Die Datei wird nicht an Steuerberater, DATEV oder andere Fachanwendungen gesendet. ' +
          'Ein Export verbleibt bei Ihnen, bis Sie ihn selbst weitergeben.',
        'Hosting: Hetzner Online GmbH, Industriestraße 25, 91710 Gunzenhausen, Deutschland, ' +
          'ist Auftragsverarbeiter für Server, Netz und Backup (Rechenzentrum Nürnberg). ' +
          'Es besteht ein AV-Vertrag nach Art. 28 DSGVO (abgeschlossen im Hetzner-Kundenkonto). ' +
          'Der KoSIT-Validator läuft als lokaler Java-Prozess auf demselben Server, nicht als ' +
          'externer Cloud-Dienst.',
        'Kontaktpostfach und transaktionale Auth-Mails (Bestätigung, Anmeldelink, ' +
          'Passwort-Reset) laufen über Hetzner Online GmbH, Deutschland. Zahlungsdienst ' +
          'und object storage sind noch nicht eingesetzt; die Liste wird ergänzt, sobald ' +
          'sie genutzt werden.',
      ],
    },
    {
      heading: '6. Cookies und Schriftarten',
      paragraphs: [
        'eInvoice setzt ein Sitzungs-Cookie nur nach Anmeldung (httpOnly). Funnel-Zähler sind ' +
          'anonyme Zählereignisse ohne Nutzerprofil.',
        'Die Website verwendet lokale Systemschriftarten und lädt keine Schriftarten von ' +
          'externen Anbietern.',
      ],
    },
    {
      heading: '7. Ihre Rechte',
      paragraphs: [
        'Sie haben die Rechte auf Auskunft, Berichtigung, Löschung, Einschränkung, ' +
          'Datenübertragbarkeit und Widerspruch sowie das Beschwerderecht bei einer ' +
          'Aufsichtsbehörde.',
        'Weil Rechnungsdateien nach der Anfrage (Gast) bzw. nach kurzer Batch-Frist (Plus) ' +
          'nicht dauerhaft gespeichert werden, können wir danach in der Regel keine Kopie ' +
          'Ihrer hochgeladenen Datei mehr herausgeben oder löschen — sie ist dann bereits entfernt.',
        `Kontakt für Datenschutzanfragen: ${SUPPORT_EMAIL}`,
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

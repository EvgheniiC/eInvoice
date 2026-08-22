export type FaqItem = {
  id: string
  question: string
  paragraphs: string[]
  listItems?: string[]
}

export const FAQ_ITEMS: FaqItem[] = [
  {
    id: 'was-ist-xml',
    question: 'Was ist eine XML-Rechnung?',
    paragraphs: [
      'Eine XRechnung ist eine maschinenlesbare Datei (XML), kein klassisches Papier-PDF. ' +
        'Viele Programme zeigen sie als unlesbaren Text. eInvoice liest die Datei und zeigt ' +
        'Nummer, Betrag, Fälligkeit und IBAN in einer normalen Rechnungssicht.',
      'ZUGFeRD und Factur-X sind PDFs mit derselben XML-Rechnung im Inneren. Ohne eingebettetes ' +
        'XML ist ein normales PDF für diesen Dienst nicht verarbeitbar.',
    ],
  },
  {
    id: 'formate',
    question: 'Welche Dateien werden unterstützt?',
    paragraphs: [
      'Aktuell: XRechnung (UBL Invoice, UBL CreditNote, UN/CEFACT CII) und ZUGFeRD/Factur-X ' +
        'als PDF mit eingebettetem XML. Geprüfte Profile: EN 16931 und XRechnung 3.0. ' +
        'Im Gastmodus eine Datei pro Anfrage. Mit Plus mehrere Dateien oder ein ZIP.',
    ],
    listItems: [
      'Maximale Dateigröße: 10 MB (Gastmodus); Plus und Team höher',
      'Gastmodus: eine Datei pro Anfrage, begrenzte Prüfungen und Exporte pro Tag',
      'Nicht unterstützt: Scan-PDF, Foto, openTRANS, andere XML-Formate, verschachtelte ZIP-Archive',
      'DATEV-Export ist eine Buchungsstapel-CSV, kein DATEVconnect',
    ],
  },
  {
    id: 'mismatch',
    question: 'PDF und XML weichen ab — was soll ich zahlen?',
    paragraphs: [
      'Wenn sichtbares PDF und eingebettetes XML unterschiedliche Nummer, Summe, MwSt oder IBAN ' +
        'zeigen, nicht einfach den PDF-Betrag überweisen.',
      'Nächster Schritt: den Lieferanten um eine korrigierte E-Rechnung bitten. Die Entscheidung ' +
        'über Zahlung und Vorsteuer bleibt bei Ihnen bzw. Ihrem Steuerberater.',
    ],
  },
  {
    id: 'steuerberater',
    question: 'Was übergebe ich dem Steuerberater?',
    paragraphs: [
      'Nutzen Sie „Paket für Steuerberater“ für eine Datei. Mit Plus: mehrere Rechnungen ' +
        'hochladen und „Ein ZIP für die Buchhaltung“ — ein Paket mit Originaldateien, ' +
        'Kurzfassung, Prüfbericht, Excel und DATEV-CSV.',
      'Unter Organisation können Sie Steuernummer, USt-IdNr., IBAN und die E-Mail der ' +
        'Kanzlei hinterlegen. Diese Angaben stehen dann in mandant.txt im ZIP. ' +
        'Den Versand an die Kanzlei machen Sie vorerst selbst.',
      'Die Datei bleibt bei Ihnen: eInvoice speichert im Gastmodus kein Rechnungsarchiv. ' +
        'Sie senden das ZIP selbst an die Kanzlei.',
    ],
  },
  {
    id: 'lesbare-pdf',
    question: 'Kann ich eine lesbare PDF herunterladen?',
    paragraphs: [
      'Ja. Nach dem Lesen zeigt eInvoice die Rechnungsdaten und kann daraus eine lesbare PDF ' +
        'erzeugen — eine Arbeitskopie, keine Originalrechnung und kein steuerlicher Beleg.',
      'Eine Datei: Schaltfläche „Lesbare PDF herunterladen“. Mehrere Dateien mit Plus: ' +
        '„Alle als lesbare PDF“ als ZIP. Für die Buchhaltung bleibt das Steuerberater-Paket ' +
        'mit Excel und DATEV.',
    ],
  },
  {
    id: 'speicherung',
    question: 'Wird meine Rechnung gespeichert?',
    paragraphs: [
      'Im Gastmodus nein. Die Datei liegt nur während der Anfrage im Speicher und in ' +
        'kurzlebigen Temp-Dateien für den Validator. Danach wird sie gelöscht.',
      'Mit Plus bleiben Originaldateien kurz im Temp-Verzeichnis, damit Sie ein ' +
        'Buchhaltungspaket laden können. Nach wenigen Stunden werden sie gelöscht.',
      'Einen Verlauf gibt es nur nach ausdrücklicher Zustimmung unter Organisation: ' +
        'standardmäßig Metadaten und Datei-Hash, keine Originaldatei. „Dateien merken“ ' +
        'bewahrt das Original begrenzt (Orientierung: 30 Tage), damit Sie das Paket erneut ' +
        'laden können. Ohne Häkchen wird nichts gespeichert.',
    ],
  },
  {
    id: 'support',
    question: 'Wie erreiche ich den Support?',
    paragraphs: [
      'Nutzen Sie das Formular unten. Bitte keine Rechnungsdatei, kein XML, keine IBAN und ' +
        'keine personenbezogenen Rechnungsdaten einfügen.',
      'Eine feste Support-E-Mail und die erwartete Antwortzeit folgen mit den Betreiberangaben ' +
        'vor dem öffentlichen Betrieb.',
    ],
  },
]

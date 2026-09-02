# Auftragsverarbeitung (AVV / DPA)

eInvoice ist **Verantwortlicher** gegenüber dem Nutzer, der eine Datei hochlädt.
Der Hosting-Anbieter ist **Auftragsverarbeiter** des Betreibers (Art. 28 DSGVO).

Der verbindliche AV-Vertrag mit dem Hoster liegt **nicht** in diesem Repository:
er wurde im Hetzner-Kundenkonto abgeschlossen. Diese Datei ist die interne
Subprocessor-Liste für Datenschutztexte und Reviews.

Wenn eine Kanzlei eInvoice als Werkzeug für Mandantenakten einsetzt, kann
zusätzlich ein AVV zwischen Kanzlei und Betreiber nötig sein.

## 1. Parteien

- Verantwortlicher: Svetlana Costina (Einzelunternehmen), Elbinger Straße 70, 27755 Delmenhorst, support@erechnung-smart.de
- Auftragsverarbeiter (Hosting): Hetzner Online GmbH, Industriestraße 25, 91710 Gunzenhausen, Deutschland; Rechenzentrum Nürnberg
- Gegenstand: Bereitstellung der eInvoice-Webanwendung (Upload, Prüfung, Export)
- AV-Vertrag Hosting: abgeschlossen im Hetzner-Kundenkonto (Art. 28 DSGVO)

## 2. Art der Daten

- Rechnungsinhalte aus XRechnung/ZUGFeRD (Namen, Adressen, IBAN, Beträge, USt-IdNr.)
- Optional gespeicherte Firmendaten der Organisation (Steuernummer, USt-IdNr., IBAN,
  E-Mail des Steuerberaters), nur nach Eingabe unter Organisation
- Technische Logs ohne Rechnungsinhalt (Request-ID, Dateiname, Größe, Status)

## 3. Zweck und Dauer

- Zweck: Lesen, Prüfen und Exportieren der vom Nutzer übermittelten Datei
- Speicherung der Datei: Gast — nur für die Dauer der HTTP-Anfrage; Plus-Batch —
  kurzlebiges Temp-Verzeichnis bis zum Buchhaltungspaket oder TTL (kein Archiv)
- Kein GoBD-Archiv. Verlauf nur nach Zustimmung: Metadaten und Datei-Hash;
  Originaldatei nur bei Opt-in „Dateien merken“ und begrenzter Aufbewahrung
  (Orientierung: 30 Tage)

## 4. Weisungen und Sicherheit

- Verarbeitung nur zur Erfüllung der Anfrage des Nutzers
- TLS, Zugriffsbeschränkung der API auf localhost hinter nginx
- Keine Rechnungsinhalte in Anwendungsprotokollen
- KoSIT-Validator als lokaler Prozess, nicht als Drittanbieter-API
- TOMs des Hosters: Anlage zum Hetzner-AV-Vertrag (Abruf im Kundenkonto)

## 5. Subunternehmer (Stand: 31. August 2026)

| Subunternehmer | Rolle | Ort | AVV |
|----------------|-------|-----|-----|
| Hetzner Online GmbH | Server, Backup, Netz | Nürnberg, Deutschland | ja, Kundenkonto |
| Hetzner Online GmbH | Kontaktpostfach und transaktionale Auth-Mails | Deutschland | ja, Kundenkonto (Webhosting) |

Nicht vorgesehen: DATEV-Cloud, Steuerberater-API, Analyse-Tracker, Rechnungsarchiv.
Geplant (noch nicht eingesetzt, Liste vor Go-live aktualisieren): Zahlungsdienst
(Stripe oder Mollie), object storage in DE nur für Opt-in-Dateien.

Hetzner-Subunternehmer des Hosters: siehe [Hetzner-Liste](https://www.hetzner.com/AV/subunternehmer.pdf).

## 6. Löschung und Nachweis

Nach Ende jeder Anfrage: temporäre Dateien löschen. Auf Verlangen des
Verantwortlichen: Bestätigung, dass kein Rechnungsarchiv existiert.
Server-Logs ohne Rechnungsinhalt unterliegen der betrieblichen Aufbewahrung des
Hosters.

## 7. Offene Punkte

- [x] Name des Verantwortlichen: Svetlana Costina (Einzelunternehmen)
- [x] Anschrift des Verantwortlichen: Elbinger Straße 70, 27755 Delmenhorst
- [x] Hosting-AVV und TOMs: Hetzner Online GmbH, abgeschlossen im Kundenkonto
- [x] Genaues Rechenzentrum: Nürnberg
- [ ] Endgültige Subprocessor-Liste nach Stripe/Mollie und Auth-Mail
- [ ] Rechtsprüfung dieser Übersicht

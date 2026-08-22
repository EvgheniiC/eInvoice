# Auftragsverarbeitungsvertrag (AVV / DPA) — Vorlage

Diese Vorlage ist **kein** fertiger Vertrag. Betreiber, Hosting und
Subunternehmer sind noch nicht eingesetzt. Vor einem öffentlichen Cloud-Betrieb
müssen die Platzhalter ersetzt und der Text von einer fachkundigen Person
geprüft werden.

eInvoice ist in der Regel **Verantwortlicher** gegenüber dem Handwerksbetrieb,
der eine Datei hochlädt. Der Hosting-Anbieter ist dann **Auftragsverarbeiter**
des Betreibers (Art. 28 DSGVO).

Wenn eine Kanzlei eInvoice als Werkzeug für Mandantenakten einsetzt, kann
zusätzlich ein AVV zwischen Kanzlei und Betreiber nötig sein.

## 1. Parteien

- Verantwortlicher: _folgt_
- Auftragsverarbeiter (Hosting): _folgt_
- Gegenstand: Bereitstellung der eInvoice-Webanwendung (Upload, Prüfung, Export)

## 2. Art der Daten

- Rechnungsinhalte aus XRechnung/ZUGFeRD (Namen, Adressen, IBAN, Beträge, USt-IdNr.)
- Technische Logs ohne Rechnungsinhalt (Request-ID, Dateiname, Größe, Status)

## 3. Zweck und Dauer

- Zweck: Lesen, Prüfen und Exportieren der vom Nutzer übermittelten Datei
- Speicherung der Datei: Gast — nur für die Dauer der HTTP-Anfrage; Plus-Batch —
  kurzlebiges Temp-Verzeichnis bis zum Buchhaltungspaket oder TTL (kein Archiv)
- Kein dauerhaftes Rechnungsarchiv, kein GoBD-Archiv
- Geplantes Kontomodell (nicht Vertragsgegenstand, solange nicht eingesetzt):
  Metadaten der Verarbeitung; Originaldatei nur bei Opt-in und begrenzter
  Aufbewahrung; Rechtsgrundlage und AVV vor Go-live separat festlegen

## 4. Weisungen und Sicherheit

- Verarbeitung nur zur Erfüllung der Anfrage des Nutzers
- TLS, Zugriffsbeschränkung der API auf localhost hinter nginx
- Keine Rechnungsinhalte in Anwendungsprotokollen
- KoSIT-Validator als lokaler Prozess, nicht als Drittanbieter-API

## 5. Subunternehmer (Liste — Stand Vorlage)

| Subunternehmer | Rolle | Ort | AVV |
|----------------|-------|-----|-----|
| _folgt (Hosting / VPS)_ | Server, Backup, Netz | EU bevorzugt | _folgt_ |
| Google Ireland Ltd. (Google Fonts), falls nicht selbst gehostet | Schriftarten beim Seitenaufruf (IP) | ggf. Drittland | gesondert prüfen oder Schriften selbst hosten |

Nicht vorgesehen: DATEV-Cloud, Steuerberater-API, Analyse-Tracker, Rechnungsarchiv.
Geplant (noch nicht eingesetzt, Liste vor Go-live aktualisieren): E-Mail für
Support/Feedback, Zahlungsdienst (Stripe oder Mollie), object storage in DE nur
für Opt-in-Dateien.

## 6. Löschung und Nachweis

Nach Ende jeder Anfrage: temporäre Dateien löschen. Auf Verlangen des
Verantwortlichen: Bestätigung, dass kein Rechnungsarchiv existiert.
Server-Logs ohne Rechnungsinhalt unterliegen der betrieblichen Aufbewahrung des
Hosters (_Frist folgt_).

## 7. Offene Punkte vor Unterschrift

- [ ] Name, Anschrift, Register des Verantwortlichen
- [ ] Hosting-Vertrag und TOMs des Auftragsverarbeiters
- [ ] Endgültige Subprocessor-Liste
- [ ] Rechtsprüfung dieser Vorlage

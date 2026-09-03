# Steuerberater-Pilot — Gesprächsleitfaden

Kurztext für die Sitzung (Ende der Woche). Keine echten Mandantenakten.
Testdateien liegen lokal unter `backend/tests/xml_files/` und `backend/tests/pdf_files/`
(nicht im Git). Pakete auf **https://erechnung-smart.de** erzeugen, damit Format
und KoSIT dem Production-Stand entsprechen.

Exportvertrag: Format **1.0**, siehe `docs/EXPORT_MAPPING.md`.

---

## 1. Was wir mitgebracht haben (vorlesen / per Mail)

> eInvoice ist ein Empfangswerkzeug für XRechnung und ZUGFeRD: Datei öffnen,
> prüfen, lesbar machen und ein Paket für die Buchhaltung erzeugen.
> Es ist **keine** Buchhaltung, **kein** DATEVconnect und **kein** Ersatz für
> DATEV Unternehmen online.
>
> Im ZIP liegen: Original (XML, bei ZUGFeRD auch PDF), Prüfbericht, Kurzfassung,
> Excel und ein **minimaler DATEV-Buchungsstapel-CSV** (Semikolon, CP1252,
> deutsche Dezimalzahlen). Eine Buchungszeile über den **Bruttobetrag**.
> Konto, Gegenkonto, BU-Schlüssel, Beraternummer, Mandantennummer und
> Wirtschaftsjahr bleiben leer — das soll die Kanzlei ergänzen.
>
> Wir möchten den CSV **in DATEV Kanzlei-Rechnungswesen** importieren, nicht
> nur in Excel öffnen. Testdaten, keine Live-Mandanten.

---

## 2. Dateien für den Test-ZIP

Quellen auf dem Entwicklungsrechner. **Keine** Rechnungen echter Kunden.

| # | Quelldatei | Wozu |
|---|------------|------|
| 1 | `xml_files/xml_text_from_zugpferd.xml` | Normale DE-Rechnung, 19 % |
| 2 | `xml_files/xml_text_from_xml.xml` | Ermäßigter Satz 7 % |
| 3 | `xml_files/credit_note_positive_amounts.xml` | Gutschrift (Soll/Haben = `H`) |
| 4 | `pdf_files/Rechnung_1096393995.pdf` | ZUGFeRD-PDF mit eingebettetem XML |
| 5 | `xml_files/discount_new_position.xml` | Sonderfall: mehrere Sätze, negative Position (Leergut) |

Nicht in den Pilot-ZIP (nur zum Zeigen der Prüfung, nicht zum DATEV-Import):

- `pdf_files/Mismatch_iban_1096393995.pdf` — PDF≠XML
- `xml_files/Invalid_XR_inconsistent_totals.xml` — unstimmige Beträge

### ZIP erzeugen (Production)

1. https://erechnung-smart.de — ohne Login: Datei 1–4 einzeln öffnen → **Paket für Steuerberater**.
2. Plus-Konto (falls vorhanden): dieselben Dateien als **Batch** → ein Sammel-ZIP.
3. Dateien umbenennen, z. B. `01_rechnung_19pct.zip` … `05_batch.zip`.
4. SHA-256 merken (Windows): `Get-FileHash .\01_rechnung_19pct.zip -Algorithm SHA256`

Erwarteter Inhalt jedes Einzel-ZIP:

- `export_manifest.txt` (Format 1.0)
- `datev_hinweise.txt`
- `summary.txt`
- `pruefbericht_*.txt`
- `*.xlsx`
- `datev_*.csv`
- `original/*.xml` und bei ZUGFeRD `original/*.pdf`
- optional `mandant.txt`, nur wenn unter Organisation Profildaten stehen

---

## 3. Was wir die Kanzlei bitten zu prüfen

Bitte in **DATEV Kanzlei-Rechnungswesen** (nicht nur Excel):

1. Welcher Kontenrahmen: **SKR03 oder SKR04**? Welches Wirtschaftsjahr?
2. Welcher Importweg ist zulässig (Buchungsstapel / ASCII / anderer)?
3. Wird CP1252, Semikolon, Datum `TTMMJJJJ`, Betrag mit Komma akzeptiert?
4. Stimmen Anzahl der Belege, Brutto, Steuer, Währung EUR, Soll/Haben?
5. Bleibt Belegfeld 1 (Rechnungsnummer) und Buchungstext lesbar (Umlaute)?
6. Welche Felder muss die Kanzlei **immer** nachziehen: Konto, Gegenkonto,
   BU-Schlüssel, Beraternummer, Mandantennummer, Wirtschaftsjahr?
7. Reicht eine Brutto-Zeile, oder brauchen Sie später Splittung je MwSt-Satz?
8. Gutschrift: Kennzeichen `H` korrekt?
9. Schriftliche Kurzbestätigung: geeignet für einen Handwerk-Piloten — ja / nein,
   mit den konkreten Nacharbeiten.

Bitte keine echten Mandantendaten in Screenshots; Testmandant reicht.

---

## 4. Was wir nicht versprechen

- DATEVconnect, DATEV Unternehmen online, GoBD-Archiv
- Automatisches SKR-Mapping / Kreditorenstamm
- Vorsteuer-Garantie
- Peppol-Zugang

Ziel: Brücke Handwerk → Kanzlei (prüfen + Paket), nicht Ersatz der DATEV-Welt.

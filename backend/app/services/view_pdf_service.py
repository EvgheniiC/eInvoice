"""Human-readable working-copy PDF from a parsed invoice DTO — not an original invoice."""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from decimal import Decimal
from typing import Optional
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.helper_functions.filenames import safe_filename_stem
from app.schemas.invoice import (
    InvoiceParseResponse,
    LineItem,
    ParseStatus,
    PartyInfo,
    TaxBreakdown,
    ValidationStatus,
)

DISCLAIMER: str = (
    "Lesbare Ansicht aus den gelesenen XML-Daten. "
    "Dies ist keine Originalrechnung und kein steuerlicher Beleg."
)
MISSING: str = "—"
HEADER_FILL: colors.Color = colors.HexColor("#5a5a5a")
ROW_FILL: colors.Color = colors.HexColor("#f4f4f4")
LINE_COLOR: colors.Color = colors.HexColor("#b5b5b5")
MUTED: colors.Color = colors.HexColor("#555555")
WARN_FILL: colors.Color = colors.HexColor("#f7efe6")
PAGE_LEFT: float = 14 * mm
PAGE_RIGHT: float = 14 * mm
PAGE_TOP: float = 14 * mm
PAGE_BOTTOM: float = 16 * mm
USABLE_WIDTH: float = A4[0] - PAGE_LEFT - PAGE_RIGHT

_LABEL_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_label",
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=colors.black,
    alignment=TA_LEFT,
)
_VALUE_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_value",
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.black,
    alignment=TA_LEFT,
)
_BODY_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_body",
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=colors.black,
    alignment=TA_LEFT,
)
_TH_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_th",
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10,
    textColor=colors.white,
    alignment=TA_LEFT,
)
_TD_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_td",
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=colors.black,
    alignment=TA_LEFT,
)
_TD_RIGHT_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_td_right",
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=colors.black,
    alignment=TA_RIGHT,
)
_TITLE_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_title",
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    alignment=TA_CENTER,
    textColor=colors.black,
    spaceAfter=2 * mm,
)
_SECTION_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_section",
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=colors.black,
    spaceBefore=3 * mm,
    spaceAfter=1.5 * mm,
)
_DISCLAIMER_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_disclaimer",
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=MUTED,
    alignment=TA_LEFT,
)
_WARN_STYLE: ParagraphStyle = ParagraphStyle(
    "view_pdf_warn",
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor("#7a3d12"),
    alignment=TA_LEFT,
)


class ViewPdfService:
    """Render one working-copy PDF or a ZIP of several."""

    def render(self, invoice: InvoiceParseResponse) -> tuple[bytes, str, str]:
        """Return (pdf_bytes, media_type, download_filename)."""
        if not invoice_is_viewable(invoice):
            raise ValueError("Fehlerhafte Rechnung kann nicht als PDF dargestellt werden.")
        buffer: io.BytesIO = io.BytesIO()
        document: SimpleDocTemplate = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=PAGE_LEFT,
            rightMargin=PAGE_RIGHT,
            topMargin=PAGE_TOP,
            bottomMargin=PAGE_BOTTOM,
            title=_document_title(invoice),
            author="eInvoice",
            subject=DISCLAIMER,
        )
        document.build(
            _story(invoice),
            onFirstPage=_draw_page_chrome,
            onLaterPages=_draw_page_chrome,
        )
        filename: str = build_view_pdf_filename(invoice)
        return buffer.getvalue(), "application/pdf", filename

    def render_batch(
        self,
        invoices: list[InvoiceParseResponse],
        completed_at: datetime,
    ) -> tuple[bytes, str, str]:
        """ZIP of working-copy PDFs for every viewable invoice in the batch."""
        viewable: list[InvoiceParseResponse] = [
            invoice for invoice in invoices if invoice_is_viewable(invoice)
        ]
        if not viewable:
            raise ValueError("Keine lesbare Rechnung in diesem Auftrag.")
        buffer: io.BytesIO = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            used_names: set[str] = set()
            for index, invoice in enumerate(viewable, start=1):
                pdf_bytes, _, pdf_name = self.render(invoice)
                member: str = _unique_member_name(index, pdf_name, used_names)
                used_names.add(member)
                archive.writestr(member, pdf_bytes)
        zip_name: str = build_batch_view_pdf_filename(completed_at, len(viewable))
        return buffer.getvalue(), "application/zip", zip_name


def invoice_is_viewable(invoice: InvoiceParseResponse) -> bool:
    """True when the DTO has enough parsed content to draw a working copy."""
    return invoice.status != ParseStatus.ERROR


def build_view_pdf_filename(invoice: InvoiceParseResponse) -> str:
    """Filename: lesbare_supplier_invoiceNo_date.pdf"""
    supplier: str = safe_filename_stem(invoice.seller.name if invoice.seller else None) or "supplier"
    number: str = safe_filename_stem(invoice.invoice_number) or "invoice"
    date_part: str = (invoice.issue_date or "nodate").replace("-", "")
    return f"lesbare_{supplier}_{number}_{date_part}.pdf"


def build_batch_view_pdf_filename(completed_at: datetime, invoice_count: int) -> str:
    """ZIP filename: lesbare_ansicht_YYYYMMDD_NDateien.zip"""
    date_part: str = completed_at.strftime("%Y%m%d")
    return f"lesbare_ansicht_{date_part}_{invoice_count}Dateien.zip"


def _story(invoice: InvoiceParseResponse) -> list[Flowable]:
    story: list[Flowable] = [
        Paragraph("E I N V O I C E", _TITLE_STYLE),
        _boxed(Paragraph(DISCLAIMER, _DISCLAIMER_STYLE), fill=ROW_FILL),
        Spacer(1, 4 * mm),
        _parties_table(invoice),
        Spacer(1, 4 * mm),
        _facts_table(invoice),
    ]
    warning: Optional[Flowable] = _status_banner(invoice)
    if warning is not None:
        story.append(Spacer(1, 3 * mm))
        story.append(warning)
    story.append(Spacer(1, 4 * mm))
    story.append(_tax_and_reference_row(invoice))
    if invoice.line_items:
        story.append(Paragraph("Positionen", _SECTION_STYLE))
        story.append(_positions_table(invoice))
    story.append(Spacer(1, 3 * mm))
    story.append(
        HRFlowable(width="100%", thickness=0.6, color=LINE_COLOR, spaceBefore=1 * mm, spaceAfter=2 * mm)
    )
    story.append(Paragraph("Zahlung", _SECTION_STYLE))
    story.append(_payment_table(invoice))
    return [KeepTogether(story[:4]), *story[4:]]


def _parties_table(invoice: InvoiceParseResponse) -> Table:
    table: Table = Table(
        [[_party_block("Lieferant", invoice.seller), _party_block("Empfänger", invoice.buyer)]],
        colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5],
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 6),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("LEFTPADDING", (1, 0), (1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _party_block(title: str, party: Optional[PartyInfo]) -> Paragraph:
    lines: list[str] = [f"<b>{escape(_pdf_text(title))}</b>"]
    if party is None:
        lines.append(escape(MISSING))
        return Paragraph("<br/>".join(lines), _BODY_STYLE)
    name: str = _pdf_text(party.name) if party.name else MISSING
    lines.append(escape(name))
    if party.address:
        lines.append(escape(_pdf_text(party.address)).replace("\n", "<br/>"))
    if party.vat_id:
        lines.append(escape(f"USt-IdNr.: {_pdf_text(party.vat_id)}"))
    return Paragraph("<br/>".join(lines), _BODY_STYLE)


def _facts_table(invoice: InvoiceParseResponse) -> Table:
    currency: Optional[str] = invoice.totals.currency if invoice.totals else None
    document_type: str = "Gutschrift" if invoice.document_type == "credit_note" else "Rechnung"
    left: list[tuple[str, str]] = [
        ("Rechnungsnummer", _pdf_text(invoice.invoice_number)),
        ("Rechnungsdatum", _format_date(invoice.issue_date)),
        ("Typ", document_type),
        ("Fällig", _format_date(invoice.due_date)),
        ("Zahlungsreferenz", _pdf_text(invoice.payment_reference)),
    ]
    right: list[tuple[str, str]] = [
        ("Betrag", _format_amount(invoice.totals.gross if invoice.totals else None, currency)),
        ("Netto", _format_amount(invoice.totals.net if invoice.totals else None, currency)),
        ("MwSt", _format_amount(invoice.totals.tax if invoice.totals else None, currency)),
        ("Währung", _pdf_text(currency)),
        ("IBAN", _format_iban(invoice.seller.iban if invoice.seller else None)),
    ]
    rows: list[list[Paragraph]] = []
    for index in range(len(left)):
        left_label, left_value = left[index]
        right_label, right_value = right[index]
        rows.append(
            [
                _p(left_label, _LABEL_STYLE),
                _p(left_value, _VALUE_STYLE),
                _p(right_label, _LABEL_STYLE),
                _p(right_value, _VALUE_STYLE),
            ]
        )
    col: float = USABLE_WIDTH / 4
    table: Table = Table(rows, colWidths=[col, col, col, col])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2 * mm),
                ("LINEBELOW", (0, 0), (-1, -2), 0.2, colors.HexColor("#e0e0e0")),
            ]
        )
    )
    return table


def _status_banner(invoice: InvoiceParseResponse) -> Optional[Flowable]:
    mismatched: bool = any(
        field.xml_value is not None and not field.matched for field in invoice.mismatch_fields
    )
    if mismatched:
        return _boxed(
            Paragraph(
                "PDF und XML weichen ab. Nicht als Zahlungsgrundlage verwenden — "
                "Lieferanten um eine korrigierte Rechnung bitten.",
                _WARN_STYLE,
            ),
            fill=WARN_FILL,
        )
    if invoice.validation_status == ValidationStatus.INVALID:
        return _boxed(
            Paragraph(
                "Prüfung: ungültig. Diese Ansicht ist eine Arbeitskopie, kein gültiger Beleg.",
                _WARN_STYLE,
            ),
            fill=WARN_FILL,
        )
    return None


def _tax_and_reference_row(invoice: InvoiceParseResponse) -> Table:
    currency: Optional[str] = invoice.totals.currency if invoice.totals else None
    tax_rows: list[list[Paragraph]] = [
        [_p("Steuersatz", _TH_STYLE), _p("Steuerbetrag", _TH_STYLE)],
    ]
    breakdown: list[TaxBreakdown] = invoice.totals.tax_breakdown if invoice.totals else []
    if breakdown:
        for item in breakdown:
            tax_rows.append(
                [
                    _p(_format_percent(item.rate), _TD_STYLE),
                    _p(_format_amount(item.amount, currency), _TD_RIGHT_STYLE),
                ]
            )
    else:
        tax_rows.append([_p(MISSING, _TD_STYLE), _p(MISSING, _TD_RIGHT_STYLE)])
    tax_rows.append(
        [
            _p("MwSt gesamt", _LABEL_STYLE),
            _p(_format_amount(invoice.totals.tax if invoice.totals else None, currency), _TD_RIGHT_STYLE),
        ]
    )
    tax_table: Table = _grid_table(tax_rows, [USABLE_WIDTH * 0.22, USABLE_WIDTH * 0.26])
    reference: str = _pdf_text(invoice.payment_reference)
    info_table: Table = _grid_table(
        [
            [_p("Buyer Reference", _TH_STYLE)],
            [_p(reference, _TD_STYLE)],
        ],
        [USABLE_WIDTH * 0.44],
    )
    wrapper: Table = Table(
        [[tax_table, info_table]],
        colWidths=[USABLE_WIDTH * 0.52, USABLE_WIDTH * 0.48],
    )
    wrapper.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 8),
                ("LEFTPADDING", (1, 0), (1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return wrapper


def _positions_table(invoice: InvoiceParseResponse) -> Table:
    currency: Optional[str] = invoice.totals.currency if invoice.totals else None
    header: list[Paragraph] = [
        _p("Nr", _TH_STYLE),
        _p("Beschreibung", _TH_STYLE),
        _p("Menge", _TH_STYLE),
        _p("Preis", _TH_STYLE),
        _p("Gesamt", _TH_STYLE),
        _p("MwSt %", _TH_STYLE),
    ]
    rows: list[list[Paragraph]] = [header]
    for index, item in enumerate(invoice.line_items):
        position: str = str(item.position) if item.position is not None else str(index + 1)
        total: Optional[Decimal] = item.net_amount if item.net_amount is not None else item.gross_amount
        rows.append(
            [
                _p(position, _TD_STYLE),
                _p(_pdf_text(item.description), _TD_STYLE),
                _p(_format_quantity(item), _TD_RIGHT_STYLE),
                _p(_format_amount(item.unit_price, currency), _TD_RIGHT_STYLE),
                _p(_format_amount(total, currency), _TD_RIGHT_STYLE),
                _p(_format_percent(item.tax_rate), _TD_RIGHT_STYLE),
            ]
        )
    widths: list[float] = [
        USABLE_WIDTH * 0.07,
        USABLE_WIDTH * 0.41,
        USABLE_WIDTH * 0.12,
        USABLE_WIDTH * 0.14,
        USABLE_WIDTH * 0.14,
        USABLE_WIDTH * 0.12,
    ]
    table: Table = _grid_table(rows, widths, repeat_header=True)
    return table


def _payment_table(invoice: InvoiceParseResponse) -> Table:
    iban: str = _format_iban(invoice.seller.iban if invoice.seller else None)
    reference: str = _pdf_text(invoice.payment_reference)
    rows: list[list[Paragraph]] = [
        [_p("IBAN", _TH_STYLE), _p("Zahlungsreferenz", _TH_STYLE)],
        [_p(iban, _TD_STYLE), _p(reference, _TD_STYLE)],
    ]
    return _grid_table(rows, [USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])


def _grid_table(
    rows: list[list[Paragraph]],
    col_widths: list[float],
    repeat_header: bool = False,
) -> Table:
    table: Table = Table(rows, colWidths=col_widths, repeatRows=1 if repeat_header else 0)
    commands: list[tuple[object, ...]] = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_FILL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if len(rows) > 2:
        for row_index in range(1, len(rows) - 1, 2):
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), colors.white))
    table.setStyle(TableStyle(commands))
    return table


def _boxed(inner: Flowable, fill: colors.Color) -> Table:
    table: Table = Table([[inner]], colWidths=[USABLE_WIDTH])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), fill),
                ("BOX", (0, 0), (-1, -1), 0.4, LINE_COLOR),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _draw_page_chrome(canvas: Canvas, doc: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(PAGE_LEFT, 8 * mm, "eInvoice — Lesbare Ansicht, keine Originalrechnung")
    canvas.drawRightString(A4[0] - PAGE_RIGHT, 8 * mm, f"Seite {doc.page}")
    canvas.restoreState()


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_pdf_text(text)).replace("\n", "<br/>"), style)


def _pdf_text(value: Optional[str]) -> str:
    if value is None or value.strip() == "":
        return MISSING
    return value.encode("cp1252", "replace").decode("cp1252")


def _format_date(value: Optional[str]) -> str:
    if not value:
        return MISSING
    if len(value) >= 10 and value[4] == "-" and value[7] == "-":
        return f"{value[8:10]}.{value[5:7]}.{value[0:4]}"
    return _pdf_text(value)


def _format_iban(value: Optional[str]) -> str:
    if not value:
        return MISSING
    compact: str = value.replace(" ", "")
    grouped: str = " ".join(compact[index : index + 4] for index in range(0, len(compact), 4))
    return _pdf_text(grouped)


def _format_amount(value: Optional[Decimal], currency: Optional[str]) -> str:
    if value is None:
        return MISSING
    number: str = _de_number(value)
    if currency:
        return f"{number} {_pdf_text(currency)}"
    return number


def _format_percent(value: Optional[Decimal]) -> str:
    if value is None:
        return MISSING
    if value == value.to_integral_value():
        return f"{int(value)} %"
    quantized: Decimal = value.quantize(Decimal("0.1"))
    text: str = f"{quantized}".replace(".", ",")
    return f"{text} %"


def _format_quantity(item: LineItem) -> str:
    if item.quantity is None:
        return MISSING
    quantity: Decimal = item.quantity
    if quantity == quantity.to_integral_value():
        text: str = str(int(quantity))
    else:
        text = f"{quantity}".replace(".", ",")
    if item.unit:
        return f"{text} {_pdf_text(item.unit)}"
    return text


def _de_number(value: Decimal) -> str:
    quantized: Decimal = value.quantize(Decimal("0.01"))
    negative: bool = quantized < 0
    absolute: Decimal = abs(quantized)
    raw: str = f"{absolute:.2f}"
    whole, fraction = raw.split(".")
    grouped: str = ""
    while len(whole) > 3:
        grouped = "." + whole[-3:] + grouped
        whole = whole[:-3]
    grouped = whole + grouped
    result: str = f"{grouped},{fraction}"
    return f"-{result}" if negative else result


def _document_title(invoice: InvoiceParseResponse) -> str:
    number: str = invoice.invoice_number or "ohne Nummer"
    return f"Lesbare Ansicht {number}"


def _unique_member_name(index: int, filename: str, used: set[str]) -> str:
    candidate: str = f"{index:02d}_{filename}"
    if candidate not in used:
        return candidate
    stem: str = filename[:-4] if filename.endswith(".pdf") else filename
    return f"{index:02d}_{stem}_{index}.pdf"

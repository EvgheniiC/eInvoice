from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from xml.etree.ElementTree import Element

from .xml_query import _text_or_none


def _tax_scheme_from_id_elem(id_elem: Optional[Element]) -> str:
    if id_elem is None:
        return ""
    scheme: Optional[str] = id_elem.get("schemeID")
    if scheme:
        return scheme.strip().upper()
    return ""


def extract_specified_tax_registration_vat_id(
    party: Optional[Element],
    prefer_schemes: Tuple[str, ...] = ("VA", "VAT"),
) -> Optional[str]:
    """
    Read SpecifiedTaxRegistration/ID from a RAM trade party.
    Prefer EU VAT scheme (VA/VAT); otherwise first non-empty registration ID.
    """
    if party is None:
        return None
    pairs: List[Tuple[str, str]] = []
    for reg in party.findall("SpecifiedTaxRegistration"):
        id_elem: Optional[Element] = reg.find("ID")
        if id_elem is None or not id_elem.text:
            continue
        pairs.append((_tax_scheme_from_id_elem(id_elem), id_elem.text.strip()))
    if not pairs:
        return None
    for pref in prefer_schemes:
        up: str = pref.strip().upper()
        for scheme, text in pairs:
            if scheme == up:
                return text
    return pairs[0][1]


def extract_seller_vat_id_zugferd(transaction_root: Optional[Element]) -> Optional[str]:
    """Seller VAT from ApplicableHeaderTradeAgreement/SellerTradeParty (VA preferred)."""
    if transaction_root is None:
        return None
    agr: Optional[Element] = transaction_root.find("./ApplicableHeaderTradeAgreement")
    if agr is None:
        return None
    seller: Optional[Element] = agr.find("SellerTradeParty")
    return extract_specified_tax_registration_vat_id(seller)


def extract_invoicee_or_buyer_vat_id(transaction_root: Optional[Element]) -> Optional[str]:
    """
    Recipient VAT: InvoiceeTradeParty if present, else BuyerTradeParty (VA preferred).
    """
    if transaction_root is None:
        return None
    settlement: Optional[Element] = transaction_root.find("./ApplicableHeaderTradeSettlement")
    if settlement is not None:
        invoicee: Optional[Element] = settlement.find("InvoiceeTradeParty")
        vid: Optional[str] = extract_specified_tax_registration_vat_id(invoicee)
        if vid:
            return vid
    agr: Optional[Element] = transaction_root.find("./ApplicableHeaderTradeAgreement")
    if agr is None:
        return None
    buyer: Optional[Element] = agr.find("BuyerTradeParty")
    return extract_specified_tax_registration_vat_id(buyer)


def extract_payment_means_list(element: Optional[Element]) -> List[Dict[str, Optional[str]]]:
    """
    Extract PaymentMeans / SpecifiedTradeSettlementPaymentMeans blocks.
    Each dict: PaymentMeansCode, PaymentID, AccountID, BranchID.
    """
    if element is None:
        return []
    result: List[Dict[str, Optional[str]]] = []
    for pm in element.findall(".//PaymentMeans"):
        code_elem: Optional[Element] = pm.find("PaymentMeansCode")
        pid_elem: Optional[Element] = pm.find("PaymentID")
        payee: Optional[Element] = pm.find("PayeeFinancialAccount")
        account_id: Optional[str] = None
        branch_id: Optional[str] = None
        if payee is not None:
            id_elem: Optional[Element] = payee.find("ID")
            account_id = _text_or_none(id_elem)
            branch: Optional[Element] = payee.find("FinancialInstitutionBranch")
            if branch is not None:
                branch_id_elem: Optional[Element] = branch.find("ID")
                if branch_id_elem is None:
                    fin_inst: Optional[Element] = branch.find("FinancialInstitution")
                    if fin_inst is not None:
                        branch_id_elem = fin_inst.find("ID")
                branch_id = _text_or_none(branch_id_elem)
        result.append(
            {
                "PaymentMeansCode": _text_or_none(code_elem),
                "PaymentID": _text_or_none(pid_elem),
                "AccountID": account_id,
                "BranchID": branch_id,
            }
        )

    settlement_payment_ref: Optional[str] = None
    settlement: Optional[Element] = element.find("./ApplicableHeaderTradeSettlement")
    if settlement is None:
        settlement = element.find(".//ApplicableHeaderTradeSettlement")
    if settlement is not None:
        settlement_payment_ref = _text_or_none(settlement.find("PaymentReference"))

    for pm in element.findall(".//SpecifiedTradeSettlementPaymentMeans"):
        type_code: Optional[str] = _text_or_none(pm.find("TypeCode"))
        info: Optional[str] = _text_or_none(pm.find("Information"))
        payment_ref_local: Optional[str] = _text_or_none(pm.find("PaymentReference"))
        payment_id_val: Optional[str] = payment_ref_local or settlement_payment_ref or info
        account_id = None
        branch_id = None
        payee_fin: Optional[Element] = pm.find("PayeePartyCreditorFinancialAccount")
        if payee_fin is not None:
            iban_el: Optional[Element] = payee_fin.find("IBANID")
            account_id = _text_or_none(iban_el)
            if account_id is None:
                account_id = _text_or_none(payee_fin.find("ProprietaryID"))
            if account_id:
                account_id = account_id.replace(" ", "")
        cred_fin: Optional[Element] = pm.find("PayeeSpecifiedCreditorFinancialInstitution")
        if cred_fin is not None:
            bic_el: Optional[Element] = cred_fin.find("BICID")
            branch_id = _text_or_none(bic_el)
        if branch_id is None and payee_fin is not None:
            pi_el: Optional[Element] = payee_fin.find("PaymentServiceProviderID")
            branch_id = _text_or_none(pi_el)
        result.append(
            {
                "PaymentMeansCode": type_code,
                "PaymentID": payment_id_val,
                "AccountID": account_id,
                "BranchID": branch_id,
            }
        )
    return result

# com.sixt.lib.python.eInvoice
[![Python Version 3.10.6](https://img.shields.io/badge/Python%20Version-3.10.6-informational.svg)](https://www.python.org/downloads/)

## System Information
- System: Darwin 24.5.0
- Python Version: 3.10.6



This Python script reads data from eInvoice files.
the script receives an XML file in str format, processes and finds data in it and returns it to the Chronos_new/chronox/eInvoice/eInvoice_start_extraction repository

## Setup

```shell
0 in com.sixt.lib.python.eInvoice -> source venv/bin/activate- > get (venv) "yousession" com.sixt.lib.python.eInvoice)
1 in com.sixt.lib.python.eInvoice ->(venv) python setup.py sdist
2 copy .tar.gz file from folder dist (for exam com.sixt.lib.python.eInvoice-0.1.tar.gz)
3 in Chronos_new repository -> chronox_extraction/eInvoice/eInvoice_repo, for exam com.sixt.lib.python.eInvoice-0.1.tar.gz
4 in Chronos_new repository in eInvoice/eInvoice_repo: 
5 pip uninstall com.sixt.lib.python.eInvoice
  Proceed (Y/n)? -> Y
6 pip install com.sixt.lib.python.eInvoice-0.1.tar.gz

```

## Usage

| Module                | Function                                                                                                            |
|-----------------------|---------------------------------------------------------------------------------------------------------------------|
| xml_parser_header     | - get_xml_header(xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger)-> read header data                      |
| xml_parser_positions  | - get_xml_positions(xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger) ->XmlInvoiceHeader get positions data|
| xml_pdf_extraction    | - extract_pdf_attachments(m_cn_id: str, data: dict, key: str), get_pdf_file(m_cn_id: str, xml_text: str)            |
| xml_vendor_parser     | - get_einvoice_vendor_data(m_cn_id: str, xml_text: str, logger)                                                                     |

### Configuration

After the functions are processed, the header will look like this:

```json
{'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None,
                          'HIGHWAY_ZEITSTEMPEL': None, 'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KREDITOR': None, 'M_IV_MANDANT': '1', 'M_IV_CONTRACTID': 'SX-00855',
                          'M_IV_ORDERID': None, 'M_IV_IBAN': 'DE95700400410228840500',
                          'M_IV_KINDOFINVOICE': 'RE', 'M_IV_INVOICENUMBER': '202510294',
                          'M_IV_COSTCENTER': None, 'M_IV_DAMAGENUMBER': None,
                          'M_IV_INVOICEDATE': datetime(2025, 1, 31, 0, 0),
                          'M_IV_DELIVERYDATE': datetime(2025, 1, 31, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 1, 31, 0, 0),
                          'M_IV_INVOICEAMOUNT': '227.50', 'M_IV_TOTALAMOUNT': '270.73',
                          'M_IV_TOTALTAXAMOUNT': '43.23', 'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXAMOUNT1': '43.23', 'M_IV_TAXRATE2': None, 'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXRATE3': None, 'M_IV_TAXAMOUNT3': None, 'M_IV_TAXRATE4': None,
                          'M_IV_TAXAMOUNT4': None, 'M_IV_TAXRATE5': None, 'M_IV_TAXAMOUNT5': None,
                          'M_IV_CURRENCY': 'EUR', 'M_IV_VIN': None, 'M_IV_EMPFAENGER': None,
                          'M_IV_CONTRACT_START': None, 'M_IV_CONTRACT_END': None,
                          'TRIGGER_HIGHWAY': '0', 'M_CN_MAIL_ID': None, 'EMAIL_NAME': None}
```

After the functions are processed, the positions will look like this:

```json
[{'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'Arbeitspreis', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.09995, 'M_IP_TOTALNETPRICE': 135.13, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Stromsteuer', 'M_IP_QUANTITY': 1352.0, 'M_IP_SINGLENETPRICE': 0.0205,
                           'M_IP_TOTALNETPRICE': 27.72, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Arbeitspreis Netz', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.0762, 'M_IP_TOTALNETPRICE': 103.02, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Leistungspreis Netz', 'M_IP_QUANTITY': 7.0,
                           'M_IP_SINGLENETPRICE': 22.36, 'M_IP_TOTALNETPRICE': 13.29, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Messkosten', 'M_IP_QUANTITY': 31.0, 'M_IP_SINGLENETPRICE': 98.5,
                           'M_IP_TOTALNETPRICE': 8.37, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'Entgelt fur Messstellenbetrieb,Messung', 'M_IP_QUANTITY': 31.0,
                           'M_IP_SINGLENETPRICE': 330.27, 'M_IP_TOTALNETPRICE': 28.05, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Kraft-Warme-Kopplung (KWK)', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.00277, 'M_IP_TOTALNETPRICE': 3.75, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 8,
                           'M_IP_POSITIONSTEXT': 'Aufschlag fur besondere Netznutzung', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.01558, 'M_IP_TOTALNETPRICE': 21.06, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Offshore-Umlage', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.00816, 'M_IP_TOTALNETPRICE': 11.03, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 10,
                           'M_IP_POSITIONSTEXT': 'Konzessionsabgabe Sonderkunde', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.0011, 'M_IP_TOTALNETPRICE': 1.49, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]
```


After the functions are processed, the vendor will look like this:

```json
{'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum Berlin',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum Berlin',
                          'S_KR_IBAN': 'DE55160500003504000405',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_ORT': 'Potsdam',
                          'S_KR_ORT_DELIVERY': 'Schnefeld',
                          'S_KR_POSTLEITZAHL': '14482',
                          'S_KR_POSTLEITZAHL_DELIVERY': '12529',
                          'S_KR_STRASSE': 'Fritz-Zubeil-Strae 70-78',
                          'S_KR_STRASSE_DELIVERY': 'Am Airport 7',
                          'S_KR_USTID': 'DE138410797'}
```
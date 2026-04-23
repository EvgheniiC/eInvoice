import unittest
from scr.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data
from unittest.mock import Mock
from scr.helper_functions.einvoice_helper import read_xml_file_to_str


class TestClientParser(unittest.TestCase):
    def test_get_einvoice_client_data(self):
        m_cn_id = "5208214"
        xml_text_from_xml = read_xml_file_to_str('xml_files/xml_text_from_xml.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_from_xml, logger=Mock())
        self.assertEqual(clients_data, {'M_CN_ID': '5208214',
                                        'S_KR_APPROVAL': None,
                                        'S_KR_BUDGET': None,
                                        'S_KR_BUYERREFERENCE': None,
                                        'S_KR_CLIENT_NAME': '[Buyer name]',
                                        'S_KR_CLIENT_NAME_BILLING': '[Buyer name]',
                                        'S_KR_CLIENT_NAME_DELIVERY': None,
                                        'S_KR_CONTACT': 'seller@email.de',
                                        'S_KR_EMPLOYEE_ID': None,
                                        'S_KR_IBAN': 'DE75512108001245126199',
                                        'S_KR_LAND': 'DE',
                                        'S_KR_PEPPOL_ID': None,
                                        'S_KR_LAND_BILLING': 'DE',
                                        'S_KR_LAND_DELIVERY': None,
                                        'S_KR_NAME1': '[Seller name]',
                                        'S_KR_ORT': '[Seller city]',
                                        'S_KR_ORT_BILLING': '[Buyer city]',
                                        'S_KR_ORT_DELIVERY': None,
                                        'S_KR_POSTLEITZAHL': '12345',
                                        'S_KR_POSTLEITZAHL_BILLING': '12345',
                                        'S_KR_POSTLEITZAHL_DELIVERY': None,
                                        'S_KR_STRASSE': '[Seller address line 1]',
                                        'S_KR_STRASSE_BILLING': '[Buyer address line 1]',
                                        'S_KR_STRASSE_DELIVERY': None,
                                        'S_KR_TRIP_INFO': None,
                                        'S_KR_TRIP_PURPOSE': None,
                                        'S_KR_USTID': 'DE 123456789',
                                        'S_KR_USTID_BILLING': None,
                                        'S_KR_VEHICLE_ID': None,
                                        'S_KR_VEHICLE_ODOMETER_READING': None,
                                        'S_KR_VEHICLE_REGISTRATION': None,
                                        'S_KR_CLIENT_NUMBER': 'Es gelten unsere Allgem. Geschftsbedingungen, die Sie unter [] finden..Die letzte Lieferung im Rahmen des abgerechneten Abonnements erfolgt in 12/2016 Lieferung erfolgt / erfolgte direkt vom Verlag',
                                        'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '58',
                                                                'PaymentID': None,
                                                                'AccountID': 'DE75512108001245126199',
                                                                'BranchID': None}]})
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_none(self):
        m_cn_id = "5208215"
        xml_text_none = read_xml_file_to_str('xml_files/xml_text_none.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_none, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5208215',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': '99000000-01514-29',
                          'S_KR_CLIENT_NAME': 'EntServDE',
                          'S_KR_CLIENT_NAME_BILLING': 'Deutsches Patent - und\n\t\t\t\t\tMarkenamt',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Anderer Leistungsempfnger',
                          'S_KR_CONTACT': 'kontakt@Rechnungssteller.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE84600400710561515801',
                          'S_KR_LAND': 'DK',
                          'S_KR_PEPPOL_ID': 'rechnungsausgang@test.com',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'EntServ Deutschland GmbH',
                          'S_KR_ORT': 'Ort Rechnungssteller',
                          'S_KR_ORT_BILLING': 'Ort Rechnungsempfnger',
                          'S_KR_ORT_DELIVERY': 'Anderer Leistungsempfnger Ort',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': 'DE84 6004 0071 0561 5158 01',
                                                  'BranchID': 'XXX0561515801',
                                                  'PaymentID': 'Verwendungszweck',
                                                  'PaymentMeansCode': '30'}],
                          'S_KR_POSTLEITZAHL': '12345',
                          'S_KR_POSTLEITZAHL_BILLING': '67890',
                          'S_KR_POSTLEITZAHL_DELIVERY': '45678',
                          'S_KR_STRASSE': 'Strae Rechnungssteller 1',
                          'S_KR_STRASSE_BILLING': 'Strae Rechnungsempfnger 1',
                          'S_KR_STRASSE_DELIVERY': 'Anderer Leistungsempfnger Strae 1',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'ATU13585627',
                          'S_KR_USTID_BILLING': '90000000-03083-12',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_all_data(self):
        m_cn_id = "5207492"
        xml_text_from_zugpferd = read_xml_file_to_str('xml_files/xml_text_from_zugpferd.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_from_zugpferd,
                                                          logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt SE',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt SE',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'XRechnung@kmlz.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_IBAN': 'DE95700400410228840500',
                          'S_KR_LAND': 'DE',
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_ORT': 'Munchen',
                          'S_KR_ORT_BILLING': 'Pullach',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_POSTLEITZAHL_BILLING': '82049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Unterer Anger 3',
                          'S_KR_STRASSE_BILLING': 'Zugspitzstr.1',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE814742004',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': 'Die in Ihrem Auftrag erbrachten Leistungen werden vereinbarungsgemass wie folgt abgerechnet:.Commerzbank Munchen IBAN: DE95700400410228840500 BIC: COBADEFFXXX.Bartel, Tim',
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '30',
                                                  'PaymentID': None,
                                                  'AccountID': 'DE95700400410228840500',
                                                  'BranchID': 'COBADEFFXXX'}]})
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_no(self):
        m_cn_id = "5207492"
        xml_test_iban_none = read_xml_file_to_str('xml_files/xml_test_iban_none.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_test_iban_none, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Verbrauchsstelle',
                          'S_KR_CONTACT': 'GKBetreuung@eon.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_IBAN': None,
                          'S_KR_LAND': 'DE',
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': 'DE',
                          'S_KR_NAME1': 'E.ON Energie Deutschland GmbH',
                          'S_KR_ORT': 'Landshut',
                          'S_KR_ORT_BILLING': '82049 Pullach',
                          'S_KR_ORT_DELIVERY': 'Koln',
                          'S_KR_POSTLEITZAHL': '84001',
                          'S_KR_POSTLEITZAHL_BILLING': '82049',
                          'S_KR_POSTLEITZAHL_DELIVERY': '50739',
                          'S_KR_STRASSE': 'Postfach 14 75',
                          'S_KR_STRASSE_BILLING': 'Zugspitzstr. 1',
                          'S_KR_STRASSE_DELIVERY': 'Robert-Perthel-Str. 26',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE259922663',
                          'S_KR_USTID_BILLING': 'DE223999470',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': 'Weitere Angaben zu §40 EnWG entnehmen Sie dem Papierbeleg.Die vor der Ausfuhrung der Leistung vereinnahmten Teilentgelte und die darauf entfallenden Steuerbetrage sind in Abschnitt 1 in der CSV-Datei im Anhang der E-Rechnung aufgefuhrt..Ihr neuer Abschlag und ein Uberblick der Falligkeiten fur das kommende Verbrauchsjahr sind in Abschnitt 2 in der CSV-Datei im Anhang der E-Rechnung aufgefuhrt..[Erlaeuterung, Datum, Art, Betrag Brutto].Abschlagszahlungen:20240123,gezahlte Abschlage Strom, 22.15;20240207,gezahlte Abschlage Strom, 13.85;20240306,gezahlte Abschlage Strom, 36.00;20240404,gezahlte Abschlage Strom, 36.00;20240503,gezahlte Abschlage Strom, 36.00;20240605,gezahlte Abschlage Strom, 36.00;20240703,gezahlte Abschlage Strom, 36.00;20240805,gezahlte Abschlage Strom, 36.00;20240904,gezahlte Abschlage Strom, 36.00;20241002,gezahlte Abschlage Strom, 36.00;20241106,gezahlte Abschlage Strom, 36.00;20241204,gezahlte Abschlage Strom, 36.00;.[Erlaeuterung, Zahlernummer, Datum-Von, Datum-Bis, Zahlerstand-von, Zahlerstand-bis, Faktor, Verbrauch].Zaehlerstaende:12247797,20240101,20240528,224481,224589,108,1;  1APA0184432582,20240529,20241231,1,181,180,1;.[Erlaeuterung, Datum, Betrag].Abschlagsplan:20250506, 26.00;20250606, 26.00;20250707, 26.00;20250806, 26.00;20250908, 26.00;20251006, 26.00;20251106, 26.00;20251208, 26.00;',
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '30',
                                                  'PaymentID': '232081412135',
                                                  'AccountID': None,
                                                  'BranchID': None}]})
        self.assertEqual(supplier, '')

    # not zugpferd, only XML file
    def test_get_einvoice_client_data_not_zugpferd(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/clear_xml_from_gerd.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': 'Bestellung SIXT-000000025218',
                          'S_KR_CLIENT_NAME': None,
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'inspire-buchhaltung@mrknow.ai',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE13664900000023969700',
                          'S_KR_LAND': 'DE',
                          'S_KR_PEPPOL_ID': 'inspire-buchhaltung@mrknow.ai',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Inspire Technologies GmbH',
                          'S_KR_ORT': 'St. Georgen',
                          'S_KR_ORT_BILLING': 'Pullach',
                          'S_KR_ORT_DELIVERY': 'St. Georgen',
                          'S_KR_POSTLEITZAHL': '78112',
                          'S_KR_POSTLEITZAHL_BILLING': '82049',
                          'S_KR_POSTLEITZAHL_DELIVERY': '78112',
                          'S_KR_STRASSE': 'Leopoldstr. 1',
                          'S_KR_STRASSE_BILLING': 'Zugspitzstrasse 1',
                          'S_KR_STRASSE_DELIVERY': 'Leopoldstr. 1',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE260569738',
                          'S_KR_USTID_BILLING': 'DE234567890',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None,
                          'S_KR_PAYMENT_MEANS': [
                              {'PaymentMeansCode': '58', 'PaymentID': '3250124002',
                               'AccountID': 'DE13664900000023969700', 'BranchID': 'GENODE61OG1'}
                          ]})

        self.assertEqual(supplier, None)

    def test_get_einvoice_client_10(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_test_mandant_10.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt SE',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt SE',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'XRechnung@kmlz.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE95700400410228840500',
                          'S_KR_LAND': 'DE',
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_ORT': 'Munchen',
                          'S_KR_ORT_BILLING': 'Pullach',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_POSTLEITZAHL_BILLING': '82049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Unterer Anger 3',
                          'S_KR_STRASSE_BILLING': 'Zugspitzstr.1',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE814742004',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': 'Die in Ihrem Auftrag erbrachten Leistungen werden vereinbarungsgemass wie folgt abgerechnet:.Commerzbank Munchen IBAN: DE95700400410228840500 BIC: COBADEFFXXX.Bartel, Tim',
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '30',
                                                  'PaymentID': None,
                                                  'AccountID': 'DE95700400410228840500',
                                                  'BranchID': 'COBADEFFXXX'}]})

        self.assertEqual(supplier, None)

    def test_get_einvoice_SWFM_5490(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_text_find_VIN_USTD_SWFM-5490.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': 'KUNDE',
                          'S_KR_CLIENT_NAME': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum '
                                                      'Berlin',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum '
                                                       'Berlin',
                          'S_KR_CONTACT': 'service@autohaus-babelsberg.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE55160500003504000405',
                          'S_KR_LAND': 'DE',
                          'S_KR_PEPPOL_ID': 'DE138410797',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_ORT': 'Potsdam',
                          'S_KR_ORT_BILLING': 'Schnefeld',
                          'S_KR_ORT_DELIVERY': 'Schnefeld',
                          'S_KR_POSTLEITZAHL': '14482',
                          'S_KR_POSTLEITZAHL_BILLING': '12529',
                          'S_KR_POSTLEITZAHL_DELIVERY': '12529',
                          'S_KR_STRASSE': 'Fritz-Zubeil-Strae 70-78',
                          'S_KR_STRASSE_BILLING': 'Am Airport 7',
                          'S_KR_STRASSE_DELIVERY': 'Am Airport 7',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE138410797',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None,
                          'S_KR_PAYMENT_MEANS': [
                              {'PaymentMeansCode': '30', 'PaymentID': None,
                               'AccountID': 'DE55160500003504000405', 'BranchID': None}
                          ]})

        self.assertEqual(supplier, None)

    def test_get_einvoice_85018982AutohausBabelsberg(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/85018982AutohausBabelsberg.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': 'KUNDE',
                          'S_KR_CLIENT_NAME': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum '
                                                      'Berlin',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum '
                                                       'Berlin',
                          'S_KR_CONTACT': 'service@autohaus-babelsberg.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE55160500003504000405',
                          'S_KR_LAND': 'DE',
                          'S_KR_PEPPOL_ID': 'DE138410797',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_ORT': 'Potsdam',
                          'S_KR_ORT_BILLING': 'Schnefeld',
                          'S_KR_ORT_DELIVERY': 'Schnefeld',
                          'S_KR_POSTLEITZAHL': '14482',
                          'S_KR_POSTLEITZAHL_BILLING': '12529',
                          'S_KR_POSTLEITZAHL_DELIVERY': '12529',
                          'S_KR_STRASSE': 'Fritz-Zubeil-Strae 70-78',
                          'S_KR_STRASSE_BILLING': 'Am Airport 7',
                          'S_KR_STRASSE_DELIVERY': 'Am Airport 7',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE138410797',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None,
                          'S_KR_PAYMENT_MEANS': [
                              {'PaymentMeansCode': '30', 'PaymentID': None,
                               'AccountID': 'DE55160500003504000405', 'BranchID': None}
                          ]})

        self.assertEqual(supplier, None)

    def test_get_einvoice_85000159(self):
        m_cn_id = "7697763"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/85000159.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '7697763',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'buchhaltung@asd-offenbach.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE36512500000001178040',
                          'S_KR_LAND': 'DE',
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Abschleppdienst Offenbach GmbH',
                          'S_KR_ORT': 'Offenbach am Main',
                          'S_KR_ORT_BILLING': 'Rostock',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '63069',
                          'S_KR_POSTLEITZAHL_BILLING': '18049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Sprendlinger Landstrae 167',
                          'S_KR_STRASSE_BILLING': None,
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE113527818',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': 'M-BW 5472 BMW 520d',
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '58',
                                                  'PaymentID': 'OF-R2517108',
                                                  'AccountID': 'DE36512500000001178040',
                                                  'BranchID': 'HELADEF1TSK'}]})

        self.assertEqual(supplier, None)

    # HW_5648
    def test_get_einvoice_HW_5648(self):
        m_cn_id = "5209222"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_text_SAP_BE_HW_5648.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5209222',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'BuyerTradingName AS',
                          'S_KR_CLIENT_NAME_BILLING': None,
                          'S_KR_CLIENT_NAME_DELIVERY': 'Delivery party Name',
                          'S_KR_CONTACT': None,
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': None,
                          'S_KR_LAND': 'GB',
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'SupplierTradingName Ltd.',
                          'S_KR_ORT': 'London',
                          'S_KR_ORT_BILLING': None,
                          'S_KR_ORT_DELIVERY': 'Stockholm',
                          'S_KR_POSTLEITZAHL': 'GB 123 EW',
                          'S_KR_POSTLEITZAHL_BILLING': None,
                          'S_KR_POSTLEITZAHL_DELIVERY': '21234',
                          'S_KR_STRASSE': 'Main street 1',
                          'S_KR_STRASSE_BILLING': None,
                          'S_KR_STRASSE_DELIVERY': 'Delivery street 2',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'GB1232434',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None,
                          'S_KR_PAYMENT_MEANS': [
                              {'PaymentMeansCode': '30', 'PaymentID': 'Snippet1',
                               'AccountID': 'IBAN32423940', 'BranchID': 'BIC324098'}
                          ]})

        self.assertEqual(supplier, '99887766')

    def test_get_einvoice_sap(self):
        m_cn_id = "5209222"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/first_sap.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5209222',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': '5197871',
                          'S_KR_CLIENT_NAME': 'SOCIAAL SECRETARIAAT VZW',
                          'S_KR_CLIENT_NAME_BILLING': 'BV SIXT BELGIUM',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': None,
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'BE64734003185952',
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '0473329910',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'SOCIAAL SECRETARIAAT VZW',
                          'S_KR_ORT': 'Leuven',
                          'S_KR_ORT_BILLING': 'MACHELEN',
                          'S_KR_ORT_DELIVERY': 'Leuven',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': 'BE64734003185952',
                                                  'BranchID': None,
                                                  'PaymentID': '+++004/4123/71362+++',
                                                  'PaymentMeansCode': '42'}],
                          'S_KR_POSTLEITZAHL': '3000',
                          'S_KR_POSTLEITZAHL_BILLING': '1831',
                          'S_KR_POSTLEITZAHL_DELIVERY': '3000',
                          'S_KR_STRASSE': 'Diestsepoort 1',
                          'S_KR_STRASSE_BILLING': 'KOUTERVELDSTRAAT 6/C',
                          'S_KR_STRASSE_DELIVERY': 'Diestsepoort 1',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0473329910',
                          'S_KR_USTID_BILLING': '0465341266',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    # HW-5825
    def test_get_client_address(self):
        m_cn_id = "7983677"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/adressedesLiferanten.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '7983677',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': 'N/A',
                          'S_KR_CLIENT_NAME': 'Ac Brussels NV',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt Belgium Bv',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'BE0821129645@xpower.be',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'BE09363065981157',
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '0821129645',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Ac Brussels NV',
                          'S_KR_ORT': 'Zaventem',
                          'S_KR_ORT_BILLING': 'Machelen',
                          'S_KR_ORT_DELIVERY': 'Zaventem',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': 'BE09363065981157',
                                                  'BranchID': 'BBRUBEBB',
                                                  'PaymentID': '+++900/3711/10695+++',
                                                  'PaymentMeansCode': '42'}],
                          'S_KR_POSTLEITZAHL': '1930',
                          'S_KR_POSTLEITZAHL_BILLING': '1830',
                          'S_KR_POSTLEITZAHL_DELIVERY': '1930',
                          'S_KR_STRASSE': 'Leuvensesteenweg 430',
                          'S_KR_STRASSE_BILLING': 'Kouterveldstraat 6',
                          'S_KR_STRASSE_DELIVERY': 'Leuvensesteenweg 430',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0821129645',
                          'S_KR_USTID_BILLING': '0465341266',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    # HW-5851
    def test_get_employee(self):
        m_cn_id = "7980166"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/cc_budget_and_another.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '7980166',
                          'S_KR_APPROVAL': '10001036866',
                          'S_KR_BUDGET': '41872 - TRAVEL TRAINEES',
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Egencia Belgium',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt Belgium BV',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': None,
                          'S_KR_EMPLOYEE_ID': '9000052024',
                          'S_KR_IBAN': None,
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '0403266810',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Egencia Belgium',
                          'S_KR_ORT': 'Brussels',
                          'S_KR_ORT_BILLING': 'Zaventem',
                          'S_KR_ORT_DELIVERY': 'Brussels',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': None,
                                                  'BranchID': None,
                                                  'PaymentID': None,
                                                  'PaymentMeansCode': '48'}],
                          'S_KR_POSTLEITZAHL': '1000',
                          'S_KR_POSTLEITZAHL_BILLING': '1930',
                          'S_KR_POSTLEITZAHL_DELIVERY': '1000',
                          'S_KR_STRASSE': None,
                          'S_KR_STRASSE_BILLING': None,
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': 'Branch Support/Different Work Location',
                          'S_KR_TRIP_PURPOSE': 'NO',
                          'S_KR_USTID': 'BE0403266810',
                          'S_KR_USTID_BILLING': 'BE0465341266',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    # HW-5851
    def test_get_bayer_reference(self):
        m_cn_id = "7973848"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/buyerreference.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '7973848',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': '2HER88505632',
                          'S_KR_CLIENT_NAME': 'LOUYET AUTOMOTIVE SOUTH',
                          'S_KR_CLIENT_NAME_BILLING': 'SIXT BELGIUM BV',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'info@louyet.be',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'BE62260003045061',
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '0757976014',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'LOUYET AUTOMOTIVE SOUTH',
                          'S_KR_ORT': 'Charleroi',
                          'S_KR_ORT_BILLING': 'Diegem',
                          'S_KR_ORT_DELIVERY': 'MACHELEN',
                          'S_KR_POSTLEITZAHL': '6000',
                          'S_KR_POSTLEITZAHL_BILLING': '1831',
                          'S_KR_POSTLEITZAHL_DELIVERY': '1831',
                          'S_KR_STRASSE': 'Rue de Mons 80',
                          'S_KR_STRASSE_BILLING': 'Kouterveldstraat 6C',
                          'S_KR_STRASSE_DELIVERY': 'Kouterveldstraat 6c',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0757976014',
                          'S_KR_USTID_BILLING': 'BE0465341266',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_PAYMENT_MEANS': [
                              {'PaymentMeansCode': '30', 'PaymentID': '340600035974',
                               'AccountID': 'BE62260003045061', 'BranchID': 'GEBABEBB'}
                          ],
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    def test_get_sixt_adress(self):
        m_cn_id = "7973848"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/sixt_adress.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '7973848',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': '9600556384 VV9721',
                          'S_KR_CLIENT_NAME': 'Geevers Auto Parts Belgium NV',
                          'S_KR_CLIENT_NAME_BILLING': 'BV SIXT BELGIUM',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'info@geevers.be',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'BE36733023702281',
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '0870392282',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Geevers Auto Parts Belgium NV',
                          'S_KR_ORT': 'Hamont-Achel',
                          'S_KR_ORT_BILLING': 'Machelen',
                          'S_KR_ORT_DELIVERY': 'Aarschot',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': 'BE36733023702281',
                                                  'BranchID': 'KREDBEBB',
                                                  'PaymentID': None,
                                                  'PaymentMeansCode': '57'}],
                          'S_KR_POSTLEITZAHL': '3930',
                          'S_KR_POSTLEITZAHL_BILLING': '1831',
                          'S_KR_POSTLEITZAHL_DELIVERY': '3200',
                          'S_KR_STRASSE': 'Nijverheidsstraat',
                          'S_KR_STRASSE_BILLING': 'Kouterveldstraat 6c',
                          'S_KR_STRASSE_DELIVERY': 'Nieuwlandlaan 5',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0870392282',
                          'S_KR_USTID_BILLING': '419261',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    def test_get_contact(self):
        m_cn_id = "8000039"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/contact.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '8000039',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': '9600484818 /',
                          'S_KR_CLIENT_NAME': 'QTeam Services NV',
                          'S_KR_CLIENT_NAME_BILLING': 'SIXT BELGIUM BV',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'Admin.sintniklaas@qteam.be',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'BE69393042417078',
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '5488888216563',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'QTeam Services NV',
                          'S_KR_ORT': 'Zellik',
                          'S_KR_ORT_BILLING': 'Diegem',
                          'S_KR_ORT_DELIVERY': 'Zellik',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': 'BE69393042417078',
                                                  'BranchID': 'BBRUBEBB',
                                                  'PaymentID': '+++001/9620/02226+++',
                                                  'PaymentMeansCode': '42'}],
                          'S_KR_POSTLEITZAHL': '1731',
                          'S_KR_POSTLEITZAHL_BILLING': '1831',
                          'S_KR_POSTLEITZAHL_DELIVERY': '1731',
                          'S_KR_STRASSE': 'Z. 3 DOORNVELD 60',
                          'S_KR_STRASSE_BILLING': 'KOUTERVELDSTRAAT 6 C',
                          'S_KR_STRASSE_DELIVERY': 'Z. 3 DOORNVELD 60',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0452263488',
                          'S_KR_USTID_BILLING': '0465341266',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    def test_get_additional_info(self):
        m_cn_id = "8000039"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/additions_info.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '8000039',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': 'F-5073-2026-217',
                          'S_KR_CLIENT_NAME': 'Midas Rhodes',
                          'S_KR_CLIENT_NAME_BILLING': 'SIXT BELGIUM',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'sint-genesius-rode@midasbelgium.net',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': None,
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': '0423518034',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'Midas Rhodes',
                          'S_KR_ORT': 'Rhode-Saint-Genese',
                          'S_KR_ORT_BILLING': 'DIEGEM',
                          'S_KR_ORT_DELIVERY': 'Rhode-Saint-Genese',
                          'S_KR_PAYMENT_MEANS': [],
                          'S_KR_POSTLEITZAHL': '1640',
                          'S_KR_POSTLEITZAHL_BILLING': '1831',
                          'S_KR_POSTLEITZAHL_DELIVERY': '1640',
                          'S_KR_STRASSE': 'Chaussée de Hal 28',
                          'S_KR_STRASSE_BILLING': '6C KOUTERVELDSTRAAT',
                          'S_KR_STRASSE_DELIVERY': 'Chaussée de Hal 28',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0423518034',
                          'S_KR_USTID_BILLING': '0465341266',
                          'S_KR_VEHICLE_ID': 'VXFVLEHS2S7800434',
                          'S_KR_VEHICLE_ODOMETER_READING': '37991',
                          'S_KR_VEHICLE_REGISTRATION': '2GHA914',
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    # HW-5938
    def test_get_ergenzungen(self):
        m_cn_id = "8000039"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/ergenzungen_HW-5938.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '8000039',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'AG BXL',
                          'S_KR_CLIENT_NAME_BILLING': 'SIXT BELGIUM BV',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'info.autoglassbxl@gmail.com',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'BE30363136136611',
                          'S_KR_LAND': 'BE',
                          'S_KR_PEPPOL_ID': 'BE0554904534',
                          'S_KR_LAND_BILLING': None,
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'AG BXL',
                          'S_KR_ORT': 'Evere',
                          'S_KR_ORT_BILLING': 'Machelen (Brab.)',
                          'S_KR_ORT_DELIVERY': 'Evere',
                          'S_KR_PAYMENT_MEANS': [{'AccountID': 'BE30363136136611',
                                                  'BranchID': 'BBRUBEBB',
                                                  'PaymentID': '+++002/0260/04240+++',
                                                  'PaymentMeansCode': '1'}],
                          'S_KR_POSTLEITZAHL': '1140',
                          'S_KR_POSTLEITZAHL_BILLING': '1831',
                          'S_KR_POSTLEITZAHL_DELIVERY': '1140',
                          'S_KR_STRASSE': 'Haachtsesteenweg 1018',
                          'S_KR_STRASSE_BILLING': 'Kouterveldstraat 6 bus C',
                          'S_KR_STRASSE_DELIVERY': 'Haachtsesteenweg 1018',
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'BE0554904534',
                          'S_KR_USTID_BILLING': '0465341266',
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    def test_get_payment_means_from_ergenzungen(self):
        """Test extraction of PaymentMeans list from ergenzungen_HW-5938.xml (cac:PaymentMeans block)."""
        m_cn_id = "8000039"
        xml_text = read_xml_file_to_str('xml_files/ergenzungen_HW-5938.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text, logger=Mock())
        payment_means = clients_data.get("S_KR_PAYMENT_MEANS")
        self.assertIsInstance(payment_means, list)
        self.assertEqual(len(payment_means), 1)
        row = payment_means[0]
        self.assertEqual(row["PaymentMeansCode"], "1")
        self.assertEqual(row["PaymentID"], "+++002/0260/04240+++")
        self.assertEqual(row["AccountID"], "BE30363136136611")
        self.assertEqual(row["BranchID"], "BBRUBEBB")

    # HW-5930
    def test_get_ergenzungen_44101357(self):
        m_cn_id = "8055132"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/HW-5930_44101357.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '8055132',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'kfz-technik@mtautoshop.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE87215400600211221700',
                          'S_KR_LAND': 'DE',
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'MT Autoshop UG(haftungsbeschrankt)',
                          'S_KR_ORT': 'Sieverstedt',
                          'S_KR_ORT_BILLING': 'Rostock',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '30',
                                                  'PaymentID': None,
                                                  'AccountID': 'DE87215400600211221700',
                                                  'BranchID': None}],
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_POSTLEITZAHL': '24885',
                          'S_KR_POSTLEITZAHL_BILLING': '18049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Schleswiger Strasse 9',
                          'S_KR_STRASSE_BILLING': 'Reparaturen',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE317971502',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': None})

        self.assertEqual(supplier, None)

    # HW-5930
    def test_get_ergenzungen_44101466(self):
        m_cn_id = "8057845"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/HW-5930_44101466.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd,
                                                          logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '8057845',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'kfz-technik@mtautoshop.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE87215400600211221700',
                          'S_KR_LAND': 'DE',
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'MT Autoshop UG(haftungsbeschrankt)',
                          'S_KR_ORT': 'Sieverstedt',
                          'S_KR_ORT_BILLING': 'Rostock',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '30',
                                                  'PaymentID': None,
                                                  'AccountID': 'DE87215400600211221700',
                                                  'BranchID': None}],
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_POSTLEITZAHL': '24885',
                          'S_KR_POSTLEITZAHL_BILLING': '18049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Schleswiger Strasse 9',
                          'S_KR_STRASSE_BILLING': 'Reparaturen',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE317971502',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': 'Motorolfilter erneuern\nMotorol erneuern\nDichtring fur Olablassschraube\n                        erneuern'})

        self.assertEqual(supplier, None)

    # HW-5930
    def test_get_ergenzungen_44101664(self):
        m_cn_id = "8064923"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/HW-5930_44101664.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd,
                                                          logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '8064923',
                          'S_KR_APPROVAL': None,
                          'S_KR_BUDGET': None,
                          'S_KR_BUYERREFERENCE': None,
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_CONTACT': 'kfz-technik@mtautoshop.de',
                          'S_KR_EMPLOYEE_ID': None,
                          'S_KR_IBAN': 'DE87215400600211221700',
                          'S_KR_LAND': 'DE',
                          'S_KR_LAND_BILLING': 'DE',
                          'S_KR_LAND_DELIVERY': None,
                          'S_KR_NAME1': 'MT Autoshop UG(haftungsbeschrankt)',
                          'S_KR_ORT': 'Sieverstedt',
                          'S_KR_ORT_BILLING': 'Rostock',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_PAYMENT_MEANS': [{'PaymentMeansCode': '30',
                                                  'PaymentID': None,
                                                  'AccountID': 'DE87215400600211221700',
                                                  'BranchID': None}],
                          'S_KR_PEPPOL_ID': None,
                          'S_KR_POSTLEITZAHL': '24885',
                          'S_KR_POSTLEITZAHL_BILLING': '18049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Schleswiger Strasse 9',
                          'S_KR_STRASSE_BILLING': 'Reparaturen',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_TRIP_INFO': None,
                          'S_KR_TRIP_PURPOSE': None,
                          'S_KR_USTID': 'DE317971502',
                          'S_KR_USTID_BILLING': None,
                          'S_KR_VEHICLE_ID': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None,
                          'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_CLIENT_NUMBER': 'Auftragsnummer: 9600614865\nSchaden-Nr.: \nKennzeichen: M- JP 1461\nvon: Sixt\n                        Celle \nnach: Stellantis Nedderfeld Hamburg'})

        self.assertEqual(supplier, None)

    # HW-5930
    def test_get_ergenzungen_44138108_add_client_number(self):
        m_cn_id = "8206925"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/HW-5930_add_client_number.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd,
                                                          logger=Mock())

        self.assertEqual(clients_data,
                         {'M_CN_ID': '8206925', 'S_KR_NAME1': 'R-TECH AUTOGLAS GMBH',
                          'S_KR_STRASSE': 'Lebacherstrae 123', 'S_KR_STRASSE_DELIVERY': None, 'S_KR_ORT': 'Saarbrcken',
                          'S_KR_ORT_DELIVERY': None, 'S_KR_POSTLEITZAHL': '66113', 'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_LAND': 'DE', 'S_KR_LAND_DELIVERY': None, 'S_KR_USTID': 'DE451426873',
                          'S_KR_USTID_BILLING': 'DE223999470',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH Co. Autovermietung KG Reparaturen',
                          'S_KR_CLIENT_NAME_DELIVERY': None, 'S_KR_IBAN': 'DE67100179977977328460',
                          'S_KR_EMPLOYEE_ID': None, 'S_KR_BUDGET': None, 'S_KR_TRIP_INFO': None, 'S_KR_APPROVAL': None,
                          'S_KR_TRIP_PURPOSE': None, 'S_KR_BUYERREFERENCE': None,
                          'S_KR_CONTACT': 'info@r-tech-autoglas.de',
                          'S_KR_CLIENT_NAME_BILLING': 'Sixt GmbH Co. Autovermietung KG Reparaturen',
                          'S_KR_STRASSE_BILLING': None, 'S_KR_POSTLEITZAHL_BILLING': '18049',
                          'S_KR_ORT_BILLING': 'Rostock', 'S_KR_LAND_BILLING': 'DE', 'S_KR_VEHICLE_REGISTRATION': None,
                          'S_KR_VEHICLE_ODOMETER_READING': None, 'S_KR_VEHICLE_ID': None, 'S_KR_PAYMENT_MEANS': [
                             {'PaymentMeansCode': '42', 'PaymentID': None, 'AccountID': 'DE67100179977977328460',
                              'BranchID': 'HOLVDEB1XXX'}], 'S_KR_PEPPOL_ID': None,
                          'S_KR_CLIENT_NUMBER': 'Kunde-Nr.: 6790.Kunde-ID.: 9700.Der Kunde ist vorsteuerabzugsberechtigt..KFZ-Kennz.: M - JP 2960.Fahrgestell-Nr.: WVGZZZR4XSW027614.Modellbezeichnung: VW TIGUAN III.Kilometerstand: 14925.Geschftsfhrer: Bahram Rahmati.Handelsregister: HRB 110802.Registergericht: Saarbrcken.USt-IdNr: DE451426873.Steuernummer: 040/117/01987.Bankverbindung: Holvi IBAN: DE67 1001 7997 7977 3284 60 BIC: HOLVDEB1XXX.Rechnungsanteil Kunde - 610.64'}
                         )

        self.assertEqual(supplier, '')


if __name__ == '__main__':
    unittest.main()

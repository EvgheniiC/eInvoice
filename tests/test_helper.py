# all XML variables are stored here in string format for tests

xml_text_from_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:BusinessProcessSpecifiedDocumentContextParameter>
            <ram:ID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</ram:ID>
        </ram:BusinessProcessSpecifiedDocumentContextParameter>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>123456XX</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">Dies ist kein Datum</udt:DateTimeString>
        </ram:IssueDateTime>
        <ram:IncludedNote>
            <ram:Content>Es gelten unsere Allgem. Geschftsbedingungen, die Sie unter [] finden.</ram:Content>
            <ram:SubjectCode>ADU</ram:SubjectCode>
        </ram:IncludedNote>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>Zeitschrift [...]</ram:LineID>
                <ram:IncludedNote>
                    <ram:Content>Die letzte Lieferung im Rahmen des abgerechneten Abonnements erfolgt in 12/2016 Lieferung erfolgt / erfolgte direkt vom Verlag</ram:Content>
                </ram:IncludedNote>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:SellerAssignedID>246</ram:SellerAssignedID>
                <ram:Name>Zeitschrift [...]</ram:Name>
                <ram:Description>Zeitschrift Inland</ram:Description>
                <ram:DesignatedProductClassification>
                    <ram:ClassCode listID="IB">0721-880X</ram:ClassCode>
                </ram:DesignatedProductClassification>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:BuyerOrderReferencedDocument>
                    <ram:LineID>6171175.1</ram:LineID>
                </ram:BuyerOrderReferencedDocument>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>288.79</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="XPP">1</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>7</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:BillingSpecifiedPeriod>
                    <ram:StartDateTime>
                        <udt:DateTimeString format="102">20160101</udt:DateTimeString>
                    </ram:StartDateTime>
                    <ram:EndDateTime>
                        <udt:DateTimeString format="102">20161231</udt:DateTimeString>
                    </ram:EndDateTime>
                </ram:BillingSpecifiedPeriod>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>288.79</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>Porto + Versandkosten</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:Name>Porto + Versandkosten</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>26.07</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="XPP">1</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>7</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>26.07</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>04011000-12345-03</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>[Seller name]</ram:Name>
                <ram:Description>123/456/7890, HRA-Eintrag in []</ram:Description>
                <ram:SpecifiedLegalOrganization>
                    <ram:ID>[HRA-Eintrag]</ram:ID>
                    <ram:TradingBusinessName>[Seller trading name]</ram:TradingBusinessName>
                </ram:SpecifiedLegalOrganization>
                <ram:DefinedTradeContact>
                    <ram:PersonName>nicht vorhanden</ram:PersonName>
                    <ram:TelephoneUniversalCommunication>
                        <ram:CompleteNumber>+49 1234-5678</ram:CompleteNumber>
                    </ram:TelephoneUniversalCommunication>
                    <ram:EmailURIUniversalCommunication>
                        <ram:URIID>seller@email.de</ram:URIID>
                    </ram:EmailURIUniversalCommunication>
                </ram:DefinedTradeContact>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>12345</ram:PostcodeCode>
                    <ram:LineOne>[Seller address line 1]</ram:LineOne>
                    <ram:CityName>[Seller city]</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:URIUniversalCommunication>
                    <ram:URIID schemeID="EM">seller@seller.com</ram:URIID>
                </ram:URIUniversalCommunication>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE 123456789</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:ID>[Buyer identifier]</ram:ID>
                <ram:Name>[Buyer name]</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>12345</ram:PostcodeCode>
                    <ram:LineOne>[Buyer address line 1]</ram:LineOne>
                    <ram:CityName>[Buyer city]</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:URIUniversalCommunication>
                    <ram:URIID schemeID="EM">buyer@buyer.com</ram:URIID>
                </ram:URIUniversalCommunication>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeDelivery/>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementPaymentMeans>
                <ram:TypeCode>58</ram:TypeCode>
                <ram:PayeePartyCreditorFinancialAccount>
                    <!-- dies ist eine nicht existerende aber valide IBAN als test dummy -->
                    <ram:IBANID>DE75512108001245126199</ram:IBANID>
                </ram:PayeePartyCreditorFinancialAccount>
            </ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>22.04</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>314.86</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>7</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradePaymentTerms>
                <ram:Description>Zahlbar sofort ohne Abzug.</ram:Description>
            </ram:SpecifiedTradePaymentTerms>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>314.86</ram:LineTotalAmount>
                <ram:TaxBasisTotalAmount>314.86</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">22.04</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>336.9</ram:GrandTotalAmount>
                <ram:DuePayableAmount>336.9</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""

xml_text_none = """<?xml version="1.0" encoding="UTF-8"?>

<!-- This is just a technical example it does not reflect any busines case and hence might not reflect anything real -->
<ns0:Invoice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:cec="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:ns0="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">
    <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
    <cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID>
    <cbc:ID>1234567890</cbc:ID>
    <cbc:IssueDate>2018-10-15</cbc:IssueDate>
    <cbc:DueDate>2018-10-29</cbc:DueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:Note>Bemerkung zu der Rechnung gibt es nicht, da dies eine Testrechnung
		ist.</cbc:Note>
    <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
    <cbc:BuyerReference>99000000-01514-29</cbc:BuyerReference>
    <cac:InvoicePeriod>
        <cbc:StartDate>2018-10-01</cbc:StartDate>
        <cbc:EndDate>2018-10-23</cbc:EndDate>
    </cac:InvoicePeriod>
    <cac:OrderReference>
        <cbc:ID>2345678901</cbc:ID>
        <cbc:SalesOrderID>Auftragsreferenz</cbc:SalesOrderID>
    </cac:OrderReference>
    <cac:BillingReference>
        <cac:InvoiceDocumentReference>
            <cbc:ID>PRG1502168</cbc:ID>
            <cbc:IssueDate>2018-10-13</cbc:IssueDate>
        </cac:InvoiceDocumentReference>
    </cac:BillingReference>
    <cac:OriginatorDocumentReference>
        <cbc:ID>Vergabe-und Losreferenz</cbc:ID>
    </cac:OriginatorDocumentReference>
    <cac:ContractDocumentReference>
        <cbc:ID>Vertragsreferenz</cbc:ID>
    </cac:ContractDocumentReference>
    <cac:AdditionalDocumentReference>
        <cbc:ID>Dokument Referenz</cbc:ID>
        <cbc:DocumentDescription>Beschreibung der angehngten JPG-Datei</cbc:DocumentDescription>
    </cac:AdditionalDocumentReference>
    <cac:AdditionalDocumentReference>
        <cbc:ID>Kennung des Objekts</cbc:ID>
        <cbc:DocumentDescription>ATS</cbc:DocumentDescription>
    </cac:AdditionalDocumentReference>
    <!-- BT-11 -->
    <cac:ProjectReference>
        <cbc:ID>Projektreferenz</cbc:ID>
    </cac:ProjectReference>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cbc:EndpointID schemeID="EM">rechnungsausgang@test.com</cbc:EndpointID>
            <cac:PartyIdentification>
                <cbc:ID schemeID="0013">987654321</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyIdentification>
                <cbc:ID schemeID="0013">987654320</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>EntServDE</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Strae Rechnungssteller 1</cbc:StreetName>
                <cbc:AdditionalStreetName>Erweiterte Anschrift
					Rechnungssteller</cbc:AdditionalStreetName>
                <cbc:CityName>Ort Rechnungssteller</cbc:CityName>
                <cbc:PostalZone>12345</cbc:PostalZone>
                <cbc:CountrySubentity>Bundesland Rechnungssteller</cbc:CountrySubentity>
                <cac:Country>
                    <cbc:IdentificationCode>DK</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>ATU13585627</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>456</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>AAA</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>EntServ Deutschland GmbH</cbc:RegistrationName>
                <cbc:CompanyID schemeID="0198">123456789</cbc:CompanyID>
                <cbc:CompanyLegalForm>Weitere rechtliche
					Informationen</cbc:CompanyLegalForm>
            </cac:PartyLegalEntity>
            <cac:Contact>
                <cbc:Name>EntServ Deutschland</cbc:Name>
                <cbc:Telephone>0123 456789</cbc:Telephone>
                <cbc:ElectronicMail>kontakt@Rechnungssteller.de</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cbc:EndpointID schemeID="EM">rechnungseingang@test.de</cbc:EndpointID>
            <cac:PartyIdentification>
                <cbc:ID schemeID="0094">DPMA-678</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>Abweichender Handelsname Rechnungsempfnger</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Strae Rechnungsempfnger 1</cbc:StreetName>
                <cbc:AdditionalStreetName>Erweitere Adresse
					Rechnungempfnger</cbc:AdditionalStreetName>
                <cbc:CityName>Ort Rechnungsempfnger</cbc:CityName>
                <cbc:PostalZone>67890</cbc:PostalZone>
                <cbc:CountrySubentity>Bundesland
					Rechnungsempfnger</cbc:CountrySubentity>
                <cac:Country>
                    <cbc:IdentificationCode>CN</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>ATU13585627</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>Deutsches Patent - und
					Markenamt</cbc:RegistrationName>
                <cbc:CompanyID schemeID="0094">90000000-03083-12</cbc:CompanyID>
            </cac:PartyLegalEntity>
            <cac:Contact>
                <cbc:Name>Kontakt Rechnungsempfnger</cbc:Name>
                <cbc:Telephone>0987 654321</cbc:Telephone>
                <cbc:ElectronicMail>tina@tester.de</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:PayeeParty>
        <cac:PartyIdentification>
            <cbc:ID schemeID="0118">AZE</cbc:ID>
        </cac:PartyIdentification>
        <cac:PartyName>
            <cbc:Name>Abweichender Zahlungsempfnger</cbc:Name>
        </cac:PartyName>
        <cac:PartyLegalEntity>
            <cbc:CompanyID schemeID="0198">AZE-123</cbc:CompanyID>
        </cac:PartyLegalEntity>
    </cac:PayeeParty>
    <cac:Delivery>
        <cbc:ActualDeliveryDate>2018-10-22</cbc:ActualDeliveryDate>
        <cac:DeliveryLocation>
            <cbc:ID schemeID="0088">AL</cbc:ID>
            <cac:Address>
                <cbc:StreetName>Anderer Leistungsempfnger Strae 1</cbc:StreetName>
                <cbc:AdditionalStreetName>Anderer Leistungsempfnger erweiterte
					Adresse</cbc:AdditionalStreetName>
                <cbc:CityName>Anderer Leistungsempfnger Ort</cbc:CityName>
                <cbc:PostalZone>45678</cbc:PostalZone>
                <cbc:CountrySubentity>Anderer Leistungempfnger
					Bundesland</cbc:CountrySubentity>
                <cac:Country>
                    <cbc:IdentificationCode>BS</cbc:IdentificationCode>
                </cac:Country>
            </cac:Address>
        </cac:DeliveryLocation>
        <cac:DeliveryParty>
            <cac:PartyName>
                <cbc:Name>Anderer Leistungsempfnger</cbc:Name>
            </cac:PartyName>
        </cac:DeliveryParty>
    </cac:Delivery>
    <cac:PaymentMeans>
        <cbc:PaymentMeansCode name="Credit transfer">30</cbc:PaymentMeansCode>
        <cbc:PaymentID>Verwendungszweck</cbc:PaymentID>
        <cac:PayeeFinancialAccount>
            <cbc:ID>DE84 6004 0071 0561 5158 01</cbc:ID>
            <cbc:Name>EntServ Deutschland GmbH</cbc:Name>
            <cac:FinancialInstitutionBranch>
                <cbc:ID>XXX0561515801</cbc:ID>
            </cac:FinancialInstitutionBranch>
        </cac:PayeeFinancialAccount>
    </cac:PaymentMeans>
    <cac:PaymentTerms>
        <cbc:Note>Zahlungsbedingungen gibt es nicht, da dies eine Testrechnung
			ist.</cbc:Note>
    </cac:PaymentTerms>
    <cac:AllowanceCharge>
        <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
        <cbc:AllowanceChargeReason>Grund fr den Nachlass auf
			Dokumentenebene</cbc:AllowanceChargeReason>
        <cbc:MultiplierFactorNumeric>50.00</cbc:MultiplierFactorNumeric>
        <cbc:Amount currencyID="EUR">1000.00</cbc:Amount>
        <cbc:BaseAmount currencyID="EUR">2000.00</cbc:BaseAmount>
        <cac:TaxCategory>
            <cbc:ID>S</cbc:ID>
            <cbc:Percent>19</cbc:Percent>
            <cac:TaxScheme>
                <cbc:ID>VAT</cbc:ID>
            </cac:TaxScheme>
        </cac:TaxCategory>
    </cac:AllowanceCharge>
    <cac:AllowanceCharge>
        <cbc:ChargeIndicator>true</cbc:ChargeIndicator>
        <cbc:AllowanceChargeReason>Grund fr den Zuschlag auf
			Dokumentenenbene</cbc:AllowanceChargeReason>
        <cbc:MultiplierFactorNumeric>10.00</cbc:MultiplierFactorNumeric>
        <cbc:Amount currencyID="EUR">400.00</cbc:Amount>
        <cbc:BaseAmount currencyID="EUR">4000.00</cbc:BaseAmount>
        <cac:TaxCategory>
            <cbc:ID>Z</cbc:ID>
            <cbc:Percent>0</cbc:Percent>
            <cac:TaxScheme>
                <cbc:ID>VAT</cbc:ID>
            </cac:TaxScheme>
        </cac:TaxCategory>
    </cac:AllowanceCharge>
    <cac:AllowanceCharge>
        <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
        <cbc:AllowanceChargeReason>Grund fr Nachlass 2</cbc:AllowanceChargeReason>
        <cbc:MultiplierFactorNumeric>10.00</cbc:MultiplierFactorNumeric>
        <cbc:Amount currencyID="EUR">1500.00</cbc:Amount>
        <cbc:BaseAmount currencyID="EUR">15000.00</cbc:BaseAmount>
        <cac:TaxCategory>
            <cbc:ID>E</cbc:ID>
            <cbc:Percent>0</cbc:Percent>
            <cac:TaxScheme>
                <cbc:ID>VAT</cbc:ID>
            </cac:TaxScheme>
        </cac:TaxCategory>
    </cac:AllowanceCharge>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="EUR">510.00</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">400.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">0</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>Z</cbc:ID>
                <cbc:Percent>0</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">10000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">700.00</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>7</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">-1000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">-190.00</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>19</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">-1500.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">0</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>E</cbc:ID>
                <cbc:Percent>0</cbc:Percent>
                <cbc:TaxExemptionReason>Grund fr die Befreiung</cbc:TaxExemptionReason>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="EUR">10000.00</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">7900.00</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="EUR">8410.00</cbc:TaxInclusiveAmount>
        <cbc:AllowanceTotalAmount currencyID="EUR">2500.00</cbc:AllowanceTotalAmount>
        <cbc:ChargeTotalAmount currencyID="EUR">400.00</cbc:ChargeTotalAmount>
        <cbc:PrepaidAmount currencyID="EUR">500.00</cbc:PrepaidAmount>
        <cbc:PayableRoundingAmount currencyID="EUR">210.00</cbc:PayableRoundingAmount>
        <cbc:PayableAmount currencyID="EUR">8120.00</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    <cac:InvoiceLine>
        <cbc:ID>123</cbc:ID>
        <cbc:InvoicedQuantity unitCode="LTR">10.00</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="EUR">10000.00</cbc:LineExtensionAmount>
        <cbc:AccountingCost>BRE</cbc:AccountingCost>
        <cac:InvoicePeriod>
            <cbc:StartDate>2018-10-05</cbc:StartDate>
            <cbc:EndDate>2018-10-07</cbc:EndDate>
        </cac:InvoicePeriod>
        <cac:OrderLineReference>
            <cbc:LineID>RPB</cbc:LineID>
        </cac:OrderLineReference>
        <cac:DocumentReference>
            <cbc:ID schemeID="AAD">7362789</cbc:ID>
            <cbc:DocumentTypeCode>130</cbc:DocumentTypeCode>
        </cac:DocumentReference>
        <cac:AllowanceCharge>
            <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
            <cbc:AllowanceChargeReason>Grund Nachlass 1</cbc:AllowanceChargeReason>
            <cbc:MultiplierFactorNumeric>10.00</cbc:MultiplierFactorNumeric>
            <cbc:Amount currencyID="EUR">10.00</cbc:Amount>
            <cbc:BaseAmount currencyID="EUR">100.00</cbc:BaseAmount>
        </cac:AllowanceCharge>
        <cac:AllowanceCharge>
            <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
            <cbc:AllowanceChargeReason>Grund Nachlass 2</cbc:AllowanceChargeReason>
            <cbc:MultiplierFactorNumeric>50.00</cbc:MultiplierFactorNumeric>
            <cbc:Amount currencyID="EUR">100.00</cbc:Amount>
            <cbc:BaseAmount currencyID="EUR">200.00</cbc:BaseAmount>
        </cac:AllowanceCharge>
        <cac:AllowanceCharge>
            <cbc:ChargeIndicator>true</cbc:ChargeIndicator>
            <cbc:AllowanceChargeReason>Grund Zuschlag 1</cbc:AllowanceChargeReason>
            <cbc:MultiplierFactorNumeric>50.00</cbc:MultiplierFactorNumeric>
            <cbc:Amount currencyID="EUR">100.00</cbc:Amount>
            <cbc:BaseAmount currencyID="EUR">200.00</cbc:BaseAmount>
        </cac:AllowanceCharge>
        <cac:AllowanceCharge>
            <cbc:ChargeIndicator>true</cbc:ChargeIndicator>
            <cbc:AllowanceChargeReason>Grund Zuschlag 2</cbc:AllowanceChargeReason>
            <cbc:MultiplierFactorNumeric>10.00</cbc:MultiplierFactorNumeric>
            <cbc:Amount currencyID="EUR">10.00</cbc:Amount>
            <cbc:BaseAmount currencyID="EUR">100.00</cbc:BaseAmount>
        </cac:AllowanceCharge>
        <cac:Item>
            <cbc:Description>Beschreibung Artikel</cbc:Description>
            <cbc:Name>Bezeichung Artikel</cbc:Name>
            <cac:BuyersItemIdentification>
                <cbc:ID>BB</cbc:ID>
            </cac:BuyersItemIdentification>
            <cac:SellersItemIdentification>
                <cbc:ID>456</cbc:ID>
            </cac:SellersItemIdentification>
            <cac:StandardItemIdentification>
                <cbc:ID schemeID="0088">1234567890128</cbc:ID>
            </cac:StandardItemIdentification>
            <cac:CommodityClassification>
                <cbc:ItemClassificationCode listID="ZZZ" listVersionID="1.0"
                    >12344321</cbc:ItemClassificationCode>
            </cac:CommodityClassification>
            <cac:ClassifiedTaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>7</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:ClassifiedTaxCategory>
            <cac:AdditionalItemProperty>
                <cbc:Name>Farbe</cbc:Name>
                <cbc:Value>blau</cbc:Value>
            </cac:AdditionalItemProperty>
            <cac:AdditionalItemProperty>
                <cbc:Name>Gre</cbc:Name>
                <cbc:Value>XL</cbc:Value>
            </cac:AdditionalItemProperty>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="EUR">1000</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
</ns0:Invoice>
"""

xml_text_from_zugpferd = """<?xml version="1.0" encoding="utf-8"?>
<rsm:CrossIndustryInvoice xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
   <rsm:ExchangedDocumentContext>
      <ram:BusinessProcessSpecifiedDocumentContextParameter>
         <ram:ID>OUT-380</ram:ID>
      </ram:BusinessProcessSpecifiedDocumentContextParameter>
      <ram:GuidelineSpecifiedDocumentContextParameter>
         <ram:ID>urn:cen.eu:en16931:2017</ram:ID>
      </ram:GuidelineSpecifiedDocumentContextParameter>
   </rsm:ExchangedDocumentContext>
   <rsm:ExchangedDocument>
      <ram:ID>2025/10294</ram:ID>
      <ram:TypeCode>380</ram:TypeCode>
      <ram:IssueDateTime>
         <udt:DateTimeString format="102">20250131</udt:DateTimeString>
      </ram:IssueDateTime>
      <ram:IncludedNote>
         <ram:Content>Die in Ihrem Auftrag erbrachten Leistungen werden vereinbarungsgemass wie folgt abgerechnet:</ram:Content>
      </ram:IncludedNote>
      <ram:IncludedNote>
         <ram:Content>Commerzbank Munchen IBAN: DE95700400410228840500 BIC: COBADEFFXXX</ram:Content>
      </ram:IncludedNote>
      <ram:IncludedNote>
         <ram:Content>Bartel, Tim</ram:Content>
      </ram:IncludedNote>
   </rsm:ExchangedDocument>
   <rsm:SupplyChainTradeTransaction>
      <ram:IncludedSupplyChainTradeLineItem>
         <ram:AssociatedDocumentLineDocument>
            <ram:LineID>1</ram:LineID>
         </ram:AssociatedDocumentLineDocument>
         <ram:SpecifiedTradeProduct>
            <ram:Name>Umsatzsteuerrechtliche Beratung gemass Zeitaufstellung

Partner:</ram:Name>
            <ram:Description>Satz: 390,00</ram:Description>
         </ram:SpecifiedTradeProduct>
         <ram:SpecifiedLineTradeAgreement>
            <ram:NetPriceProductTradePrice>
               <ram:ChargeAmount>390.00</ram:ChargeAmount>
            </ram:NetPriceProductTradePrice>
         </ram:SpecifiedLineTradeAgreement>
         <ram:SpecifiedLineTradeDelivery>
            <ram:BilledQuantity unitCode="HUR">0.2500</ram:BilledQuantity>
         </ram:SpecifiedLineTradeDelivery>
         <ram:SpecifiedLineTradeSettlement>
            <ram:ApplicableTradeTax>
               <ram:TypeCode>VAT</ram:TypeCode>
               <ram:CategoryCode>S</ram:CategoryCode>
               <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementLineMonetarySummation>
               <ram:LineTotalAmount>97.50</ram:LineTotalAmount>
            </ram:SpecifiedTradeSettlementLineMonetarySummation>
         </ram:SpecifiedLineTradeSettlement>
      </ram:IncludedSupplyChainTradeLineItem>
      <ram:IncludedSupplyChainTradeLineItem>
         <ram:AssociatedDocumentLineDocument>
            <ram:LineID>2</ram:LineID>
         </ram:AssociatedDocumentLineDocument>
         <ram:SpecifiedTradeProduct>
            <ram:Name>Associates:</ram:Name>
            <ram:Description>Satz: 260,00</ram:Description>
         </ram:SpecifiedTradeProduct>
         <ram:SpecifiedLineTradeAgreement>
            <ram:NetPriceProductTradePrice>
               <ram:ChargeAmount>260.00</ram:ChargeAmount>
            </ram:NetPriceProductTradePrice>
         </ram:SpecifiedLineTradeAgreement>
         <ram:SpecifiedLineTradeDelivery>
            <ram:BilledQuantity unitCode="HUR">0.5000</ram:BilledQuantity>
         </ram:SpecifiedLineTradeDelivery>
         <ram:SpecifiedLineTradeSettlement>
            <ram:ApplicableTradeTax>
               <ram:TypeCode>VAT</ram:TypeCode>
               <ram:CategoryCode>S</ram:CategoryCode>
               <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementLineMonetarySummation>
               <ram:LineTotalAmount>130.00</ram:LineTotalAmount>
            </ram:SpecifiedTradeSettlementLineMonetarySummation>
         </ram:SpecifiedLineTradeSettlement>
      </ram:IncludedSupplyChainTradeLineItem>
      <ram:ApplicableHeaderTradeAgreement>
         <ram:BuyerReference/>
         <ram:SellerTradeParty>
            <ram:Name>KMLZ Rechtsanwaltsges. mbH</ram:Name>
            <ram:DefinedTradeContact>
               <ram:PersonName>Bartel, Tim</ram:PersonName>
               <ram:TelephoneUniversalCommunication>
                  <ram:CompleteNumber>089 217501220</ram:CompleteNumber>
               </ram:TelephoneUniversalCommunication>
               <ram:EmailURIUniversalCommunication>
                  <ram:URIID>XRechnung@kmlz.de</ram:URIID>
               </ram:EmailURIUniversalCommunication>
            </ram:DefinedTradeContact>
            <ram:PostalTradeAddress>
               <ram:PostcodeCode>80331</ram:PostcodeCode>
               <ram:LineOne>Unterer Anger 3</ram:LineOne>
               <ram:CityName>Munchen</ram:CityName>
               <ram:CountryID>DE</ram:CountryID>
            </ram:PostalTradeAddress>
            <ram:URIUniversalCommunication>
               <ram:URIID schemeID="EM">XRechnung@kmlz.de</ram:URIID>
            </ram:URIUniversalCommunication>
            <ram:SpecifiedTaxRegistration>
               <ram:ID schemeID="VA">DE814742004</ram:ID>
            </ram:SpecifiedTaxRegistration>
         </ram:SellerTradeParty>
         <ram:BuyerTradeParty>
            <ram:ID>52296</ram:ID>
            <ram:Name>Sixt SE</ram:Name>
            <ram:DefinedTradeContact>
               <ram:PersonName>Sixt SE</ram:PersonName>
            </ram:DefinedTradeContact>
            <ram:PostalTradeAddress>
               <ram:PostcodeCode>82049</ram:PostcodeCode>
               <ram:LineOne>Zugspitzstr.1</ram:LineOne>
               <ram:CityName>Pullach</ram:CityName>
               <ram:CountryID>DE</ram:CountryID>
            </ram:PostalTradeAddress>
            <ram:URIUniversalCommunication>
               <ram:URIID schemeID="EM">eingangsrechnungenpdf@sixt.com</ram:URIID>
            </ram:URIUniversalCommunication>
         </ram:BuyerTradeParty>
         <ram:BuyerOrderReferencedDocument>
            <ram:IssuerAssignedID>SX-00855</ram:IssuerAssignedID>
         </ram:BuyerOrderReferencedDocument>
         <ram:AdditionalReferencedDocument>
            <ram:IssuerAssignedID>Anlage_1</ram:IssuerAssignedID>
            <ram:URIID>#ef=Anlage_1.pdf</ram:URIID>
            <ram:TypeCode>916</ram:TypeCode>
            <ram:Name>Anlage 1</ram:Name>
         </ram:AdditionalReferencedDocument>
      </ram:ApplicableHeaderTradeAgreement>
      <ram:ApplicableHeaderTradeDelivery>
         <ram:ActualDeliverySupplyChainEvent>
            <ram:OccurrenceDateTime>
               <udt:DateTimeString format="102">20250107</udt:DateTimeString>
            </ram:OccurrenceDateTime>
         </ram:ActualDeliverySupplyChainEvent>
      </ram:ApplicableHeaderTradeDelivery>
      <ram:ApplicableHeaderTradeSettlement>
         <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
         <ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:TypeCode>30</ram:TypeCode>
            <ram:PayeePartyCreditorFinancialAccount>
               <ram:IBANID>DE95700400410228840500</ram:IBANID>
            </ram:PayeePartyCreditorFinancialAccount>
            <ram:PayeeSpecifiedCreditorFinancialInstitution>
               <ram:BICID>COBADEFFXXX</ram:BICID>
            </ram:PayeeSpecifiedCreditorFinancialInstitution>
         </ram:SpecifiedTradeSettlementPaymentMeans>
         <ram:ApplicableTradeTax>
            <ram:CalculatedAmount>43.23</ram:CalculatedAmount>
            <ram:TypeCode>VAT</ram:TypeCode>
            <ram:BasisAmount>227.50</ram:BasisAmount>
            <ram:CategoryCode>S</ram:CategoryCode>
            <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
         </ram:ApplicableTradeTax>
         <ram:SpecifiedTradePaymentTerms>
            <ram:Description>Bitte uberweisen Sie den Rechnungsbetrag von 270,73 EUR bis zum 20.02.2025.</ram:Description>
            <ram:DueDateDateTime>
               <udt:DateTimeString format="102">20250220</udt:DateTimeString>
            </ram:DueDateDateTime>
         </ram:SpecifiedTradePaymentTerms>
         <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
            <ram:LineTotalAmount>227.50</ram:LineTotalAmount>
            <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
            <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
            <ram:TaxBasisTotalAmount>227.50</ram:TaxBasisTotalAmount>
            <ram:TaxTotalAmount currencyID="EUR">43.23</ram:TaxTotalAmount>
            <ram:GrandTotalAmount>270.73</ram:GrandTotalAmount>
            <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
            <ram:DuePayableAmount>270.73</ram:DuePayableAmount>
         </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
      </ram:ApplicableHeaderTradeSettlement>
   </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""

xml_test_iban_none = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:a="urn:un:unece:uncefact:data:standard:QualifiedDataType:100" xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100" xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:10" xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:cen.eu:en16931:2017</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>212732918642</ram:ID>
    <ram:TypeCode>381</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20250415</udt:DateTimeString>
    </ram:IssueDateTime>
    <ram:IncludedNote>
      <ram:Content>Weitere Angaben zu §40 EnWG entnehmen Sie dem Papierbeleg</ram:Content>
      <ram:SubjectCode>REG</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>Die vor der Ausfuhrung der Leistung vereinnahmten Teilentgelte und die darauf entfallenden Steuerbetrage sind in Abschnitt 1 in der CSV-Datei im Anhang der E-Rechnung aufgefuhrt.</ram:Content>
      <ram:SubjectCode>TXD</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>Ihr neuer Abschlag und ein Uberblick der Falligkeiten fur das kommende Verbrauchsjahr sind in Abschnitt 2 in der CSV-Datei im Anhang der E-Rechnung aufgefuhrt.</ram:Content>
      <ram:SubjectCode>AGN</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>[Erlaeuterung, Datum, Art, Betrag Brutto]</ram:Content>
      <ram:SubjectCode>SUR</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>Abschlagszahlungen:20240123,gezahlte Abschlage Strom, 22.15;20240207,gezahlte Abschlage Strom, 13.85;20240306,gezahlte Abschlage Strom, 36.00;20240404,gezahlte Abschlage Strom, 36.00;20240503,gezahlte Abschlage Strom, 36.00;20240605,gezahlte Abschlage Strom, 36.00;20240703,gezahlte Abschlage Strom, 36.00;20240805,gezahlte Abschlage Strom, 36.00;20240904,gezahlte Abschlage Strom, 36.00;20241002,gezahlte Abschlage Strom, 36.00;20241106,gezahlte Abschlage Strom, 36.00;20241204,gezahlte Abschlage Strom, 36.00;</ram:Content>
      <ram:SubjectCode>SUR</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>[Erlaeuterung, Zahlernummer, Datum-Von, Datum-Bis, Zahlerstand-von, Zahlerstand-bis, Faktor, Verbrauch]</ram:Content>
      <ram:SubjectCode>SUR</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>Zaehlerstaende:12247797,20240101,20240528,224481,224589,108,1;  1APA0184432582,20240529,20241231,1,181,180,1;</ram:Content>
      <ram:SubjectCode>SUR</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>[Erlaeuterung, Datum, Betrag]</ram:Content>
      <ram:SubjectCode>SUR</ram:SubjectCode>
    </ram:IncludedNote>
    <ram:IncludedNote>
      <ram:Content>Abschlagsplan:20250506, 26.00;20250606, 26.00;20250707, 26.00;20250806, 26.00;20250908, 26.00;20251006, 26.00;20251106, 26.00;20251208, 26.00;</ram:Content>
      <ram:SubjectCode>SUR</ram:SubjectCode>
    </ram:IncludedNote>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>1</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000798</ram:GlobalID>
        <ram:Name>Entgelt fur Messstellenbetrieb,Messung</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>12247797</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>8.69000000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="DAY">365</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="DAY">148</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20240528</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>3.52</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>2</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000798</ram:GlobalID>
        <ram:Name>Entgelt fur Messstellenbetrieb</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>16.80964800</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="DAY">365</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="DAY">217</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240529</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>9.99</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>3</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">4044038000447</ram:GlobalID>
        <ram:Name>Arbeitspreis</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.10994000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>31.66</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>4</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000087</ram:GlobalID>
        <ram:Name>Grundpreis Netz</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>160.00000000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="DAY">365</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="DAY">365</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>160.00</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>5</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">4044038000294</ram:GlobalID>
        <ram:Name>Stromsteuer</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.02050000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>5.90</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>6</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000269</ram:GlobalID>
        <ram:Name>Arbeitspreis Netz</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.06030000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>17.37</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>7</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000334</ram:GlobalID>
        <ram:Name>Kraft-Warme-Kopplung (KWK)</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.00275000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>0.79</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>8</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000681</ram:GlobalID>
        <ram:Name>§19 Strom NEV Umlage</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.00643000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>1.85</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>9</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000706</ram:GlobalID>
        <ram:Name>Offshore-Umlage</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.00656000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>1.89</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>10</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:GlobalID schemeID="0088">9990001000417</ram:GlobalID>
        <ram:Name>Konzessionsabgabe Tarifkunde</ram:Name>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlpunkt</ram:Description>
          <ram:Value>DE0010795073900000000000000349574</ram:Value>
        </ram:ApplicableProductCharacteristic>
        <ram:ApplicableProductCharacteristic>
          <ram:Description>Zahlernummer</ram:Description>
          <ram:Value>1APA0184432582</ram:Value>
        </ram:ApplicableProductCharacteristic>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>0.02390000</ram:ChargeAmount>
          <ram:BasisQuantity unitCode="KWH">1</ram:BasisQuantity>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="KWH">288</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>S</ram:CategoryCode>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:BillingSpecifiedPeriod>
          <ram:StartDateTime>
            <udt:DateTimeString format="102">20240101</udt:DateTimeString>
          </ram:StartDateTime>
          <ram:EndDateTime>
            <udt:DateTimeString format="102">20241231</udt:DateTimeString>
          </ram:EndDateTime>
        </ram:BillingSpecifiedPeriod>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>6.88</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:ApplicableHeaderTradeAgreement>
      <ram:BuyerReference/>
      <ram:SellerTradeParty>
        <ram:ID>9903323000007</ram:ID>
        <ram:Name>E.ON Energie Deutschland GmbH</ram:Name>
        <ram:DefinedTradeContact>
          <ram:PersonName>Geschaftskundenbetreuung</ram:PersonName>
          <ram:DepartmentName>Geschaftskundenbetreuung</ram:DepartmentName>
          <ram:TelephoneUniversalCommunication>
            <ram:CompleteNumber>089 95469920</ram:CompleteNumber>
          </ram:TelephoneUniversalCommunication>
          <ram:EmailURIUniversalCommunication>
            <ram:URIID>GKBetreuung@eon.de</ram:URIID>
          </ram:EmailURIUniversalCommunication>
        </ram:DefinedTradeContact>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>84001</ram:PostcodeCode>
          <ram:LineOne>Postfach 14 75</ram:LineOne>
          <ram:CityName>Landshut</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
        <ram:URIUniversalCommunication>
          <ram:URIID schemeID="EM">GKBetreuung@eon.de</ram:URIID>
        </ram:URIUniversalCommunication>
        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="VA">DE259922663</ram:ID>
        </ram:SpecifiedTaxRegistration>
      </ram:SellerTradeParty>
      <ram:BuyerTradeParty>
        <ram:ID>232081412135</ram:ID>
        <ram:Name>Sixt GmbH &amp; Co. Autovermietung KG</ram:Name>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>82049</ram:PostcodeCode>
          <ram:LineOne>Zugspitzstr. 1</ram:LineOne>
          <ram:CityName>82049 Pullach</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
        <ram:URIUniversalCommunication>
          <ram:URIID schemeID="EM">einvoices-germany@identity.sixt.com</ram:URIID>
        </ram:URIUniversalCommunication>
        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="VA">DE223999470</ram:ID>
        </ram:SpecifiedTaxRegistration>
      </ram:BuyerTradeParty>
      <ram:BuyerOrderReferencedDocument>
        <ram:IssuerAssignedID/>
      </ram:BuyerOrderReferencedDocument>
      <ram:ContractReferencedDocument>
        <ram:IssuerAssignedID>232081412135</ram:IssuerAssignedID>
      </ram:ContractReferencedDocument>
      <ram:AdditionalReferencedDocument>
        <ram:IssuerAssignedID>212732918642</ram:IssuerAssignedID>
        <ram:TypeCode>916</ram:TypeCode>
        <ram:AttachmentBinaryObject mimeCode="text/csv" filename="212732918642.csv">QWJzY2huaXR0IDE7Ozs7OwpVZWJlcnNpY2h0IGRlciBnZWxlaXN0ZXRlbiBBbnphaGx1bmdlbjs7Ozs7CkJlemVpY2hudW5nO0RhdHVtO05ldHRvYmV0cmFnKEVVUik7VVN0LihFVVIpO1N0ZXVlcnNhdHooJSk7QnJ1dHRvYmV0cmFnKEVVUikKQWJzY2hsYWc7MjMuMDEuMjAyNDstMTgsNjE7LTMsNTQ7MTk7LTIyLDE1CkFic2NobGFnOzA3LjAyLjIwMjQ7LTExLDY0Oy0yLDIxOzE5Oy0xMyw4NQpBYnNjaGxhZzswNi4wMy4yMDI0Oy0zMCwyNTstNSw3NTsxOTstMzYsMDAKQWJzY2hsYWc7MDQuMDQuMjAyNDstMzAsMjU7LTUsNzU7MTk7LTM2LDAwCkFic2NobGFnOzAzLjA1LjIwMjQ7LTMwLDI1Oy01LDc1OzE5Oy0zNiwwMApBYnNjaGxhZzswNS4wNi4yMDI0Oy0zMCwyNTstNSw3NTsxOTstMzYsMDAKQWJzY2hsYWc7MDMuMDcuMjAyNDstMzAsMjU7LTUsNzU7MTk7LTM2LDAwCkFic2NobGFnOzA1LjA4LjIwMjQ7LTMwLDI1Oy01LDc1OzE5Oy0zNiwwMApBYnNjaGxhZzswNC4wOS4yMDI0Oy0zMCwyNTstNSw3NTsxOTstMzYsMDAKQWJzY2hsYWc7MDIuMTAuMjAyNDstMzAsMjU7LTUsNzU7MTk7LTM2LDAwCkFic2NobGFnOzA2LjExLjIwMjQ7LTMwLDI1Oy01LDc1OzE5Oy0zNiwwMApBYnNjaGxhZzswNC4xMi4yMDI0Oy0zMCwyNTstNSw3NTsxOTstMzYsMDAKOzs7OzsKQWJzY2huaXR0IDI7Ozs7OwpJaHIgbmV1ZXIgQWJzY2hsYWdzcGxhbiBmdWVyIGRhcyBWZXJicmF1Y2hzamFociAyMDI1Ozs7OzsKQmV6ZWljaG51bmc7RmFlbGxpZ2tlaXQ7TmV0dG9iZXRyYWcoRVVSKTtVU3QuKEVVUik7U3RldWVyc2F0eiglKTtCcnV0dG9iZXRyYWcoRVVSKQpBYnNjaGxhZ3Nmb3JkZXJ1bmc7MDYuMDUuMjAyNTsyMSw4NTs0LDE1OzE5OzI2LDAwCkFic2NobGFnc2ZvcmRlcnVuZzswNi4wNi4yMDI1OzIxLDg1OzQsMTU7MTk7MjYsMDAKQWJzY2hsYWdzZm9yZGVydW5nOzA3LjA3LjIwMjU7MjEsODU7NCwxNTsxOTsyNiwwMApBYnNjaGxhZ3Nmb3JkZXJ1bmc7MDYuMDguMjAyNTsyMSw4NTs0LDE1OzE5OzI2LDAwCkFic2NobGFnc2ZvcmRlcnVuZzswOC4wOS4yMDI1OzIxLDg1OzQsMTU7MTk7MjYsMDAKQWJzY2hsYWdzZm9yZGVydW5nOzA2LjEwLjIwMjU7MjEsODU7NCwxNTsxOTsyNiwwMApBYnNjaGxhZ3Nmb3JkZXJ1bmc7MDYuMTEuMjAyNTsyMSw4NTs0LDE1OzE5OzI2LDAwCkFic2NobGFnc2ZvcmRlcnVuZzswOC4xMi4yMDI1OzIxLDg1OzQsMTU7MTk7MjYsMDAKOzs7OzsK</ram:AttachmentBinaryObject>
      </ram:AdditionalReferencedDocument>
    </ram:ApplicableHeaderTradeAgreement>
    <ram:ApplicableHeaderTradeDelivery>
      <ram:ShipToTradeParty>
        <ram:ID>50205028589</ram:ID>
        <ram:Name>Verbrauchsstelle</ram:Name>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>50739</ram:PostcodeCode>
          <ram:LineOne>Robert-Perthel-Str. 26</ram:LineOne>
          <ram:CityName>Koln</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
      </ram:ShipToTradeParty>
    </ram:ApplicableHeaderTradeDelivery>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:PaymentReference>232081412135</ram:PaymentReference>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      <ram:SpecifiedTradeSettlementPaymentMeans>
        <ram:TypeCode>30</ram:TypeCode>
        <ram:Information>per Uberweisung</ram:Information>
        <ram:PayeePartyCreditorFinancialAccount>
          <ram:IBANID/>
        </ram:PayeePartyCreditorFinancialAccount>
      </ram:SpecifiedTradeSettlementPaymentMeans>
      <ram:ApplicableTradeTax>
        <ram:CalculatedAmount>45.57</ram:CalculatedAmount>
        <ram:TypeCode>VAT</ram:TypeCode>
        <ram:BasisAmount>239.85</ram:BasisAmount>
        <ram:CategoryCode>S</ram:CategoryCode>
        <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
      </ram:ApplicableTradeTax>
      <ram:BillingSpecifiedPeriod>
        <ram:StartDateTime>
          <udt:DateTimeString format="102">20240101</udt:DateTimeString>
        </ram:StartDateTime>
        <ram:EndDateTime>
          <udt:DateTimeString format="102">20241231</udt:DateTimeString>
        </ram:EndDateTime>
      </ram:BillingSpecifiedPeriod>
      <ram:SpecifiedTradePaymentTerms>
        <ram:Description/>
        <ram:DueDateDateTime>
          <udt:DateTimeString format="102">20250417</udt:DateTimeString>
        </ram:DueDateDateTime>
      </ram:SpecifiedTradePaymentTerms>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>239.85</ram:LineTotalAmount>
        <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
        <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
        <ram:TaxBasisTotalAmount>239.85</ram:TaxBasisTotalAmount>
        <ram:TaxTotalAmount currencyID="EUR">45.57</ram:TaxTotalAmount>
        <ram:RoundingAmount>0.00</ram:RoundingAmount>
        <ram:GrandTotalAmount>285.42</ram:GrandTotalAmount>
        <ram:TotalPrepaidAmount>318.00</ram:TotalPrepaidAmount>
        <ram:DuePayableAmount>-32.58</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""
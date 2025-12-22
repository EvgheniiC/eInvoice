from dataclasses import dataclass


# This class use for NFZ(infleet) invoices
@dataclass
@dataclass
class XmlInvoiceEquipment:
    """
    Represents an equipment line item for NFZ (infleet) invoices.

    This class manages equipment position data that can be serialized to XML format
    for invoice processing in the infleet system.

    Attributes:
        m_cn_header_id (str): Reference ID linking to the parent invoice header.
        pos_nummer (int): Sequential position/line number of this item in the invoice.
        pos_code (str): Equipment code or SKU identifier.
        pos_description (str): Detailed textual description of the equipment item.
        pos_price (float, optional): Base price of the equipment. Defaults to 0.0.
        pos_price_paid (str, optional): Actual price paid for the equipment.
            Can be None if not yet paid. Defaults to None.
        pos_msrp_price (float, optional): Manufacturer's Suggested Retail Price.
            Defaults to 0.0.

    Methods:
        get_xml_equipment_attributes(): Returns a dictionary with XML-formatted
            attribute names and their corresponding values.

    Example:
        >>> equipment = XmlInvoiceEquipment(
        ...     m_cn_header_id="123456",
        ...     pos_nummer=1,
        ...     pos_code="GPS-PRO",
        ...     pos_description="Premium GPS Navigation",
        ...     pos_price=299.99
        ... )
        >>> xml_data = equipment.get_xml_equipment_attributes()
    """

    def __init__(self,
                 m_cn_header_id: str,
                 pos_nummer: int,
                 pos_code: str,
                 pos_description: str,
                 pos_price: float = 0.0,
                 pos_price_paid: str = None,
                 pos_msrp_price: float = 0.0):
        self.m_cn_header_id = m_cn_header_id
        self.pos_nummer = pos_nummer
        self.pos_code = pos_code
        self.pos_description = pos_description
        self.pos_price = pos_price
        self.pos_price_paid = pos_price_paid
        self.pos_msrp_price = pos_msrp_price

    def get_xml_equipment_attributes(self):
        """
        Converts equipment attributes to XML-compatible dictionary format.

        Returns:
            dict: Dictionary with XML attribute names as keys and their
                corresponding values. Keys include: M_CN_POS_ID, M_CN_HEADER_ID,
                POS_NUM, POS_CODE, POS_DESC, POS_PRICE, POS_PRICE_PAID,
                POS_MSRP_PRICE.
        """
        return {"M_CN_HEADER_ID": self.m_cn_header_id,
                "POS_NUM": self.pos_nummer,
                "POS_CODE": self.pos_code,
                "POS_DESC": self.pos_description,
                "POS_PRICE": self.pos_price,
                "POS_PRICE_PAID": self.pos_price_paid,
                "POS_MSRP_PRICE": self.pos_msrp_price}

    @property
    def pos_nummer(self):
        return self.__pos_nummer

    @pos_nummer.setter
    def pos_nummer(self, value: str):
        self.__pos_nummer = value

    @property
    def pos_code(self):
        return self.__pos_code

    @pos_code.setter
    def pos_code(self, value: str):
        self.__pos_code = value

    @property
    def pos_description(self):
        return self.__pos_description

    @pos_description.setter
    def pos_description(self, value: str):
        self.__pos_description = value

    @property
    def pos_price(self):
        return self.__pos_price

    @pos_price.setter
    def pos_price(self, value: float):
        self.__pos_price = value

    @property
    def pos_price_paid(self):
        return self.__pos_price_paid

    @pos_price_paid.setter
    def pos_price_paid(self, value: str):
        self.__pos_price_paid = value

    @property
    def pos_msrp_price(self):
        return self.__pos_msrp_price

    @pos_msrp_price.setter
    def pos_msrp_price(self, value: float):
        self.__pos_msrp_price = value

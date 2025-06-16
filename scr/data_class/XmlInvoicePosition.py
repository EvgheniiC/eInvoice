from dataclasses import dataclass


@dataclass
class XmlInvoicePosition:
    """
    Represents an invoice position in XML format.

    This class is used to define and manage attributes related to an XML representation of an
    invoice position. It includes various fields such as item position, quantity, tax rate,
    and associated metadata such as cost center, discount values, and tax codes. The purpose
    of the class is to organize and transform these attributes into a structured dictionary
    format for XML processing or other use cases.

    Attributes
    ----------
    m_cn_id : int
        Identifier of the entity or transaction.
    invoice_id : int
        Unique identifier of the associated invoice.
    quantity : float
        Quantity of the item in the position.
    single_net_price : float
        Net price per single unit of the item.
    total_net_price : float
        Total net price for the position.
    tax_rate : float
        Tax rate applied to the item.
    inventory_account : float
        Inventory account associated with this position.
    position_text : str
        Descriptive text for the position.
    typ : str
        Type of the position, default is "ET".
    tax_code : str
        Tax code applicable to this position.
    article_number : str
        Article number of the item in the position.
    article_number2 : str
        Secondary article number of the item in the position.
    discount_percent : float
        Discount percentage applied to the position.
    discount_amount : float
        Discount amount applied to the position.
    quantity_unit : float
        Unit of measurement for the quantity.
    order_pos_id : str
        Identifier for the order position.
    goods_inward_pos_id : str
        Identifier for goods inward associated with this position.
    item_pos : int
        Position index of the item in the order or invoice.
    e_class : str
        Classification of the item.
    cost_center : str
        Cost center associated with the position.
    cost_carrier : str
        Cost carrier related to the position.

    Methods
    -------
    get_xml_positions_attributes()
        Returns a dictionary representation of the position's attributes suitable for XML
        processing.

    Properties
    ----------
    m_cn_id : str
        Getter and setter for `m_cn_id` attribute.
    invoice_id : int
        Getter and setter for `invoice_id` attribute.
    quantity : float
        Getter and setter for `quantity` attribute.
    single_net_price : float
        Getter and setter for `single_net_price` attribute.
    total_net_price : float
        Getter and setter for `total_net_price` attribute.
    tax_rate : float
        Getter and setter for `tax_rate` attribute.
    inventory_account : str
        Getter and setter for `inventory_account` attribute.
    position_text : str
        Getter and setter for `position_text` attribute.
    typ : str
        Getter and setter for `typ` attribute.
    tax_code : str
        Getter and setter for `tax_code` attribute.
    article_number : str
        Getter and setter for `article_number` attribute.
    article_number2 : str
        Getter and setter for `article_number2` attribute.
    discount_percent : float
        Getter and setter for `discount_percent` attribute.
    discount_amount : float
        Getter and setter for `discount_amount` attribute.
    quantity_unit : float
        Getter and setter for `quantity_unit` attribute.
    order_pos_id : str
        Getter and setter for `order_pos_id` attribute.
    goods_inward_pos_id : str
        Getter and setter for `goods_inward_pos_id` attribute.
    item_pos : int
        Getter and setter for `item_pos` attribute.
    e_class : str
        Getter and setter for `e_class` attribute.
    cost_center : str
        Getter and setter for `cost_center` attribute.
    cost_carrier : str
        Getter and setter for `cost_carrier` attribute.
    """

    def __init__(self,
                 item_pos: int = 1,
                 position_text: str = None,
                 quantity: float = 1,
                 single_net_price: float = None,
                 tax_rate: float = None,
                 total_net_price: float = None,
                 invoice_id: int = None,
                 m_cn_id: int = None,
                 typ: str = "ET",
                 article_number: str = None,
                 quantity_unit: float = None,
                 discount_percent: float = None,
                 inventory_account: float = None,
                 tax_code: str = None,
                 article_number2: str = None,
                 discount_amount: float = None,
                 order_pos_id: str = "",
                 goods_inward_pos_id: str = "",
                 e_class: str = "",
                 cost_center: str = "",
                 cost_carrier: str = ""):
        self.m_cn_id = m_cn_id
        self.invoice_id = invoice_id
        self.quantity = quantity
        self.single_net_price = single_net_price
        self.total_net_price = total_net_price
        self.tax_rate = tax_rate
        self.inventory_account = inventory_account
        self.position_text = position_text
        self.typ = typ
        self.tax_code = tax_code
        self.article_number = article_number
        self.article_number2 = article_number2
        self.discount_percent = discount_percent
        self.discount_amount = discount_amount
        self.quantity_unit = quantity_unit
        self.order_pos_id = order_pos_id
        self.goods_inward_pos_id = goods_inward_pos_id
        self.item_pos = item_pos
        self.e_class = e_class
        self.cost_center = cost_center
        self.cost_carrier = cost_carrier

    def get_xml_positions_attributes(self):
        return {"M_CN_ID": self.m_cn_id,
                "M_CN_INVOICEID": self.invoice_id,
                "M_IP_ITEMPOS": self.item_pos,
                "M_IP_POSITIONSTEXT": self.position_text,
                "M_IP_QUANTITY": self.quantity,
                "M_IP_SINGLENETPRICE": self.single_net_price,
                "M_IP_TOTALNETPRICE": self.total_net_price,
                "M_IP_TAXRATE": self.tax_rate,
                "M_IP_COSTCENTER": self.cost_center,
                "M_IP_KOSTENTRAEGER": self.cost_carrier,
                "M_IP_INVENTORYACC": self.inventory_account,
                "M_IP_ARTICLENUMBER": self.article_number,
                "M_IP_ARTICLENUMBER2": self.article_number2,
                "M_IP_DISCOUNTAMOUNT": self.discount_amount,
                "M_IP_QUANTITYUNIT": self.quantity_unit,
                "M_IP_TYP": self.typ,
                "M_IP_DISCOUNTPERCENT": self.discount_percent,
                "M_IP_TAXCODE": self.tax_code,
                "M_IP_ORDERPOSID": self.order_pos_id,
                "M_IP_GOODSINWARDPOSID": self.goods_inward_pos_id,
                "M_IP_ECLASS": self.e_class}

    def get_xml_positions_attributes_for_hw(self):
        return {"M_IP_ID": self.m_cn_id,
                "M_IP_INVOICEID": self.invoice_id,
                "M_IP_ITEMPOS": self.item_pos,
                "M_IP_POSITIONSTEXT": self.position_text,
                "M_IP_QUANTITY": self.quantity,
                "M_IP_SINGLENETPRICE": self.single_net_price,
                "M_IP_TOTALNETPRICE": self.total_net_price,
                "M_IP_TAXRATE": self.tax_rate,
                "M_IP_COSTCENTER": self.cost_center,
                "M_IP_KOSTENTRAEGER": self.cost_carrier,
                "M_IP_INVENTORYACC": self.inventory_account,
                "M_IP_ARTICLENUMBER": self.article_number,
                "M_IP_ARTICLENUMBER2": self.article_number2,
                "M_IP_DISCOUNTAMOUNT": self.discount_amount,
                "M_IP_QUANTITYUNIT": self.quantity_unit,
                "M_IP_TYP": self.typ,
                "M_IP_DISCOUNTPERCENT": self.discount_percent,
                "M_IP_TAXCODE": self.tax_code,
                "M_IP_ORDERPOSID": self.order_pos_id,
                "M_IP_GOODSINWARDPOSID": self.goods_inward_pos_id,
                "M_IP_ECLASS": self.e_class}

    @property
    def article_number(self):
        return self.__article_number

    @article_number.setter
    def article_number(self, value: str):
        self.__article_number = value

    @property
    def article_number2(self):
        return self.__article_number2

    @article_number2.setter
    def article_number2(self, value: str):
        self.__article_number2 = value

    @property
    def discount_amount(self):
        return self.__discount_amount

    @discount_amount.setter
    def discount_amount(self, value: str):
        self.__discount_amount = value

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value: float):
        self.__quantity = value

    @property
    def quantity_unit(self):
        return self.__quantity_unit

    @quantity_unit.setter
    def quantity_unit(self, value: float):
        self.__quantity_unit = value

    @property
    def single_net_price(self):
        return self.__single_net_price

    @single_net_price.setter
    def single_net_price(self, value: float):
        self.__single_net_price = value

    @property
    def total_net_price(self):
        return self.__total_net_price

    @total_net_price.setter
    def total_net_price(self, value: float):
        self.__total_net_price = value

    @property
    def tax_rate(self):
        return self.__tax_rate

    @tax_rate.setter
    def tax_rate(self, value: float):
        self.__tax_rate = value

    @property
    def position_text(self):
        return self.__position_text

    @position_text.setter
    def position_text(self, value: str):
        self.__position_text = value

    @property
    def typ(self):
        return self.__typ

    @typ.setter
    def typ(self, value: str):
        self.__typ = value

    @property
    def discount_percent(self):
        return self.__discount_percent

    @discount_percent.setter
    def discount_percent(self, value: float):
        self.__discount_percent = value

    @property
    def invoice_id(self):
        return self.__invoice_id

    @invoice_id.setter
    def invoice_id(self, value: int):
        self.__invoice_id = value

    @property
    def inventory_account(self):
        return self.__inventory_account

    @inventory_account.setter
    def inventory_account(self, value: str):
        self.__inventory_account = value

    @property
    def tax_code(self):
        return self.__tax_code

    @tax_code.setter
    def tax_code(self, value: str):
        self.__tax_code = value

    @property
    def order_pos_id(self):
        return self.__order_pos_id

    @order_pos_id.setter
    def order_pos_id(self, value: str):
        self.__order_pos_id = value

    @property
    def goods_inward_pos_id(self):
        return self.__goods_inward_pos_id

    @goods_inward_pos_id.setter
    def goods_inward_pos_id(self, value: str):
        self.__goods_inward_pos_id = value

    @property
    def item_pos(self):
        return self.__item_pos

    @item_pos.setter
    def item_pos(self, value: int):
        self.__item_pos = value

    @property
    def e_class(self):
        return self.__e_class

    @e_class.setter
    def e_class(self, value: str):
        self.__e_class = value

    @property
    def cost_center(self):
        return self.__cost_center

    @cost_center.setter
    def cost_center(self, value: str):
        self.__cost_center = value

    @property
    def cost_carrier(self):
        return self.__cost_carrier

    @cost_carrier.setter
    def cost_carrier(self, value: str):
        self.__cost_carrier = value

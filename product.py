class Product:
    def __init__(self, name, price, url, price_alert, currency, error=None):
        self.__name = name
        self.__price = price
        self.__url = url
        self.__currency = currency
        self.__price_alert = price_alert
        self.__error = error

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def set_price(self, price):
        if isinstance(price, float) or isinstance(price, int):
            self.__price = price
        else:
            raise ValueError("Price must be type of Integer or Float")

    def get_url(self):
        return self.__url

    def get_price_alert(self):
        return self.__price_alert

    def get_currency(self):
        return self.__currency

    def get_error(self):
        return self.__error

    def set_error(self, message):
        self.__error = message

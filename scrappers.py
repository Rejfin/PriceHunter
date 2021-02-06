import product as p
from bs4 import BeautifulSoup
import re


class Scrappers:
    async def scrap(self, product, content):
        if "www.morele.net" in product.get_url():
            return await self.__morele(product, content)
        elif "www.alsen.pl" in product.get_url():
            return await self.__alsen(product, content)
        elif "www.zadowolenie.pl" in product.get_url():
            return await self.__zadowolenie(product, content)
        elif "www.komputronik.pl" in product.get_url():
            return await self.__komputronik(product, content)
        elif "www.bestbuy.com" in product.get_url():
            return await self.__bestbuy(product, content)
        elif "www.amazon" in product.get_url():
            return await self.__amazon(product, content)
        elif "www.ebay" in product.get_url():
            return await self.__ebay(product, content)
        elif "www.walmart" in product.get_url():
            return await self.__walmart(product, content)
        elif "www.etsy" in product.get_url():
            return await self.__etsy(product, content)
        elif "www.homedepot" in product.get_url():
            return await self.__homedepot(product, content)
        else:
            product.set_error("no matching scrapper")
            return product

    @staticmethod
    async def __morele(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            if soup.find("button",
                         class_="add-to-cart__disabled btn btn-grey btn-block btn-sidebar btn-disabled") is not None:
                error_message = "product unavailable"
            else:
                price = soup.find("div", class_="product-price", id="product_price_brutto")
                price = float(price["content"])
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(), product.get_currency(), error_message)

    @staticmethod
    async def __alsen(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = 0
        try:
            full = soup.find("div", class_="m-priceBox_new is-medium")
            if full is None:
                price = None
                error_message = "product unavailable"
            else:
                price = full.find("span", class_="m-priceBox_price")
                rest = full.find("span", class_="m-priceBox_rest")
                price = float(price.text)
                rest = float(rest.text)
                price += rest
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(), product.get_currency(), error_message)

    @staticmethod
    async def __zadowolenie(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            if soup.find("div", class_="b-offer_unavailable") is not None:
                error_message = "product unavailable"
                price = None
            else:
                price = soup.find("div", class_="m-priceBox_price m-priceBox_promo")
                price = float(price.text.replace(',', ".").strip(' \t\n\r').split()[0])
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(), product.get_currency(), error_message)

    @staticmethod
    async def __komputronik(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            x = soup.find("div", class_="delivery grey disabled")
            if x is not None:
                price = None
                error_message = "product unavailable"
            else:
                price = soup.find("span", class_="proper")
                price = float(price.text.split('z')[0].replace(u'\xa0', "").replace(",", "."))
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(), product.get_currency(), error_message)

    @staticmethod
    async def __bestbuy(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            if soup.find("button", class_="btn btn-disabled btn-lg btn-block add-to-cart-button") is not None:
                error_message = "product unavailable"
                price = None
            else:
                price = soup.find("div", class_="priceView-hero-price priceView-customer-price").findChild(
                    "span", attrs={"aria-hidden": "true"})
                price = float(re.search("[0-9]+\.*[0-9]*", price.text.replace(',', ".")).group(0))
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(), product.get_currency(), error_message)

    @staticmethod
    async def __amazon(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            if soup.find("div", id="availability", class_="a-section a-spacing-base").findChild(
                    "span",
                    class_="a-size-medium a-color-success") is None:
                error_message = "product unavailable"
                price = None
            else:
                price = soup.find("span", id="priceblock_ourprice", class_="a-size-medium a-color-price priceBlockBuyingPriceString")
                price = float(re.search("[0-9]+\.*[0-9]*", price.text.replace(',', ".")).group(0))
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(), product.get_currency(), error_message)


    @staticmethod
    async def __ebay(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            a = soup.find("span", id="convbidPrice")
            if a is None:
                x = soup.find("span", class_="notranslate", id="prcIsum_bidPrice")
                if x is None:
                    error_message = "product unavailable"
                    price = None
                else:
                    price = float(x["content"])
            else:
                price = float(re.search("[0-9]+\.[0-9]+", a.text).group(0))
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(),
                             product.get_currency(), error_message)


    @staticmethod
    async def __walmart(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            x = soup.find("div", class_="prod-ProductOffer-oosMsg prod-PaddingTop--xxs")
            if x is not None:
                error_message = "product unavailable"
                price = None
            else:
                a = soup.find("span", class_="price-characteristic", attrs={"itemprop": "price"})
                if a is None:
                    error_message = "can't get price!"
                    price = None
                else:
                    price = float(a["content"])
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(),
                             product.get_currency(), error_message)

    @staticmethod
    async def __etsy(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            x = soup.find("p", class_="wt-text-title-03 wt-mr-xs-2")
            if x is None:
                error_message = "cant' get price"
                price = None
            else:
                price = float(re.search("[0-9]+\.[0-9]+", x.text.replace(",", ".")).group(0))
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(),
                             product.get_currency(), error_message)

    @staticmethod
    async def __homedepot(product, content):
        soup = BeautifulSoup(content, "lxml")
        error_message = None
        price = None
        try:
            x = soup.find("div", class_="price-format__large price-format__main-price")
            if x is None:
                error_message = "cant' get price"
                price = None
            else:
                s = x.find_all("span")
                price = float(f"{s[1].text}.{s[2].text}")
        except Exception as e:
            price = None
            error_message = e
        finally:
            return p.Product(product.get_name(), price, product.get_url(), product.get_price_alert(),
                             product.get_currency(), error_message)

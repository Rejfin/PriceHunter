# PriceHunter
![LICENSE MIT](https://img.shields.io/badge/License-MIT-green)
![PYTHON 3.7](https://img.shields.io/badge/Python-3.7-blue)
![FIREBASE](https://img.shields.io/badge/Firebase-integration-blue)

## Description
PriceHunter is a script written in Python. Thanks to his help you can track many product prices on many websites and all this in just a few seconds. 

The script has the ability to hook it up to firebase services, so that the results of your "hunting" can be saved in the firebase database.\
One of the additional options is to send notifications when the product we are interested in reaches the price we want.

The script currently supports online stores such as:
- walmart.com
- bestbuy.com
- Amazon
- homedepot.com
- ebay.com
- etsy.com
- alsen.pl
- morele.net
- komputronik.pl
- zadowolenie.pl

## Installation

- [download](https://github.com/Rejfin/PriceHunter/releases/download/v1.0/PriceHunter_v1.0.zip) the entire repository, and unpack it
- install all necessary packages using ```pip install -r requirements.txt```

## Usage

- first add your product to the list
    * create new json file in "products" folder
    * copy the contents of test_product.json to the newly created file
    * open it and edit values:
        * name -> it's name of your product (should be unique)
        * price_alert -> determine the price at which the information that the product is available at a lower price should appear
        * price_currency -> set price currency ex. "$", "€" (it is used only for display)
        * urls -> list of links to websites where the product appears
    * now your first product is ready for price tracking
    
- you can delete ```test_product.json``` it was for example purposes only
- run main.py to start tracking price


_you can create unlimited number of products, just add another json file_
 
## Firebase integration

[Here](FIREBASE_INTEGRATION.md) you can find instruction how to enable firebase integration in this script and how to use Android app with it
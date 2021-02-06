import random
from asyncio import gather, get_event_loop
from datetime import datetime
from aiohttp import ClientSession, TCPConnector, ClientConnectorError
from scrappers import Scrappers
from product import Product
from database import Database
from time import sleep
import os
import json
from colorama import Fore
from colorama import init as init_color
import ssl
import certifi
from firebase_admin import db as fire_db, messaging, credentials, initialize_app
from threading import Thread
import shutil

# -------------- CONFIG ------------------
# set max number of connection at once
MAX_CONNECTIONS = 30
# set max number of connection to one host
MAX_CONNECTION_PER_HOST = 2
# if set to True script will work forever, if set to False it will run only once
INFINITY_MODE = True
# set how often (in sec) sites should be checked (only if #INFINITY_MODE set to True)
REFRESH_FREQUENCY = 3600
# set how much data refresh may be delayed (in sec), thanks to this, data from the website is downloaded
# at irregular intervals, which could prevents the connection from being blocked (only if #INFINITY_MODE set to True)
# can be set to 0
REFRESH_SHIFT = 600
# set if the result should be displayed in the console
SHOW_OUTPUT_IN_CMD = True
# set if the product below or equal price alert should be displayed in the console
SHOW_PRICE_ALERT_IN_CMD = True
# variable control how long link will be displayed
# if u don't want to cut off links replace it with some big value like 300, 600 etc.
# ex. width = 300
width = shutil.get_terminal_size(fallback=(100, 50)).columns
# if you want data to be save in firebase
FIREBASE_INTEGRATION = False
# name of firebase config file, must be in root directory next to main.py file
FIREBASE_CONFIG_FILENAME = "firebase_config.json"
# url to your firebase database
FIREBASE_DATABASE_URL = "https://example_of_adress.firebaseio.com/"
# set it to True if you want to control refresh process from external app
FIREBASE_REMOTE_CONTROL = False
# set if script should send notification about price alert to connected apps.
# Works only when FIREBASE_INTEGRATION set to True
FCM_ENABLED = False
# set to True if script should send data to the firebase always after price check procedure
FIREBASE_SEND_SYNCED = True
# set to True if script should send data to the firebase, but not necessary right after price check procedure
FIREBASE_SEND_IRREGULAR = False
# set how often data should be sent to the firebase
# works only if you set #FIREBASE_SEND_IRREGULAR to True and #INFINITY_MODE set to True
FIREBASE_IRREGULAR_TIME = 3600
# set to True if you want to send best prices to firebase
# it will works only in #INFINITY_MODE and will be save to a separate branch
FIREBASE_SEND_BEST = False
# set how often (in sec) best prices will be sent to firebase
# if you set it to "SYNC" data will be send every time script it's done checking the prices
FIREBASE_BEST_TIME = 3600
# set to True if you want to send last prices to firebase
# it will works only in #INFINITY_MODE and will be save to a separate branch
FIREBASE_SEND_LAST = False
# set how often (in sec) last prices will be sent to firebase
# if you set it to "SYNC" data will be send every time script it's done checking the prices
# I recommend using "SYNC" if you are using the mobile application
FIREBASE_LAST_TIME = "SYNC"
# set to True if you want to send best prices to firebase


# ----GLOBAL VARIABLES (DON'T TOUCH)----
products_names = []
active_connections = 0
sites_to_check = 0
ssl_context = ssl.create_default_context(cafile=certifi.where())
app = None
control = None
fcm = None
DATABASE_MAIN_TABLE = "products"
DATABASE_LAST_PRICE_TABLE = "last_prices"
DATABASE_BEST_PRICE_TABLE = "best_prices"
FIREBASE_TOKENS = []
# --------------------------------------


# create session and start the data acquisition process
async def fetch_sites(list_of_products):
    tasks = []
    conn = TCPConnector(limit_per_host=MAX_CONNECTION_PER_HOST, limit=MAX_CONNECTIONS, ssl=ssl_context)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.88 Safari/537.36',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'cookie': "intl_splash=false"}
    async with ClientSession(connector=conn, headers=headers) as session:
        for product in list_of_products:
            task = loop.create_task(get_data(product, session))
            tasks.append(task)

        await gather(*tasks)
        print("\r[" + Fore.GREEN + "OK" + Fore.RESET + "] All sites has been checked")
    return tasks


# wait for downloaded data and extract price from it
async def get_data(product, session):
    global active_connections
    active_connections += 1
    html_page, status = await fetch(product.get_url(), session)
    active_connections -= 1

    print("\r[INFO] Number of sites remaining to be checked: {0} ".
          format(str(active_connections) + "/" + str(sites_to_check)), end=' ')

    if status != 200:
        product.set_error("response status: {0}".format(status))
        return product
    else:
        return await Scrappers().scrap(product, html_page)


# download data from web page
async def fetch(url, session):
    async with session.get(url, allow_redirects=True) as response:
        return await response.read(), response.status


# find best price from fetched data
def get_lowest_price(product_list):
    best_deals = []
    price_alert_list = []

    # iterate over all elements and create list of best price product
    for item_name in products_names:
        if [x for x in product_list if x.get_name() == item_name]:
            best = min((x for x in product_list if x.get_name() == item_name and x.get_price() is not None),
                       key=lambda y: y.get_price())
            list_of_best = [x for x in product_list if x.get_name() == item_name and x.get_price() == best.get_price()]

            urls = ""
            for i in list_of_best:
                urls += i.get_url() + ","
            urls = urls[:-1]

            best_product = Product(item_name, best.get_price(), urls, best.get_price_alert(), best.get_currency())
            best_deals.append(best_product)

            if best.get_price() <= float(best.get_price_alert()):
                price_alert_list.append(best_product)

    price_alert_appeared(price_alert_list)
    return best_deals


# show alert when price is equals or lower than set value
def price_alert_appeared(best_product_list):
    if len(best_product_list) > 0:
        if SHOW_PRICE_ALERT_IN_CMD:
            print("\n[" + Fore.MAGENTA + "PRICE ALERT!!" + Fore.RESET + "]")
            for product in best_product_list:
                print(product.get_name() + " " + Fore.GREEN + str(product.get_price()) + product.get_currency()
                      + " " + Fore.RESET + (product.get_url()[:width] + '...' if len(product.get_url()) > width else product.get_url()))

        if FIREBASE_INTEGRATION and FCM_ENABLED and len(FIREBASE_TOKENS) > 0:
            for product in best_product_list:
                mess = messaging.MulticastMessage(data={
                    "name": product.get_name(),
                    "price": str(product.get_price()),
                    "price_alert": str(product.get_price_alert()),
                    "currency": str(product.get_currency()),
                    "product_id": str(products_names.index(product.get_name())),
                    "url": product.get_url()
                }, tokens=FIREBASE_TOKENS)
                messaging.send_multicast(mess)


# load all products saved in files in folder parts_files and save it to list
def load_products():
    global products_names
    products = []
    products_names = []
    files_path = "{0}/products".format(os.getcwd())
    files = os.listdir(files_path)

    for f in files:
        if f.endswith(".json") and os.stat(os.path.join(files_path, f)).st_size != 0:
            with open(os.path.join(files_path, f), 'r') as file:
                try:
                    json_data = json.load(file)
                    for url in json_data["urls"]:
                        products.append(Product(json_data["name"],
                                                None,
                                                url,
                                                json_data["price_alert"],
                                                json_data["price_currency"])
                                        )
                    products_names.append(json_data["name"])
                except Exception:
                    print(Fore.YELLOW + "[WARN] JSON ERROR, check if the file is valid for JSON format "
                                        "and if it has all required fields -> {0}".format(f) + Fore.RESET)
    return products


# listener for firebase db to control refresh data from android app
# noinspection PyUnresolvedReferences
def control_listener(event):
    if INFINITY_MODE:
        if event.data == 1 and event.path == "/forceRefresh":
            try:
                if not loop.is_running():
                    # force refresh data if data are not refreshing
                    print(Fore.YELLOW + "[INFO] Forced data refresh" + Fore.RESET)
                    loop.run_until_complete(main())
            except Exception as exception:
                print(exception)

            control.update({"forceRefresh": 0})


def new_fcm_token(event):
    if isinstance(event.data, dict):
        for i in event.data.values():
            if i not in FIREBASE_TOKENS:
                FIREBASE_TOKENS.append(i)
    else:
        x = event.data.split(":")[1]
        if x not in FIREBASE_TOKENS:
            FIREBASE_TOKENS.append(x)


# noinspection PyUnresolvedReferences
async def main():
    if FIREBASE_INTEGRATION:
        control.update({"isRefreshing": 1})

    # get list of products
    list_of_products = load_products()

    # set number of sites to check
    global sites_to_check
    sites_to_check = len(list_of_products)

    # get date for db records
    date = "{0} {1}".format(datetime.date(datetime.now()), datetime.time(datetime.now()).replace(microsecond=0))
    print("\n[INFO] Start checking prices ({0})".format(date))

    # start fetching site
    task = loop.create_task(fetch_sites(list_of_products))
    await task

    # check lowest price only for products without error note
    right_products = []
    for p in task.result():
        if p.result().get_error() is None:
            right_products.append(p.result())

    list_of_best_price = get_lowest_price(right_products)
    # print list of best prices
    if SHOW_OUTPUT_IN_CMD:
        print(Fore.CYAN + "\n----------BEST PRICES------------" + Fore.RESET)
        for i in list_of_best_price:
            print(i.get_name() + " " + Fore.GREEN + str(i.get_price()) + i.get_currency() + " " + Fore.RESET +
                  (i.get_url()[:width] + '...' if len(i.get_url()) > width else i.get_url()))

        # print information about the products with the problem
        error_page = []
        for i in [x for x in task.result() if x.result().get_error() is not None]:
            error_page.append(i)

        if len(error_page) > 0:
            print(Fore.YELLOW + "\n---------ERROR PRODUCTS----------" + Fore.RESET)
            for i in error_page:
                print(i.result().get_name() + " " + Fore.RED + str(i.result().get_error()) + Fore.RESET +
                      " " + (i.result().get_url()[:width] + '...' if len(i.result().get_url()) > width else i.result().get_url()))

    # create database
    db = Database("items.db")
    db.clear_database(DATABASE_LAST_PRICE_TABLE)
    db.create_price_table(DATABASE_LAST_PRICE_TABLE)
    db.create_price_table(DATABASE_BEST_PRICE_TABLE)

    # save prices to database
    for i in list_of_best_price:
        db.create_database(i.get_name())
        db.insert_record(i, date)
        db.insert_record_last_prices(DATABASE_LAST_PRICE_TABLE, i, date)

    # check best price saved in db and replace if actual is lower
    for i in list_of_best_price:
        if db.select_database(i.get_name(), DATABASE_BEST_PRICE_TABLE) is not None:
            if db.select_database(i.get_name(), DATABASE_BEST_PRICE_TABLE)[2] > i.get_price():
                db.insert_record_last_prices(DATABASE_BEST_PRICE_TABLE, i, date)
        else:
            db.insert_record_last_prices(DATABASE_BEST_PRICE_TABLE, i, date)

    print("\n[" + Fore.GREEN + "OK" + Fore.RESET + "] Prices have been saved to the local database")

    if FIREBASE_INTEGRATION:
        if FIREBASE_SEND_SYNCED or FIREBASE_SEND_LAST or FIREBASE_SEND_BEST:
            print("[INFO] SENDING DATA TO FIREBASE...")
            if FIREBASE_SEND_SYNCED:
                send_to_firebase(db.get_all(DATABASE_LAST_PRICE_TABLE), DATABASE_MAIN_TABLE)
            if FIREBASE_SEND_LAST and FIREBASE_LAST_TIME == "SYNC":
                send_to_firebase(db.get_all(DATABASE_LAST_PRICE_TABLE), DATABASE_LAST_PRICE_TABLE)
            if FIREBASE_SEND_BEST and FIREBASE_BEST_TIME == "SYNC":
                send_to_firebase(db.get_all(DATABASE_BEST_PRICE_TABLE), DATABASE_BEST_PRICE_TABLE)

            print("[INFO] DATA HAS BEEN SENT")

        control.update({"isRefreshing": 0})


# send data to firebase
def send_to_firebase(list_of_parts, branch_name):
    root = fire_db.reference(branch_name)

    if branch_name == DATABASE_MAIN_TABLE:
        for part in list_of_parts:
            path = part[0] + "/" + part[1]
            root.child(path).set({
                'name': part[0],
                'price': part[2],
                'date': part[1],
                'urls': part[3].split(","),
                'currency': part[4]
            })
    else:
        for part in list_of_parts:
            root.child(part[0]).set({
                'name': part[0],
                'price': part[2],
                'date': part[1],
                'urls': part[3].split(","),
                'currency': part[4]
            })


# load and check config variable
def load_config():
    print("[INFO] LOADING CONFIG...")

    # init colored text output in console
    init_color()

    if INFINITY_MODE:
        print("[" + Fore.GREEN + "ON" + Fore.RESET + "] INFINITY MODE")
    else:
        print("[" + Fore.RED + "OFF" + Fore.RESET + "] INFINITY MODE")

    # ------------------ init firebase ------------------------
    global app
    global control
    global fcm

    if FIREBASE_INTEGRATION:
        print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase integration")
        try:
            cred = credentials.Certificate("{0}/{1}".format(os.getcwd(), FIREBASE_CONFIG_FILENAME))
            app = initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
            control = fire_db.reference("control")
            fcm = fire_db.reference("fcm_tokens")
        except FileNotFoundError:
            print(Fore.RED + "[WARN]File '{0}' not found, if you don't want to use firebase turn off 'FIREBASE "
                             "INTEGRATION' in config section".format(FIREBASE_CONFIG_FILENAME) + Fore.RESET)
            exit()

        # set listener for control force Refresh
        if INFINITY_MODE and FIREBASE_REMOTE_CONTROL:
            control.listen(control_listener)
            print(
                "[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase remote control")
        else:
            print("[" + Fore.RED + "OFF" + Fore.RESET + "] Firebase remote control (works only in INFINITY MODE)")

        if FCM_ENABLED:
            fcm.listen(new_fcm_token)
            print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase Cloud Messaging")
        else:
            print("[" + Fore.RED + "OFF" + Fore.RESET + "] Firebase Cloud Messaging")

        if FIREBASE_SEND_SYNCED and FIREBASE_SEND_IRREGULAR:
            print(Fore.RED + "[ERROR] Variable #FIREBASE_SEND_SYNCED and #FIREBASE_SEND_IRREGULAR"
                             " cannot be set to true at one time" + Fore.RESET)
            exit()

        if FIREBASE_SEND_IRREGULAR:
            if INFINITY_MODE:
                if isinstance(FIREBASE_IRREGULAR_TIME, int):
                    # run firebase send data loop with new thread
                    t1 = Thread(target=firebase_send_loop)
                    t1.start()
                    print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase IRREGULAR SEND DATA")
                else:
                    print(Fore.RED + "[ERROR] Variable #FIREBASE_IRREGULAR_TIME is not a number" + Fore.RESET)
                    exit()
            else:
                print("[" + Fore.RED + "OFF" + Fore.RESET + "] Firebase IRREGULAR SEND DATA "
                                                            "(works only in #INFINITY_MODE)")

        if FIREBASE_SEND_BEST:
            if INFINITY_MODE:
                if isinstance(FIREBASE_BEST_TIME, int):
                    # run firebase send data loop with new thread
                    t2 = Thread(target=firebase_send_best_loop)
                    t2.start()
                    print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase SEND BEST PRICES")
                elif FIREBASE_BEST_TIME == "SYNC":
                    print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase SEND BEST PRICES (SYNC MODE)")
                else:
                    print(Fore.RED + "[ERROR] Variable #FIREBASE_BEST_TIME is not a number" + Fore.RESET)
                    exit()
            else:
                print("[" + Fore.RED + "OFF" + Fore.RESET + "] Firebase SEND BEST PRICES "
                                                            "(works only in #INFINITY_MODE)")

        if FIREBASE_SEND_LAST:
            if INFINITY_MODE:
                if isinstance(FIREBASE_LAST_TIME, int):
                    # run firebase send data loop with new thread
                    t3 = Thread(target=firebase_send_last_loop)
                    t3.start()
                    print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase SEND LAST PRICES")
                elif FIREBASE_LAST_TIME == "SYNC":
                    print("[" + Fore.GREEN + "ON" + Fore.RESET + "] Firebase SEND LAST PRICES (SYNC MODE)")
                else:
                    print(Fore.RED + "[ERROR] Variable #FIREBASE_LAST_TIME is not a number" + Fore.RESET)
                    exit()
            else:
                print("[" + Fore.RED + "OFF" + Fore.RESET + "] Firebase SEND LAST PRICES "
                                                            "(works only in #INFINITY_MODE)")
    else:
        print("[" + Fore.RED + "OFF" + Fore.RESET + "] Firebase integration")
        print("[" + Fore.RED + "OFF" + Fore.RESET + "] |-> Firebase Cloud Messaging")
        print("[" + Fore.RED + "OFF" + Fore.RESET + "] |-> Firebase remote control ")
    # ---------------------------------------------------------


def firebase_send_loop():
    local_db = Database("items.db")
    while True:
        sleep(FIREBASE_IRREGULAR_TIME)
        send_to_firebase(local_db.get_all(DATABASE_LAST_PRICE_TABLE), DATABASE_MAIN_TABLE)


def firebase_send_best_loop():
    local_db = Database("items.db")
    while True:
        sleep(FIREBASE_BEST_TIME)
        send_to_firebase(local_db.get_all(DATABASE_BEST_PRICE_TABLE), DATABASE_BEST_PRICE_TABLE)


def firebase_send_last_loop():
    local_db = Database("items.db")
    while True:
        sleep(FIREBASE_LAST_TIME)
        send_to_firebase(local_db.get_all(DATABASE_LAST_PRICE_TABLE), DATABASE_LAST_PRICE_TABLE)


if __name__ == "__main__":
    load_config()
    loop = get_event_loop()

    if FIREBASE_INTEGRATION:
        control.update({"forceRefresh": 0})

    while True:
        try:
            if not loop.is_running():
                loop.run_until_complete(main())
        except ClientConnectorError as e:
            print("cant connect to site :/, check your internet connection")
            break
        except Exception as e:
            print(e)
            break

        if INFINITY_MODE:
            shift = random.randint(REFRESH_FREQUENCY, REFRESH_FREQUENCY + REFRESH_SHIFT)
            print("[INFO] Next price check in: {0}min {1}sec".format(int(shift / 60), int(shift % 60)))
            print("-------------------------------------------------")
            sleep(shift)
        else:
            break
    loop.close()
    exit()

import sqlite3


class Database:
    def __init__(self, db_name):
        self.__db_name = db_name
        self.__conn = sqlite3.connect(self.__db_name)
        self.__c = self.__conn.cursor()

    def create_price_table(self, name):
        sql = f'CREATE TABLE IF NOT EXISTS {name} (name text NOT NULL PRIMARY KEY, date text, price real, url text, currency text)'
        self.__c.execute(sql)
        self.__conn.commit()

    def create_database(self, table_name):
        sql = 'CREATE TABLE IF NOT EXISTS {0} (date text NOT NULL PRIMARY KEY, price real, url text, currency text)'.format(table_name.replace(" ", ""))
        self.__c.execute(sql)
        self.__conn.commit()

    def select_database(self, name, table_name):
        self.__c.execute("SELECT * FROM {0} WHERE name ='%s'".format(table_name.replace(" ", "")) % name)
        self.__conn.commit()
        return self.__c.fetchone()

    def clear_database(self, table_name):
        sql = f'DROP TABLE IF EXISTS {table_name}'
        self.__c.execute(sql)
        self.__conn.commit()

    def insert_record(self, product, date):
        var = [date, product.get_price(), product.get_url(), product.get_currency()]
        com = 'INSERT OR REPLACE INTO {0}(date,price,url,currency) VALUES(?,?,?,?)'.format(product.get_name().replace(" ", ""))
        self.__c.execute(com, var)
        self.__conn.commit()

    def insert_record_last_prices(self, table_name, product, date):
        var = [product.get_name(), date, product.get_price(), product.get_url(), product.get_currency()]
        com = 'INSERT OR REPLACE INTO {0}(name,date,price,url,currency) VALUES(?,?,?,?,?)'.format(table_name.replace(" ", ""))
        self.__c.execute(com, var)
        self.__conn.commit()

    def get_all(self, table_name):
        self.__c.execute(f"SELECT * From {table_name}")
        self.__conn.commit()
        return self.__c.fetchall()

import sqlite3, decimal, secrets

D = decimal.Decimal


# def adapt_decimal(d):
#     return str(d)


# def convert_decimal(s):
#     return D(s)


# Register the adapter
# sqlite3.register_adapter(D, adapt_decimal)

# # Register the converter
# sqlite3.register_converter("decimal", convert_decimal)


class Database:
    def __init__(self):
        self.con = sqlite3.connect(
            "scraper.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.con.cursor()
    
    def createAuthTable(self):
        self.cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='auth' ''')
        row = self.cursor.fetchone()
        print("ROW IS ", row)
        if row[0] == 1:
            print("auth Table already exists")
            self.cursor.execute(''' DELETE FROM auth ''')
        else:
            self.cursor.execute("""CREATE TABLE auth ( id INTEGER PRIMARY KEY AUTOINCREMENT, apikey VARCHAR(32), active INTEGER)""")
            print("Successfully created auth table.")


    def createScraperTable(self):
        print("Creating Products Table")

        # To check if table already exists
        self.cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='products' ''')

        row = self.cursor.fetchone()
        print("ROW IS ", row)
        if row[0] == 1:
            print("products Table already exists")
            self.cursor.execute(''' DELETE FROM products ''')
        else:
            self.cursor.execute("""CREATE TABLE products (
                sku VARCHAR(254), 
                title VARCHAR(254), 
                price TEXT,
                category_id VARCHAR(254),
                category_title VARCHAR(254),
                images TEXT,
                description TEXT,
                flag_status VARCHAR(254) DEFAULT 'N',
                PRIMARY KEY (sku, category_id)
                )""")
            print("Successfully created products table.")

    def generateAuthKey(self):
        print("Generating new auth key")
        token = secrets.token_urlsafe(32)
        data = ("VWPwlDelPZ_uAz9lzDeq8s_3XjAe54UaUNBBDKNfqmU", 1)
        self.cursor.execute("""INSERT INTO auth (apikey, active) VALUES (?,?)""", data)
        self.con.commit()
        print("Generate new auth key {0}".format(token))

    def checkIfAuthenticated(self, apikey):
        if apikey:
            print(apikey)
            row = self.cursor.execute("""SELECT count(1) FROM auth WHERE apikey = ?""", (apikey,)).fetchone()[0]
            if row:
                return True
        return False

    def insertProductDetails(self, details):
        print("Inserting Product Details")
        self.cursor.execute("""
        INSERT INTO products (sku,title,price,category_id,category_title,images,description) VALUES (?,?,?,?,?,?,?)""", details)
        print("Product Details Inserted")
        self.con.commit()

    def getProductDetails(self, sku):
        rows = self.cursor.execute(
            """SELECT sku,title,price,images,description,category_id,category_title,flag_status FROM products WHERE sku LIKE ?""", ("%" + sku + "%",)).fetchall()
        data = {}
        if rows:
            for index, row in enumerate(rows):
                data[index] = {
                    'sku': row[0],
                    'title': row[1],
                    'price': row[2],
                    'images': row[3],
                    'description': row[4],
                    'category_id': row[5],
                    'category_title': row[6],
                    'flag_status': row[7]
                }
        return data

    def updateProductFlagStatus(self, sku, category_id, previous, new):
        self.cursor.execute(
            "UPDATE products SET flag_status = ? WHERE sku = ? AND category_id = ? AND flag_status = ?", (new, sku, category_id, previous))
        self.con.commit()
        if self.cursor.rowcount < 1:
            return False
        return True

    def getFlagStatusProducts(self, status):
        rows = self.cursor.execute(
            "SELECT sku,title,price,images,description,category_id,category_title,flag_status FROM products WHERE flag_status = ?", (status)).fetchall()
        data = {}
        if rows:
            for index, row in enumerate(rows):
                data[index] = {
                    'sku': row[0],
                    'title': row[1],
                    'price': row[2],
                    'images': row[3],
                    'description': row[4],
                    'category_id': row[5],
                    'category_title': row[6],
                    'flag_status': row[7]
                }
        return data

    def getCategoryList(self):
        rows = self.cursor.execute(
            "SELECT DISTINCT category_id, category_title FROM products").fetchall()
        data = {}
        if rows:
            for index, row in enumerate(rows):
                data[index] = {
                    'category_id': row[0],
                    'category_title': row[1],
                }
        return data

    def closeConnection(self):
        self.con.close()


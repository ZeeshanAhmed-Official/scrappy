from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests
import json
import csv
import urllib.request
import os.path
import urllib.parse as urlparse
from re import sub
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
from database import Database
import decimal
import shutil

D = decimal.Decimal


PRODUCT_URL = "https://store.ashleyfurniturehomestore.co.ke"
# URL = "https://testabc.com/"


class CategoryScraper:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.soup = None
        self.categories = {}

    def createScraper(self):
        self.html = requests.get(self.url)
        self.soup = BeautifulSoup(self.html.content, 'html.parser')

    def scrapeCategories(self, pretty_output=False):
        for nav in self.soup.find_all('ul', class_="wsmenu-list"):
            for ul in nav.find_all('ul'):
                parent = None
                if ( len(ul.find_all('li')) == 0 ):
                    zeroNavLink = ul.find_parent('div').find_previous_siblings('a')
                    self.categories[zeroNavLink[0].text] = PRODUCT_URL + zeroNavLink[0]['href']
                    continue

                # UNCOMMENT THIS CODE AT THE END, SCRAPPING LINKS FOR THE CATEGORIES
                for li in ul.find_all('li'):
                    link = li.select('a')
                    name = link[0].text

                    if li.has_attr('class') and li['class'][0] == 'title':
                        if pretty_output == True:
                            parent = name
                            self.categories[parent] = {}
                        else:
                            continue
                    else:
                        if parent and pretty_output == True:
                            self.categories[parent][name] = link[0]['href']
                        else:
                            self.categories[name] = link[0]['href']

    def getScrapedCategories(self):
        return self.categories


class CategoryProductsScraper():
    def __init__(self, categories):

        if not categories:
            print(
                "No catergories are loaded, please make sure that categories exist and are scraped!")
            return
        self.counter = 1
        self.categories = categories
        self.products = {}

    def processCategories(self):
        for category_name, url in self.categories.items():
            if ( url.startswith('/page') | url.startswith('/index') ) :
                url = PRODUCT_URL + url
            # print('category Name:', category_name, 'Link: ', url)
            self.scrapeProducts(category_name, url)

    def scrapeProducts(self, name, url):
        api_url = self.createScrapeUrl(url)
        paginate = True
        current_page = 1

        if api_url:
            while paginate:
                category_url = "{}&pagenumber={}&ajax=1&sortby=1".format(
                    api_url, current_page)
                # print("SCRAPING URL", category_url)
                html = requests.get(category_url)
                soup = BeautifulSoup(html.content, 'html.parser')
                products = soup.findAll(
                    True, {'class': ['col-xs-12', 'col-sm-4', 'col-md-4', 'mob-col-6']})

                for product in products:
                    product_info = self.extractProductInfo(product)
                    if product_info:
                        self.products[self.counter] = {
                            product_info['name']: product_info['link']}
                        self.counter += 1
                    # else:
                        # print("\nISSUE\n")
                if len(products) - 1 == 12:
                    current_page += 1
                else:
                    paginate = False

    # Generates API URL for fetcing products
    def createScrapeUrl(self, url):
        parsed = urlparse.urlparse(url).path
        extracted = os.path.split(parsed)
        try:
            subcategory = int(extracted[1])
        except ValueError:
            return None

        return "https://store.ashleyfurniturehomestore.co.ke{}?subcategory[]={}".format(extracted[0].replace('/subcategory', ''), subcategory)

    def extractProductInfo(self, product):
        try:
            for link in product.findAll(True, {'class': ['cat-ProName']}):
                product_link = link.select('a')
                return {'name': product_link[0].text.rstrip().strip(), 'link': 'https://store.ashleyfurniturehomestore.co.ke/{}'.format(product_link[0]['href'])}
        except:
            return None

    def getScrapedProducts(self):
        return self.products

# Product Scraper
# Scrapes details for a single product
class ProductScraper:
    def __init__(self):
        self.url = None
        self.page_source = None
        self.product = {}
        self.SKUsInserted = list()
        self.db = Database()

        # Checking whether the specified path exists
        isExisting = os.path.exists('products/')
        print("Directory Exists ", isExisting)
        if isExisting: 
            shutil.rmtree('products/')
        # MAKE New directory named products
        os.mkdir('products/')
        print("Directory Created ", os.path.exists('products/'))

    def setProductUrl(self, url):
        self.url = url

    def loadDyanmicContent(self):
        self.page_source = requests.get(self.url)

    def scrapeProduct(self):
        if not self.page_source:
            print("Missing HTML body...")
            return  

        soup = BeautifulSoup(self.page_source.content, 'html.parser')
        for nav in soup.find_all('div', class_="detailContainer"):

            # Product Title
            item_title = nav.find(True, {'class': 'ProDtlTitle'}).get_text()
            # Product Price
            item_price = nav.find(
                True, {'class': 'Price'}).get_text().replace('KShs', '')
            item_price = str(D(sub(r'[^\d.]', '', item_price)))

            # Product SKU
            item_sku = nav.find(True, {'class': 'product-number'})
            if item_sku:
                item_sku = item_sku.find('span').get_text().strip()

            # Product Images
            images = ''
            slideshow = nav.find(True, {'class': 'ProDtlImg'}).select('ul > li')
            for item in slideshow:
                image = item.select('img')[0]['src']
                filename = 'products/' + image.split('/')[-1]

                image_url = image
                if 'http' not in image:
                    image_url = PRODUCT_URL + image
                
                new_image_url = image_url + 'products/' + image

                print("Image URL : ", image_url)
                # print("New Image URL : ", new_image_url)

                received_image = requests.get(image_url)
                with open(filename, 'wb') as outfile:
                    outfile.write(received_image.content)
                images += image_url + "\n"

            desc = ''
            divs = nav.find(True, {'class': 'ProDesc'}).select('div')

            for div in divs:
                if div.select('ul > li'):
                    heading = div.select('h5, h5 > b')
                    if heading:
                        desc += ("\n{} \n\n").format(heading[0].text)
                    for detail in div.select('ul > li'):
                        desc += detail.text + "\n"
                else:
                    desc += div.text + "\n"

            # Product Category
            category = nav.find(True, {'class': 'Breadcum'}).select('ul li a')
            if len(category) > 1:
                category_id = category[-1]['href'].split('/')[-1]
                category_title = category[-1].text

            product_data = (
                item_sku,
                item_title,
                item_price,
                category_id,
                category_title,
                images,
                desc,
            )
            print("Images are ", images)

            compositeKey = item_sku+"_"+item_title.lower().replace(" ", "_")
            print("product_data", item_sku, category_id, item_title, compositeKey, json.dumps(self.SKUsInserted, sort_keys=True, indent=4))
            if compositeKey in self.SKUsInserted :
                print("skipping this product, already added")
            else :
                self.db.insertProductDetails(product_data)
                self.SKUsInserted.append(compositeKey)
            
            print("\n")

        # self.db.closeConnection()

# RUNNING SCRIPTS FROM HERE
db = Database()
db.createAuthTable()
db.createScraperTable()
db.generateAuthKey()
cat = CategoryScraper(PRODUCT_URL)
cat.createScraper()
cat.scrapeCategories()
categories = cat.getScrapedCategories()
print("CATEGORIES SCRAPED", len(categories), "\n") # , list(categories.keys())) #json.dumps(categories, sort_keys=True, indent=4))

# categories = {'Sectional Sofas': 'https://store.ashleyfurniturehomestore.co.ke/category/showsorted/categoryid/7/subcategory/12', 'Sleeper Sofas': 'https://store.ashleyfurniturehomestore.co.ke/category/showsorted/categoryid/7/subcategory/13'}
# categories = {'Sectional Sofas': 'https://store.ashleyfurniturehomestore.co.ke/category/showsorted/categoryid/7/subcategory/12'}
# print(categories)
catprod = CategoryProductsScraper(categories)
catprod.processCategories()
products = catprod.getScrapedProducts()
# products = {1: {'Black/Gray Bardarson 5-Piece Sectional with Chaise': 'https://store.ashleyfurniturehomestore.co.ke//category/living-room/black-gray-bardarson-5-piece-sectional-with-chaise194.html'}, 2: {'Dellara 4-Piece Sectional with Chaise': 'https://store.ashleyfurniturehomestore.co.ke//category/living-room/dellara-4-piece-sectional-with-chaise.html'}}

# print("\nPRODUCTS SCRAPED", list(products.values())) # json.dumps(products, sort_keys=True, indent=4))
print("\nPRODUCTS SCRAPED SIZE", len(products)) #, products) # json.dumps(products, sort_keys=True, indent=4))

ps = ProductScraper()
for index in products:
    print("adding product number ", index);
    product = products[index]
    url = list(product.values())[0]
    ps.setProductUrl(url)
    ps.loadDyanmicContent()
    ps.scrapeProduct()

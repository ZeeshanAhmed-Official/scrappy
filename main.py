import requests
from bs4 import BeautifulSoup

#PRODUCT_URL = "https://www.ashleyfurniture.com/p/antonlini_sofa/2100138.html?cgid=sofas-and-couches"
PRODUCT_URL = "https://www.ashleyfurniture.com/p/kids_louvered_twin_low_loft_bed/B600000440.html?cgid=kids-bunk-beds#start=2"

class ProductScraper:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.content = None
        self.soup = None
        self.images = None
        self.product_payload = {}
    
    def stripTags( self, html ):
        soup = BeautifulSoup( html, features="html.parser" )
        return soup.get_text()
    
    def getDescriptionFeatures( self, detail ):
        listing_found = False
        payload = {}
        
        if( detail.find('h3') ):
            print("HEADING FOUND", detail.find('h3').get_text() )
            payload['title'] = detail.find('h3').get_text()
        
        if( detail.find_all('li') ):
            listing_found = True
            print([item.get_text() for item in detail.find_all('li')])
            for index, item in enumerate([item.get_text() for item in detail.find_all('li')]):
                split_text = self.extractKeyValue( item )
                if len(split_text) == 2:
                    payload[ split_text[0].lower() ] = split_text[1].strip()
                else:
                    payload[ index ] = item

        
        if( not listing_found and detail.get_text() ):
            print( "TEXT FOUND", detail.get_text().split() )
        
        return payload
    
    def extractKeyValue( self, string ):
        items = string.split(':')
        return items
    
    def createScraper( self ):
        self.html = requests.get(self.url)
        self.soup = BeautifulSoup(self.html.content, 'html.parser')
        self.content = self.soup.find_all('div', class_="product-info")
        self.images = self.soup.find_all('div', class_="product-image-container")
    
    def processProduct( self ):
        for item in self.content:
            description = item.select(".detail-column-left div:nth-child(1)")
            print("DESCRIPTION", description)
            product_details_right = item.select(".detail-column-right .detail-row")
            product_details_left = item.select(".detail-column-left .detail-row")
            
            for detail in product_details_right:
                print("PRINTING PROPERTIES RIGHT")
                items = self.getDescriptionFeatures(detail)
                print(items)
                print("===================")
            
            for detail in product_details_left:
                print("PRINTING PROPERTIES LEFT")
                items = self.getDescriptionFeatures(detail)
                print(items)
                print("===================")
        
        # Extract Product Images
        for image in self.images:
            product_images = image.select(".slick-slider li img")
            for item in product_images:
                print("PRINTING IMAGE SRC")
                print(item['src'])
                print("===================")
    

obj = ProductScraper(PRODUCT_URL)
obj.createScraper()
obj.processProduct()
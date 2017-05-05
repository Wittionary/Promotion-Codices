from urllib.request import urlopen as uRequest
from bs4 import BeautifulSoup as soup
import urllib.request

#http://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"
uOpener = AppURLopener()

my_url = 'https://www.relay.fm/connected/140'

# Opens the connection, grabs the page
uClient = uOpener.open(my_url) 
page_html = uClient.read()

# Closes connection
uClient.close()

# HTML parsing
page_soup = soup(page_html, "html.parser")

# Grabs all (1) promo div elements with class of "sp-area"
sp_areas = page_soup.findAll("div", {"class":"sp-area"}) # This is an array
sp_areas[0].ul.li.a["href"] # 'http://casper.com/connected'
sp_areas[0].ul.li.a.text # 'Casper'

promo = sp_areas[0].findAll("li") # This is an array

# TODO: Iterate through array 'promo' and print results
# promo[0].text
# promo[0].a["href"]

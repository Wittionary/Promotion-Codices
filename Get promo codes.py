# Following the tutorial at: 
# https://www.youtube.com/watch?v=XQgXKtPSzUI
from urllib.request import urlopen as uRequest
from bs4 import BeautifulSoup as soup
import urllib.request

#http://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

uOpener = AppURLopener()

# --------------- Get list of podcasts ---------------
my_url = 'https://www.relay.fm/shows'

# Opens the connection, grabs the page
uClient = uOpener.open(my_url) 
page_html = uClient.read()

# Closes connection
uClient.close()

# HTML parsing
page_soup = soup(page_html, "html.parser")

# Grabs both active and retired shows
podcasts = page_soup.findAll("div", {"class":"small-12 medium-8 columns"})
# podcasts[32].h4.a.text # 'Virtual'
# podcasts[32].h4.a["href"] # '\virtual'

# https://docs.python.org/3/tutorial/errors.html
for podcast in podcasts:
	try:
		podcast.h4.a["href"]
		podcast.h4.text
	except TypeError: # This was being thrown by Master Feed since there's no URL to show
		pass

# TODO:
# - Filter out RETIRED shows from ACTIVE one
# - Make full show URL
# - Get last 5 episodes
# - Iterate through each url with code below and put promos in list
# - Filter duplicate promos out removing the oldest codes first

# --------------- Episode page ---------------
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

promos = sp_areas[0].findAll("li") # This is an array

# https://www.tutorialspoint.com/python/python_for_loop.htm
for promo in promos:
	promo.a["href"]
	promo.text

# Gets publish date of episode
pubdates = page_soup.findAll("p", {"class":"pubdate"})
pubdates[0].small.text
# TODO: format date so that it's mm-dd-yyyy and not '\nMay 2nd, 2017\n·\n67\nminutes'
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
podcasts = page_soup.findAll("h3", {"class":"broadcast__name"})
numOfPodcasts = len(podcasts)
podcastURL = []
# podcasts[1].a.text # 'Analog(ue)'
# podcasts[1].a["href"] # '\analogue'

# https://docs.python.org/3/tutorial/errors.html
# Make dictionary of all the podcast names, partial URLs, and full URLs
podcastURL = []
podcastText = []

for podcast in podcasts:
	try:
		podcastURL.append(podcast.a["href"])
		podcastText.append(podcast.a.text)
	except TypeError: # This was being thrown by Master Feed since there's no URL to show
		pass




# TODO:
# - Filter out RETIRED shows from ACTIVE ones
# - Make full show/episode URL
# - Iterate through each url with code below and put promos in list
# - Filter duplicate promos out removing the oldest codes first

# --------------- Episode page ---------------
# TODO: Iterate through 5 most recent shows; compare with today's date and only grab stuff in the past 3 months?
episode_url = 'https://www.relay.fm/connected/202'

# Opens the connection, grabs the page
uClient = uOpener.open(episode_url) 
page_html = uClient.read()

# Closes connection
uClient.close()

# HTML parsing
page_soup = soup(page_html, "html.parser")

# Grabs all (1) promo div elements with class of "sp-area"
sp_areas = page_soup.findAll("div", {"class":"sp-area"}) # This is an array
sp_areas[0].ul.li.a["href"] # 'https://smilesoftware.com/'
sp_areas[0].ul.li.a.text # 'TextExpander'

promos = sp_areas[0].findAll("li") # This is an array

# https://www.tutorialspoint.com/python/python_for_loop.htm
for promo in promos:
	promo.a["href"]
	promo.text

# Gets publish date of episode
pubdates = page_soup.findAll("p", {"class":"pubdate"})
pubdate = pubdates[0].small.text.split('·')
print(pubdate[0].strip('\n'))

# TODO: format date so that it's mm-dd-yyyy and 
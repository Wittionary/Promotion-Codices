from urllib.request import urlopen as uRequest
from bs4 import BeautifulSoup as soup

my_url = 'https://www.relay.fm/connected/140'
uClient = uRequest(my_url) #throws 403 error, adjust HTML user-agent per http://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping

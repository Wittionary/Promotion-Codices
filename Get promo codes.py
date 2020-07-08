# Following the tutorial at:
# https://www.youtube.com/watch?v=XQgXKtPSzUI
from urllib.request import urlopen as uRequest
from bs4 import BeautifulSoup as soup
import urllib.request

# TODO:
# - Filter out RETIRED shows from ACTIVE ones
# - Filter duplicate promos out removing the oldest codes first

# http://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"


uOpener = AppURLopener()
root_url = "https://www.relay.fm"
ShowCatalog = []

# --------------- List of podcasts/shows ---------------
def GetShows():
    """Returns a list of dictionaries with show titles and URLs"""
    showlist_url = root_url + "/shows"

    # Opens the connection, grabs the page
    uClient = uOpener.open(showlist_url)
    showlist_html = uClient.read()

    # Closes connection
    uClient.close()

    # HTML parsing
    showlist_soup = soup(showlist_html, "html.parser")

    # Grabs both active and retired shows
    shows = showlist_soup.findAll("h3", {"class": "broadcast__name"})
    # https://docs.python.org/3/tutorial/errors.html
    # Make dictionary of all the podcast names, partial URLs, and full URLs

    for show in shows:
        try:
            Dictionary = {}
            
            if show.a:
                Dictionary['title'] = show.a.text
                Dictionary['url'] = show.a["href"]
                ShowCatalog.append(Dictionary)
        except TypeError:  # This was being thrown by Master Feed since there's no URL to show
            pass
        except AttributeError:
            pass

    return ShowCatalog

#print("There are " + str(len(podcastURL)) + " shows.")
# --------------- Get most recent episodes ---------------
def GetEpisodeURLs(ShowCatalog):
    """Input the ShowCatalog object.
    Example: TODO
    
    Adds the URLs for the most recent episodes in a list to the ShowCatalog object.
    Example: TODO """
    for Show in ShowCatalog:
        show_url = root_url + Show['url'] #ShowURL

        # Opens the connection, grabs the page
        uClient = uOpener.open(show_url)
        show_html = uClient.read()
        uClient.close() # Closes connection

        # HTML parsing
        show_soup = soup(show_html, "html.parser")
        episode_wrap = show_soup.findAll("div", {"class": "episode-wrap animated"})

        Show['episodes'] = []
        for episode in episode_wrap[:10]:  # Will have to load the next page if we want to get more episodes
            Dictionary = {}
            episode_line = episode.h3.a.text
            episode_info = episode_line.split(":")
            Dictionary['number'] = episode_info[0].strip("#")
            Dictionary['title'] = episode_info[1].strip()
            Show['episodes'].append(Dictionary)
        
    return ShowCatalog

# --------------- Episode page ---------------
def GetPromoCodes(ShowCatalog):
    """doc strings?"""
    for Show in ShowCatalog:
        show_url = root_url + Show['url']  #ShowURL

        for Episode in Show['episodes']:
            episode_url = show_url + '/' + Episode['number']

            # Opens the connection, grabs the page
            uClient = uOpener.open(episode_url)
            episode_html = uClient.read()

            # Closes connection
            uClient.close()

            # HTML parsing
            episode_soup = soup(episode_html, "html.parser")

            # Grabs all (1) promo div elements with class of "sp-area"
            sp_areas = episode_soup.findAll("div", {"class": "sp-area"})  # This is an array
            sp_areas[0].ul.li.a["href"]  # 'https://smilesoftware.com/'
            sp_areas[0].ul.li.a.text  # 'TextExpander'

            promos = sp_areas[0].findAll("li")  # This is an array

            Episode['promos'] = []
            for promo in promos:
                information = promo.text
                information = information.split(":",1)
                Dictionary = {}
                Dictionary['sponsor'] = information[0]
                Dictionary['url'] = promo.a["href"]
                Dictionary['description'] = information[1]
                Episode['promos'].append(Dictionary)
            
    return ShowCatalog


            # Gets publish date of episode
            #pubdates = episode_soup.find("p", {"class": "pubdate"})
            #pubdate = pubdates.small.text.split("·")
            #pubdate = pubdate[0].strip("\n")
            #print(pubdate)

# TODO: format date so that it's mm-dd-yyyy and

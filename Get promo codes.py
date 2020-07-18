# Following the tutorial at:
# https://www.youtube.com/watch?v=XQgXKtPSzUI
#from urllib.request import urlopen as uRequest
from bs4 import BeautifulSoup as soup
import requests, logging, time, json
from os import path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

# TODO:
# - Filter out RETIRED shows from ACTIVE ones
# - Filter duplicate promos out removing the oldest codes first

root_url = "https://www.relay.fm"
ShowCatalog = []
FAKE_CACHE_FILEPATH = 'fakecache.txt'
using_cache = False

# --------------- Ghetto caching ---------------
if path.exists(FAKE_CACHE_FILEPATH):
    # Check to see if it's been recently made (past 7 days) 
    seven_days_ago = (datetime.today() - timedelta(days=7)).timestamp()
    file_modified_time = path.getmtime(FAKE_CACHE_FILEPATH)
    if seven_days_ago < file_modified_time:
        # Fresh cache; use it
        using_cache = True
        fakecache = open(FAKE_CACHE_FILEPATH, 'r')
        ShowCatalog = json.load(fakecache)
    else:
        # Don't use the file, make a new one
        using_cache = False
        fakecache = open(FAKE_CACHE_FILEPATH, 'w+')
else:
    # Make the file
    using_cache = False
    fakecache = open(FAKE_CACHE_FILEPATH, 'w+')

# --------------- List of podcasts/shows ---------------
def GetShows():
    """Returns a list of dictionaries with show titles and URLs"""
    showlist_url = root_url + "/shows"

    # Opens the connection, grabs the page
    response = requests.get(showlist_url)
    showlist_html = response.text

    # HTML parsing
    showlist_soup = soup(showlist_html, "html.parser")

    # Grabs both active and retired shows
    shows = showlist_soup.findAll("h3", {"class": "broadcast__name"})

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

# --------------- Get most recent episodes ---------------
def GetEpisodeURLs(ShowCatalog):
    """Input the ShowCatalog object.
    Example: TODO
    
    Adds the URLs for the most recent episodes in a list to the ShowCatalog object.
    Example: TODO """
    for Show in ShowCatalog:
        show_url = root_url + Show['url'] #ShowURL

        # Opens the connection, grabs the page
        response = requests.get(show_url)
        show_html = response.text

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
            response = requests.get(episode_url)
            episode_html = response.text

            # HTML parsing
            episode_soup = soup(episode_html, "html.parser")

            # Grabs all (1) promo div elements with class of "sp-area"
            sp_areas = episode_soup.findAll("div", {"class": "sp-area"})  # This is an array
            #sp_areas[0].ul.li.a["href"]  # 'https://smilesoftware.com/'
            #sp_areas[0].ul.li.a.text  # 'TextExpander'

            if sp_areas == []:
                # If there are no promos for this episode, then we don't need to add info about them
                logging.info("No promos for " + Show['title'] + " #" + Episode['number'])
            else:
                promos = sp_areas[0].findAll("li")  # This is an array
                Episode['promos'] = []
                for promo in promos:
                    information = promo.text
                    information = information.split(":",1)
                    Dictionary = {}
                    Dictionary['sponsor'] = information[0].strip()
                    Dictionary['url'] = promo.a["href"]
                    Dictionary['description'] = information[1].strip()
                    Episode['promos'].append(Dictionary)
                
    return ShowCatalog

# Gets publish date of episode
#pubdates = episode_soup.find("p", {"class": "pubdate"})
#pubdate = pubdates.small.text.split("·")
#pubdate = pubdate[0].strip("\n")
#print(pubdate)

# App starts here
if using_cache:
    # don't go get new info
    logging.info("Using the cache")
    database = ShowCatalog
else:
    database = GetShows()
    database = GetEpisodeURLs(database)
    database = GetPromoCodes(database)
    logging.info("Writing database object to " + FAKE_CACHE_FILEPATH)
    json.dump(database, fakecache)

if not fakecache.closed:
    fakecache.close()

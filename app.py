from bs4 import BeautifulSoup as soup
import requests, logging, time, json
from os import path, stat, remove
from datetime import datetime, timedelta

import promo_codes

logging.basicConfig(level=logging.INFO)
logging.info("Logging started")

# TODO:
# - Filter out RETIRED shows from ACTIVE ones
# - Filter duplicate promos out removing the oldest codes first

relay_fm = PodcastPlatform("https://www.relay.fm")
logging.debug(f"root_url is: {root_url}")
ShowCatalog = []
FAKE_CACHE_FILEPATH = 'fakecache.txt'
logging.debug(f"FAKE_CACHE_FILEPATH is: {FAKE_CACHE_FILEPATH}")
using_cache = False
logging.debug(f"using_cache initialized to: {using_cache}")

# --------------- Ghetto caching ---------------
logging.info("Check cache for data")
if path.exists(FAKE_CACHE_FILEPATH):
    # Check to see if it's been recently made (past 7 days) 
    seven_days_ago = (datetime.today() - timedelta(days=7)).timestamp()
    file_modified_time = path.getmtime(FAKE_CACHE_FILEPATH)
    if seven_days_ago < file_modified_time:
        logging.debug(f"seven_days_ago ({seven_days_ago}) is less than file_modified_time ({file_modified_time}).")
        # Fresh cache; use it
        logging.info(f"Using the cached data at: {FAKE_CACHE_FILEPATH}")
        using_cache = True
        logging.debug(f"using_cache is: {using_cache}")
        fakecache = open(FAKE_CACHE_FILEPATH, 'r')
        ShowCatalog = json.load(fakecache)
    else:
        # Don't use the file, make a new one
        logging.info(f"Cached data is older than seven days. Make a new cache at: {FAKE_CACHE_FILEPATH}")
        using_cache = False
        logging.debug(f"using_cache is: {using_cache}")
        fakecache = open(FAKE_CACHE_FILEPATH, 'w+')
else:
    # Make the file
    logging.info(f"No cache file found. Make a new cache at: {FAKE_CACHE_FILEPATH}")
    using_cache = False
    logging.debug(f"using_cache is: {using_cache}")
    fakecache = open(FAKE_CACHE_FILEPATH, 'w+')

def IsCacheEmpty(CacheFilePath):
    logging.debug("Starting IsCacheEmpty()")
    logging.info(f"Checking if {CacheFilePath} contains no/little data")
    filesize = stat(CacheFilePath).st_size
    if filesize < 3:
        logging.debug("IsCacheEmpty() returns: True")
        return True
    else:
        logging.debug("IsCacheEmpty() returns: False")
        return False


# --------------- List of podcasts/shows ---------------


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
    logging.info(f"Writing database object to {FAKE_CACHE_FILEPATH}")
    json.dump(database, fakecache)

if not fakecache.closed:
    logging.info("Closing fakecache object")
    fakecache.close()

if IsCacheEmpty(FAKE_CACHE_FILEPATH):
    logging.info("Deleting empty fakecache file")
    remove(FAKE_CACHE_FILEPATH)

logging.debug("End of program")
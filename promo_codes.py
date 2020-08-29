"""A class representing a podcast CMS/platform/directory."""
import logging, requests, time, json
from os import path, stat
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as soup

class PodcastPlatform:
    """A podcast platform/CMS/directory."""

    def __init__(self, root_url):
        self.root_url = root_url
        logging.debug(f"PodcastPlatform.root_url is: {self.root_url}")
        self.show_catalog = []

    def get_shows(self):
        """Returns a list of dictionaries with show titles and URLs"""
        logging.debug("Starting get_shows()")
        self.showlist_url = self.root_url + "/shows"
        logging.info(f"Showlist URL is {self.showlist_url}")

        # Opens the connection, grabs the page
        response = requests.get(self.showlist_url)
        showlist_html = response.text

        # HTML parsing
        showlist_soup = soup(showlist_html, "html.parser")

        # Grabs both active and retired shows
        shows = showlist_soup.findAll("h3", {"class": "broadcast__name"})

        for show in shows:
            logging.debug(f"Processing show: {show}")
            try:
                Dictionary = {}
                
                if show.a:
                    Dictionary['title'] = show.a.text
                    Dictionary['url'] = show.a["href"]
                    self.show_catalog.append(Dictionary)
            except TypeError:  # This was being thrown by Master Feed since there's no URL to show
                logging.error(f"TypeError occured on show: {show}")
                pass
            except AttributeError:
                logging.error(f"AttributeError occured on show: {show}")
                pass

        logging.debug("Returning show_catalog")
        return self.show_catalog

    # --------------- Get most recent episodes ---------------
    def get_episode_urls(self):
        """Input the show_catalog object.
        Example: TODO
        
        Adds the URLs for the most recent episodes in a list to the show_catalog object.
        Example: TODO """
        logging.debug("Starting get_episode_urls()")

        for show in self.show_catalog:
            show_url = self.root_url + show['url']
            logging.info(f"Show URL is {show_url}")

            # Opens the connection, grabs the page
            response = requests.get(show_url)
            show_html = response.text

            # HTML parsing
            show_soup = soup(show_html, "html.parser")
            episode_wrap = show_soup.findAll("div", {"class": "episode-wrap animated"})

            show['episodes'] = []
            for episode in episode_wrap[:10]:  # Will have to load the next page if we want to get more episodes
                Dictionary = {}
                episode_line = episode.h3.a.text
                episode_info = episode_line.split(":")
                Dictionary['number'] = episode_info[0].strip("#")
                Dictionary['title'] = episode_info[1].strip()
                logging.debug(f"Appending this to Show['episodes']: {Dictionary}")
                show['episodes'].append(Dictionary)
        
        logging.debug("Returning show_catalog")
        return self.show_catalog

    # --------------- Episode page ---------------
    def get_promo_codes(self):
        """doc strings?"""
        logging.debug("Starting get_promo_codes()")

        for show in self.show_catalog:
            show_url = self.root_url + show['url']
            logging.info(f"Show URL is {show_url}")

            for episode in show['episodes']:
                episode_url = show_url + '/' + episode['number']
                logging.debug(f"episode_url is type {episode_url}")

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
                    logging.info(f"No promos for {show['title']} episode # {episode['number']}")
                else:
                    promos = sp_areas[0].findAll("li")  # This is an array
                    logging.info(f"There are {len(promos)} promos")
                    episode['promos'] = []
                    for promo in promos:
                        information = promo.text
                        information = information.split(":",1)
                        Dictionary = {}
                        Dictionary['sponsor'] = information[0].strip()
                        Dictionary['url'] = promo.a["href"]
                        Dictionary['description'] = information[1].strip()
                        logging.debug(f"Appending this to Episode['promos']: {Dictionary}")
                        episode['promos'].append(Dictionary)
        
        logging.debug("Returning show_catalog")
        return self.show_catalog

class FakeCache:
    """Not quite a legit caching object, but it works."""

    def __init__(self, filepath="fakecache.json"):
        """Initialize the FakeCache object."""
        self.filepath = filepath
        logging.debug(f"FakeCache.filepath is: {self.filepath}")
        self.using_cache = False
        logging.debug(f"FakeCache.using_cache initialized to: {self.using_cache}")
        self.file_object = None

    # This function is doing too much. Split it into further functions.
    def load_cache(self):
        """Check the cache to see if it has stale or fresh data. Load if exists and up-to-date otherwise create new object."""
        logging.info("Check cache for data")
        if path.exists(self.filepath):
            # Check to see if it's been recently made (past 7 days) 
            seven_days_ago = (datetime.today() - timedelta(days=7)).timestamp()
            file_modified_time = path.getmtime(self.filepath)
            if seven_days_ago < file_modified_time:
                logging.debug(f"seven_days_ago ({seven_days_ago}) is less than file_modified_time ({file_modified_time}).")
                # Fresh cache; use it
                logging.info(f"Using the cached data at: {self.filepath}")
                self.using_cache = True
                logging.debug(f"FakeCache.using_cache is: {self.using_cache}")
                with open(self.filepath, 'r') as file_object:
                    self.file_object = file_object
                return json.load(self.file_object)
            else:
                # Don't use the file, make a new one
                logging.info(f"Cached data is older than seven days. Make a new cache at: {self.filepath}")
                self.using_cache = False
                logging.debug(f"cache.using_cache is: {self.using_cache}")
                with open(self.filepath, 'w+') as file_object:
                    self.file_object = file_object
                return self.file_object
        else:
            # Make the file
            logging.info(f"No cache file found. Make a new cache at: {self.filepath}")
            self.using_cache = False
            logging.debug(f"FakeCache.using_cache is: {self.using_cache}")
            with open(self.filepath, 'w+') as file_object:
                self.file_object = file_object
            return self.file_object

    def is_cache_empty(self):
        """Determines if the cache has little or no data, though it might be fresh."""
        logging.debug("Starting is_cache_empty()")
        logging.info(f"Checking if {self.filepath} contains no/little data")
        filesize = stat(self.filepath).st_size
        if filesize < 3:
            logging.debug("is_cache_empty() returns: True")
            return True
        else:
            logging.debug("is_cache_empty() returns: False")
            return False

    def is_using_cache(self):
        """Returns whether or not the cache should be used."""
        return self.using_cache
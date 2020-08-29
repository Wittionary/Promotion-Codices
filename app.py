import logging, json
from os import remove

from promo_codes import PodcastPlatform, FakeCache

logging.basicConfig(level=logging.INFO)
logging.info("Logging started")

# TODO:
# - Filter out RETIRED shows from ACTIVE ones
# - Filter duplicate promos out removing the oldest codes first

relay_fm = PodcastPlatform("https://www.relay.fm")
cache = FakeCache()
file_object = cache.load_cache()

if cache.using_cache:
    # don't go get new info
    logging.info("Using the cache")
    database = relay_fm.show_catalog
else:
    relay_fm.get_shows()
    relay_fm.get_episode_urls()
    relay_fm.get_promo_codes()
    logging.info(f"Writing database object to {cache.filepath}")
    json.dump(relay_fm.show_catalog, cache.file_object)

if cache.is_cache_empty():
    logging.info("Deleting empty FakeCache file")
    remove(cache.filepath)

logging.debug("End of program")
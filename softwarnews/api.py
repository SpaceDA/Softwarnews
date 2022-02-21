"""Source Defense-related news articles from HN API"""
import requests
import datetime


# List of defense related words
# defenseWords = ['submarine', 'army', 'navy', 'air force', 'military', 'department of defense', 'weapon',
# 'helicopter']
# defenseWords = ['navy']

# Time period to search
yesterday = datetime.date.today() - datetime.timedelta(1)
unix_time= yesterday.strftime("%s")

def fetch_articles(defense_words=None):
    """Query each defense word in HN API"""
    for x in defense_words:
        r = requests.get(url=
        f'http://hn.algolia.com/api/v1/search_by_date?tags=story&query={x}&numericFilters=created_at_i>={unix_time}')

    return r.text




import geonames.adapters.search
"""
https://github.com/dsoprea/GeonamesRdf/blob/master/dev/test.py
"""

_USERNAME = '_amaia'
sa = geonames.adapters.search.Search(_USERNAME)


def search_entity(query):
    result = sa.query(query).country('fr').max_rows(100).execute()
    list = []
    for id_, name in result.get_flat_results():
        # make_unicode() is only used here for Python version-compatibility.
        print("Found something  ",id_, name)
        list.append({id_, name})

    return list

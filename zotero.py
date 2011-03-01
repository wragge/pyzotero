#!/usr/bin/env python
# encoding: utf-8
"""
zotero.py

Created by Stephan Hügel on 2011-02-28
Copyright Stephan Hügel, 2011

License: http://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
import urllib
import urllib2
import feedparser


def open_file(to_read):
    """ Open a text file for reading, and strip the newlines
        returns a list, one list item per line
    """
    try:
        with open(to_read, 'r') as opened:
            return [got_lines.rstrip('\n') for got_lines in opened.readlines()]
    except IOError:
        print "Couldn't read values from %s\nCan't continue." % to_read
        raise



class Zotero(object):
    """ Zotero API methods
        A full list of methods can be found here:
        http://www.zotero.org/support/dev/server_api
        Most of the methods return Atom feed documents, which can be parsed
        using feedparser (http://www.feedparser.org/docs/)

        Valid optional URL parameters in all modes:
        format: "atom" or "bib", default: "atom"
        key: string, default:  null
        version: integer, default: null

        Valid optional URL parameters for format=atom:
        content: "none", "html", "bib", default: "html"
        order: string, name of field to be used, default: "dateAdded"
        sort: "asc", "desc", default varies by "order"
        limit: integer 1 - 99, default 50
        start: integer, default: 0
        pprint: boolean, default: false
    """
    user_id = None
    user_key = None
    
    def __init__(self, user_id = None, user_key = None):
        """ Store Zotero credentials
        """
        self.endpoint = 'https://api.zotero.org'
        if user_id and user_key:
            self.user_id = user_id
            self.user_key = user_key
        # Some API methods, not exhaustive
        self.api_methods = {
        'all_items':'/users/{u}/items',
        'top_level_items':'/users/{u}/items/top',
        'specific_item':'/users/{u}/items/%s',          #item_id
        'child_items':'/users/{u}/items/%s/children',   #item_id
        'item_tags':'/users/{u}/items/%s/tags',         #item_id
        'user_tags':'/users/{u}/tags',
        'items_for_tag':'/users/{u}/tags/%s/items',     # tag_id
        'collections':'/users/{u}/collections',
        'collection_items':'/users/{u}/collections/%s', # collection_id
        'group_items':'/groups/%s/items'                # group_id
        }

    def retrieve_data(self,
        request, url_params = None, request_param = None):
        """ Method for retrieving Zotero items via the API
            returns a dict containing feed items and lists of entries
        """
        # Add the user ID to the API call if it's required
        request = self.api_methods[request].format(u = self.user_id)
        # Add URL parameters if they're passed
        if url_params:
            data = urllib.urlencode(url_params)
            request = '%s%s%s' % (request, '?', data)
        # Add a request parameter if it's required
        if request_param:
            request = request % urllib.quote(request_param)
        full_url = '%s%s' % (self.endpoint, request)
        data = urllib2.urlopen(full_url).read()
        # parse the result into Python data structures
        feed_data = feedparser.parse(data)
        return feed_data

def main():
    """ main function
    """
    # Read a file from your cwd. Expects user id on line 1, key on line 2, LF
    auth_values = open_file(os.path.join(os.path.expanduser('~'),
    'zotero_keys.txt'))
    zot_id = auth_values[0]
    zot_key = auth_values[1]
    zot = Zotero(zot_id, zot_key)
    # Pass optional request parameters in a dict
    par = {'limit': '10', 'start': 50}
    item = zot.retrieve_data('all_items', par)
    # We can now do whatever we like with the returned data, e.g.:
    title_id = [j for j in zip([t['title'] for t in item.entries],
    [z['zapi_key'] for z in item.entries])]
    for entry in title_id:
        print entry


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        # actually raise these, for a clean exit
        raise
    except Exception, error:
        # all other exceptions: display the error
        print error
    else:
        pass
    finally:
        # exit cleanly once we've done everything else
        sys.exit(0)
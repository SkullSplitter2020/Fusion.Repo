from tmdbhelper.lib.addon.permissions import __access__
from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler

if __access__.has_access('internal'):
    CLIENT_ID = '3ebcaa46dfe47bf742f3b01251a9a5f8d1fb75e17e59d0b39e224f29cadca458'
    CLIENT_SECRET = 'db9d815d67f40e4367edea63d51ff20b46e6c0d596f444b63f64c3453cffd922'
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')

elif __access__.has_access('trakt'):
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')

else:
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    USER_TOKEN = TokenHandler()

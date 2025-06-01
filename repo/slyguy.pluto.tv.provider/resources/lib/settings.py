from slyguy.settings import CommonSettings
from slyguy.settings.types import Bool

from .language import _


DATA_URL = 'https://i.mjh.nz/PlutoTV/.channels.json.gz'
ALL = 'all'
MY_CHANNELS = 'my_channels'
UUID_NAMESPACE = '122e1611-0232-4336-bf43-e054c8ecd0d5'
PLAYBACK_URL = 'https://jmp2.uk/plu-{id}.m3u8'


class Settings(CommonSettings):
    SHOW_COUNTRIES = Bool('show_countries', _.SHOW_COUNTRIES, default=True)
    SHOW_GROUPS = Bool('show_groups', _.SHOW_GROUPS, default=True)
    SHOW_CHNOS = Bool('show_chnos', default=True)
    SHOW_EPG = Bool('show_epg', default=True)
    ALT_USER_AGENT = Bool('alt_user_agent', _.ALT_USER_AGENT, default=True)


settings = Settings()

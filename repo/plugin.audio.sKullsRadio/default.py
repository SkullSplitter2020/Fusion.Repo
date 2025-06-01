import sys
import xbmcplugin
import xbmcgui
import urllib.parse
import os

# Konstanten für das Add-on
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Pfade zu den Bildverzeichnissen
KATEGORIE_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'images', 'kategorie')
STREAMS_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'images', 'streams')

# Dictionary mit Streams
streams = {
    'M1.FM': [
        {'name': '80ER', 'url': 'https://tuner.m1.fm/80er.mp3'},
        {'name': '90ER', 'url': 'https://tuner.m1.fm/90er.mp3'},
        {'name': 'ChillOut', 'url': 'https://tuner.m1.fm/chillout.mp3'},
        {'name': 'CLUBMIX', 'url': 'https://tuner.m1.fm/clubmix.mp3'},
        {'name': 'PARTYSCHLAGER', 'url': 'https://pool.radiopaloma.de/RP-Partyschlager_rde.mp3'},
        {'name': 'OLDIES', 'url': 'https://tuner.m1.fm/oldies.mp3'},
        {'name': 'ROCK', 'url': 'https://tuner.m1.fm/rock.mp3'},
        {'name': 'SCHLAGER', 'url': 'https://pool.radiopaloma.de/RADIOPALOMA_rde.mp3'},
        {'name': 'SOFT POP', 'url': 'https://tuner.m1.fm/softpop.mp3'},
        {'name': 'THE HITS', 'url': 'https://tuner.m1.fm/hits.mp3'},
        {'name': 'TOP OF THE CHARTS', 'url': 'https://tuner.m1.fm/charts.mp3'},
        {'name': 'URBAN', 'url': 'https://icepool.silvacast.com/DEFJAY_rde.mp3'},
     ],
    'bigFM': [
        {'name': 'bigFM Berlin', 'url': 'https://streams.bigfm.de/bigfm-berlin-128-aac'},
        {'name': 'bigFM CHARTS', 'url': 'https://streams.bigfm.de/bigfm-charts-64-aac'},
        {'name': 'bigFM DANCE', 'url': 'https://streams.bigfm.de/bigfm-dance-64-aac'},
        {'name': 'bigFM Dancehall & Reggae Vibez', 'url': 'https://streams.bigfm.de/bigfm-reggaevibes-64-aac'},
        {'name': 'bigFM Deep & Tech House', 'url': 'https://streams.bigfm.de/bigfm-nitroxdeep-64-aac'},
        {'name': 'bigFM Deutsche Hip-Hop Charts', 'url': 'https://streams.bigfm.de/bigfm-dhiphopcharts-128-mp3'},
        {'name': 'bigFM Deutschrap', 'url': 'https://streams.bigfm.de/bigfm-deutschrap-128-mp3'},
        {'name': 'bigFM EDM & Progressive', 'url': 'https://streams.bigfm.de/bigfm-nitroxedm-64-aac'},
        {'name': 'bigFM GROOVENIGHT', 'url': 'https://streams.bigfm.de/bigfm-groovenight-64-aac'},
        {'name': 'bigFM HIP-HOP', 'url': 'https://streams.bigfm.de/bigfm-hiphop-64-aac'},
        {'name': 'bigFM MASHUP', 'url': 'https://streams.bigfm.de/bigfm-mashup-64-aac'},
        {'name': 'bigFM Oldschool Deutschrap', 'url': 'https://streams.bigfm.de/bigfm-oldschooldeutsch-128-mp3'},
        {'name': 'bigFM Party', 'url': 'https://ilr.bigfm.de/bigfm-party-128-mp3'},
        {'name': 'bigFM Rap Feature', 'url': 'https://streams.bigfm.de/bigfm-rapfeature-128-aac'},
        {'name': 'bigFM Oldschool Rap & Hip-Hop', 'url': 'https://streams.bigfm.de/bigfm-oldschool-128-mp3'},
        {'name': 'bigFM RNB', 'url': 'https://streams.bigfm.de/bigfm-rnb-128-mp3'},
        {'name': 'bigFM Sunset Lounge', 'url': 'https://streams.bigfm.de/bigfm-sunsetlounge-64-aac'},
        {'name': 'bigFM US RAP & HIP-HOP', 'url': 'https://streams.bigfm.de/bigfm-usrap-64-aac'},
    ],
    'I Love Music': [
        {'name': 'I LOVE RADIO', 'url': 'https://streams.ilovemusic.de/iloveradio1.mp3'},
        {'name': 'I LOVE 2 DANCE', 'url': 'https://streams.ilovemusic.de/iloveradio2.mp3'},
        {'name': 'I LOVE BASS', 'url': 'https://streams.ilovemusic.de/iloveradio29-aac.mp3'},
        {'name': 'I LOVE CHILLHOP', 'url': 'https://streams.ilovemusic.de/iloveradio17-aac.mp3'},
        {'name': 'I LOVE DANCE FIRST!', 'url': 'https://streams.ilovemusic.de/iloveradio103.mp3'},
        {'name': 'I LOVE DANCE HISTORY', 'url': 'https://streams.ilovemusic.de/iloveradio26-aac.mp3'},
        {'name': 'I LOVE DEUTSCHRAP BESTE', 'url': 'https://streams.ilovemusic.de/iloveradio6.mp3'},
        {'name': 'I LOVE DEUTSCHRAP FIRST!', 'url': 'https://streams.ilovemusic.de/iloveradio104.mp3'},
        {'name': 'I LOVE GREATEST HITS', 'url': 'https://streams.ilovemusic.de/iloveradio16.mp3'},
        {'name': 'I LOVE HARDSTYLE', 'url': 'https://streams.ilovemusic.de/iloveradio21.mp3'},
        {'name': 'I LOVE HIP HOP', 'url': 'https://streams.ilovemusic.de/iloveradio3.mp3'},
        {'name': 'I LOVE HIP HOP HISTORY', 'url': 'https://streams.ilovemusic.de/iloveradio27-aac.mp3'},
        {'name': 'I LOVE TOP 100 CHARTS', 'url': 'https://streams.ilovemusic.de/iloveradio9.mp3'},
        {'name': 'I LOVE HITS HISTORY', 'url': 'https://streams.ilovemusic.de/iloveradio12.mp3'},
        {'name': 'I LOVE MAINSTAGE MADNESS', 'url': 'https://streams.ilovemusic.de/iloveradio22.mp3'},
        {'name': 'I LOVE MASHUP', 'url': 'https://streams.ilovemusic.de/iloveradio5.mp3'},
        {'name': 'I LOVE MONSTERCAT', 'url': 'https://streams.ilovemusic.de/iloveradio24-aac.mp3'},
        {'name': 'I LOVE MUSIC & CHILL', 'url': 'https://streams.ilovemusic.de/iloveradio10.mp3'},
        {'name': 'I LOVE NEW POP', 'url': 'https://streams.ilovemusic.de/iloveradio11.mp3'},
        {'name': 'I LOVE THE BEACH', 'url': 'https://streams.ilovemusic.de/iloveradio7.mp3'},
        {'name': 'I LOVE THE CLUB', 'url': 'https://streams.ilovemusic.de/iloveradio20.mp3'},
        {'name': 'I LOVE THE DJ', 'url': 'https://streams.ilovemusic.de/iloveradio4.mp3'},
        {'name': '.I LOVE THE SUN', 'url': 'https://streams.ilovemusic.de/iloveradio15.mp3'},
        {'name': 'I LOVE PARTY HARD', 'url': 'https://streams.ilovemusic.de/iloveradio14.mp3'},
        {'name': 'I LOVE WORKOUT', 'url': 'https://streams.ilovemusic.de/iloveradio23-aac.mp3'},
    ],
    'Rautemusik': [
        {'name': '80s HITS by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream16.radiohost.de/rm-80s_mp3-192'},
        {'name': '90s HITS by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream13.radiohost.de/90s'},
        {'name': 'Caribbean Wave by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream18.radiohost.de/caribbean-wave_mp3-192'},
        {'name': 'Best of Schlager by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream14.radiohost.de/rm-best-of-schlager_mp3-192'},
        {'name': 'Club by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream14.radiohost.de/club'},
        {'name': 'COFFEE-MUSIC by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream15.radiohost.de/coffee-music_aac-48'},
        {'name': 'Bass by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream12.radiohost.de/breakz'},
        {'name': 'Deutsche Hits by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream15.radiohost.de/rm-deutsche-hits_mp3-192'},
        {'name': 'Deutschrap by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream13.radiohost.de/deutschrap'},
        {'name': 'Deutschrap Charts by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream17.radiohost.de/rm-deutschrap-charts_mp3-192'},
        {'name': 'Deutschrap Classic by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream14.radiohost.de/rm-deutschrap-classic_mp3-192'},
        {'name': 'Goldies by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream16.radiohost.de/goldies'},
        {'name': 'Happy by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream18.radiohost.de/happy'},
        {'name': 'Happy Hardcore by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream11.radiohost.de/happyhardcore'},
        {'name': 'HardeR by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream11.radiohost.de/harder'},
        {'name': 'House by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream17.radiohost.de/house'},
        {'name': 'JaM by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream15.radiohost.de/jam'},
        {'name': 'Schlager Oldies by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream13.radiohost.de/rm-schlager-oldies_mp3-192'},
        {'name': 'Sex by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream14.radiohost.de/sex'},
        {'name': 'Techhouse by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream15.radiohost.de/techhouse'},
        {'name': 'Top40 by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream15.radiohost.de/top40'},
        {'name': 'Trance by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream15.radiohost.de/trance'},
        {'name': 'Trap by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream16.radiohost.de/trap'},
        {'name': 'Traurig by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream12.radiohost.de/traurig'},
        {'name': 'Workout by Rautemusik', 'url': 'https://Rautemusik-de-hz-fal-stream12.radiohost.de/workout'},
    ],
    'Sunshine Live': [
        {'name': 'Sunshine Live', 'url': 'http://stream.sunshine-live.de/live/mp3-192'},
        {'name': 'Sunshine Live - 90er', 'url': 'http://stream.sunshine-live.de/90er/mp3-192'},
        {'name': 'Sunshine Live - Classics', 'url': 'http://stream.sunshine-live.de/classics/mp3-192'},
        {'name': 'Sunshine Live - Drum ´n Bass', 'url': 'http://stream.sunshine-live.de/dnb/mp3-192'},
        {'name': 'Sunshine Live - EDM', 'url': 'http://stream.sunshine-live.de/edm/mp3-192'},
        {'name': 'Sunshine Live - Festival', 'url': 'http://stream.sunshine-live.de/festival/mp3-192'},
        {'name': 'Sunshine Live - Hard', 'url': 'http://stream.sunshine-live.de/hard/mp3-192'},
        {'name': 'Sunshine Live - House', 'url': 'http://stream.sunshine-live.de/house/mp3-192'},
        {'name': 'Sunshine Live - Mayday', 'url': 'http://stream.sunshine-live.de/mayday/mp3-192'},
        {'name': 'Sunshine Live - Nature One', 'url': 'http://stream.sunshine-live.de/natureone/mp3-192'},
        {'name': 'Sunshine Live - Time Warp', 'url': 'http://stream.sunshine-live.de/timewarp/mp3-192'},
        {'name': 'Sunshine Live - Live ´n Pride', 'url': 'http://stream.sunshine-live.de/sslpride/mp3-192'},
        {'name': 'Sunshine Live - Lounge', 'url': 'http://stream.sunshine-live.de/lounge/mp3-192'},
        {'name': 'Sunshine Live - Party', 'url': 'http://stream.sunshine-live.de/party/mp3-192'},
        {'name': 'Sunshine Live - Techno', 'url': 'http://stream.sunshine-live.de/techno/mp3-192'},
        {'name': 'Sunshine Live - Trance', 'url': 'http://stream.sunshine-live.de/trance/mp3-192'},
    ],
        'RadioBob': [
        {'name': 'Classic Rock', 'url': 'http://streams.radiobob.de/bob-classicrock/mp3-192'},
        {'name': 'Best of Rock', 'url': 'http://streams.radiobob.de/bob-bestofrock/mp3-192'},
        {'name': 'Rockhits', 'url': 'http://streams.radiobob.de/bob-rockhits/mp3-192'},
        {'name': 'Metal', 'url': 'http://streams.radiobob.de/bob-metal/mp3-192'},
        {'name': 'Hardrock', 'url': 'http://streams.radiobob.de/bob-hardrock/mp3-192'},
        {'name': 'Rock Festival', 'url': 'http://streams.radiobob.de/bob-festival/mp3-192'},
        {'name': 'Grunge', 'url': 'http://streams.radiobob.de/bob-grunge/mp3-192'},
        {'name': 'AC DC', 'url': 'http://streams.radiobob.de/bob-acdc/mp3-192'},
        {'name': 'Queen', 'url': 'http://streams.radiobob.de/bob-queen/mp3-192'},
        {'name': 'Kuschelrock', 'url': 'http://streams.radiobob.de/bob-kuschelrock/mp3-192'},
    ],
        'Radio Nrj': [
        {'name': 'Energy-German Top 40', 'url': 'http://nrj.de/germanytop40'},
        {'name': 'Energy-Made in Germany', 'url': 'http://nrj.de/madeingermany'},
        {'name': 'Energy-German Hiphop', 'url': 'http://nrj.de/deutschrap'},
        {'name': 'Energy-Lounge', 'url': 'http://nrj.de/lounge'},
        {'name': 'Energy-Dance', 'url': 'http://nrj.de/dance'},
        {'name': 'Energy-Hits', 'url': 'http://nrj.de/hits'},
        {'name': 'Energy-Mastermix', 'url': 'http://nrj.de/master'},
        {'name': 'Energy-Partyhits', 'url': 'http://nrj.de/partyhits'},
        {'name': 'Energy-Reggae', 'url': 'http://nrj.de/reggae'},
        {'name': 'Energy-Hit Remix', 'url': 'http://nrj.de/hitsremix'},
    ],
        'Delta Radio': [
        {'name': 'Delta Radio-Deutsch', 'url': 'http://streams.deltaradio.de/delta-deutsch/mp3-192'},
        {'name': 'Delta Radio-Hiphop', 'url': 'http://streams.deltaradio.de/hiphop/mp3-192'},
        {'name': 'Delta Radio-Sommer', 'url': 'http://streams.deltaradio.de/delta-sommer/mp3-192'},
        {'name': 'Delta Radio-Alternativ', 'url': 'http://streams.deltaradio.de/delta-alternative/mp3-192'},
        {'name': 'Delta Radio — Hardrock & heavy Metal (Föhnfrisur)', 'url': 'http://streams.deltaradio.de/delta-foehnfrisur/mp3-128'},
        {'name': 'Delta Radio-Unplugged', 'url': 'http://streams.deltaradio.de/delta-unplugged/mp3-192'},
        {'name': 'Delta Radio-Rockpop', 'url': 'http://streams.deltaradio.de/delta-poprock/mp3-192'},
        {'name': 'Delta Radio-Grunge', 'url': 'http://streams.deltaradio.de/delta-grunge/mp3-192'},
        
    ],
        'RSA Sachsen': [
        {'name': 'RSA-Maxis-Maximal', 'url': 'http://streams.rsa-sachsen.de/maxis/mp3-192'},
        {'name': 'RSA-Disco', 'url': 'http://streams.rsa-sachsen.de/disco/mp3-192'},
        {'name': 'RSA-Oldies', 'url': 'http://streams.rsa-sachsen.de/rsa-oldies/mp3-192'},
        {'name': 'RSA-Rockzirkus', 'url': 'http://streams.rsa-sachsen.de/rsa-rockzirkus/mp3-192'},
        {'name': 'RSA-60er', 'url': 'http://streams.rsa-sachsen.de/60er/mp3-192'},
        {'name': 'RSA-70er', 'url': 'http://streams.rsa-sachsen.de/70er/mp3-192'},
        {'name': 'RSA-80er', 'url': 'http://streams.rsa-sachsen.de/80er/mp3-192'},
        
    ],
        'Radio SAW': [
        {'name': 'SAW-70er', 'url': 'http://saw-de-hz-fal-stream04-cluster01.radiohost.de/saw-70er_128'},
        {'name': 'SAW-80er', 'url': 'http://saw-de-hz-fal-stream03-cluster01.radiohost.de/saw-80er_128'},
        {'name': 'SAW-90er', 'url': 'http://saw-de-hz-fal-stream03-cluster01.radiohost.de/saw-90er_128'},
        {'name': 'SAW-2000er', 'url': 'http://saw-de-hz-fal-stream05-cluster01.radiohost.de/saw-2000er_128'},
        {'name': 'SAW-Deutsche Hits', 'url': 'http://saw-de-hz-fal-stream04-cluster01.radiohost.de/saw-deutsch_128'},
        {'name': 'SAW-Party Hits', 'url': 'http://saw-de-hz-fal-stream07-cluster01.radiohost.de/saw-party_128'},
        {'name': 'SAW-Partyschlager', 'url': 'http://saw-de-hz-fal-stream02-cluster01.radiohost.de/saw-partyschlager_128'},
        {'name': 'SAW-Rock Songs', 'url': 'http://saw-de-hz-fal-stream04-cluster01.radiohost.de/saw-rock_128'},
        {'name': 'SAW-Rockland', 'url': 'http://saw-de-hz-fal-stream07-cluster01.radiohost.de/rockland_128'},

    ],
        'Wacken Radio': [
        {'name': 'Wacken Radio', 'url': 'https://Rautemusik-de-hz-fal-stream17.radiohost.de/wackenradio'},
        {'name': 'RADIO BOB! BOBs Wacken Nonstop', 'url': 'https://bob.hoerradar.de/radiobob-wacken-mp3-mq'},
        {'name': 'Wacken', 'url': 'https://wacken.stream.laut.fm/wacken'},

    ],
        'Unsorted': [
        {'name': 'CampFM - Das Festivalradio', 'url': 'https://campfm.radionetz.de:8001/campfm.mp3'},
        {'name': 'Tomorrowland - One World Radio', 'url': 'https://playerservices.streamtheworld.com/api/livestream-redirect/OWR_INTERNATIONAL.mp3'},
        {'name': 'Top 100 Germany', 'url': 'http://stream.laut.fm/top100germany'},
        {'name': '1Live', 'url': 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3'},
        {'name': 'Radio Guetersloh', 'url': 'http://mp3.radioguetersloh.c.nmdn.net/radioguetersloh/livestream.mp3'},
        {'name': 'RTL-Deutsch Rap', 'url': 'http://stream.89.0rtl.de/deutsch-rap/mp3-128'},
        {'name': '90s90s Radio-Boygroups', 'url': 'http://streams.90s90s.de/boygroup/mp3-192/streams.90s90s.de/'},
        {'name': '90s90s Radio-Dance', 'url': 'http://streams.90s90s.de/eurodance/mp3-192/streams.90s90s.de/'},
        {'name': '90s90s Radio-Hits', 'url': 'http://streams.90s90s.de/pop/mp3-192/streams.90s90s.de/'},
        {'name': 'Rock am Ring', 'url': 'https://streams.bigfm.de/bigfm-rockamring-128-mp3'},
   ]
}

def list_categories():
    """
    Zeigt die Hauptkategorien (Sender) an.
    """
    for domain in streams:
        url = f'{BASE_URL}?action=list_streams&domain={urllib.parse.quote(domain)}'
        li = xbmcgui.ListItem(label=domain)
        
        # Pfad zum Kategoriebild
        category_image = os.path.join(KATEGORIE_IMAGE_PATH, f"{domain.replace(' ', '_')}.png")
        if os.path.exists(category_image):
            li.setArt({'icon': category_image})
        else:
            li.setArt({'icon': 'DefaultFolder.png'})  # Standardordner-Icon
        
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_streams(domain):
    """
    Zeigt die Streams einer bestimmten Kategorie (Sender) an.
    """
    for entry in streams.get(domain, []):
        li = xbmcgui.ListItem(label=entry['name'])
        li.setInfo('music', {'title': entry['name']})
        li.setProperty('IsPlayable', 'true')
        
        # Pfad zum Stream-Bild
        stream_image_dir = os.path.join(STREAMS_IMAGE_PATH, domain.replace(' ', '_'))
        image_name = f"{entry['name'].replace(' ', '_')}.png"
        image_path = os.path.join(stream_image_dir, image_name)
        
        if os.path.exists(image_path):
            li.setArt({'thumb': image_path, 'icon': image_path})
        else:
            # Fallback: Standardbild verwenden, falls kein Bild gefunden wurde
            li.setArt({'thumb': 'DefaultMusic.png', 'icon': 'DefaultMusic.png'})
        
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=entry['url'], listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def router(paramstring):
    """
    Verarbeitet die Parameter und ruft die entsprechende Funktion auf.
    """
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'list_streams':
            list_streams(params['domain'])
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:])
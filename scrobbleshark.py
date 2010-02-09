#!/usr/bin/python
#-*- coding:UTF-8 -*-

import feedparser
import pylast
import calendar
import os
import time

# opening configuration file
config_file = os.curdir+'/info.cfg'
param = {}
if os.access( config_file, os.F_OK):
    for line in file( config_file ):
        if not line[0]=='#':
            key, value = line.split('=')
            param[key.strip()] = value.strip()
else:
    param['last_updated_song'] = 0

#pulling feed
print "Getting information from Grooveshark...",
feed_url = "http://api.grooveshark.com/feeds/1.0/users/" + param['groove_username'] + "/recent_listens.rss"
feed = feedparser.parse( feed_url )
entries = feed['entries']
print "\tDone"

# getting recent plays, from last first (that's why "reverse")
print "Searching for unscrobbled tracks...",
entries.reverse()
scrobble_list = []
for entry in entries:
    track_artist = entry['title'].split(' - ')
    artist = track_artist[-1].strip()
    title = (" ".join( track_artist[:-1] ))
    time = calendar.timegm( entry['updated_parsed'] )
    if int(param['last_updated_song']) < time:
        #save track for scrobbling
        scrobble_list.append( (artist, title, time) )
        param['last_updated_song'] = time
print "\tFound %d unscrobbled" % len(scrobble_list)
if len(scrobble_list) == 0:
    print "Nothing to scrobble"
    exit()

print "Connecting to Last.fm",
password_hash = pylast.md5( param['lastfm_password'] )
try:
    network = pylast.get_lastfm_network( api_key = param['lastfm_api'], \
                                        api_secret = param['lastfm_secret'], \
                                        username = param['lastfm_username'], \
                                        password_hash = password_hash)
except:
    print "\tcouldn't establish connection. Sorry :( '"
    exit()
else:
    print "successfully! :)"

scrobbler = network.get_scrobbler('tst', '1.0')
print "Scrobbling..."
for artist, title, time in scrobble_list:
    try:
        track = network.get_track(artist, title)
        duration = int(track.get_duration()) / 1000
        print "%s - %s (%d:%d)" % (artist, title, (duration / 60), (duration % 60)),
        scrobbler.scrobble( artist, \
                            title,\
                            time, \
                            pylast.SCROBBLE_SOURCE_USER, \
                            pylast.SCROBBLE_MODE_PLAYED, \
                            duration \
                )
        print "\t Ok"
    except:
        print "\nConnection troubles"

print "\nScrobbling finished"
save = open(config_file, 'w')
for k,v in param.iteritems():
    save.write("%s = %s\n" % (k,v))
save.close()

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
    param['last_update'] = 0

#pulling feed
feed_url = "http://api.grooveshark.com/feeds/1.0/users/" + groove_username + "/recent_listens.rss"
feed = feedparser.parse( feed_url )
entries = feed['entries']

# getting recent plays, from last first (that's why "reverse")
entries.reverse()
scrobble_list = []
for entry in entries:
    songname_artist = entry['title'].split('-')
    artist = songname_artist[-1].strip()
    songname = (" ".join( songname_artist[:-1] ))
    time = calendar.timegm( entry['updated_parsed'] )
    if param['last_update'] < time:
        #scrobble track
        print "Artist: %s, song: %s" % (artist, songname)
        scrobble_list.append( (artist,songname) )
        param['last_update'] = time



save = open(config_file, 'w')
for k,v in param.iteritems():
    save.write("%s=%s" % (k,v))
save.close()

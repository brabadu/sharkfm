#!/usr/bin/python
#-*- coding:UTF-8 -*-

import feedparser
import pylast
import calendar
import os
import time

class Sharkfm:
    def __init__(self):
        self.param = {}
        self.scrobble_list = []
        self.config_file = ""
        
        self.read_config()
        self.pull_feed()
        self.get_unscrobbled_tracks()
        if len(self.scrobble_list) > 0:
            self.connect_to_lastfm()
            self.scrobble()
        else:
            print "Nothing to scrobble"
        self.save_config()
    
    def read_config(self):
        # opening configuration file
        self.config_file = os.curdir+'/info.cfg'
        if os.access( self.config_file, os.F_OK):
            for line in file( self.config_file ):
                if not line[0]=='#':
                    key, value = line.split('=')
                    self.param[key.strip()] = value.strip()
        else:
            # TODO: raise exception and tell user to create config file
            print " Config file was not found. Create file 'info.cfg' in the same directory with sharkfm.py.", \
                "There must be these parameters (without angle-brackets '<>')\n", \
                "groove_username = <your grooveshark username>\n", \
                "lastfm_username = <your last.fm username>\n", \
                "lastfm_password = <your last.fm password>\n", \
                "lastfm_secret = <your API secret from lastfm>\n", \
                "lastfm_api = <your API key from lastfm>\n", \
                "last_updated_song = 0\n"

    def pull_feed(self):
        #pulling feed
        print "Getting information from Grooveshark...",
        feed_url = "http://api.grooveshark.com/feeds/1.0/users/" + self.param['groove_username'] + "/recent_listens.rss"
        feed = feedparser.parse( feed_url )
        self.entries = feed['entries']
        print "\tDone"

    def get_unscrobbled_tracks(self):
        # getting recent plays, from last first (that's why "reverse")
        print "Searching for unscrobbled tracks...",
        #self.entries.reverse()
        for entry in self.entries:
            track_artist = entry['title'].split(' - ')
            artist = track_artist[-1].strip()
            title = (" ".join( track_artist[:-1] ))
            time = calendar.timegm( entry['updated_parsed'] )
            if int(self.param['last_updated_song']) < time:
                #save track for scrobbling
                self.scrobble_list.append( (artist, title, time) )
                self.param['last_updated_song'] = time
        print "\tFound %d unscrobbled" % len(self.scrobble_list)

    def connect_to_lastfm(self):
        print "Connecting to Last.fm",
        password_hash = pylast.md5( self.param['lastfm_password'] )
        try:
            self.network = pylast.get_lastfm_network( api_key = self.param['lastfm_api'], \
                                                api_secret = self.param['lastfm_secret'], \
                                                username = self.param['lastfm_username'], \
                                                password_hash = password_hash)
        except:
            print "\tcouldn't establish connection. Sorry :( '"
            exit()
        else:
            print "successfully! :)"

    def scrobble(self):
        scrobbler = self.network.get_scrobbler('ssk', '1.0')
        print "Scrobbling..."
        for artist, title, time in self.scrobble_list:
            try:
                track = self.network.get_track(artist, title)
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

    def save_config(self):
        save = open(self.config_file, 'w')
        for k,v in self.param.iteritems():
            save.write("%s = %s\n" % (k,v))
        save.close()
        
if __name__ == '__main__':
    sharkfm = Sharkfm()

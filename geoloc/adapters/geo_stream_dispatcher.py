#!/usr/bin/env python
"""
Grab geo tweets from Twitter Streaming API
For English, geotagged users, grab his/her screen_name
most recent 200 tweets 
Throw any users that are not realiable (with fewer than 10 geotagged tweets or not 5 of them are from one location)
Predict users and save both input and result on disk in .gz format 
"""

import ujson as json
import os
pkg_path = os.environ["geoloc"]
import langid
from twython import TwythonStreamer
import twython
import time
import sys
from datetime import datetime
import requests

sname_list = []
sname_limit = 100

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        global index
        # filter geo and English records
        if 'coordinates' in data and data['coordinates']:
            if data['coordinates']["type"] == "Point":
                text = data["text"]
                if langid.classify(text)[0] == 'en':
                    sname = data["user"]["screen_name"]
                    ts = datetime.now().strftime("%y%m%d%H%M")
                    coords = data['coordinates']["coordinates"]
                    lat = coords[1]
                    lon = coords[0]
                    #print ts, sname, lat, lon
                    if len(sname_list) <= sname_limit:
                        sname_list.append(sname)
                    else:
                        raise BufferError

    def on_error(self, status_code, data):
        pass
        #print status_code
        # stop trying to get data because of an error
        #self.disconnect()

def monitor_stream():
    # reading credentials
    credentials = [l.strip() for l in open("{0}/data/credential.txt".format(pkg_path))]
    APP_KEY = credentials[0]
    APP_SECRET = credentials[1]
    OAUTH_TOKEN = credentials[2]
    OAUTH_TOKEN_SECRET = credentials[3]

    #TODO: incremental backup time interval?
    back_up_interval = 90
    client_args = {'headers': {'Accept-Encoding': 'deflate, gzip'}}
    #client_args = {'headers': {'User-Agent': 'geoloc', 'Accept-Encoding': 'deflate, gzip', 'Host': 'api.twitter.com'}}
    while True:
        try:
            stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, client_args = client_args)
            stream.statuses.filter(locations='-180,-90,180,90')
        except twython.TwythonRateLimitError:
            time.sleep(back_up_interval)
        except twython.TwythonAuthError:
            time.sleep(back_up_interval)
        except twython.TwythonError:
            time.sleep(back_up_interval)
        except requests.exceptions.ChunkedEncodingError:
            pass
        except requests.exceptions.ConnectionError:
            time.sleep(back_up_interval)
        except BufferError:
            break

def get_sname_list(sname_number):
    global sname_limit, sname_list
    sname_limit = sname_number
    monitor_stream()
    return sname_list

def main():
    print get_sname_list(100)

if __name__ == "__main__":
    main()

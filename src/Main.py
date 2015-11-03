# -*- coding: utf-8 -*-
"""
Created on Sun Nov 01 23:33:08 2015

@author: jeprawih
"""

#!/usr/bin/env python

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import os
from tweetprocessor import *

FN1 = 'tweet_output/ft1.txt'
FN2 = 'tweet_output/ft2.txt'

# loads Twitter credentials from .twitter file that is in the same directory as this script
file_dir = os.path.dirname(os.path.realpath(__file__))
with open(file_dir + '/.twitter-example') as twitter_file:
    twitter_cred = json.load(twitter_file)

# authentication from the credentials file above
access_token = twitter_cred["access_token"]
access_token_secret = twitter_cred["access_token_secret"]
consumer_key = twitter_cred["consumer_key"]
consumer_secret = twitter_cred["consumer_secret"]

class StdOutListener(StreamListener):
    """ A listener handles tweets that are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, filename,write_to_file, ff1, ff2):
        self.filename = filename
        self.__writetofile = write_to_file
        self.__mySD = SlidingWindow()
        self.__TweetProcessor = Tweets()
        self.__unicodeCounter = 0
        self.__ll = 0 #counter for valid tweets
        self.__tt = 0 #counter for total stream
        self.__ff1 = ff1 #ft1.txt handler
        self.__ff2 = ff2 #ft2.txt handler

    # this is the event handler for new data
    def on_data(self, data):
        if self.__writetofile:
            if not os.path.isfile(self.filename):    # check if file doesn't exist
                f = file(self.filename, 'w')
                f.close()
            with open(self.filename, 'ab') as f:
                #print "writing to {}".format(self.filename)
                f.write(data)

        #Process the tweets        
        self.__tt += 1
        if self.__TweetProcessor.Process(data):
            if self.__TweetProcessor.ucode:
                self.__unicodeCounter += self.__TweetProcessor.ucodeCounter
            self.__ll+= 1
            self.__ff1.write(self.__TweetProcessor.cleanedTxt + "\n")

            rollavg = "%0.2f" %(self.__mySD.Add(self.__TweetProcessor.hashtags,self.__TweetProcessor.timestamp),)
            self.__ff2.write(rollavg + "\n")

            #Output progress meter every 100 valid tweets            
            if self.__ll%100 == 0:
                print "Processing %i tweets, %i contain unicode, rolling average = %s" %(self.__ll, self.__unicodeCounter, rollavg)

    # this is the event handler for errors
    def on_error(self, status):
        print(status)
        
    @property
    def unicodeLines(self):
        return self.__unicodeCounter
    
    @property 
    def processedLines(self):
        return self.__ll
    
    @property
    def totalLines(self):
        return self.__tt

if __name__ == "__main__" :
    print "Twitter Data Cleaner - Jerry Prawiharjo"
    Q1 = raw_input("Use streaming data [st], or example file [ex]? [st/ex] : ")

    basedir = os.path.abspath(os.path.join(file_dir, '..'))
    filename = os.path.abspath(os.path.join(basedir, "tweet_input/tweets.txt"))
    fn1 = os.path.abspath(os.path.join(basedir, FN1))
    fn2 = os.path.abspath(os.path.join(basedir, FN2))

    if Q1.lower() == 'st':
        Q2 = raw_input("Store tweet streams to tweets.txt? [y/n]: ").lower() == "y" 
        
        ff1 = open(fn1, 'w')
        ff2 = open(fn2, 'w')
    
        listener = StdOutListener(filename, Q2, ff1, ff2) #modified from 
        try:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
        
            print "Use CTRL + C to exit at any time.\n"
            stream = Stream(auth, listener)
            stream.filter(locations=[-180,-90,180,90]) # this is the entire world, any tweet with geo-location enabled
        except Exception as ex:
            print ex.message
        finally:
            ff1.close()
            ff2.close()
            
            print "Received %i data, %i valid tweets. %i contained unicode" %(listener.totalLines, listener.processedLines, listener.unicodeLines)
    else:
        tweets = open(filename,'r')

        ff1 = open(fn1, 'w')
        ff2 = open(fn2, 'w')

        mySD = SlidingWindow()
        TweetProcessor = Tweets()
        unicodeCounter = 0

        ll = 0
        tt = 0
        for line in tweets:
            line = line.encode('ascii')
            tt +=1

            if TweetProcessor.Process(line):
                if TweetProcessor.ucode:
                    unicodeCounter += TweetProcessor.ucodeCounter
                ll+= 1
                ff1.write(TweetProcessor.cleanedTxt + "\n")
                rollavg = "%0.2f\n" %(mySD.Add(TweetProcessor.hashtags,TweetProcessor.timestamp),)
                ff2.write(rollavg)

        ss = "%i tweets contained unicode." %(unicodeCounter,)
        ff1.write("\n")
        ff1.write(ss)
        print "Finished processing %i lines, %i valid tweets. %i contain unicode characters" %(tt, ll, unicodeCounter)
        tweets.close()
        ff1.close()
        ff2.close()

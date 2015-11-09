# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 15:53:59 2015

@author: jeprawih
"""
import re
import time
import copy
from datetime import datetime, timedelta
from collections import deque, Counter

ReHash = re.compile('#[0-9A-Za-z]+') # Regex to trap hashtags
ReUcode = re.compile('\\\\u[0-9a-f]{4}') #regex to trap unicodes
ReEscSeq = re.compile(r'\\[fnrtv\/\'\"\?\\]') #Regex to trap escape sequences

class Tweets(object):
    # Twitter cleaner class
    # There is an option to use json module instead of string
    # However, I believe that string processing give better performance    
    
    def __init__(self):
        pass

    def Process(self,strin):
        m0 = strin.find('\"created_at\":')
        m1 = strin.find('\"text\":', m0+50) #Text is located between text and source
        m2 = strin.find('\"source\":', m1+10)
        
        if m0 <0 or m1<0 or m2<0:
            return False
        timestamptxt = strin[m0+14:m0+44]
        timestamp = time.strptime(timestamptxt, '%a %b %d %H:%M:%S +0000 %Y')
        
        #timestamp is converted to datetime for easier processing
        timestamp = datetime.fromtimestamp(time.mktime(timestamp))
        txt = strin[m1+8:m2-2]
    
        # Process regex for unicode
        Ucode = False
        a = ReUcode.finditer(txt)
        for k in a:
            y = k.group(0)
            txt = txt.replace(y,'')
            Ucode = True
    
        # Process regex for hashtags
        hashtags = []        
        b = ReHash.finditer(txt)
        for k in b:
            hashtags.append(k.group(0).lower())
    
        # Process regex for escape sequences
        c = ReEscSeq.finditer(txt)
        for k in c:
            y = k.group(0)
            if y == "\\n" or y == "\\r" or y == "\\t":
                txt = txt.replace(y," ")
            else:
                txt = txt.replace(y,y[1])
    
        self.__txt = txt
        self.__timestamptxt = timestamptxt
        self.__timestamp = timestamp
        self.__ucode = Ucode
        self.__hashtags = deque(set(hashtags))
        return True            

    @property
    def textOnly(self):
        return self.__txt
    
    @property
    def cleanedTxt(self):
        return self.__txt + " (timestamp: " + self.__timestamptxt + ")"
    
    @property
    def ucodeCounter(self):
        return 1 if self.__ucode else 0
        
    @property
    def hashtags(self):
        return self.__hashtags

    @property    
    def timestamp(self):
        return self.__timestamp
        
    @property 
    def ucode(self):
        return self.__ucode

class SlidingWindow(object):
    # Sliding window class keeps the data on the graph as dictionary
    # The dictionary keeps count of the number of hashtags, so that de-registration will
    # change the count
    # Hastags and timestamp are stored as deque, for performance purpose on append and left
    # at head and tail [O(1) performance]
    
    __window = 60    # Sliding window width in seconds
    
    def __init__(self):
        self.__hashtags = deque()
        self.__graphs = {}
        self.__timestamp = deque()
        self.__sum = 0 #Sum for all the nodes
        self.__counter = 0 #Counter for the hashtags kept within the sliding window
        self.__denom = 0 #Counter for the graph nodes
        
    def Add(self,hashtags,timestamp):
        self.__hashtags.append(hashtags)
        self.__timestamp.append(timestamp)
        self.__counter += 1
    
        # Only consider hashtags if it's more than 1
        if len(hashtags) > 1:
            for k in range(len(hashtags)):
                # Adds hashtags in cyclical manner to the graph dictionary
                tempkey = hashtags.popleft()
                templist = list(copy.copy(hashtags))
                
                if tempkey not in self.__graphs:
                    #Initial count is 1 for each
                    self.__graphs[tempkey] = Counter(templist)
                    self.__sum += len(templist)
                    # Keep count for the total graph nodes
                    self.__denom += 1
                else:
                    for l in range(len(templist)) :
                        if templist[l] not in self.__graphs[tempkey]:
                            self.__sum += 1
                    self.__graphs[tempkey] += Counter(templist)
                # Add the hashtags back to retain the cyclical manner
                hashtags.append(tempkey)

        while timedelta.total_seconds(timestamp - self.__timestamp[0]) > self.__window:
            self.__timestamp.popleft()
            hashtags = self.__hashtags.popleft()

            #Only consider if hashtags length is more than 1
            if len(hashtags) > 1:
                for k in range(len(hashtags)):
                    # Remove hashtags in cyclical manner to the graph dictionary
                    tempkey = hashtags.popleft()
                    templist = list(copy.copy(hashtags))
                    
                    self.__graphs[tempkey] -= Counter(templist)
    
                    for l in range(len(templist)) :
                        if not self.__graphs[tempkey].has_key(templist[l]):
                            self.__sum -= 1
                    if len(self.__graphs[tempkey]) == 0:
                        del self.__graphs[tempkey]
                        self.__denom -= 1
                    
                    hashtags.append(tempkey)
        
        if self.__denom > 0 :
            slidingavg = float(self.__sum)/self.__denom
        else:
            slidingavg = 0.0
        return slidingavg
    
    @property
    def TotalHashtags(self):
        return len(self.__graphs)

    @property
    def HashtagsVertexLengths(self):
        L = []
        for kk in self.__graphs.itervalues():
            L.append(len(kk))
        return L

    @property
    def Graphs(self):
        return self.__graphs

if __name__ == "__main__":
    filename = "C:/Users/jeprawih/Downloads/coding-challenge-master/coding-challenge-master/data-gen/tweets.txt"

    txt = open(filename,'r')
    
    
    mySD = SlidingWindow()
    TweetProcessor = Tweets()
    unicodeCounter = 0
    
    ll = 0
    tt = 0
    for line in txt:
        line = line.encode('ascii')
        tt +=1
        
        if TweetProcessor.Process(line):
            if TweetProcessor.ucode: 
                unicodeCounter += TweetProcessor.ucodeCounter
            ll+= 1
            print TweetProcessor.cleanedTxt
            print "%0.2f, %i" %(mySD.Add(TweetProcessor.hashtags,TweetProcessor.timestamp),mySD.TotalHashtags)
        
    txt.close()
    print ll, tt, unicodeCounter

    
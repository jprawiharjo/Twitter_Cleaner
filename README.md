# TwitterCleaner #

Solution for the InsightDataEngineering coding-challenge

The *Main.py* contains the main program, while *tweetprocessor.py* contains the subroutine to process the tweets (i.e. feature 1), and to count the rolling average of the graph nodes (i.e. feature 2)

Upon calling *run.sh*, the code will ask whether user wants to use the example file [ex ] (*tweets.txt* in *tweet_input* folder), or the live stream data from Twitter [st], using the twitter API.

a *.twitter-example* file with the credentials need to exist in the src folder for the twitter API to work.
    
> Use streaming data [st], or example file [ex]? [st/ex] : 

When choosing to use the live streaming data, the software will ask whether user wants to append the streams into the *tweets.txt* file:

> Store tweet streams to tweets.txt? [y/n]: 

**Modules Imported:**

Except for tweepy, these imported modules are usually standard in a python distribution

1. re
2. datetime
3. time
4. json
5. collections
6. copy
7. os
8. tweepy [Please refer to tweepy website for installation]

## Solution ##

**Feature 1**

The solution for cleaning the tweets [feature 1] employs two strategies: 

1. Searching for the text using internal string module
2. Searching for unicodes, hashtags and escape sequences using Regular Expression (**re** module)

While one can employ json module to extract the text, I believe that string provides better performance

**Feature 2**

The graph is stored as dictionary in python. In addition, I keep the number of hashtags associated with the connected nodes in the dictionary. Adding and removing the hashtags will increment or decrement the counter, and once it reaches zero, the connected node will be removed.

Another counter is used to keep tabs of the graph nodes, and the total sum of the connected vertices.

This way, the subroutine avoids recalculating the graph for every tweets.
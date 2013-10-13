#!/usr/bin/env python

'''Predict the number of retweets that a tweet is likely to have.'''

__author__ = 'joy4luck'

import getopt
import json
import numpy
import requests
import sys
import time
#some namespace pollution, but just a few constants
from bpt_constants import *
from requests_oauthlib import OAuth1
from secrets import *

def PrintUsageAndExit():
  print USAGE
  sys.exit(2)

class Tweet:
  '''Tweet struct.'''
  def __init__(self, retweets, tweet_id, user_id, followers_count,
              friends_count, listed_count, previous_average,
              hashtags, urls, tweet_len, is_a_reply, age):
    #data point ID
    self.retweets = retweets    # Use only for training
    self.tweet_id = tweet_id
    self.user_id = user_id
    # user features
    self.followers_count = followers_count
    self.friends_count = friends_count
    self.listed_count = listed_count
    self.previous_average = previous_average
    # tweet features
    self.hashtags = hashtags
    self.urls = urls
    self.tweet_len = tweet_len
    self.is_a_reply = is_a_reply
    self.age = age

    self.data = [self.retweets,
      self.tweet_id,
      self.user_id,
      self.followers_count,
      self.friends_count,
      self.listed_count,
      self.previous_average,
      self.hashtags,
      self.urls,
      self.tweet_len,
      self.is_a_reply,
      self.age]
               
  def __str__(self):
    return "%s, %s" % (self.tweet_id, self.retweets)

  def __repr__(self):
    return ','.join([str(d) for d in self.data])

class Searcher(object):
  '''Interface to Twitter API.'''
  _timeout = 15
  twitter_api_base = 'https://api.twitter.com/1.1'
  search_tweets = 'search/tweets.json'
  status_show = 'statuses/show.json'
  status_timeline = 'statuses/user_timeline.json'

  def __init__(self):
    self.__auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET,
                    ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

  def _Get(self, url):
    '''
    OAuth frosted GET call to the Twitter API.

    Args:
      url: the query
    '''
    print "GET URL = %s" % url
    return requests.get(
      url,
      auth=self.__auth,
      timeout=Searcher._timeout)

  def Search(self, params):
    '''
    General Twitter Search call. For data collection.

    Args:
      params: a dictionary of key value pairs to narrow the query.
    '''
    url = '/'.join([Searcher.twitter_api_base, Searcher.search_tweets])
    url += "?" + "&".join([k + '=' + params[k] for k in params])
    return self._Get(url)

  def GetTweetJson(self, tweetid):
    '''
    Acquires a tweet's info, given its ID.
    '''
    url = '/'.join([Searcher.twitter_api_base, Searcher.status_show])
    url += "?id=" + str(tweetid)
    return self._Get(url)

  def getTimeline(self, user_id):
    '''
    Returns a user's past 20 tweets.
    '''
    url = '/'.join([Searcher.twitter_api_base, Searcher.status_timeline])
    url += '?user_id=' + unicode(user_id)
    url += '&count=20'
    return self._Get(url)
  

class Parser(object):
  def __init__(self):
    self.searcher = Searcher()

  def ParseTweet(self, tweet_json, skip_retweet=True, get_avg=True):
    '''
    Parse json representation of a tweet.

    Args:
      tweet_json: the json string returned by twitter API call.
      skip_retweet: if true, instead get information of original tweet.

    Returns:
      tweet object with populated data
      
    '''
    if skip_retweet and tweet_json.get('retweeted_status'):
      # This is a retweet, consider it a dupe of the original post.
      tweet_json = tweet_json.get('retweeted_status')

    tweet_dict = {}
    for key in TWEET_KEYS:
      if tweet_json.get(key):
        tweet_dict[key] = unicode(tweet_json[key])
      
    c_a = tweet_dict.get('created_at').strip()
    t_since_epoch = time.mktime(time.strptime(c_a, TIME_PATTERN))
    age = time.time() - t_since_epoch + 14400 # account for GMT

    user_dict = self.ParseUser(tweet_json['user'])

    
    prev_rtwt = 0
    if get_avg:
      prev_rtwt = self.getAverage(user_dict.get('id_str'),
                                  skip=tweet_dict.get('id_str'))

    tweet = Tweet(int(tweet_json['retweet_count']),
                  tweet_dict.get('id_str'),
                  user_dict.get('id_str'),
                  int(user_dict.get('followers_count', 0)),
                  int(user_dict.get('friends_count', 0)),
                  int(user_dict.get('listed_count', 0)),
                  prev_rtwt,
                  len(tweet_json.get('entities').get('hashtags')),
                  len(tweet_json.get('entities').get('urls')),
                  len(tweet_dict.get('text')),
                  1 if tweet_dict.get('in_reply_to_user_id_str', '') else 0,
                  age,)
    return tweet

  def ParseUser(self, user_json):
    # Single level interesting entries for a user.
    user_dict = {}
    for key in USER_KEYS:
      if user_json.get(key):
        user_dict[key] = unicode(user_json[key])
    return user_dict

  def ParseTimeline(self, timeline_json):
    '''Parse multiple tweets from a timeline.
    Args:
      json string returned by twitter API call.

    Returns:
      list of Tweet objects
    '''
    tweets = []
    for t in timeline_json:
      t = self.ParseTweet(t, get_avg=False)
      tweets.append(t)
    return tweets

  def getAverage(self, user_id, skip=None):
    '''
    Finds a user's past 20 tweets and averages their retweet count.
    '''
    http_response = self.searcher.getTimeline(user_id)
    with open("timeline_query.txt", 'w') as f:
      f.write(http_response.content)
    tweets = self.ParseTimeline(json.loads(http_response.content))
    
    return numpy.mean([t.retweets for t in tweets if not t.tweet_id == skip])

def main():
  try:
    shortflags = 'h'
    longflags = ['help', 'tweetid=', 'debug']
    opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
  except getopt.GetoptError:
    PrintUsageAndExit()

  # Default tweetid is the backplane post
  tweetid = 385166654486749184

  # debug mode is currently used to toggle between collection and search.
  debug = False
  for o, a in opts:
    if o in ("-h", "--help"):
      PrintUsageAndExit()
    if o in ("--tweetid"):
      tweetid = a
    if o in ("--debug"):
      debug = True

  searcher = Searcher()
  parser = Parser()

  if debug:
    print "AVERAGE %s" % parser.getAverage('127925808')
    return

  else: # Currently searches for tweet data.
    http_response = searcher.GetTweetJson(tweetid)
    # Save the raw json results of a tweet query.
    with open("last_tweet_query.txt", 'w') as f:
      f.write(http_response.content)

    data = json.loads(http_response.content)

    tweet = parser.ParseTweet(data, skip_retweet=False)
    print DIV
    print str(tweet)
    print DIV
    print repr(tweet)
    
    print "PREDICTED RETWEETS = %s" % predict(tweet)
    print "Done. :D"

def collectData(filename='big_tweet_list.txt'):
  '''
  Used to train a predictor.
  '''
  params = {
    'lang':'en',
    'count': '200',
    'include_entities' : 'false'}

  with open(filename, 'w') as f:
    for s in SEEDS:
      for d in DATES:
        params['q'] = s
        params['until'] = d
        http_response = searcher.Search(params).content
        data = json.loads(http_response)
        if not data.get('statuses'):
          continue
        for r in data['statuses']:
          tweet = parser.ParseTweet(r)
          # Write each new data point as a comma separated list on a new line.
          f.write(repr(tweet) + '\n')
          # sort by date. Only train on tweets 1-3 hours old
          # TODO Save and use data

  print "Done collecting. :D"

def predict(tweet):
  '''
  Use previously trained predictor to guess number of retweets in an hour.
  '''
  # TODO
  return 0

def sampleTweets(filename='baby_tweets.txt'):
  '''
  Collect tweet data on tweets younger than 5 minutes.
  Make predictions and save into file under filename.
  '''
  # TODO
  searcher = Searcher()
  parser = Parser()
  for s in SEEDS:
    pass

def scoreAllTweets(filename='baby_tweets.txt'):
  '''
  Find actual counts, score previous predictions.
  '''
  # TODO
  original = open(filename, 'r')
  update = open("scored_" + filename, 'w')
  for line in original:
    tweet_id = line.strip()
    update.write(new_line + '\n')

if __name__ == "__main__":
  main()

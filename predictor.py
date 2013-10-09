#!/usr/bin/env python

'''Predict the number of retweets that a tweet is likely to have.'''

__author__ = 'joy4luck'

import getopt
import sys
import requests
import json
from requests_oauthlib import OAuth1
#some namespace pollution, but just a few constants
from secrets import *
from bpt_constants import *

def PrintUsageAndExit():
  print USAGE
  sys.exit(2)

class Searcher(object):
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
    url += '?user_id=' + unicode(tweetid)
    url += '&count=20'
    return self._Get(url)

class Parser(object):
  def ParseTweet(self, tweet_json, skip_retweet=True):
    '''
    Convert the json representation of a tweet into a few features we
    care about.

    Args:
      tweet_json: the json string returned by twitter API call.
      skip_retweet: if true, instead get information of original tweet.

    Returns tuple of:
      retweets: number of retweets the tweet currently has
      tweet_dict: short dict of a few features of a tweet. See bpt_constants.
      user_dict: short dict of a few features of a tweet. See bpt_constants.
      
    '''
    if skip_retweet and tweet_json.get('retweeted_status'):
      # If this is a retweet, consider it a dupe of the original post.
      tweet_json = tweet_json.get('retweeted_status')

    tweet_dict = {}
    for key in TWEET_KEYS:
      if tweet_json.get(key):
        tweet_dict[key] = unicode(tweet_json[key])
      
    retweets = str(tweet_json['retweet_count']) # Use only for training
    user_dict = self.ParseUser(tweet_json['user'])

    ENTITIES = 'entities'
    # TODO(joyc) handle hashtags/other references

    return retweets, tweet_dict, user_dict

  def ParseUser(self, user_json):
    # Single level interesting entries for a user.
    user_dict = {}
    for key in USER_KEYS:
      if user_json.get(key):
        user_dict[key] = unicode(user_json[key])
    return user_dict

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

  if debug: # Currently used to search the database to collect some numbers.
    params = {
      'lang':'en',
      'count': '200',
      'include_entities' : 'false'}

    with open('big_tweet_list.txt', 'w') as f:
      for s in SEEDS:
        for d in DATES:
          params['q'] = s
          params['until'] = d
          http_response = searcher.Search(params).content
          data = json.loads(http_response)
          if not data.get('statuses'):
            continue
          for r in data['statuses']:
            retweets, tweet, user = parser.ParseTweet(r)
            data_point = ','.join([
              retweets,
              tweet.get('id_str'),
              user.get('id_str'),
              user.get('followers_count', '0'),
              user.get('friends_count', '0'),
              user.get('listed_count', '0'),
              tweet.get('in_reply_to_user_id_str', ''),
              tweet.get('created_at'),])
            # Write each new data point as a comma separated list on a new line.
            f.write(data_point + '\n')
          break
        break

    print "Done collecting. :D"

  else: # Currently searches for tweet data.
    http_response = searcher.GetTweetJson(tweetid)
    data = json.loads(http_response.content)

    retweets, tweet, user = parser.ParseTweet(data, skip_retweet=False)
    print DIV
    print "RETWEET_COUNT = %s" % retweets
    for k in tweet:
      print k + ": " + tweet[k]
    print DIV
    for k in user:
      print k + ": " + user[k]

    # Save the raw json results of a tweet query.
    with open("last_tweet_query.txt", 'w') as f:
      f.write(http_response.content)

    #TODO Prediction magicks
    print "Done. :D"

if __name__ == "__main__":
  main()

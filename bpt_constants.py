'''Global constants to save clutter in predictor.py '''

__author__ = 'joy4luck'

DIV =  "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

USAGE = '''Usage: predict --tweetid=[id]

  Guess how many retweets this tweet will have!

  Options:
    -h --help : print this help
    --tweetid: the tweet id to look up. Defaults to backplane post.
    --debug: for dev purposes. Does whatever I want it do.
'''

# Single level interesting entries for a tweet.
TWEET_KEYS = [
  'id_str',
  'created_at',
  'text',
  'in_reply_to_user_id_str',
  'lang']

USER_KEYS = [
  'id_str',
  'followers_count',
  'friends_count',
  'listed_count',
  'lang']

# collection of random seed values
SEEDS = [
  'Google', 
  'Amazon',
  'Gaga',
  'eminem',
  'babies',
  'children',
  'highschool',
  'middleage',
  'nfl',
  'skater',
  'business',
  'republicans',
  'democrats',
  'food',
  'cats',
  'IGN',
  'traffic',
  'storm',
  'algorithm',
  'yoloswag']

# collection of dates to crawl
DATES = [
  '2013-10-08',
  '2013-10-07',
  '2013-10-06',
  '2013-10-05',
  '2013-10-04',
]

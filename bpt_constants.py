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

TIME_PATTERN = "%a %b %d %H:%M:%S +0000 %Y"

# Time intervals in seconds
FIVE_MINUTES = 300
ONE_HOUR = 3600
THREE_HOURS = 10800

PICKLED_REGRESSION = 'regression.pkl'

# Single level interesting entries for a tweet.
TWEET_KEYS = [
  'text',
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

# collection of 20 random seed values
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
]

'''Scripts used for developing predictor.'''

__author__ = 'joy4luck'

import json
import numpy
import pickle
import predictor
from bpt_constants import *
from sklearn import linear_model

def collectData(filename='big_tweet_list.txt'):
  '''
  Used to obtain training data.
  '''
  searcher = predictor.Searcher()
  parser = predictor.Parser()
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
          tweet = parser.ParseTweet(r, get_avg=False)
          # Only train on tweets >1 hour old
          if tweet.age > ONE_HOUR:
            # Write each new data point as a comma separated list on a new line.
            f.write(repr(tweet) + '\n')

  print "Done collecting. :D"

def trainAndTestClassifier(filename='big_tweet_list.txt'):
  '''Use saved tweet data to train a linear regression.'''
  clf = linear_model.LinearRegression()
  tweets = []
  tweet_file = open(filename, 'r')
  x = []
  y = []
  for l in range(2869): # train on first half of data
    data_point = tweet_file.readline().strip().split(',')
    x.append([float(d) for d in data_point[3:-1]])
    y.append(int(data_point[0]))

  x = numpy.array(x)
  y = numpy.array(y)
  clf.fit(x, y)
  r2 = clf.score(x, y)
  print "R^2 %s" % r2
  print clf.coef_

  # save regression into a file for later
  output = open('regression.pkl', 'wb')
  pickle.dump(clf, output)
  output.close()

  pred_f = open('predict.txt', 'w')
  misclassify = 0
  total = 0
  p_errs = []
  for l in range(2870, 5739): # test on second half
    data_point = tweet_file.readline().strip().split(',')
    x = [float(d) for d in data_point[3:-1]]
    prediction = int(max([clf.predict(numpy.array(x)), 0]))
    actual = int(data_point[0])

    total += 1
    if actual == 0:
      if prediction > 0:
        misclassify += 1
      else:
        # No retweets, and predicted so correctly.
        pass
    else:
      p_error = float(prediction-actual)/actual
      p_errs.append(p_error)
      line = '%s \t %s \t %s' % (prediction, actual, p_error)
      pred_f.write(line + '\n')
  pred_f.close()

  print 'Total number of test points: %s' % total
  print 'Points misclassified: %s' % misclassify
  print 'Misclassified: %s' % (float(misclassify)/total)

def sampleTweets(filename='baby_tweets.txt'):
  '''
  Collect tweet data on tweets younger than 5 minutes.
  '''
  searcher = predictor.Searcher()
  parser = predictor.Parser()
  params = {
    'lang':'en',
    'count': '200',
    'include_entities' : 'false'}
  with open(filename, 'w') as f:
    for s in SEEDS:
      params['q'] = s
      http_response = searcher.Search(params).content
      data = json.loads(http_response)
      if not data.get('statuses'):
        continue
      for r in data['statuses']:
        tweet = parser.ParseTweet(r, get_avg=False)
        # Only keep tweets younger than 5 minutes
        if tweet.age < FIVE_MINUTES:
          # Write each new data point as a comma separated list on a new line.
          f.write(repr(tweet) + '\n')

def scoreAllTweets(filename='baby_tweets.txt'):
  '''
  Find current counts of earlier caught tweets, predict and score.
  '''
  original = open(filename, 'r')
  update = open("scored_" + filename, 'w')

  # Reload saved regression
  pkl_file = open('regression.pkl', 'rb')
  clf = pickle.load(pkl_file)
  pkl_file.close()

  misclassify = 0
  total = 0
  p_errs = []
  searcher = predictor.Searcher()
  parser = predictor.Parser()
  for line in original:
    data_point = line.strip().split(',')
    x = [float(d) for d in data_point[3:-1]]
    prediction = int(max([clf.predict(numpy.array(x)), 0]))
    
    http_response = searcher.GetTweetJson(data_point[1])
    data = json.loads(http_response.content)
    try:
      tweet = parser.ParseTweet(data, get_avg=False)
      actual = tweet.retweets

      total += 1
      if actual == 0:
        if prediction > 0:
          misclassify += 1
        else:
          # No retweets, and predicted so correctly.
          pass
      else:
        p_error = float(prediction-actual)/actual
        p_errs.append(p_error)
        line = '%s \t %s \t %s' % (prediction, actual, p_error)
        update.write(line + '\n')
    except AttributeError as e:
      print e

  print 'Total number of test points: %s' % total
  print 'Points misclassified: %s' % misclassify
  print 'Misclassified: %s' % (float(misclassify)/total)

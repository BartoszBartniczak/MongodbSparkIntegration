from pymongo import MongoClient
from bson.json_util import dumps

mongodbClient = MongoClient()
mongodbTweets = mongodbClient.tweets

cursor = mongodbClient.tweets.tweets.find()

count_tweets = cursor.count();

print("There is %s tweets in the database." % str(count_tweets))

for tweet in cursor.skip(count_tweets-10):
    print dumps(tweet)

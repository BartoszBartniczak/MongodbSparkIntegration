from TwitterConfiguration.Configuration import Reader
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
from bson.json_util import loads

configurationReader = Reader()
apiConf = configurationReader.read_from_yaml_file('config.yaml')

mongodbClient = MongoClient()
mongodbTweets = mongodbClient.tweets


class MongoDBListener(StreamListener):
    def __init__(self, mongodb):
        self.mongodb = mongodb

    def on_data(self, data):
        jsonData = loads(data)
        #print jsonData
        result = self.mongodb.tweets2.insert_one(jsonData)
        print result
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
        # This handles Twitter authetification and the connection to Twitter Streaming API
    listener = MongoDBListener(mongodbTweets)
    auth = OAuthHandler(apiConf.consumerKey, apiConf.consumerSecret)
    auth.set_access_token(apiConf.accessToken, apiConf.accessTokenSecret)
    stream = Stream(auth, listener)

    # This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['Dash', 'museumselfie','planet nine','black history month','Foxx','Pluto','trending'])

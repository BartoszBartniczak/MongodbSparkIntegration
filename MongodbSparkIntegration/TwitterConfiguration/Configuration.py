import yaml


class Configuration:
    accessToken = ''
    accessTokenSecret = ''
    consumerKey = ''
    consumerSecret = ''

    def __init__(self, accessToken, accesssTokenSecret, consumerKey, consumerSecret):
        self.accessToken = accessToken
        self.accessTokenSecret = accesssTokenSecret
        self.consumerKey = consumerKey
        self.consumerSecret = consumerSecret


class Reader:
    def read_from_yaml_file(self, path):
        with open(path, 'r') as f:
            doc = yaml.load(f)
        return Configuration(doc['access_token'], doc['access_token_secret'], doc['consumer_key'],
                             doc['consumer_secret'])

import tweepy


class DeveloperConfig:
    # Get your Twitter API credentials and enter them here
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_key = access_key
        self.access_secret = access_secret

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_key, access_secret)
        self.api_auth = tweepy.API(self.auth, wait_on_rate_limit=True)

import os

PROD, TEST = range(2)

# for test, let CURRENT_PROFILE = TEST config
CURRENT_PROFILE = PROD

CURRENT_CONFIG = [
    dict(
        # prod
        # Get your Twitter API credentials and enter them here
        TWITTER_DEV=dict(
            CONSUMER_KEY="CONSUMER_KEY",
            CONSUMER_SECRET="CONSUMER_SECRET",
            ACCESS_KEY="YOUR ACCESS_KEY",
            ACCESS_SECRET="YOUR ACCESS_SECRET",
        ),

        SOLR_URL='',

        NEWS_ACCOUNTS='../data/TwitterNewsAgencies.csv',
        TWEETS_PATH='',
        TWEETS_4HOUR_PATH='',

        ARTICLE_PATH='',

    ),
    dict(
        # TEST
        # Get your Twitter API credentials and enter them here
        TWITTER_DEV=dict(
            CONSUMER_KEY="CONSUMER_KEY",
            CONSUMER_SECRET="CONSUMER_SECRET",
            ACCESS_KEY="YOUR ACCESS_KEY",
            ACCESS_SECRET="YOUR ACCESS_SECRET",
        ),

        SOLR_URL='',

        TWEETS_PATH='',

        TWEETS_4HOUR_PATH='',

        ARTICLE_PATH='',
    )
][CURRENT_PROFILE]

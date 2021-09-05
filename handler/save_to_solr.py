import os
import sys
import json
import pysolr
import datetime
import pandas as pd
from config.NewsConfig import *


def tweets_save_solr(record_list):
    """
    upload records to solr
    :param record_list:
    :return:
    """
    url = CURRENT_CONFIG['SOLR_URL']
    solr = pysolr.Solr(url, timeout=180)
    solr.add(record_list, softCommit=True)


def convert_time(dd):
    """
    convert current time format to fit SOLR time format
    :param dd:
    :return:
    """
    # dd = "Tue Jun 22 23:42:35 +0000 2021"
    GMT_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'
    # YYYY-MM-DDTHH:mm:ssZ
    datetimeformat = "%Y-%m-%dT%H:%M:%SZ"
    temp_time = datetime.datetime.strptime(dd, GMT_FORMAT)
    return temp_time.strftime(datetimeformat)


def tweets_parse(tweet_path, article_path):
    """
    parse tweets and articles and then combine them to a single record
    :param tweet_path: collected tweet path
    :param article_path: collected article path
    :return:
    """
    for file in os.listdir(tweet_path):
        if not file.endswith('.csv'):
            continue

        tweets_list = []
        tweets = pd.read_csv(tweet_path + file, header=None)
        articles = pd.read_csv(article_path + file)

        num = tweets.shape[0]

        for i in range(num):
            if not pd.isnull(articles.loc[i, 'article']):
                each = {}
                row = tweets.loc[i]
                tweet = json.loads(row[4])
                
                each['tweet_id'] = str(row[1])
                each['created_at'] = convert_time(tweet['created_at'])
                each['user_screen_name'] = tweet['user']['screen_name']
                each['user_name'] = tweet['user']['name']
                each['user_id'] = str(tweet['user']['id'])
                each['users_followers_count'] = str(tweet['user']['followers_count'])
                each['users_friends_count'] = str(tweet['user']['friends_count'])
                each['users_description'] = tweet['user']['description']
                each['full_text'] = row[2]
                each['news_source'] = row[0]
                each['favorite_count'] = str(tweet['favorite_count'])
                each['retweet_count'] = str(tweet['retweet_count'])
                each['user_location_original'] = ''
                each['user_location'] = str(tweet['retweet_count'])

                content = json.loads(articles.loc[i, 'article'])
                each['article_title'] = content['title']
                each['article_authors'] = content['authors']
                each['article_text'] = content['text']
                each['article_url'] = content['url']
                each['article_top_image'] = content['top_image']
                each['article_movies'] = content['movies']
                each['article_summary'] = content['summary']
                each['article_keywords'] = content['keywords']
                tweets_list.append(each)

        print("Uploading to Solr: {}".format(file))
        tweets_save_solr(tweets_list)


def create_solr(timestamp):
    """
    creating solr and upload records
    :param timestamp:
    :return:
    """
    tweet_path = CURRENT_CONFIG['TWEETS_4HOUR_PATH'] + timestamp + '/'
    article_path = CURRENT_CONFIG['ARTICLE_PATH'] + timestamp + '/'

    tweets_parse(tweet_path, article_path)


if __name__ == '__main__':
    date = sys.argv[1]
    create_solr(date)

import os
import csv
import sys
import json
import pandas as pd
from newspaper import Article
from datetime import datetime, timedelta
from handler.save_to_solr import create_solr
from config.NewsConfig import *


def get_newspaper(useurl, username, tweetid, csv_writer):
    news = {}
    article = Article(url=useurl)

    try:
        article.download()
        article.parse()
    except:
        csv_writer.writerow([username, tweetid, ''])
        return

    news['title'] = article.title
    news['authors'] = article.authors
    news['text'] = article.text
    if 'JavaScript is not available' in news['text'] or news['text'] == '':
        csv_writer.writerow([username, tweetid, ''])
        return

    news['url'] = useurl
    news['top_image'] = article.top_image
    news['movies'] = article.movies

    article.nlp()
    news['summary'] = article.summary
    news['keywords'] = article.keywords

    csv_writer.writerow([username, tweetid, json.dumps(news)])


def read_file(read_path, date_dir):
    for file in os.listdir(read_path):
        if not file.endswith('.csv'):
            continue

        write_path = date_dir + file

        if not os.path.exists(write_path):
            try:
                df = pd.read_csv(read_path + file, header=None)
                num = df.shape[0]

                f = open(write_path, 'a+', encoding='utf-8')
                os.chmod(write_path, 0o744)
                csv_writer = csv.writer(f)
                csv_writer.writerow(['username', 'tweetid', 'article'])

                for i in range(num):
                    username = df.loc[i, 0]
                    tweetid = df.loc[i, 1]
                    link = df.loc[i, 3]

                    if pd.isnull(df.loc[i, 3]):
                        if df.loc[i, 4][1] == '"':
                            content = json.loads(df.loc[i, 4])
                        else:
                            content = eval(df.loc[i, 4])

                        if content['entities']['urls']:
                            use = content['entities']['urls']
                            for item in use:
                                if 'expanded_url' in item.keys():
                                    get_newspaper(item['expanded_url'], username, tweetid, csv_writer)
                                    break

                        elif 'retweeted_status' in content.keys():
                            if content['retweeted_status']['entities']['urls']:
                                use = content['retweeted_status']['entities']['urls']
                                for item in use:
                                    if 'expanded_url' in item.keys():
                                        get_newspaper(item['expanded_url'], username, tweetid, csv_writer)
                                        break

                            else:
                                csv_writer.writerow([username, tweetid, ''])

                        else:
                            csv_writer.writerow([username, tweetid, ''])

                    else:
                        get_newspaper(link, username, tweetid, csv_writer)

                f.close()
                print('Create ' + file)

            except:
                print("PermissionError")


def create_article():
    date = datetime.now().strftime("%Y_%m_%d")
    read_path = CURRENT_CONFIG['TWEETS_4HOUR_PATH'] + date + '/'
    date_dir = CURRENT_CONFIG['ARTICLE_PATH'] + date + '/'

    if not os.path.exists(date_dir):
        os.mkdir(date_dir)
        os.chmod(date_dir, 0o744)

        yesterday = (datetime.now()-timedelta(days=1)).strftime("%Y_%m_%d")
        check_read = CURRENT_CONFIG['TWEETS_4HOUR_PATH'] + yesterday + '/'
        check_write = CURRENT_CONFIG['ARTICLE_PATH'] + yesterday + '/'

        while len(os.listdir(check_read)) != len(os.listdir(check_write)):
            read_file(check_read, check_write)

        create_solr(yesterday)

    if os.path.exists(read_path):
        while len(os.listdir(read_path)) != len(os.listdir(date_dir)):
            read_file(read_path, date_dir)


if __name__ == '__main__':
    create_article()

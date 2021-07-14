import csv
import datetime
import tweepy
import json
import os
import time
from config.developer_config import DeveloperConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from config.NewsConfig import *
# Get your Twitter API credentials and enter them here
consumer_key = CURRENT_CONFIG['CONSUMER_KEY']
consumer_secret = CURRENT_CONFIG['CONSUMER_SECRET']
access_key = CURRENT_CONFIG['ACCESS_KEY']
access_secret = CURRENT_CONFIG['ACCESS_SECRET']
developer_config = DeveloperConfig(consumer_key, consumer_secret, access_key, access_secret)
api_auth = developer_config.api_auth


def extended_tweet(tweet_id):
    try:
        status = api_auth.get_status(tweet_id, tweet_mode="extended")
    except Exception as e:
        print(e)
        return '', ''
    try:
        full_text = status.retweeted_status.full_text
    except AttributeError:  # Not a Retweet
        # print(status.full_text)
        full_text = status.full_text
    index = full_text.find("https://t.co/")
    # print(url[index:index+23])
    # print(full_text+'\n')
    return full_text.replace('\n', ' '), full_text[index:index + 23]


def get_tweets_daily(since_id, max_id, startdate, enddate, screen_name):
    tweets_for_csv = []
    counter = 1
    begin = time.time()
    global api_auth
    # for tweet in tweepy.Cursor(api_auth.user_timeline, tweet_mode="extended", since_id=since_id, max_id=max_id, screen_name=screen_name).items():
    try:
        for tweet in tweepy.Cursor(api_auth.user_timeline, tweet_mode="extended", screen_name=screen_name).items():

            if enddate > tweet.created_at >= startdate:
                counter += 1
                if counter % 100 == 0:
                    round_end = time.time()
                    print("round: " + str(counter / 100) + "  time spent: " + str(round_end - begin))
                full_text, url = extended_tweet(tweet.id)
                tweets_for_csv.append([screen_name, tweet.id, full_text, url, json.dumps(tweet._json)])
                # print(tweets_for_csv[-1])
            elif tweet.created_at < startdate:
                # print(tweet.created_at)
                break
            else:
                # print(tweet.created_at)
                continue
    except tweepy.error.TweepError as e:
        print(e)
        print("Switching to new api_auth and sleep for 90 seconds......")
        time.sleep(90)
        new_developer_config = DeveloperConfig(consumer_key, consumer_secret, access_key, access_secret)
        # global api_auth
        api_auth = new_developer_config.api_auth
        get_tweets_daily(since_id, max_id, startdate, enddate, screen_name)
        return
    # timestamp = str(datetime.datetime.today().date()).replace('-', '_')
    timestamp = str(startdate.date()).replace('-', '_')

    folder_path = CURRENT_CONFIG['TWEETS_4HOUR_PATH'] + timestamp + "/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, 0o777)
    datetime_format = "%Y_%m_%d_%H"
    file_timestamp = str(startdate.strftime(datetime_format))
    outfile = folder_path + screen_name + '_' + file_timestamp + ".csv"

    print("{}: writing to {}".format(str(datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')), outfile))
    if len(tweets_for_csv) > 0:
        with open(outfile, 'a+', encoding="utf-8", newline='') as file:
            os.chmod(outfile, 0o700)
            writer = csv.writer(file, delimiter=',')
            writer.writerows(tweets_for_csv)
        os.chmod(outfile, 0o777)


def get_news_account(filepath):
    accounts = []
    with open(filepath, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
        for row in rows:
            user_name = str(row[0]).replace('@', '')
            accounts.append(user_name)
    return accounts


def get_zero_time(offset=1):
    now = datetime.datetime.now()
    zero_date = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                         microseconds=now.microsecond)
    end_date = zero_date - datetime.timedelta(days=offset - 1)
    start_date = zero_date - datetime.timedelta(days=offset)
    return start_date, end_date


def generate_time(offset=1, block=6):
    length_time = 24 / block
    now = datetime.datetime.now()
    zero_date = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                         microseconds=now.microsecond)
    # end_date = zero_date - datetime.timedelta(days=offset - 1)
    start_date = zero_date - datetime.timedelta(days=offset)
    end_time = start_date + datetime.timedelta(hours=length_time)
    time_list = [[start_date, end_time]]
    for i in range(block - 1):
        start_time = start_date + datetime.timedelta(hours=(i + 1) * length_time)
        end_time = start_date + datetime.timedelta(hours=(i + 2) * length_time)
        time_list.append([start_time, end_time])
    return time_list


def get_time_slot(offset=0):
    time_list_yesterday = generate_time(offset=offset+1)
    time_list_today = generate_time(offset=offset)
    current_time = datetime.datetime.now()
    # print(time_list_today[0][0], time_list_today[0][1])
    if time_list_today[0][0] <= current_time < time_list_today[0][1]:
        return [time_list_yesterday[5][0], time_list_yesterday[5][1]]
    else:
        for i in range(6 - 1):
            if time_list_today[i][1] <= current_time < time_list_today[i + 1][1]:
                print(time_list_today[i][0], 'to', time_list_today[i][1])
                return [time_list_today[i][0], time_list_today[i][1]]


def job_get_tweets():
    # time.sleep(1000)
    print('daily_get_tweets_job starting: ' + str(datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')))
    news_accounts_path = '../data/TwitterNewsAgencies.csv'
    dates = [1]
    for i in dates:
        # start_date, end_date = get_zero_time(i)
        start_time, end_time = get_time_slot()
        news_accounts = get_news_account(news_accounts_path)
        for news_account in news_accounts:
            try:
                get_tweets_daily(1, 2, start_time, end_time, news_account)
            except Exception as e:
                print(e)
    return

# if __name__ == '__main__':
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    job_get_tweets()
    scheduler.add_job(job_get_tweets, 'cron', hour=00, minute=2,
                      id='daily_get_tweets_job0_' + str(datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')))
    scheduler.start()


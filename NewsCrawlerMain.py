from handler.get_articles import create_article
from handler.get_tweets_timeline import job_get_tweets
from apscheduler.schedulers.blocking import BlockingScheduler


if __name__ == "__main__":
    """
    Start by BlockingScheduler, collecting tweets every 4 hours 
    and then crawling articles job
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(job_get_tweets, 'cron', hour='00,4,8,12,16,20', minute=2)
    scheduler.add_job(create_article, 'cron', hour='00,4,8,12,16,20', minute=50)
    scheduler.start()

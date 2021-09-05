# News Crawler



## Run system

The main entry of this project is NewsCrawlerMain.py, after configuring the environment and the corresponding parameters in config folder, use the following shell command and enter the dice password to run it for long period.

```shell
longjob -28day -c ./job.sh
```

## Project structure

> config
>
> > NewsConfig.py : get your Twitter API credentials and enter them here and path settings, etc.
> >
> > developer_config.py : Twitter API class
>
> data
>
> > TwitterNewsAgencies.csv: the accounts we choose to crawl
> >
> 
> handler
> 
> > get_articles.py: use extracted URLs to crawl
> >
> > get_tweets_timeline.py: get tweets timeline job
> >
>> save_to_solr.py: save articles and tweets to solr
> 
>job.sh : running job
> 
> NewsCrawlerMain.py: main entry of this project 
> 


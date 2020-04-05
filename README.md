# Pipeline_Tweetbot

- This pipeline project involves three Docker containers and a Metabase dashboard container that, in short, does:
  - Listens to tweets about a given keyword. User can set a maximum limit or stream continuously, depending on the keyword. Code is adapted from (https://github.com/pawlodkowski/twitter-mongoDB/blob/master/twitter_streamer.py).
  - Listened tweets are stored in a MongoDB.
  - An ETL job that takes Tweets and collects metadata into a Postgres DB.
  - A simple sentiment analysis is done via VaderSentiment to transform the tweet to sentiments and stored in the same table as tweets in Postgres DB.
  - A Metabase dashboard is built to visualize the geodata of the tweets with sentiments, composing the average sentiment per hour of the day and show a pie chart of the sentiment distribution among other stats. The Metabase dashboard can be reached via (localhost:3000) at the browser.
  - Finally, a Slackbot template is provided to post Slack messages to a specific channel. The user can modify the sentiment binning to post tweets in good, ok or bad sentiment.
- Whole project is wrapped up in an Airflow container to ensure a continuous monitor of the ETL job.

## Improvements to be Done
- Tweet collector needs to be improved to take:
  - User input about the keyword from the command line interface
  - Extracting meta location more reliably: the locations can be coarse grained to the country only.
  - It needs to be deployed to Airflow.
- A sentiment model can be trained on Tweets, though not necessary.

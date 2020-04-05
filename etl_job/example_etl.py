'''
The module etl.py extracts twitter data from a MongoDB database, transforms it
and loads it into a PostgreSQL database.
Thanks to Stefan!
'''
import time
import logging
import random
import re
import pymongo
from sqlalchemy import create_engine, exc
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


#MongoDB Setup
CLIENT = pymongo.MongoClient("mongodb")
DB = CLIENT.tweets

DATABASE_UP = False


## we could try and wait for a database connection to be established before continuing, the below code achieves this
while not DATABASE_UP:
    try:
        PG = create_engine('postgres://postgres:1234@postgresdb:5432')
        PG.execute('''DELETE FROM tweets;''')
        PG.execute('''CREATE TABLE IF NOT EXISTS tweets (
        id BIGSERIAL,
        tweet_id BIGSERIAL,
        text VARCHAR(512),
        sentiment NUMERIC
        );
        ''')
        # Postgres Meta Setup
        PG.execute('''CREATE TABLE IF NOT EXISTS tweets_meta_location (
        id BIGSERIAL,
        tweet_id BIGSERIAL,
        location VARCHAR(512),
        longitude REAL,
        latitude REAL
        );
        ''')
        PG.execute('''CREATE TABLE IF NOT EXISTS tweets_time (
        id BIGSERIAL,
        tweet_id BIGSERIAL,
        time TIMESTAMPTZ
        );
        ''')
        DATABASE_UP = True
    except exc.OperationalError:
        time.sleep(1)
        continue

s = SentimentIntensityAnalyzer()

def extract_all():
    """gets aLL tweets"""
    tweets = list(DB.Covid19.find())
    return tweets
    #if tweets:
    #    t = random.choice(tweets)
        #logging.critical("random tweet: " + t['text'])
    #    return t
def extract_random():
    """gets a random tweet"""
    tweets = list(DB.Covid19.find())
    if tweets:
        t = random.choice(tweets)
        logging.critical("random tweet: " + t['text'])
        return t

def extract_meta_location():
    tweets_with_location = list(DB.Covid19.find({'tweet_location': {"$exists": "true" }}))
    return tweets_with_location
    # if tweets_with_location:
    #     t = random.choice(tweets_with_location)
    #     return t

def pick_meta_location(tweets):
    for tweet in tweets:
        tweet_id = tweet['id']
        location = tweet['tweet_location']
        if len(location) > 1:
            p = PG.execute(f"""SELECT COUNT(tweet_id) FROM tweets_meta_location WHERE tweet_id = {tweet['id']};""").first()[0] #maybe convert to int
            if p == 0:
                location_new =location[0].replace("'", " ")
                PG.execute(f"""INSERT INTO tweets_meta_location (tweet_id, location, latitude, longitude) VALUES ({tweet_id}, '''{location_new}''', {location[1][0][0][0]},{location[1][0][0][1]});""")
        if len(location) == 1:
            p = PG.execute(f"""SELECT COUNT(tweet_id) FROM tweets_meta_location WHERE tweet_id = {tweet['id']};""").first()[0] #maybe convert to int
            if p == 0:
                location_new =location[0].replace("'", " ")
                PG.execute(f"""INSERT INTO tweets_meta_location (tweet_id, location, latitude, longitude) VALUES ({tweet_id}, '''{location_new}''', {0},{0});""")
        # else:
    #     PG.execute(f"""INSERT INTO tweets_meta_location (tweet_id, location, latitude, longitude) VALUES ({tweet_id}, '''NULL''', {0},{0});""")

def pick_meta_time(tweets):
    for tweet in tweets:
        tweet_id = tweet['id']
        tweet_time = tweet['tweet_created_at']
        t = PG.execute(f"""SELECT COUNT(tweet_id) FROM tweets_time WHERE tweet_id = {tweet['id']};""").first()[0] #maybe convert to int
        if t == 0:
            tweet_time =tweet_time.split()
            final_time = tweet_time[1]+'-'+tweet_time[2]+'-'+tweet_time[-1]+' '+tweet_time[3]+tweet_time[4][0:3]
            PG.execute(f"""INSERT INTO tweets_time (tweet_id, time) VALUES ({tweet_id}, '''{final_time}''');""")

def transform(tweet):
    #here we will insert the sentiment analysis results
    text = re.sub("'", "", tweet['text'])
    text = re.sub("%", "per cent", text)
    sentiment = s.polarity_scores(text)
    sentiment = sentiment['compound']
    return sentiment

def load(tweets):
    for tweet in tweets:
        tweet_id = tweet['id']
        text = re.sub("'", "", tweet['text'])
        text = re.sub("%", "per cent", text)
        s = PG.execute(f"""SELECT COUNT(tweet_id) FROM tweets WHERE tweet_id = {tweet_id};""").first()[0] #maybe convert to int
        if s == 0:
            sentiment_tweet = transform(tweet)
            PG.execute(f"""INSERT INTO tweets (tweet_id, text, sentiment) VALUES ({tweet_id}, '''{text}''', {sentiment_tweet});""")

# here we will define an Airflow task

logging.critical("Hello from the ETL job")

while True:
    tweet = extract_all()
    tweet2 = extract_meta_location()
    pick_meta_time(tweet)
    load(tweet)
    pick_meta_location(tweet2)
    time.sleep(10)


# while True:
#
#         #result = transform(tweet)
#         #load(result[0], result[1])
#     time.sleep(3)

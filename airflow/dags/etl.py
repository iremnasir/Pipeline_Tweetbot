from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import logging
import random
import pymongo
import re
from sqlalchemy import create_engine, exc
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


#MongoDB Setup
CLIENT = pymongo.MongoClient("mongodb")
DB = CLIENT.tweets


PG = create_engine('postgres://postgres:1234@postgresdb:5432')
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

s = SentimentIntensityAnalyzer()
def extract_all():
    """gets aLL tweets"""
    tweets = list(DB.Covid19.find())
    return tweets

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

def pick_meta_location(**context):
    extract_connection = context['task_instance']
    tweets = extract_connection.xcom_pull(task_ids="extract_meta_location")
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

def pick_meta_time(**context):
    extract_connection = context['task_instance']
    tweets = extract_connection.xcom_pull(task_ids="extract_all")
    for tweet in tweets:
        tweet_id = tweet['id']
        tweet_time = tweet['tweet_created_at']
        t = PG.execute(f"""SELECT COUNT(tweet_id) FROM tweets_time WHERE tweet_id = {tweet['id']};""").first()[0] #maybe convert to int
        if t == 0:
            tweet_time =tweet_time.split()
            final_time = tweet_time[1]+'-'+tweet_time[2]+'-'+tweet_time[-1]+' '+tweet_time[3]+tweet_time[4][0:3]
            PG.execute(f"""INSERT INTO tweets_time (tweet_id, time) VALUES ({tweet_id}, '''{final_time}''');""")

def transform(text):
    #here we will insert the sentiment analysis results
    text = re.sub("'", "", text)
    text = re.sub("%", "per cent", text)
    sentiment = s.polarity_scores(text)
    sentiment = sentiment['compound']
    return sentiment

def load(**context):
    extract_connection = context['task_instance']
    tweets = extract_connection.xcom_pull(task_ids="extract_all")
    for tweet in tweets:
        tweet_id = tweet['id']
        text = re.sub("'", "", tweet['text'])
        text = re.sub("%", "per cent", text)
        s = PG.execute(f"""SELECT COUNT(tweet_id) FROM tweets WHERE tweet_id = {tweet_id};""").first()[0] #maybe convert to int
        if s == 0:
            sentiment_tweet = transform(tweet['text'])
            PG.execute(f"""INSERT INTO tweets (tweet_id, text, sentiment) VALUES ({tweet_id}, '''{text}''', {sentiment_tweet});""")



##### 2. define default arguments #####
default_args = {
                'owner': 'airflow',
                'start_date': datetime(2020,4,3),
                #'end_date':
                'email': ['iremnasir@gmail.com'],
                'email_on_failure': False,
                'email_on_retry': False,
                "retries": 1,
                "retry_delay": timedelta(minutes=2)}

##### 3. instantiate a DAG #####
dag = DAG('etl', description='', catchup=False, schedule_interval=timedelta(minutes=10), default_args=default_args)

##### 4. create the tasks #####
t1 = PythonOperator(task_id='extract_all', python_callable=extract_all, dag=dag)
t3 = PythonOperator(task_id='extract_meta_location', python_callable=extract_meta_location, dag=dag)


t4 = PythonOperator(task_id='pick_meta_location', provide_context=True, python_callable=pick_meta_location, dag=dag)
t5 = PythonOperator(task_id='pick_meta_time', provide_context=True, python_callable=pick_meta_time, dag=dag)
t7 = PythonOperator(task_id='load', provide_context=True, python_callable=load, dag=dag)

##### 5. Set up dependencies #####
t1>>t7
t1>>t5
t3>>t4

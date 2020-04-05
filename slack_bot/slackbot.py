import slack
from sqlalchemy import create_engine
import time
from random import randint

oauth_token = "xoxb-944156563620-1031046221105-3CiFDNbaPFVdWQ0jll2iVcbY"

client = slack.WebClient(token=oauth_token)
PG = create_engine('postgres://postgres:1234@postgresdb:5432')


while True:
    tweet_result_disaster = PG.execute('''SELECT text FROM tweets WHERE sentiment < -0.3 ORDER BY random() LIMIT(1);''').fetchall()
    tweet_result_neutral = PG.execute('''SELECT text FROM tweets WHERE sentiment BETWEEN -0.29 AND 0.3 ORDER BY random() LIMIT(1);''').fetchall()
    tweet_result_ok = PG.execute('''SELECT text FROM tweets WHERE sentiment > 0.31 ORDER BY random() LIMIT(1);''').fetchall()
    value = randint(1, 3)
    if value == 1:
        response = client.chat_postMessage(channel='#slackymcchatty_1', text=f"Here is a disaster tweet:\n {tweet_result_disaster[0][0]}")
    if value == 2:
        response = client.chat_postMessage(channel='#slackymcchatty_1', text=f"Here is a not so bad tweet:\n {tweet_result_neutral[0][0]}")
    if value == 3:
        response = client.chat_postMessage(channel='#slackymcchatty_1', text=f"Here is a good tweet:\n {tweet_result_ok[0][0]}")

    time.sleep(60)

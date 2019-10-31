from os import listdir, path
import tweepy, json, time
import operator
from collections import OrderedDict
import emoji

def extract_emojis(str):
    return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)


auth = tweepy.OAuthHandler("PAKAd5cDFEvhlaMClRetKuX52", "Iva6kXk2bibYNMvzuKSuYnpTr4UZ9ri7hYuc3TELI2C3RQSfy4")
auth.set_access_token("16474279-FHQlTOkLnPW3xuNFMXd6ZrRkzzvojqtaxW0bJGFvn", "G5Ktm7XQvHXN7EynDLbdV1AtPTbY8CG29peFlj5R97gjn")

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)



files = listdir("./TweetScraper/Data/tweet/")
print(len(files), "files found.")




for id in files:
    if not path.exists('./json/'+id): print("Downloading...")
    if not path.exists('./json/'+id):
        tweet = api.get_status(id, tweet_mode='extended')
        json_data = tweet._json
        with open('./json/'+id, 'w+') as f:
            json.dump(json_data, f)





# process tweets
print("Processing...")


from os import listdir, path
from pprint import pprint
import json
from datetime import datetime

files = listdir("./json/")


google, sessions, workshops = [], [], []
session_tweets, workshop_tweets, _session_emojis, session_emojis = {}, {}, {}, {}

for f in files:
    with open("./json/"+f) as f:
        json_data = json.load(f)

    # get google links
    if len(json_data['entities']['urls']) > 0:
        for x in json_data['entities']['urls']:
            if "google" in x['expanded_url'].split("/")[2]: google.append(x['expanded_url'])

    # fix created date
    created_at = datetime.strptime(json_data['created_at'], '%a %b %d %H:%M:%S %z %Y')
    if(created_at.year == 2019 and created_at.month == 7):
        pass #created_at.day

    emojis = extract_emojis(json_data['full_text'])

    # track session tweets
    for x in json_data['entities']['hashtags']:
        session_low = x['text'].lower()

        if "s" in session_low[0] and session_low[-1].isdigit() and len(session_low) == 3: # we got a paper session
            sessions.append(session_low)
            if session_low not in session_tweets: session_tweets[session_low] = []
            session_tweets[session_low].append({
                'id': json_data['id_str'],
                'screen_name': json_data['user']['screen_name'],
                'user_name': json_data['user']['name'],
                'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'created_at_ts': int(created_at.timestamp()),
                'full_text': json_data['full_text'],
                'reply_to_status': json_data['in_reply_to_status_id_str'],
                'reply_to_user': json_data['in_reply_to_user_id_str']
            })

            if len(emojis) > 0: 
                if session_low not in _session_emojis: _session_emojis[session_low] = []
                _session_emojis[session_low].append(emojis)

        if "wkshp" in session_low: # we have a workshop session
            workshops.append(session_low)
            if session_low not in workshop_tweets: workshop_tweets[session_low] = []
            workshop_tweets[session_low].append({
                'id': json_data['id_str'],
                'screen_name': json_data['user']['screen_name'],
                'user_name': json_data['user']['name'],
                'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'created_at_ts': int(created_at.timestamp()),
                'full_text': json_data['full_text'],
                'reply_to_status': json_data['in_reply_to_status_id_str'],
                'reply_to_user': json_data['in_reply_to_user_id_str']
            })


for session, emoji_list in _session_emojis.items():
    if session not in session_emojis: session_emojis[session] = "".join(emoji_list)

d={}
for session in sessions: d[session] = d.get(session, 0) + 1
_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
# we have it sorted, we are not just using it yet
_d = OrderedDict(_d)

with open("web/_data/session-data.yml", "w+") as f:
    f.write("labels: " + str(list(_d.keys())) + "\ndata: " + str(list(_d.values())))

with open("web/_data/session-emojis.yml", "w+") as f:
    for session, emojis in session_emojis.items():
        f.write(f'"{session.upper()}": "{emojis}"\n')


with open("web/_data/session-tweets.yml", "w+") as f:
    f.write("---")
    for session, tweets in session_tweets.items():
        tweets = sorted(tweets, key = lambda i: i['created_at_ts']) 

        f.write(f"\n\n{session}:")
        for tweet in tweets:
            f.write(f'\n-')
            for key, value in tweet.items():
                if value is not None:
                    try:
                        value = value.replace('"', '\\"')
                        value = value.replace('\n', '<br />')
                    except:
                        pass
                    if key == "created_at" or key == "created_at_ts":
                        f.write(f'\n  {key}: {value}') # for dates, skip the quotation mark
                    else:
                        f.write(f'\n  {key}: "{value}"')





d={}
for session in workshops: d[session] = d.get(session, 0) + 1
with open("web/_data/workshop-data.yml", "w+") as f:
    f.write("labels: " + str(list(d.keys())) + "\ndata: " + str(list(d.values())))

with open("web/_data/workshop-tweets.yml", "w+") as f:
    f.write("---")
    for session, tweets in workshop_tweets.items():
        tweets = sorted(tweets, key = lambda i: i['created_at_ts']) 

        f.write(f"\n\n{session}:")
        for tweet in tweets:
            f.write(f'\n-')
            for key, value in tweet.items():
                if value is not None:
                    try:
                        value = value.replace('"', '\\"')
                        value = value.replace('\n', '<br />')
                    except:
                        pass
                    if key == "created_at" or key == "created_at_ts":
                        f.write(f'\n  {key}: {value}') # for dates, skip the quotation mark
                    else:
                        f.write(f'\n  {key}: "{value}"')




print("Done!")


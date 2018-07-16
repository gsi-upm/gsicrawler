import tweepy
import json
import os
import argparse
import time


def retrieve_tweets(query, filePath, count=200):

    consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
    consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]
    access_token = os.environ["TWITTER_ACCESS_TOKEN"]
    access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    max_tweets = count
    max_tweets = int(max_tweets)
    print(max_tweets)
    searched_tweets = []
    last_id = -1
    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1))
            if not new_tweets:
                break
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # depending on TweepError.code, one may want to retry or wait
            # to keep things simple, we will give up on an error
            break
    with open(filePath, 'a') as output:  
        final_tweets = []      
        for item in searched_tweets:
            jsontweet = json.dumps(item._json)
            tweet = json.loads(jsontweet)
            mytweet = {}
            #print(tweet)
        
            if tweet["in_reply_to_status_id"]:
                mytweet["_id"] = tweet["id"]
                mytweet["@type"] =  ["schema:BlogPosting","schema:Comment"]
                mytweet["@id"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet['user']['screen_name'], id=tweet["id"])
                mytweet["schema:about"] = query
                mytweet["schema:articleBody"] = tweet["text"]
                mytweet["schema:headline"] = tweet["text"]
                mytweet["schema:creator"] = tweet['user']['screen_name']
                mytweet["schema:author"] = 'twitter'
                mytweet["schema_datePublished"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
                mytweet["schema:parentItem"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet["in_reply_to_screen_name"], id=tweet["in_reply_to_status_id"])
                json.dump(mytweet, output)
                output.write('\n')
            else:
                mytweet["_id"] = tweet["id"]
                mytweet["@type"] =  "schema:BlogPosting"
                mytweet["@id"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet['user']['screen_name'], id=tweet["id"])
                mytweet["schema:about"] = query
                mytweet["schema:headline"] = tweet["text"]
                mytweet["schema:articleBody"] = tweet["text"]
                mytweet["schema:creator"] = tweet['user']['screen_name']
                mytweet["schema:author"] = 'twitter'
                mytweet["schema:datePublished"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

                #json.dump(mytweet, output)
                #output.write('\n')
                final_tweets.append(mytweet)
        return(final_tweets)

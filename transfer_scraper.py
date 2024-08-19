import tweepy
import re
import json
import csv
import gspread
import pprint


# authenticate to twitter
def authenticate():
    auth = tweepy.OAuthHandler("YGPP8hPJkPYORFE1Ng1UChwjB",
                               "V7k8BGt8vY7GSGhK6c26LMUQKyNDv9HvkhzsElCv3T4UL6djVy")
    auth.set_access_token("1304501171449737216-exR7VDevY82Xbsxn8DAa2HUmvMHVIo",
                          "L3j7LTtYAwGcad1fnrfAYWHteY2GZ3LkrvfPa0Hm4Xxxn")
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
        print("Authentication Success")
    except Exception as e:
        print("Authentication Failure")

    return api


def scrape_sheet():
    gc = gspread.service_account()
    book = gc.open("Transfer Rumour Guide")
    sheet = book.get_worksheet(0)

    with open('transfer_sources.csv', mode='w+', newline="\n") as transfer_sources:
        writer = csv.writer(transfer_sources, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Tier 1", "Tier 2", "Tier 3"])
        transfer_sources.flush()

        tier_1, tier_2, tier_3 = [], [], []
        for col in ['B', 'C']:
            for row in range(5, 35):
                name = sheet.acell(str(col) + str(row)).value
                if name:
                    if 5 <= row <= 8:
                        tier_1.append(name)
                    if 11 <= row <= 20:
                        tier_2.append(name)
                    if 24 <= row <= 34:
                        tier_3.append(name)

        sheet_contents = []
        for i in range(max(len(tier_1), len(tier_2), len(tier_3))):
            for tier_x in [tier_1, tier_2, tier_3]:
                try:
                    tier_x[i] = tier_x[i].split(" ")[0] + tier_x[i].split(" ")[1]
                    tier_x[i] = tier_x[i].split(",")[0]
                    tier_x[i] = tier_x[i].split("(")[0]
                    tier_x[i] = re.sub('KristofTerreur', 'HLNinEngeland', tier_x[i])
                    tier_x[i] = re.sub('JamesDucker', 'TelegraphDucker', tier_x[i])
                    tier_x[i] = re.sub('MohammedBouhafsi', 'mohamedbouhafsi', tier_x[i])
                except IndexError:
                    tier_x.append("")

            sheet_contents.append([tier_1[i], tier_2[i], tier_3[i]])
        rows = zip(sheet_contents)
        for r in rows:
            writer.writerows(r)
        transfer_sources.flush()


def choose_source(tier):
    sources = []
    header = 0
    if tier == 'Tier 1':
        header = 0
    elif tier == 'Tier 2':
        header = 1
    elif tier == 'Tier 3':
        header = 2
    with open('transfer_sources.csv', mode='r+', newline="\n") as transfer_sources:
        csv_reader = csv.reader(transfer_sources, delimiter=',')
        for row in csv_reader:
            if row[0] == 'Tier 1':
                continue
            sources.append(row[header])
    return sources


def scrape_source(api, source, keywords):
    user = api.get_user(source)
    print("\n" + user.name)
    print(user.description)

    tweet_objects = api.user_timeline(id=user.id, count=50, tweet_mode="extended")
    tweets_json = []
    for tweet in tweet_objects:
        json_init = json.dumps(tweet._json)
        tweets_json.append(json.loads(json_init))

    filtered_tweets = []
    for tweet in tweets_json:
        for keyword in keywords:
            if keyword in tweet['full_text']:
                filtered_tweets.append([tweet['id'],
                                        tweet['full_text'],
                                        tweet['user']['name'],
                                        tweet['user']['screen_name'],
                                        tweet['created_at']])
                break

    return filtered_tweets


def embed_tweets(tweets):
    embedded_tweets = []
    for tweet in tweets:
        try:
            template = '<blockquote class="twitter-tweet" data-conversation="none" data-cards="hidden"' \
                       ' data-align="center" data-dnt="true" data-theme="dark"><a href="https://twitter.com/' \
                       'screen_name/status/id?ref_src=twsrc%5Etfw"></a></blockquote> ' \
                       '<script async src="https://platform.twitter.com/' \
                       'widgets.js" charset="utf-8"></script>'
            embedded_tweet = re.sub('id\?', (str(tweet[0])+'?'), template)
            embedded_tweet = re.sub('screen_name', tweet[3], embedded_tweet)
            embedded_tweets.append(embedded_tweet)
        except IndexError:
            pass
    return embedded_tweets


def main():
    t_api = authenticate()
    source_choice = choose_source(tier="Tier 1")
    filtered_tweets = []
    for choice in source_choice:
        if choice == "":
            continue
        filtered = scrape_source(t_api, choice, keywords=['Chelsea', 'Havertz', 'Rice', 'Declan', 'Mendy'])
        filtered_tweets.extend(filtered)
    pprint.pprint(filtered_tweets)
    embedded_tweets = embed_tweets(filtered_tweets)
    print(embedded_tweets)


main()


'''bearer_token = "AAAAAAAAAAAAAAAAAAAAANSOHgEAAAAAGvB43NAVwU43mUvMfiWpH2J2d98%3DuGSq" \
               "NQc2OVooAZau5UdZU1kKsNJdZopd6hg9IW4ex9kiypS7Lz"'''
'''class MySnoopBot(tweepy.StreamListener):

    def __init__(self, api):
        super().__init__(api)
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        print(f"{tweet.user.name}:{tweet.text}")

    def on_error(self, status):
        print("Error detected")


tweets_listener = MyStreamListener(api)
stream = tweepy.Stream(api.auth, tweets_listener)
stream.filter(follow=330262748, track=["Rice", "Declan"], languages=["en"])'''
